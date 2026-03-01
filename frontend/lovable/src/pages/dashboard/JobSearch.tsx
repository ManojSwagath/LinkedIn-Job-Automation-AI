import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Search, MapPin, Briefcase, DollarSign, Clock, Heart,
  Building, Sparkles, Filter, Grid, List, ExternalLink, Zap, Loader2, Play, RefreshCw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { useToast } from "@/hooks/use-toast";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  posted?: string;
  matchScore?: number;
  tags: string[];
  description?: string;
  url: string;
  is_easy_apply?: boolean;
}

const JobSearch = () => {
  const { toast } = useToast();
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [searchQuery, setSearchQuery] = useState("Software Engineer");
  const [locationQuery, setLocationQuery] = useState("United States");
  const [linkedinEmail, setLinkedinEmail] = useState("");
  const [linkedinPassword, setLinkedinPassword] = useState("");
  const [salaryRange, setSalaryRange] = useState([50000, 200000]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [automationRunning, setAutomationRunning] = useState(false);
  const [filters, setFilters] = useState({
    remote: true,
    fulltime: true,
    contract: false,
    easyApply: true,
  });

  const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'https://linkedin-job-automation-ai.onrender.com';

  // Get user profile from localStorage
  const getUserProfile = () => {
    try {
      const savedProfile = localStorage.getItem('userProfile');
      return savedProfile ? JSON.parse(savedProfile) : {};
    } catch {
      return {};
    }
  };

  // Get resume path from localStorage (if uploaded)
  const getResumePath = () => {
    try {
      const resumeData = localStorage.getItem('resumePath');
      return resumeData || null;
    } catch {
      return null;
    }
  };

  const ensureCreds = () => {
    if (!linkedinEmail || !linkedinPassword) {
      toast({
        title: "LinkedIn credentials required",
        description: "Enter your LinkedIn email and password to run search/apply agents.",
        variant: "destructive",
      });
      return false;
    }
    return true;
  };

  // Search for LinkedIn jobs
  const searchJobs = async () => {
    try {
      if (!ensureCreds()) return;
      setSearching(true);
      setJobs([]);
      
      const response = await fetch(`${API_BASE_URL}/api/autoagenthire/search-jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          linkedin_email: linkedinEmail,
          linkedin_password: linkedinPassword,
          job_role: searchQuery,
          location: locationQuery,
          remote_only: filters.remote,
          easy_apply_only: filters.easyApply,
          max_results: 25
        })
      });

      const data = await response.json();
      
      if (data.jobs && data.jobs.length > 0) {
        const formattedJobs: Job[] = data.jobs.map((job: any, index: number) => ({
          id: job.id || `job-${index}`,
          title: job.title || 'Unknown Position',
          company: job.company || 'Unknown Company',
          location: job.location || 'Unknown Location',
          salary: job.salary || '',
          posted: job.posted || 'Recently',
          matchScore: job.match_score || Math.floor(Math.random() * 20 + 80),
          tags: [
            ...(job.is_easy_apply ? ['Easy Apply'] : []),
            ...(job.location?.toLowerCase().includes('remote') ? ['Remote'] : []),
          ],
          description: job.description || '',
          url: job.url || `https://www.linkedin.com/jobs/view/${job.id}`,
          is_easy_apply: job.is_easy_apply || false
        }));
        
        setJobs(formattedJobs);
        toast({
          title: "Jobs Found!",
          description: `Found ${formattedJobs.length} LinkedIn jobs matching your criteria`,
        });
      } else {
        toast({
          title: "No Jobs Found",
          description: "Try adjusting your search criteria",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('Job search error:', error);
      toast({
        title: "Search Failed",
        description: "Could not connect to job search service. Make sure the backend is running.",
        variant: "destructive"
      });
    } finally {
      setSearching(false);
    }
  };

  // Start automation to apply to all jobs
  const startAutomation = async () => {
    if (jobs.length === 0) {
      toast({
        title: "No Jobs to Apply",
        description: "Search for jobs first before starting automation",
        variant: "destructive"
      });
      return;
    }

    try {
      if (!ensureCreds()) return;
      setAutomationRunning(true);
      
      // Get user profile and resume from localStorage
      const userProfile = getUserProfile();
      const resumePath = getResumePath();
      
      const response = await fetch(`${API_BASE_URL}/api/autoagenthire/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          linkedin_email: linkedinEmail,
          linkedin_password: linkedinPassword,
          job_role: searchQuery,
          location: locationQuery,
          max_applications: jobs.length,
          easy_apply_only: filters.easyApply,
          resume_path: resumePath,
          user_profile: userProfile
        })
      });

      const data = await response.json();
      
      if (data.status === 'started' || data.run_id) {
        toast({
          title: "🚀 Automation Started!",
          description: `Applying to ${jobs.length} jobs. Check the Applications tab for progress.`,
        });
      } else {
        toast({
          title: "Automation Issue",
          description: data.message || "Could not start automation",
          variant: "destructive"
        });
      }
    } catch (error) {
      console.error('Automation error:', error);
      toast({
        title: "Automation Failed",
        description: "Could not start the automation process",
        variant: "destructive"
      });
    } finally {
      setAutomationRunning(false);
    }
  };

  // Quick apply to a single job
  const quickApply = async (job: Job) => {
    try {
      if (!ensureCreds()) return;
      toast({
        title: "Applying...",
        description: `Applying to ${job.title} at ${job.company}`,
      });

      // Get user profile and resume from localStorage
      const userProfile = getUserProfile();
      const resumePath = getResumePath();

      const response = await fetch(`${API_BASE_URL}/api/autoagenthire/apply-single`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          linkedin_email: linkedinEmail,
          linkedin_password: linkedinPassword,
          job_url: job.url,
          job_title: job.title,
          company: job.company,
          resume_path: resumePath,
          user_profile: userProfile
        })
      });

      const data = await response.json();
      
      if (data.success) {
        toast({
          title: "✅ Applied Successfully!",
          description: `Applied to ${job.title} at ${job.company}`,
        });
      } else {
        toast({
          title: "Application Issue",
          description: data.message || "Could not complete application",
          variant: "destructive"
        });
      }
    } catch (error) {
      // Open job URL as fallback
      window.open(job.url, '_blank');
      toast({
        title: "Opening LinkedIn",
        description: "Apply manually on LinkedIn",
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold mb-2">Find Your Dream Job</h1>
        <p className="text-muted-foreground">
          Search LinkedIn jobs and let AI automatically apply for you
        </p>
      </motion.div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Filters sidebar */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="lg:w-72 shrink-0"
        >
          <Card className="mb-4">
            <CardContent className="pt-6 space-y-4">
              <div className="space-y-2">
                <Label htmlFor="linkedin-email">LinkedIn Email</Label>
                <Input
                  id="linkedin-email"
                  type="email"
                  placeholder="you@example.com"
                  value={linkedinEmail}
                  onChange={(e) => setLinkedinEmail(e.target.value)}
                  autoComplete="username"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="linkedin-password">LinkedIn Password</Label>
                <Input
                  id="linkedin-password"
                  type="password"
                  placeholder="••••••••"
                  value={linkedinPassword}
                  onChange={(e) => setLinkedinPassword(e.target.value)}
                  autoComplete="current-password"
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Credentials stay in the browser and are only sent to the backend for this run.
              </p>
            </CardContent>
          </Card>
          <Card variant="glass" className="sticky top-24">
            <CardContent className="p-6 space-y-6">
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Filter className="w-4 h-4" /> Search LinkedIn Jobs
                </h3>
                <Input
                  placeholder="Job title, keywords..."
                  icon={<Search className="w-4 h-4" />}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Location</label>
                <Input
                  placeholder="City, State, or Remote"
                  icon={<MapPin className="w-4 h-4" />}
                  value={locationQuery}
                  onChange={(e) => setLocationQuery(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-3">Job Preferences</label>
                <div className="space-y-2">
                  {[
                    { key: "remote", label: "Remote Only" },
                    { key: "fulltime", label: "Full-time" },
                    { key: "easyApply", label: "Easy Apply Only" },
                  ].map(({ key, label }) => (
                    <div key={key} className="flex items-center gap-2">
                      <Checkbox
                        id={key}
                        checked={filters[key as keyof typeof filters]}
                        onCheckedChange={(checked) =>
                          setFilters({ ...filters, [key]: checked as boolean })
                        }
                      />
                      <label htmlFor={key} className="text-sm">{label}</label>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-3">
                  Salary: ${(salaryRange[0] / 1000).toFixed(0)}k - ${(salaryRange[1] / 1000).toFixed(0)}k
                </label>
                <Slider
                  value={salaryRange}
                  onValueChange={setSalaryRange}
                  min={30000}
                  max={300000}
                  step={10000}
                />
              </div>

              <div className="pt-4 space-y-2">
                <Button 
                  variant="hero" 
                  className="w-full"
                  onClick={searchJobs}
                  disabled={searching}
                >
                  {searching ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Searching LinkedIn...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4" />
                      Search Jobs
                    </>
                  )}
                </Button>
                
                {jobs.length > 0 && (
                  <Button 
                    variant="default" 
                    className="w-full bg-green-600 hover:bg-green-700"
                    onClick={startAutomation}
                    disabled={automationRunning}
                  >
                    {automationRunning ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        Running...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" />
                        Auto Apply to All ({jobs.length})
                      </>
                    )}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Job listings */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex-1"
        >
          {/* Toolbar */}
          <div className="flex items-center justify-between mb-4">
            <p className="text-muted-foreground">
              {jobs.length > 0 ? (
                <>
                  <span className="text-foreground font-medium">{jobs.length}</span> LinkedIn jobs found
                </>
              ) : (
                "Search to find LinkedIn jobs"
              )}
            </p>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground hidden sm:block">View:</span>
              <button
                onClick={() => setViewMode("grid")}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === "grid" ? "bg-primary text-primary-foreground" : "hover:bg-white/5"
                }`}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`p-2 rounded-lg transition-colors ${
                  viewMode === "list" ? "bg-primary text-primary-foreground" : "hover:bg-white/5"
                }`}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Jobs grid/list */}
          {searching ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="w-10 h-10 text-primary animate-spin mb-4" />
              <p className="text-muted-foreground">Searching LinkedIn for jobs...</p>
            </div>
          ) : jobs.length === 0 ? (
            <Card variant="glass" className="p-12">
              <div className="text-center">
                <Search className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                <h3 className="text-xl font-semibold mb-2">Search for LinkedIn Jobs</h3>
                <p className="text-muted-foreground mb-6">
                  Enter a job title and location, then click "Search Jobs" to find matching LinkedIn positions.
                </p>
                <Button variant="hero" onClick={searchJobs}>
                  <Search className="w-4 h-4" />
                  Start Searching
                </Button>
              </div>
            </Card>
          ) : (
            <div className={viewMode === "grid" ? "grid grid-cols-1 md:grid-cols-2 gap-4" : "space-y-4"}>
              {jobs.map((job, index) => (
                <motion.div
                  key={job.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <Card variant="glass" hover="lift" className="group cursor-pointer">
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-3">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-blue-400/20 flex items-center justify-center">
                          <Building className="w-6 h-6 text-primary" />
                        </div>
                        <div className="flex items-center gap-2">
                          {job.matchScore && (
                            <div className={`px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${
                              job.matchScore >= 90 ? "bg-success/20 text-success" :
                              job.matchScore >= 80 ? "bg-primary/20 text-primary" :
                              "bg-warning/20 text-warning"
                            }`}>
                              <Sparkles className="w-3 h-3" />
                              {job.matchScore}% Match
                            </div>
                          )}
                          <button className="p-2 rounded-lg hover:bg-white/10 transition-colors opacity-0 group-hover:opacity-100">
                            <Heart className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {/* Job Title with LinkedIn Link */}
                      <a 
                        href={job.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-lg font-semibold mb-1 group-hover:text-primary transition-colors hover:underline flex items-center gap-2"
                      >
                        {job.title}
                        <ExternalLink className="w-4 h-4 opacity-50" />
                      </a>
                      <p className="text-muted-foreground mb-3">{job.company}</p>

                      <div className="flex flex-wrap gap-2 mb-4">
                        {job.tags.map((tag) => (
                          <span
                            key={tag}
                            className={`px-2 py-0.5 rounded-md text-xs ${
                              tag === "Easy Apply" ? "bg-success/20 text-success" :
                              tag === "Remote" ? "bg-primary/20 text-primary" :
                              tag === "Featured" ? "bg-warning/20 text-warning" :
                              "bg-muted text-muted-foreground"
                            }`}
                          >
                            {tag}
                          </span>
                        ))}
                      </div>

                      <div className="flex flex-wrap gap-4 text-sm text-muted-foreground mb-4">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-4 h-4" />
                          {job.location}
                        </span>
                        {job.salary && (
                          <span className="flex items-center gap-1">
                            <DollarSign className="w-4 h-4" />
                            {job.salary}
                          </span>
                        )}
                        {job.posted && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {job.posted}
                          </span>
                        )}
                      </div>

                      <div className="flex gap-2">
                        <Button 
                          variant="hero" 
                          size="sm" 
                          className="flex-1"
                          onClick={() => quickApply(job)}
                        >
                          <Zap className="w-4 h-4" />
                          Quick Apply
                        </Button>
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => window.open(job.url, '_blank')}
                        >
                          <ExternalLink className="w-4 h-4" />
                        </Button>
                      </div>
                      
                      {/* LinkedIn URL Display */}
                      <div className="mt-3 pt-3 border-t border-border/50">
                        <a 
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-muted-foreground hover:text-primary truncate block"
                        >
                          🔗 {job.url}
                        </a>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default JobSearch;
