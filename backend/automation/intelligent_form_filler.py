"""
Intelligent Form Filler
Automatically fills LinkedIn application forms with smart defaults for missing data
"""

import asyncio
import random
import re
from typing import Dict, List, Optional, Any
from playwright.async_api import Page, ElementHandle


class IntelligentFormFiller:
    """
    Fills LinkedIn Easy Apply forms with intelligent defaults and context-aware data
    """
    
    def __init__(self, page: Page, user_profile: Dict, resume_text: str = ""):
        """
        Initialize form filler
        
        Args:
            page: Playwright page object
            user_profile: User profile data dictionary
            resume_text: Resume text for extracting information
        """
        self.page = page
        self.user_profile = user_profile
        self.resume_text = resume_text
        
        # Extract additional info from resume
        self._extract_resume_data()
        
        # Smart defaults for common fields
        self._initialize_smart_defaults()
    
    def _extract_resume_data(self):
        """Extract useful information from resume text"""
        if not self.resume_text:
            return
        
        # Extract phone number
        phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', self.resume_text)
        if phone_match:
            # Normalize to the key used across the project
            if 'phone_number' not in self.user_profile:
                self.user_profile['phone_number'] = phone_match.group(0)
            # Back-compat for any code that still expects 'phone'
            if 'phone' not in self.user_profile:
                self.user_profile['phone'] = phone_match.group(0)
        
        # Extract LinkedIn profile URL
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', self.resume_text, re.IGNORECASE)
        if linkedin_match and 'linkedin_url' not in self.user_profile:
            self.user_profile['linkedin_url'] = f"https://{linkedin_match.group(0)}"
        
        # Extract GitHub URL
        github_match = re.search(r'github\.com/[\w-]+', self.resume_text, re.IGNORECASE)
        if github_match and 'github_url' not in self.user_profile:
            self.user_profile['github_url'] = f"https://{github_match.group(0)}"
        
        # Extract years of experience (rough estimate)
        experience_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience:?\s*(\d+)\+?\s*years?',
        ]
        for pattern in experience_patterns:
            match = re.search(pattern, self.resume_text, re.IGNORECASE)
            if match and 'years_experience' not in self.user_profile:
                self.user_profile['years_experience'] = match.group(1)
                break
    
    def _initialize_smart_defaults(self):
        """Initialize smart default answers for common questions"""
        self.smart_defaults = {
            # Work authorization
            'work_authorization': {
                'patterns': ['authorized to work', 'work authorization', 'legal authorization', 'visa status'],
                'answer': 'Yes'
            },
            
            # Sponsorship
            'sponsorship': {
                'patterns': ['require sponsorship', 'need sponsorship', 'visa sponsorship'],
                'answer': self.user_profile.get('requires_sponsorship', 'No')
            },

            # Will you now or in the future require sponsorship?
            'sponsorship_future': {
                'patterns': ['now or in the future require sponsorship', 'future sponsorship', 'require visa sponsorship'],
                'answer': self.user_profile.get('requires_sponsorship', 'No')
            },

            # Are you at least 18 years old?
            'age_18_plus': {
                'patterns': ['at least 18', '18 years old', 'over 18'],
                'answer': 'Yes'
            },
            
            # Years of experience
            'years_experience': {
                'patterns': ['years of experience', 'years experience', 'how many years'],
                'answer': self.user_profile.get('years_experience', '3')
            },
            
            # Start date
            'start_date': {
                'patterns': ['start date', 'available to start', 'when can you start', 'earliest start'],
                'answer': self.user_profile.get('start_date', 'Immediately')
            },
            
            # Salary expectations
            'salary': {
                'patterns': ['salary expectation', 'expected salary', 'compensation expectation'],
                'answer': self.user_profile.get('expected_salary', '')
            },
            
            # Notice period
            'notice_period': {
                'patterns': ['notice period', 'current notice', 'how much notice'],
                'answer': self.user_profile.get('notice_period', '2 weeks')
            },
            
            # Relocation
            'relocation': {
                'patterns': ['willing to relocate', 'open to relocation', 'relocate'],
                'answer': self.user_profile.get('willing_to_relocate', 'Yes')
            },
            
            # Remote work
            'remote_work': {
                'patterns': ['remote', 'work from home', 'hybrid'],
                'answer': 'Yes, I am open to remote, hybrid, or on-site work.'
            },
            
            # Currently employed
            'currently_employed': {
                'patterns': ['currently employed', 'are you employed', 'current employment'],
                'answer': self.user_profile.get('currently_employed', 'Yes')
            },
            
            # Referral
            'referral': {
                'patterns': ['referred by', 'referral', 'how did you hear'],
                'answer': 'LinkedIn'
            },
        }
    
    async def fill_application_form(self) -> Dict:
        """
        Fill entire application form with intelligent defaults
        
        Returns:
            Dict with fill status and field counts
        """
        print("\n📝 Filling application form with intelligent defaults...")
        
        filled_fields = 0
        skipped_fields = 0
        errors = []
        
        try:
            # Fill text inputs
            text_filled = await self._fill_text_inputs()
            filled_fields += text_filled
            
            # Fill text areas
            textarea_filled = await self._fill_textareas()
            filled_fields += textarea_filled
            
            # Select dropdowns
            dropdown_filled = await self._fill_dropdowns()
            filled_fields += dropdown_filled
            
            # Select radio buttons
            radio_filled = await self._fill_radio_buttons()
            filled_fields += radio_filled
            
            # Fill checkboxes
            checkbox_filled = await self._fill_checkboxes()
            filled_fields += checkbox_filled
            
            print(f"✅ Form filling complete: {filled_fields} fields filled")
            
            return {
                'status': 'SUCCESS',
                'filled_fields': filled_fields,
                'skipped_fields': skipped_fields,
                'errors': errors
            }
            
        except Exception as e:
            print(f"❌ Form filling error: {str(e)}")
            return {
                'status': 'FAILED',
                'filled_fields': filled_fields,
                'skipped_fields': skipped_fields,
                'errors': errors + [str(e)]
            }
    
    async def _fill_text_inputs(self) -> int:
        """Fill all text input fields"""
        filled = 0
        
        try:
            inputs = await self.page.query_selector_all('input[type="text"], input:not([type])')
            
            for input_elem in inputs:
                try:
                    # Skip if already filled
                    current_value = await input_elem.input_value()
                    if current_value and current_value.strip():
                        continue
                    
                    # Get label/placeholder to understand field
                    label = await self._get_field_label(input_elem)
                    placeholder = await input_elem.get_attribute('placeholder') or ""
                    
                    # Determine what to fill
                    value = self._get_smart_value_for_field(label, placeholder, 'text')
                    
                    if value:
                        await input_elem.fill(str(value))
                        await asyncio.sleep(random.uniform(0.3, 0.7))
                        filled += 1
                        print(f"   ✓ Filled: {label[:50]} = {str(value)[:30]}")
                        
                except Exception as e:
                    print(f"   ⚠️  Error filling input: {str(e)[:50]}")
                    continue
        
        except Exception as e:
            print(f"   ⚠️  Error processing text inputs: {str(e)}")
        
        return filled
    
    async def _fill_textareas(self) -> int:
        """Fill all textarea fields"""
        filled = 0
        
        try:
            textareas = await self.page.query_selector_all('textarea')
            
            for textarea in textareas:
                try:
                    # Skip if already filled
                    current_value = await textarea.input_value()
                    if current_value and len(current_value.strip()) > 20:
                        continue
                    
                    # Get label to understand field purpose
                    label = await self._get_field_label(textarea)
                    
                    # Get appropriate value (usually for cover letter or additional info)
                    value = self._get_smart_value_for_field(label, '', 'textarea')
                    
                    if value:
                        await textarea.fill(str(value))
                        await asyncio.sleep(random.uniform(0.5, 1))
                        filled += 1
                        print(f"   ✓ Filled textarea: {label[:50]}")
                        
                except Exception as e:
                    print(f"   ⚠️  Error filling textarea: {str(e)[:50]}")
                    continue
        
        except Exception as e:
            print(f"   ⚠️  Error processing textareas: {str(e)}")
        
        return filled
    
    async def _fill_dropdowns(self) -> int:
        """Fill all dropdown/select fields"""
        filled = 0
        
        try:
            selects = await self.page.query_selector_all('select')
            
            for select in selects:
                try:
                    # Get current selection
                    current_value = await select.input_value()
                    if current_value:
                        continue
                    
                    # Get label
                    label = await self._get_field_label(select)
                    
                    # Get options
                    options = await select.query_selector_all('option')
                    option_texts = []
                    option_values = []
                    
                    for option in options:
                        text = await option.inner_text()
                        value = await option.get_attribute('value') or ""
                        if text.strip() and value:
                            option_texts.append(text.strip())
                            option_values.append(value)
                    
                    if not option_values:
                        continue
                    
                    # Select smart option
                    selected_value = self._select_smart_option(label, option_texts, option_values)
                    
                    if selected_value:
                        await select.select_option(selected_value)
                        await asyncio.sleep(random.uniform(0.3, 0.7))
                        filled += 1
                        print(f"   ✓ Selected: {label[:50]} = {selected_value}")
                        
                except Exception as e:
                    print(f"   ⚠️  Error filling dropdown: {str(e)[:50]}")
                    continue
        
        except Exception as e:
            print(f"   ⚠️  Error processing dropdowns: {str(e)}")
        
        return filled
    
    async def _fill_radio_buttons(self) -> int:
        """Fill radio button groups"""
        filled = 0
        
        try:
            # Get all radio buttons
            radios = await self.page.query_selector_all('input[type="radio"]')
            
            # Group by name attribute
            radio_groups: Dict[str, List[ElementHandle]] = {}
            for radio in radios:
                name = await radio.get_attribute('name')
                if name:
                    if name not in radio_groups:
                        radio_groups[name] = []
                    radio_groups[name].append(radio)
            
            # Process each group
            for group_name, group_radios in radio_groups.items():
                try:
                    # Check if already selected
                    already_selected = False
                    for radio in group_radios:
                        if await radio.is_checked():
                            already_selected = True
                            break
                    
                    if already_selected:
                        continue
                    
                    # Get label for the group
                    label = await self._get_field_label(group_radios[0])
                    
                    # Get all option labels
                    option_labels = []
                    for radio in group_radios:
                        radio_label = await self._get_radio_label(radio)
                        option_labels.append(radio_label)
                    
                    # Select smart option
                    best_index = self._select_smart_radio_option(label, option_labels)
                    
                    if best_index is not None and best_index < len(group_radios):
                        await group_radios[best_index].click()
                        await asyncio.sleep(random.uniform(0.3, 0.7))
                        filled += 1
                        print(f"   ✓ Selected radio: {label[:50]} = {option_labels[best_index]}")
                        
                except Exception as e:
                    print(f"   ⚠️  Error filling radio group: {str(e)[:50]}")
                    continue
        
        except Exception as e:
            print(f"   ⚠️  Error processing radio buttons: {str(e)}")
        
        return filled
    
    async def _fill_checkboxes(self) -> int:
        """Fill checkboxes (usually agreements/certifications)"""
        filled = 0
        
        try:
            checkboxes = await self.page.query_selector_all('input[type="checkbox"]')
            
            for checkbox in checkboxes:
                try:
                    # Skip if already checked
                    if await checkbox.is_checked():
                        continue
                    
                    # Get label
                    label = await self._get_field_label(checkbox)
                    label_lower = label.lower()
                    
                    # Only check if it's an agreement or certification
                    # Don't check subscription/marketing checkboxes
                    should_check = any(word in label_lower for word in [
                        'certif', 'agree', 'consent', 'acknowledge', 'confirm',
                        'understand', 'accurate', 'complete'
                    ])
                    
                    should_not_check = any(word in label_lower for word in [
                        'subscribe', 'marketing', 'newsletter', 'promotional', 'updates'
                    ])
                    
                    if should_check and not should_not_check:
                        await checkbox.click()
                        await asyncio.sleep(random.uniform(0.3, 0.5))
                        filled += 1
                        print(f"   ✓ Checked: {label[:50]}")
                        
                except Exception as e:
                    print(f"   ⚠️  Error filling checkbox: {str(e)[:50]}")
                    continue
        
        except Exception as e:
            print(f"   ⚠️  Error processing checkboxes: {str(e)}")
        
        return filled
    
    async def _get_field_label(self, element: ElementHandle) -> str:
        """Get label text for a form field"""
        try:
            # Try to find associated label
            field_id = await element.get_attribute('id')
            if field_id:
                label = await self.page.query_selector(f'label[for="{field_id}"]')
                if label:
                    return (await label.inner_text()).strip()
            
            # Try parent label
            parent = await element.evaluate_handle('el => el.closest("label")')
            if parent:
                return (await parent.inner_text()).strip()
            
            # Try aria-label
            aria_label = await element.get_attribute('aria-label')
            if aria_label:
                return aria_label
            
            # Try name attribute
            name = await element.get_attribute('name')
            if name:
                return name
            
            return ""
        except:
            return ""
    
    async def _get_radio_label(self, radio: ElementHandle) -> str:
        """Get label for a radio button"""
        try:
            # Get associated label
            radio_id = await radio.get_attribute('id')
            if radio_id:
                label = await self.page.query_selector(f'label[for="{radio_id}"]')
                if label:
                    return (await label.inner_text()).strip()
            
            # Try value attribute
            value = await radio.get_attribute('value')
            if value:
                return value
            
            return ""
        except:
            return ""
    
    def _get_smart_value_for_field(self, label: str, placeholder: str, field_type: str) -> Any:
        """Get smart value for a field based on label/placeholder"""
        label_lower = (label + " " + placeholder).lower()
        
        # Check smart defaults
        for field_name, field_info in self.smart_defaults.items():
            if any(pattern in label_lower for pattern in field_info['patterns']):
                return field_info['answer']
        
        # Field-specific matching
        if 'first name' in label_lower:
            return self.user_profile.get('first_name', '')
        elif 'last name' in label_lower:
            return self.user_profile.get('last_name', '')
        elif 'email' in label_lower:
            return self.user_profile.get('email', '')
        elif 'phone' in label_lower:
            return self.user_profile.get('phone_number', '') or self.user_profile.get('phone', '')
        elif 'city' in label_lower or 'location' in label_lower:
            return self.user_profile.get('city', '')
        elif 'linkedin' in label_lower and 'url' in label_lower:
            return self.user_profile.get('linkedin_url', '')
        elif 'github' in label_lower or 'portfolio' in label_lower:
            return self.user_profile.get('github_url', '')
        elif 'website' in label_lower:
            return self.user_profile.get('website', '')
        
        return None
    
    def _select_smart_option(self, label: str, option_texts: List[str], option_values: List[str]) -> Optional[str]:
        """Select smart option from dropdown"""
        label_lower = label.lower()
        
        # Match based on label
        for field_name, field_info in self.smart_defaults.items():
            if any(pattern in label_lower for pattern in field_info['patterns']):
                answer = field_info['answer']
                
                # Find matching option
                for i, text in enumerate(option_texts):
                    if str(answer).lower() in text.lower() or text.lower() in str(answer).lower():
                        return option_values[i]
        
        # Default: select first non-empty, non-placeholder option
        for i, text in enumerate(option_texts):
            if text.lower() not in ['select', 'choose', 'pick one', '-- select --', '']:
                return option_values[i]
        
        return None
    
    def _select_smart_radio_option(self, label: str, option_labels: List[str]) -> Optional[int]:
        """Select smart radio button option"""
        label_lower = label.lower()
        
        # Match based on label
        for field_name, field_info in self.smart_defaults.items():
            if any(pattern in label_lower for pattern in field_info['patterns']):
                answer = str(field_info['answer']).lower()
                
                # Find matching option
                for i, option_text in enumerate(option_labels):
                    if answer in option_text.lower() or option_text.lower() in answer:
                        return i
        
        # Default: select first "yes" option if available
        for i, option_text in enumerate(option_labels):
            if option_text.lower() in ['yes', 'y', 'true', 'agree']:
                return i
        
        # Fallback: select first option
        return 0 if option_labels else None
