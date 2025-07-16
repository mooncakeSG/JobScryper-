'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

interface SocialLoginProps {
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
  mode?: 'login' | 'signup';
}

export function SocialLogin({ onSuccess, onError, mode = 'login' }: SocialLoginProps) {
  const { toast } = useToast();

  const handleGoogleLogin = async () => {
    try {
      // In a real implementation, you would redirect to Google OAuth
      // For demo purposes, we'll simulate the flow
      const googleAuthUrl = `https://accounts.google.com/o/oauth2/auth?client_id=${process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}&redirect_uri=${encodeURIComponent(window.location.origin + '/auth/callback')}&response_type=code&scope=email profile`;
      
      // For demo, we'll show a message instead of redirecting
      toast({
        title: "Google Login",
        description: "Google OAuth integration would redirect here in production",
      });
      
      // Simulate successful login
      const mockResponse = {
        access_token: "mock_google_token",
        user_id: 123,
        is_new_user: false
      };
      
      onSuccess?.(mockResponse);
    } catch (error) {
      toast({
        title: "Error",
        description: "Google login failed. Please try again.",
        variant: "destructive",
      });
      onError?.(error);
    }
  };

  const handleGitHubLogin = async () => {
    try {
      // In a real implementation, you would redirect to GitHub OAuth
      const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(window.location.origin + '/auth/callback')}&scope=user:email`;
      
      // For demo, we'll show a message instead of redirecting
      toast({
        title: "GitHub Login",
        description: "GitHub OAuth integration would redirect here in production",
      });
      
      // Simulate successful login
      const mockResponse = {
        access_token: "mock_github_token",
        user_id: 124,
        is_new_user: true
      };
      
      onSuccess?.(mockResponse);
    } catch (error) {
      toast({
        title: "Error",
        description: "GitHub login failed. Please try again.",
        variant: "destructive",
      });
      onError?.(error);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'github') => {
    try {
      // Simulate the OAuth flow
      const response = await api.post('/auth/social-login', {
        provider,
        token: `mock_${provider}_token_${Date.now()}`
      });

      if (response.data.is_new_user) {
        toast({
          title: "Welcome!",
          description: `Account created successfully with ${provider}.`,
        });
      } else {
        toast({
          title: "Welcome back!",
          description: `Logged in successfully with ${provider}.`,
        });
      }

      onSuccess?.(response.data);
    } catch (error) {
      toast({
        title: "Error",
        description: `${provider.charAt(0).toUpperCase() + provider.slice(1)} login failed. Please try again.`,
        variant: "destructive",
      });
      onError?.(error);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>{mode === 'login' ? 'Sign In' : 'Sign Up'}</CardTitle>
        <CardDescription>
          {mode === 'login' 
            ? 'Choose your preferred sign-in method' 
            : 'Create your account using one of these options'
          }
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button
          variant="outline"
          className="w-full"
          onClick={() => handleSocialLogin('google')}
        >
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continue with Google
        </Button>

        <Button
          variant="outline"
          className="w-full"
          onClick={() => handleSocialLogin('github')}
        >
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
          Continue with GitHub
        </Button>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <Separator className="w-full" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">
              Or continue with email
            </span>
          </div>
        </div>

        <div className="text-center text-sm text-muted-foreground">
          <p>
            By continuing, you agree to our{' '}
            <a href="/terms" className="underline hover:text-primary">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="/privacy" className="underline hover:text-primary">
              Privacy Policy
            </a>
          </p>
        </div>
      </CardContent>
    </Card>
  );
} 