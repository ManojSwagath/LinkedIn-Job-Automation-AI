import { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { 
  Search, MapPin, Briefcase, GraduationCap, DollarSign, 
  Clock, Zap, ArrowLeft, Play, Save, Upload, FileText 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { useRunAgent } from "@/hooks/useJobAutomation";

const JobSearchConfig = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const runAgentMutation = useRunAgent();
  
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [searchConfig, setSearchConfig] = useState({
    keywords: "",
    location: "Remote",
    skills: "",
    jobType: "Full-time",
    experienceLevel: "Mid-level",
    salaryRange: "Any",
    maxJobs: 15,
    maxApplications: 5,
    linkedinEmail: "",
    linkedinPassword: "",
    autoApply: true,
    similarityThreshold: 0.6
  });

  const handleChange = (field: string, value: any) => {
    setSearchConfig(prev => ({ ...prev, [field]: value }));
  };

  const handleStartAutomation = async () => {
    // Validation
    if (!searchConfig.keywords.trim()) {
      toast({
        title: "Keywords required",
        description: "Please enter job keywords to search for",
        variant: "destructive"
      });
      return;
    }

    if (!searchConfig.linkedinEmail || !searchConfig.linkedinPassword) {
      toast({
        title: "LinkedIn credentials required",
        description: "Please enter your LinkedIn email and password",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);

    try {
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      
      const response = await fetch(`${API_BASE_URL}/api/run-agent`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(searchConfig)
      });

      if (!response.ok) {
        throw new Error('Failed to start automation');
      }

      const result = await response.json();

      toast({
        title: "Automation Started! 🚀",
        description: "Your LinkedIn automation agent is now running. You'll see a browser window open and start searching for jobs.",
      });

      // Navigate back to dashboard
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);

    } catch (error) {
      console.error('Error starting automation:', error);
      toast({
        title: "Failed to start automation",
        description: error instanceof Error ? error.message : "Unknown error occurred",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = () => {
    localStorage.setItem('jobSearchConfig', JSON.stringify(searchConfig));
    toast({
      title: "Configuration saved",
      description: "Your search preferences have been saved"
    });
  };

  // Load saved config
  useState(() => {
    const saved = localStorage.getItem('jobSearchConfig');
    if (saved) {
      setSearchConfig(JSON.parse(saved));
    }
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate('/dashboard')}
        >
          <ArrowLeft className="w-5 h-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Configure Job Search</h1>
          <p className="text-muted-foreground mt-1">
            Set your preferences and let AI find and apply to jobs automatically
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Configuration Form */}
        <div className="lg:col-span-2 space-y-6">
          {/* Job Criteria */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Card variant="glass">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="w-5 h-5" />
                  Job Search Criteria
                </CardTitle>
                <CardDescription>
                  What kind of job are you looking for?
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="keywords">Job Keywords *</Label>
                  <Input
                    id="keywords"
                    placeholder="e.g., Software Engineer, Frontend Developer, React"
                    value={searchConfig.keywords}
                    onChange={(e) => handleChange('keywords', e.target.value)}
                    className="mt-1.5"
                  />
                  <p className="text-xs text-muted-foreground mt-1.5">
                    Separate multiple keywords with commas
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      placeholder="e.g., Remote, New York, San Francisco"
                      value={searchConfig.location}
                      onChange={(e) => handleChange('location', e.target.value)}
                      className="mt-1.5"
                    />
                  </div>

                  <div>
                    <Label htmlFor="jobType">Job Type</Label>
                    <Select
                      value={searchConfig.jobType}
                      onValueChange={(value) => handleChange('jobType', value)}
                    >
                      <SelectTrigger className="mt-1.5">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Full-time">Full-time</SelectItem>
                        <SelectItem value="Part-time">Part-time</SelectItem>
                        <SelectItem value="Contract">Contract</SelectItem>
                        <SelectItem value="Internship">Internship</SelectItem>
                        <SelectItem value="Any">Any</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="experienceLevel">Experience Level</Label>
                    <Select
                      value={searchConfig.experienceLevel}
                      onValueChange={(value) => handleChange('experienceLevel', value)}
                    >
                      <SelectTrigger className="mt-1.5">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Entry-level">Entry-level</SelectItem>
                        <SelectItem value="Mid-level">Mid-level</SelectItem>
                        <SelectItem value="Senior">Senior</SelectItem>
                        <SelectItem value="Lead">Lead</SelectItem>
                        <SelectItem value="Any">Any</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="maxResults">Max Results</Label>
                    <Input
                      id="maxResults"
                      type="number"
                      min="1"
                      max="100"
                      value={searchConfig.maxResults}
                      onChange={(e) => handleChange('maxResults', parseInt(e.target.value))}
                      className="mt-1.5"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 rounded-lg bg-primary/10 border border-primary/20">
                  <div className="flex items-center gap-3">
                    <Zap className="w-5 h-5 text-primary" />
                    <div>
                      <Label htmlFor="easyApply" className="cursor-pointer">Easy Apply Only</Label>
                      <p className="text-xs text-muted-foreground">
                        Only apply to jobs with Easy Apply button
                      </p>
                    </div>
                  </div>
                  <Switch
                    id="easyApply"
                    checked={searchConfig.easyApplyOnly}
                    onCheckedChange={(checked) => handleChange('easyApplyOnly', checked)}
                  />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* LinkedIn Credentials */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card variant="glass">
              <CardHeader>
                <CardTitle>LinkedIn Credentials</CardTitle>
                <CardDescription>
                  Required to automate job applications (stored securely, not saved on server)
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="linkedinEmail">LinkedIn Email *</Label>
                  <Input
                    id="linkedinEmail"
                    type="email"
                    placeholder="your@email.com"
                    value={searchConfig.linkedinEmail}
                    onChange={(e) => handleChange('linkedinEmail', e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                <div>
                  <Label htmlFor="linkedinPassword">LinkedIn Password *</Label>
                  <Input
                    id="linkedinPassword"
                    type="password"
                    placeholder="••••••••"
                    value={searchConfig.linkedinPassword}
                    onChange={(e) => handleChange('linkedinPassword', e.target.value)}
                    className="mt-1.5"
                  />
                </div>

                <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                  <p className="text-sm text-yellow-500">
                    🔒 Your credentials are never stored on our servers. They are only used temporarily for automation.
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Automation Settings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card variant="glass">
              <CardHeader>
                <CardTitle>Automation Settings</CardTitle>
                <CardDescription>
                  Control how the agent applies to jobs
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 rounded-lg bg-white/5">
                  <div>
                    <Label htmlFor="autoSubmit" className="cursor-pointer">Auto-Submit Applications</Label>
                    <p className="text-xs text-muted-foreground mt-1">
                      Automatically submit applications (recommended: preview first)
                    </p>
                  </div>
                  <Switch
                    id="autoSubmit"
                    checked={searchConfig.autoSubmit}
                    onCheckedChange={(checked) => handleChange('autoSubmit', checked)}
                  />
                </div>

                <div>
                  <Label htmlFor="minMatchScore">Minimum Match Score: {Math.round(searchConfig.minMatchScore * 100)}%</Label>
                  <Input
                    id="minMatchScore"
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={searchConfig.minMatchScore}
                    onChange={(e) => handleChange('minMatchScore', parseFloat(e.target.value))}
                    className="mt-2"
                  />
                  <p className="text-xs text-muted-foreground mt-1.5">
                    Only apply to jobs that match at least {Math.round(searchConfig.minMatchScore * 100)}% of your profile
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Sidebar - Summary & Actions */}
        <div className="space-y-6">
          {/* Summary */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Card variant="glow">
              <CardHeader>
                <CardTitle className="text-lg">Ready to Start?</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Searching for:</span>
                    <span className="font-medium">{searchConfig.keywords || "Not set"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Location:</span>
                    <span className="font-medium">{searchConfig.location}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Easy Apply:</span>
                    <span className="font-medium">{searchConfig.easyApplyOnly ? "Yes" : "No"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Auto-Submit:</span>
                    <span className="font-medium">{searchConfig.autoSubmit ? "Yes" : "No"}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Max Jobs:</span>
                    <span className="font-medium">{searchConfig.maxResults}</span>
                  </div>
                </div>

                <div className="pt-4 border-t border-white/10 space-y-3">
                  <Button
                    variant="hero"
                    className="w-full"
                    size="lg"
                    onClick={handleStartAutomation}
                    disabled={loading}
                  >
                    <Play className="w-5 h-5" />
                    {loading ? "Starting..." : "Start Automation"}
                  </Button>

                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={handleSaveConfig}
                  >
                    <Save className="w-4 h-4" />
                    Save Configuration
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Info */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">How it works</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-muted-foreground">
                <div className="flex gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center flex-shrink-0 text-xs font-bold">
                    1
                  </div>
                  <p>Agent logs into LinkedIn using your credentials</p>
                </div>
                <div className="flex gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center flex-shrink-0 text-xs font-bold">
                    2
                  </div>
                  <p>Searches for jobs matching your criteria</p>
                </div>
                <div className="flex gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center flex-shrink-0 text-xs font-bold">
                    3
                  </div>
                  <p>AI analyzes each job and matches with your resume</p>
                </div>
                <div className="flex gap-3">
                  <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center flex-shrink-0 text-xs font-bold">
                    4
                  </div>
                  <p>Automatically applies to matching Easy Apply jobs</p>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default JobSearchConfig;
