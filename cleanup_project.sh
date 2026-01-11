#!/bin/bash

################################################################################
# LinkedIn Job Automation - Project Cleanup Script
# This script organizes the project structure by:
# 1. Deleting all .md files except README.md
# 2. Moving frontend files to frontend/
# 3. Moving backend files to backend/
# 4. Creating scripts/ folder for all .sh files
# 5. Removing unnecessary files
################################################################################

set -e  # Exit on error

PROJECT_ROOT="/Users/sathwikadigoppula/Documents/GitHub/LinkedIn-Job-Automation-with-AI"
cd "$PROJECT_ROOT"

echo "=================================="
echo "🧹 LinkedIn Automation Cleanup"
echo "=================================="
echo ""
echo "⚠️  WARNING: This will delete files!"
echo "   Creating backup first..."
echo ""

# Create backup
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "📦 Backup location: $BACKUP_DIR"

# Function to safely delete files
safe_delete() {
    local file=$1
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/" 2>/dev/null || true
        rm "$file"
        echo "  ✓ Deleted: $file"
    fi
}

# Function to safely move files
safe_move() {
    local source=$1
    local dest=$2
    if [ -f "$source" ]; then
        cp "$source" "$BACKUP_DIR/" 2>/dev/null || true
        mv "$source" "$dest"
        echo "  ✓ Moved: $source → $dest"
    fi
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Delete .md files (keep README.md)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Delete all .md files except README.md
for md_file in *.md; do
    if [ "$md_file" != "README.md" ] && [ -f "$md_file" ]; then
        safe_delete "$md_file"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Organize Shell Scripts"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create scripts directory if it doesn't exist
mkdir -p scripts

# Move all .sh files to scripts/
for sh_file in *.sh; do
    if [ -f "$sh_file" ]; then
        # Skip this cleanup script itself
        if [ "$sh_file" != "cleanup_project.sh" ]; then
            safe_move "$sh_file" "scripts/$sh_file"
        fi
    fi
done

# Make all shell scripts executable
chmod +x scripts/*.sh 2>/dev/null || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Organize Test Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create tests directory if it doesn't exist
mkdir -p tests

# Move test files to tests/ (if they're in root)
for test_file in test_*.py debug_*.py; do
    if [ -f "$test_file" ]; then
        safe_move "$test_file" "tests/$test_file"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Clean Up Log Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Move logs to data/logs/
mkdir -p data/logs

for log_file in *.log; do
    if [ -f "$log_file" ]; then
        safe_move "$log_file" "data/logs/$log_file"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Clean Up Unnecessary Files"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Remove .DS_Store files (macOS)
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
echo "  ✓ Removed .DS_Store files"

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "  ✓ Removed __pycache__ directories"

# Remove .pyc files
find . -name "*.pyc" -type f -delete 2>/dev/null || true
echo "  ✓ Removed .pyc files"

# Clean up backup environment files (keep .env, .env.example)
if [ -f ".env.backup" ]; then
    safe_delete ".env.backup"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6: Verify Structure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if directories exist
echo "📁 Directory Structure:"
echo ""
echo "  Root files:"
[ -f "README.md" ] && echo "    ✓ README.md"
[ -f ".env" ] && echo "    ✓ .env"
[ -f ".gitignore" ] && echo "    ✓ .gitignore"
[ -f "requirements.txt" ] && echo "    ✓ requirements.txt"
[ -f "pyrightconfig.json" ] && echo "    ✓ pyrightconfig.json"

echo ""
echo "  Directories:"
[ -d "backend" ] && echo "    ✓ backend/"
[ -d "frontend" ] && echo "    ✓ frontend/"
[ -d "scripts" ] && echo "    ✓ scripts/ ($(ls -1 scripts/*.sh 2>/dev/null | wc -l | tr -d ' ') shell scripts)"
[ -d "tests" ] && echo "    ✓ tests/ ($(ls -1 tests/*.py 2>/dev/null | wc -l | tr -d ' ') test files)"
[ -d "data" ] && echo "    ✓ data/"
[ -d "docs" ] && echo "    ✓ docs/"
[ -d "venv" ] && echo "    ✓ venv/"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CLEANUP COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📦 Backup saved to: $BACKUP_DIR"
echo "   (You can delete this folder once you verify everything works)"
echo ""
echo "🎯 Next Steps:"
echo "   1. Review the changes"
echo "   2. Test the application: cd scripts && ./quick_start.sh"
echo "   3. If everything works, delete backup: rm -rf $BACKUP_DIR"
echo ""
