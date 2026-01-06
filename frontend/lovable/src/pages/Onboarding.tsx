import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Bot, Upload, FileText, MapPin, Briefcase, Clock, DollarSign, 
  Linkedin, Shield, Settings, Sparkles, Check, ArrowRight, ArrowLeft,
  X, File, AlertCircle, ChevronDown
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { useNavigate } from "react-router-dom";

const steps = [
  { id: 1, title: "Welcome", icon: Bot },
  { id: 2, title: "Upload Resume", icon: FileText },
  { id: 3, title: "Job Preferences", icon: Briefcase },
  { id: 4, title: "LinkedIn", icon: Linkedin },
  { id: 5, title: "Settings", icon: Settings },
  { id: 6, title: "Complete", icon: Sparkles },
];

const Onboarding = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const navigate = useNavigate();

  const [preferences, setPreferences] = useState({
    jobTitles: ["Software Engineer", "Full Stack Developer"],
    location: "San Francisco, CA",
    experienceLevel: "mid",
    jobTypes: { fulltime: true, remote: true, contract: false, parttime: false },
    salaryRange: [80000, 150000],
    linkedinEmail: "",
    linkedinPassword: "",
    maxApplications: 25,
    excludedCompanies: [],
    enableAICoverLetters: true,
    enableEmailNotifications: true,
  });

  const handleFileUpload = (file: File) => {
    setUploadedFile(file);
    setIsUploading(true);
    setUploadProgress(0);

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          setUploadComplete(true);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleFileUpload(file);
  };

  const nextStep = () => {
    if (currentStep < 6) setCurrentStep(currentStep + 1);
  };

  const prevStep = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="text-center max-w-lg mx-auto"
          >
            <div className="w-24 h-24 mx-auto mb-8 rounded-3xl bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center animate-float shadow-xl shadow-primary/30">
              <Bot className="w-12 h-12 text-primary-foreground" />
            </div>
            <h2 className="text-3xl font-bold mb-4">Welcome to AutoAgentHire!</h2>
            <p className="text-muted-foreground text-lg mb-8">
              Let's set up your profile so our AI can start finding and applying to jobs for you automatically.
            </p>
            <Button variant="hero" size="xl" onClick={nextStep}>
              Let's Get Started
              <ArrowRight className="w-5 h-5" />
            </Button>
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-2xl mx-auto"
          >
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-2">Upload Your Resume</h2>
              <p className="text-muted-foreground">
                Our AI will extract your information and optimize it for job applications
              </p>
            </div>

            {!uploadComplete ? (
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className="relative border-2 border-dashed border-primary/30 rounded-2xl p-12 text-center hover:border-primary/60 transition-colors cursor-pointer bg-card/30"
              >
                {isUploading ? (
                  <div className="space-y-4">
                    <div className="w-16 h-16 mx-auto rounded-2xl bg-primary/20 flex items-center justify-center">
                      <FileText className="w-8 h-8 text-primary animate-pulse" />
                    </div>
                    <p className="text-foreground font-medium">{uploadedFile?.name}</p>
                    <div className="max-w-xs mx-auto">
                      <div className="h-2 rounded-full bg-muted overflow-hidden">
                        <motion.div
                          className="h-full bg-primary"
                          initial={{ width: 0 }}
                          animate={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">
                        {uploadProgress < 30 && "Uploading..."}
                        {uploadProgress >= 30 && uploadProgress < 60 && "Parsing document..."}
                        {uploadProgress >= 60 && uploadProgress < 90 && "Extracting information..."}
                        {uploadProgress >= 90 && "Almost done..."}
                      </p>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-primary/20 flex items-center justify-center">
                      <Upload className="w-8 h-8 text-primary" />
                    </div>
                    <p className="text-lg font-medium mb-2">Drag & drop your resume here</p>
                    <p className="text-muted-foreground mb-4">or click to browse files</p>
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-muted text-sm text-muted-foreground">
                      <File className="w-4 h-4" />
                      PDF, DOC, DOCX (Max 5MB)
                    </div>
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      className="absolute inset-0 opacity-0 cursor-pointer"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFileUpload(file);
                      }}
                    />
                  </>
                )}
              </div>
            ) : (
              <div className="space-y-6">
                <div className="flex items-center gap-4 p-4 rounded-xl bg-success/10 border border-success/30">
                  <div className="w-12 h-12 rounded-xl bg-success/20 flex items-center justify-center">
                    <Check className="w-6 h-6 text-success" />
                  </div>
                  <div>
                    <p className="font-medium text-success">Resume uploaded successfully!</p>
                    <p className="text-sm text-muted-foreground">{uploadedFile?.name}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="ml-auto"
                    onClick={() => {
                      setUploadComplete(false);
                      setUploadedFile(null);
                    }}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                {/* AI Analysis Results */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-card/60 border border-white/10">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center">
                        <Sparkles className="w-4 h-4 text-primary" />
                      </div>
                      <span className="font-medium">AI Score</span>
                    </div>
                    <div className="text-4xl font-bold gradient-text">92/100</div>
                    <p className="text-sm text-muted-foreground">Excellent ATS compatibility</p>
                  </div>

                  <div className="p-4 rounded-xl bg-card/60 border border-white/10">
                    <div className="flex items-center gap-2 mb-3">
                      <div className="w-8 h-8 rounded-lg bg-success/20 flex items-center justify-center">
                        <Check className="w-4 h-4 text-success" />
                      </div>
                      <span className="font-medium">Skills Found</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {["React", "TypeScript", "Node.js", "Python"].map((skill) => (
                        <span key={skill} className="px-2 py-1 rounded-md bg-primary/10 text-primary text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="flex justify-between mt-8">
              <Button variant="outline" onClick={prevStep}>
                <ArrowLeft className="w-4 h-4" /> Back
              </Button>
              <Button variant="hero" onClick={nextStep} disabled={!uploadComplete}>
                Continue <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        );

      case 3:
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-2xl mx-auto"
          >
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-2">Job Preferences</h2>
              <p className="text-muted-foreground">
                Tell us what kind of jobs you're looking for
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">Job Titles</label>
                <div className="flex flex-wrap gap-2 mb-2">
                  {preferences.jobTitles.map((title) => (
                    <span
                      key={title}
                      className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm"
                    >
                      {title}
                      <X className="w-3 h-3 cursor-pointer" />
                    </span>
                  ))}
                </div>
                <Input placeholder="Add job title..." />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Location</label>
                <Input
                  icon={<MapPin className="w-4 h-4" />}
                  value={preferences.location}
                  onChange={(e) => setPreferences({ ...preferences, location: e.target.value })}
                  placeholder="Enter city or 'Remote'"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Experience Level</label>
                <div className="grid grid-cols-4 gap-2">
                  {["Entry", "Mid", "Senior", "Lead"].map((level) => (
                    <button
                      key={level}
                      className={`p-3 rounded-lg border text-sm font-medium transition-all ${
                        preferences.experienceLevel === level.toLowerCase()
                          ? "bg-primary text-primary-foreground border-primary"
                          : "bg-card/60 border-white/10 hover:border-primary/40"
                      }`}
                      onClick={() => setPreferences({ ...preferences, experienceLevel: level.toLowerCase() })}
                    >
                      {level}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Job Type</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { key: "fulltime", label: "Full-time" },
                    { key: "parttime", label: "Part-time" },
                    { key: "remote", label: "Remote" },
                    { key: "contract", label: "Contract" },
                  ].map(({ key, label }) => (
                    <div key={key} className="flex items-center gap-2">
                      <Checkbox
                        id={key}
                        checked={preferences.jobTypes[key as keyof typeof preferences.jobTypes]}
                        onCheckedChange={(checked) =>
                          setPreferences({
                            ...preferences,
                            jobTypes: { ...preferences.jobTypes, [key]: checked },
                          })
                        }
                      />
                      <label htmlFor={key} className="text-sm">{label}</label>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-4">
                  Salary Range: ${preferences.salaryRange[0].toLocaleString()} - ${preferences.salaryRange[1].toLocaleString()}
                </label>
                <Slider
                  value={preferences.salaryRange}
                  onValueChange={(value) => setPreferences({ ...preferences, salaryRange: value })}
                  min={30000}
                  max={300000}
                  step={5000}
                />
              </div>
            </div>

            <div className="flex justify-between mt-8">
              <Button variant="outline" onClick={prevStep}>
                <ArrowLeft className="w-4 h-4" /> Back
              </Button>
              <Button variant="hero" onClick={nextStep}>
                Continue <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        );

      case 4:
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-lg mx-auto"
          >
            <div className="text-center mb-8">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-[#0A66C2]/20 flex items-center justify-center">
                <Linkedin className="w-8 h-8 text-[#0A66C2]" />
              </div>
              <h2 className="text-3xl font-bold mb-2">Connect LinkedIn</h2>
              <p className="text-muted-foreground">
                We need your LinkedIn credentials to apply to jobs on your behalf
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">LinkedIn Email</label>
                <Input
                  type="email"
                  icon={<Linkedin className="w-4 h-4" />}
                  placeholder="your@email.com"
                  value={preferences.linkedinEmail}
                  onChange={(e) => setPreferences({ ...preferences, linkedinEmail: e.target.value })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">LinkedIn Password</label>
                <Input
                  type="password"
                  placeholder="Your LinkedIn password"
                  value={preferences.linkedinPassword}
                  onChange={(e) => setPreferences({ ...preferences, linkedinPassword: e.target.value })}
                />
              </div>

              <div className="flex items-start gap-3 p-4 rounded-xl bg-primary/10 border border-primary/20">
                <Shield className="w-5 h-5 text-primary mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-primary">Your credentials are secure</p>
                  <p className="text-xs text-muted-foreground">
                    We use enterprise-grade encryption to protect your data. Your password is never stored in plain text.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-between mt-8">
              <Button variant="outline" onClick={prevStep}>
                <ArrowLeft className="w-4 h-4" /> Back
              </Button>
              <Button variant="hero" onClick={nextStep}>
                Continue <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        );

      case 5:
        return (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-lg mx-auto"
          >
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold mb-2">Final Settings</h2>
              <p className="text-muted-foreground">
                Configure your automation preferences
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Max Applications Per Day: {preferences.maxApplications}
                </label>
                <Slider
                  value={[preferences.maxApplications]}
                  onValueChange={([value]) => setPreferences({ ...preferences, maxApplications: value })}
                  min={5}
                  max={50}
                  step={5}
                />
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 rounded-xl bg-card/60 border border-white/10">
                  <div className="flex items-center gap-3">
                    <Sparkles className="w-5 h-5 text-primary" />
                    <div>
                      <p className="font-medium">AI Cover Letters</p>
                      <p className="text-xs text-muted-foreground">Generate personalized cover letters</p>
                    </div>
                  </div>
                  <Checkbox
                    checked={preferences.enableAICoverLetters}
                    onCheckedChange={(checked) =>
                      setPreferences({ ...preferences, enableAICoverLetters: checked as boolean })
                    }
                  />
                </div>

                <div className="flex items-center justify-between p-4 rounded-xl bg-card/60 border border-white/10">
                  <div className="flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-primary" />
                    <div>
                      <p className="font-medium">Email Notifications</p>
                      <p className="text-xs text-muted-foreground">Get updates on your applications</p>
                    </div>
                  </div>
                  <Checkbox
                    checked={preferences.enableEmailNotifications}
                    onCheckedChange={(checked) =>
                      setPreferences({ ...preferences, enableEmailNotifications: checked as boolean })
                    }
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-between mt-8">
              <Button variant="outline" onClick={prevStep}>
                <ArrowLeft className="w-4 h-4" /> Back
              </Button>
              <Button variant="hero" onClick={nextStep}>
                Complete Setup <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        );

      case 6:
        return (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center max-w-lg mx-auto"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", delay: 0.2 }}
              className="w-24 h-24 mx-auto mb-8 rounded-full bg-success/20 flex items-center justify-center"
            >
              <Check className="w-12 h-12 text-success" />
            </motion.div>
            <h2 className="text-3xl font-bold mb-4">You're All Set!</h2>
            <p className="text-muted-foreground text-lg mb-8">
              Your AI assistant is now configured and ready to start applying to jobs on your behalf.
            </p>
            <Button variant="hero" size="xl" onClick={() => navigate("/dashboard")}>
              Go to Dashboard
              <ArrowRight className="w-5 h-5" />
            </Button>
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Progress bar */}
      <div className="fixed top-0 left-0 right-0 h-1 bg-muted z-50">
        <motion.div
          className="h-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${(currentStep / 6) * 100}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>

      {/* Header with steps */}
      <header className="border-b border-white/5 bg-background/80 backdrop-blur-xl">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center">
                <Bot className="w-6 h-6 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold hidden sm:block">AutoAgentHire</span>
            </div>

            {/* Step indicators */}
            <div className="flex items-center gap-2">
              {steps.map((step) => (
                <div
                  key={step.id}
                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-all ${
                    step.id === currentStep
                      ? "bg-primary text-primary-foreground"
                      : step.id < currentStep
                      ? "bg-success text-success-foreground"
                      : "bg-muted text-muted-foreground"
                  }`}
                >
                  {step.id < currentStep ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <step.icon className="w-4 h-4" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center p-8">
        <AnimatePresence mode="wait">
          {renderStep()}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default Onboarding;
