'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { SocialLogin } from '@/components/auth/SocialLogin';
import { TwoFactorAuth } from '@/components/auth/TwoFactorAuth';
import { EmailVerification } from '@/components/auth/EmailVerification';

type AuthMode = 'login' | 'signup' | '2fa' | 'verify-email' | 'forgot-password' | 'reset-password';

export default function AuthPage() {
  const [mode, setMode] = useState<AuthMode>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [twoFACode, setTwoFACode] = useState('');
  const [resetToken, setResetToken] = useState('');
  const { toast } = useToast();

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await api.post('/auth/login', {
        username: email,
        password,
        two_fa_code: twoFACode
      });

      if (response.headers['x-2fa-required']) {
        setRequires2FA(true);
        toast({
          title: "2FA Required",
          description: "Please enter your 2FA code to continue.",
        });
      } else {
        // Store token and redirect
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('refresh_token', response.data.refresh_token);
        window.location.href = '/';
      }
    } catch (error: any) {
      toast({
        title: "Login Failed",
        description: error.response?.data?.detail || "Invalid credentials",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      toast({
        title: "Error",
        description: "Passwords do not match",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await api.post('/auth/signup', {
        username,
        email,
        password,
        method: 'email'
      });

      if (response.data.verification_required) {
        setMode('verify-email');
        toast({
          title: "Account Created",
          description: "Please check your email to verify your account.",
        });
      } else {
        toast({
          title: "Success",
          description: "Account created successfully!",
        });
        setMode('login');
      }
    } catch (error: any) {
      toast({
        title: "Signup Failed",
        description: error.response?.data?.detail || "Failed to create account",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await api.post('/auth/forgot-password', { email });
      toast({
        title: "Email Sent",
        description: "If the email exists, a reset link has been sent.",
      });
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to send reset email",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      toast({
        title: "Error",
        description: "Passwords do not match",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      await api.post('/auth/reset-password', {
        token: resetToken,
        new_password: password
      });

      toast({
        title: "Success",
        description: "Password reset successfully!",
      });
      setMode('login');
    } catch (error: any) {
      toast({
        title: "Error",
        description: "Failed to reset password",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSocialLogin = (data: any) => {
    localStorage.setItem('token', data.access_token);
    if (data.refresh_token) {
      localStorage.setItem('refresh_token', data.refresh_token);
    }
    window.location.href = '/';
  };

  const handleEmailVerification = () => {
    setMode('login');
    toast({
      title: "Success",
      description: "Email verified! You can now log in.",
    });
  };

  const handle2FASetup = () => {
    setMode('login');
    toast({
      title: "2FA Enabled",
      description: "Two-factor authentication has been enabled for your account.",
    });
  };

  if (mode === 'verify-email') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <EmailVerification
          email={email}
          onVerificationComplete={handleEmailVerification}
        />
      </div>
    );
  }

  if (mode === '2fa') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <TwoFactorAuth
          onSetupComplete={handle2FASetup}
          onCancel={() => setMode('login')}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900">
            {mode === 'login' && 'Sign in to your account'}
            {mode === 'signup' && 'Create your account'}
            {mode === 'forgot-password' && 'Reset your password'}
            {mode === 'reset-password' && 'Set new password'}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {mode === 'login' && "Welcome back to Auto Applyer"}
            {mode === 'signup' && "Join Auto Applyer to streamline your job search"}
            {mode === 'forgot-password' && "Enter your email to receive a reset link"}
            {mode === 'reset-password' && "Enter your new password"}
          </p>
        </div>

        <Tabs defaultValue="social" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="social">Social Login</TabsTrigger>
            <TabsTrigger value="email">Email</TabsTrigger>
          </TabsList>

          <TabsContent value="social" className="mt-6">
            <SocialLogin
              mode={mode}
              onSuccess={handleSocialLogin}
            />
          </TabsContent>

          <TabsContent value="email" className="mt-6">
            <Card>
              <CardContent className="pt-6">
                <form onSubmit={
                  mode === 'login' ? handleEmailLogin :
                  mode === 'signup' ? handleEmailSignup :
                  mode === 'forgot-password' ? handleForgotPassword :
                  handleResetPassword
                } className="space-y-4">
                  
                  {mode === 'signup' && (
                    <div>
                      <Label htmlFor="username">Username</Label>
                      <Input
                        id="username"
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                      />
                    </div>
                  )}

                  <div>
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      required
                    />
                  </div>

                  {mode !== 'forgot-password' && (
                    <div>
                      <Label htmlFor="password">Password</Label>
                      <Input
                        id="password"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                      />
                    </div>
                  )}

                  {mode === 'signup' && (
                    <div>
                      <Label htmlFor="confirm-password">Confirm Password</Label>
                      <Input
                        id="confirm-password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                      />
                    </div>
                  )}

                  {mode === 'reset-password' && (
                    <div>
                      <Label htmlFor="confirm-password">Confirm Password</Label>
                      <Input
                        id="confirm-password"
                        type="password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                      />
                    </div>
                  )}

                  {requires2FA && (
                    <div>
                      <Label htmlFor="2fa-code">2FA Code</Label>
                      <Input
                        id="2fa-code"
                        type="text"
                        placeholder="000000"
                        value={twoFACode}
                        onChange={(e) => setTwoFACode(e.target.value)}
                        maxLength={6}
                        className="text-center font-mono"
                      />
                    </div>
                  )}

                  {mode === 'reset-password' && (
                    <div>
                      <Label htmlFor="reset-token">Reset Token</Label>
                      <Input
                        id="reset-token"
                        type="text"
                        value={resetToken}
                        onChange={(e) => setResetToken(e.target.value)}
                        placeholder="Enter token from email"
                        required
                      />
                    </div>
                  )}

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Processing...' : (
                      mode === 'login' ? 'Sign In' :
                      mode === 'signup' ? 'Create Account' :
                      mode === 'forgot-password' ? 'Send Reset Email' :
                      'Reset Password'
                    )}
                  </Button>
                </form>

                <div className="mt-4 text-center space-y-2">
                  {mode === 'login' && (
                    <>
                      <Button
                        variant="link"
                        onClick={() => setMode('forgot-password')}
                        className="text-sm"
                      >
                        Forgot your password?
                      </Button>
                      <div>
                        <span className="text-sm text-gray-600">Don't have an account? </span>
                        <Button
                          variant="link"
                          onClick={() => setMode('signup')}
                          className="text-sm p-0"
                        >
                          Sign up
                        </Button>
                      </div>
                    </>
                  )}

                  {mode === 'signup' && (
                    <div>
                      <span className="text-sm text-gray-600">Already have an account? </span>
                      <Button
                        variant="link"
                        onClick={() => setMode('login')}
                        className="text-sm p-0"
                      >
                        Sign in
                      </Button>
                    </div>
                  )}

                  {mode === 'forgot-password' && (
                    <div>
                      <span className="text-sm text-gray-600">Remember your password? </span>
                      <Button
                        variant="link"
                        onClick={() => setMode('login')}
                        className="text-sm p-0"
                      >
                        Sign in
                      </Button>
                    </div>
                  )}

                  {mode === 'reset-password' && (
                    <div>
                      <span className="text-sm text-gray-600">Remember your password? </span>
                      <Button
                        variant="link"
                        onClick={() => setMode('login')}
                        className="text-sm p-0"
                      >
                        Sign in
                      </Button>
                    </div>
                  )}
                </div>

                {mode === 'login' && (
                  <div className="mt-4 text-center">
                    <Button
                      variant="outline"
                      onClick={() => setMode('2fa')}
                      className="text-sm"
                    >
                      Setup Two-Factor Authentication
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
} 