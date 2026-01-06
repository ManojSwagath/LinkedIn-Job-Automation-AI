import { useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Bot, Mail, Lock, Eye, EyeOff, ArrowRight, Linkedin, Chrome } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    remember: false,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      window.location.href = "/dashboard";
    }, 1500);
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Illustration */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-navy-800 to-background items-center justify-center p-12 overflow-hidden">
        <div className="absolute inset-0 floating-particles opacity-30" />
        <div className="absolute top-1/3 right-1/4 w-72 h-72 bg-primary/20 rounded-full blur-[100px]" />
        <div className="absolute bottom-1/3 left-1/4 w-64 h-64 bg-blue-500/20 rounded-full blur-[100px]" />
        
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8 }}
          className="relative z-10 text-center"
        >
          <div className="w-32 h-32 mx-auto mb-8 rounded-3xl bg-gradient-to-br from-primary to-blue-400 flex items-center justify-center animate-float shadow-xl shadow-primary/30">
            <Bot className="w-16 h-16 text-primary-foreground" />
          </div>
          <h2 className="text-3xl font-bold mb-4">Welcome Back!</h2>
          <p className="text-muted-foreground max-w-sm">
            Your AI assistant is ready to continue helping with your job search.
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

          <h1 className="text-3xl font-bold mb-2">Sign in</h1>
          <p className="text-muted-foreground mb-8">
            Enter your credentials to access your dashboard
          </p>

          <form onSubmit={handleSubmit} className="space-y-5">
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
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-medium">Password</label>
                <Link to="/forgot-password" className="text-sm text-primary hover:underline">
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Input
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
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
            </div>

            <div className="flex items-center gap-3">
              <Checkbox
                id="remember"
                checked={formData.remember}
                onCheckedChange={(checked) => setFormData({ ...formData, remember: checked as boolean })}
              />
              <label htmlFor="remember" className="text-sm text-muted-foreground">
                Remember me for 30 days
              </label>
            </div>

            <Button
              type="submit"
              variant="hero"
              size="lg"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              ) : (
                <>
                  Sign In
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
              <span className="px-4 bg-background text-muted-foreground">Or continue with</span>
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
            Don't have an account?{" "}
            <Link to="/signup" className="text-primary hover:underline font-medium">
              Sign up
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;
