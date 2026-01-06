import { useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Bot, Mail, Lock, User, Eye, EyeOff, ArrowRight, Linkedin, Chrome } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";

const Signup = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeTerms: false,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate loading
    setTimeout(() => {
      setIsLoading(false);
      window.location.href = "/onboarding";
    }, 1500);
  };

  const getPasswordStrength = () => {
    const { password } = formData;
    if (!password) return { width: "0%", color: "bg-muted", label: "" };
    if (password.length < 6) return { width: "25%", color: "bg-destructive", label: "Weak" };
    if (password.length < 10) return { width: "50%", color: "bg-warning", label: "Fair" };
    if (password.length < 14) return { width: "75%", color: "bg-primary", label: "Good" };
    return { width: "100%", color: "bg-success", label: "Strong" };
  };

  const strength = getPasswordStrength();

  return (
    <div className="min-h-screen flex">
      {/* Left side - Illustration */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-navy-800 to-background items-center justify-center p-12 overflow-hidden">
        <div className="absolute inset-0 floating-particles opacity-30" />
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary/20 rounded-full blur-[100px]" />
        <div className="absolute bottom-1/4 right-1/4 w-64 h-64 bg-blue-500/20 rounded-full blur-[100px]" />
        
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="relative z-10 text-center"
        >
          <div className="w-32 h-32 mx-auto mb-8 rounded-3xl bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center animate-float shadow-xl shadow-primary/30">
            <Bot className="w-16 h-16 text-primary-foreground" />
          </div>
          <h2 className="text-3xl font-bold mb-4">Join AutoAgentHire</h2>
          <p className="text-muted-foreground max-w-sm">
            Let AI automate your job applications while you focus on what matters most.
          </p>
        </motion.div>
      </div>

      {/* Right side - Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          {/* Logo for mobile */}
          <Link to="/" className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center">
              <Bot className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">AutoAgentHire</span>
          </Link>

          <h1 className="text-3xl font-bold mb-2">Create your account</h1>
          <p className="text-muted-foreground mb-8">
            Start automating your job search today
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium mb-2">Full Name</label>
              <Input
                type="text"
                placeholder="John Doe"
                icon={<User className="w-4 h-4" />}
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <Input
                type="email"
                placeholder="john@example.com"
                icon={<Mail className="w-4 h-4" />}
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="Create a strong password"
                  icon={<Lock className="w-4 h-4" />}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {formData.password && (
                <div className="mt-2">
                  <div className="h-1.5 rounded-full bg-muted overflow-hidden">
                    <div
                      className={`h-full ${strength.color} transition-all duration-300`}
                      style={{ width: strength.width }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground mt-1">{strength.label}</span>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Confirm Password</label>
              <Input
                type={showPassword ? "text" : "password"}
                placeholder="Confirm your password"
                icon={<Lock className="w-4 h-4" />}
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                required
              />
            </div>

            <div className="flex items-start gap-3">
              <Checkbox
                id="terms"
                checked={formData.agreeTerms}
                onCheckedChange={(checked) => setFormData({ ...formData, agreeTerms: checked as boolean })}
              />
              <label htmlFor="terms" className="text-sm text-muted-foreground leading-relaxed">
                I agree to the{" "}
                <Link to="/terms" className="text-primary hover:underline">Terms of Service</Link>
                {" "}and{" "}
                <Link to="/privacy" className="text-primary hover:underline">Privacy Policy</Link>
              </label>
            </div>

            <Button
              type="submit"
              variant="hero"
              size="lg"
              className="w-full"
              disabled={isLoading || !formData.agreeTerms}
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              ) : (
                <>
                  Create Account
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </Button>
          </form>

          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-background text-muted-foreground">Or sign up with</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Button variant="outline" size="lg">
              <Linkedin className="w-5 h-5 text-[#0A66C2]" />
              LinkedIn
            </Button>
            <Button variant="outline" size="lg">
              <Chrome className="w-5 h-5" />
              Google
            </Button>
          </div>

          <p className="text-center text-muted-foreground mt-8">
            Already have an account?{" "}
            <Link to="/login" className="text-primary hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Signup;
