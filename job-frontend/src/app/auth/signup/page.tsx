"use client";

import React, { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Eye, EyeOff, Loader2, Mail, Lock, User, Github, CheckCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { apiService } from "@/lib/api";
import { useUser } from "@/context/UserContext";

const signupSchema = z.object({
  username: z
    .string()
    .min(3, "Username must be at least 3 characters")
    .max(50, "Username must be less than 50 characters")
    .regex(/^[a-zA-Z0-9_]+$/, "Username can only contain letters, numbers, and underscores"),
  email: z.string().email("Please enter a valid email address"),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type SignupFormData = z.infer<typeof signupSchema>;

export default function SignupPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [isGithubLoading, setIsGithubLoading] = useState(false);
  
  const router = useRouter();
  const { toast } = useToast();
  const { signup } = useUser();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<SignupFormData>({
    resolver: zodResolver(signupSchema),
  });

  const password = watch("password");

  const getPasswordStrength = (password: string) => {
    if (!password) return { score: 0, color: "gray", text: "" };
    
    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    if (score <= 2) return { score, color: "red", text: "Weak" };
    if (score <= 3) return { score, color: "yellow", text: "Fair" };
    if (score <= 4) return { score, color: "blue", text: "Good" };
    return { score, color: "green", text: "Strong" };
  };

  const passwordStrength = getPasswordStrength(password);

  const onSubmit = async (data: SignupFormData) => {
    setIsLoading(true);
    try {
      const response = await apiService.signup({
        username: data.username,
        email: data.email,
        password: data.password,
      });
      
      if (response.success) {
        // Auto-login after signup
        await signup({
          username: data.username,
          password: data.password,
          email: data.email,
        });
        
        toast({
          title: "Success",
          description: "Account created successfully! Please check your email for verification.",
        });
        router.push("/");
      } else {
        toast({
          title: "Error",
          description: response.error || "Signup failed",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "An unexpected error occurred",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    setIsGoogleLoading(true);
    try {
      toast({
        title: "Coming Soon",
        description: "Google signup will be available soon!",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Google signup failed",
        variant: "destructive",
      });
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleGithubSignup = async () => {
    setIsGithubLoading(true);
    try {
      toast({
        title: "Coming Soon",
        description: "GitHub signup will be available soon!",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "GitHub signup failed",
        variant: "destructive",
      });
    } finally {
      setIsGithubLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Card className="shadow-xl border-0">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-bold text-gray-900">
              Create your account
            </CardTitle>
            <CardDescription className="text-gray-600">
              Join JobScryper to start your job search journey
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Social Signup Buttons */}
            <div className="space-y-3">
              <Button
                variant="outline"
                className="w-full"
                onClick={handleGoogleSignup}
                disabled={isGoogleLoading}
              >
                {isGoogleLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Mail className="mr-2 h-4 w-4" />
                )}
                Continue with Google
              </Button>
              
              <Button
                variant="outline"
                className="w-full"
                onClick={handleGithubSignup}
                disabled={isGithubLoading}
              >
                {isGithubLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Github className="mr-2 h-4 w-4" />
                )}
                Continue with GitHub
              </Button>
            </div>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white px-2 text-gray-500">Or continue with</span>
              </div>
            </div>

            {/* Signup Form */}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="username" className="text-sm font-medium text-gray-700">
                  Username
                </label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Choose a username"
                  {...register("username")}
                  className={errors.username ? "border-red-500" : ""}
                />
                {errors.username && (
                  <p className="text-sm text-red-500">{errors.username.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-gray-700">
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Enter your email"
                  {...register("email")}
                  className={errors.email ? "border-red-500" : ""}
                />
                {errors.email && (
                  <p className="text-sm text-red-500">{errors.email.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a strong password"
                    {...register("password")}
                    className={errors.password ? "border-red-500 pr-10" : "pr-10"}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                
                {/* Password Strength Indicator */}
                {password && (
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all ${
                            passwordStrength.color === "red" ? "bg-red-500" :
                            passwordStrength.color === "yellow" ? "bg-yellow-500" :
                            passwordStrength.color === "blue" ? "bg-blue-500" :
                            "bg-green-500"
                          }`}
                          style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                        />
                      </div>
                      <span className={`text-xs font-medium ${
                        passwordStrength.color === "red" ? "text-red-500" :
                        passwordStrength.color === "yellow" ? "text-yellow-500" :
                        passwordStrength.color === "blue" ? "text-blue-500" :
                        "text-green-500"
                      }`}>
                        {passwordStrength.text}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-1 text-xs text-gray-600">
                      <div className={`flex items-center space-x-1 ${
                        password.length >= 8 ? "text-green-600" : "text-gray-400"
                      }`}>
                        <CheckCircle className="h-3 w-3" />
                        <span>8+ characters</span>
                      </div>
                      <div className={`flex items-center space-x-1 ${
                        /[A-Z]/.test(password) ? "text-green-600" : "text-gray-400"
                      }`}>
                        <CheckCircle className="h-3 w-3" />
                        <span>Uppercase</span>
                      </div>
                      <div className={`flex items-center space-x-1 ${
                        /[a-z]/.test(password) ? "text-green-600" : "text-gray-400"
                      }`}>
                        <CheckCircle className="h-3 w-3" />
                        <span>Lowercase</span>
                      </div>
                      <div className={`flex items-center space-x-1 ${
                        /[0-9]/.test(password) ? "text-green-600" : "text-gray-400"
                      }`}>
                        <CheckCircle className="h-3 w-3" />
                        <span>Number</span>
                      </div>
                    </div>
                  </div>
                )}
                
                {errors.password && (
                  <p className="text-sm text-red-500">{errors.password.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="text-sm font-medium text-gray-700">
                  Confirm Password
                </label>
                <div className="relative">
                  <Input
                    id="confirmPassword"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder="Confirm your password"
                    {...register("confirmPassword")}
                    className={errors.confirmPassword ? "border-red-500 pr-10" : "pr-10"}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                {errors.confirmPassword && (
                  <p className="text-sm text-red-500">{errors.confirmPassword.message}</p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creating account...
                  </>
                ) : (
                  <>
                    <User className="mr-2 h-4 w-4" />
                    Create account
                  </>
                )}
              </Button>
            </form>

            <div className="text-center text-sm text-gray-600">
              Already have an account?{" "}
              <Link href="/auth/login" className="text-blue-600 hover:text-blue-500 font-medium">
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 