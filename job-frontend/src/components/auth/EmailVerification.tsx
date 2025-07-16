'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

interface EmailVerificationProps {
  email: string;
  onVerificationComplete?: () => void;
  onResend?: () => void;
}

export function EmailVerification({ email, onVerificationComplete, onResend }: EmailVerificationProps) {
  const [verificationCode, setVerificationCode] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [resendCountdown, setResendCountdown] = useState(0);
  const { toast } = useToast();

  useEffect(() => {
    if (resendCountdown > 0) {
      const timer = setTimeout(() => setResendCountdown(resendCountdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCountdown]);

  const handleVerification = async () => {
    if (!verificationCode) {
      toast({
        title: "Error",
        description: "Please enter the verification code.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    try {
      await api.post('/auth/verify-email', {
        email,
        code: verificationCode
      });

      toast({
        title: "Success",
        description: "Email verified successfully!",
      });

      onVerificationComplete?.();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Verification failed. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResend = async () => {
    setIsLoading(true);
    try {
      await api.post('/auth/resend-verification', { email });
      
      toast({
        title: "Code Sent",
        description: "A new verification code has been sent to your email.",
      });

      setResendCountdown(60); // 60 second cooldown
      onResend?.();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to resend verification code.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Verify Your Email</CardTitle>
        <CardDescription>
          We've sent a verification code to <strong>{email}</strong>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <p className="text-sm text-muted-foreground">
            Check your email and enter the 6-digit verification code below
          </p>
        </div>

        <div>
          <Label htmlFor="verification-code">Verification Code</Label>
          <Input
            id="verification-code"
            type="text"
            placeholder="000000"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            maxLength={6}
            className="text-center text-lg font-mono tracking-widest"
          />
        </div>

        <Button
          onClick={handleVerification}
          disabled={isLoading || verificationCode.length !== 6}
          className="w-full"
        >
          {isLoading ? 'Verifying...' : 'Verify Email'}
        </Button>

        <div className="text-center">
          <p className="text-sm text-muted-foreground mb-2">
            Didn't receive the code?
          </p>
          <Button
            variant="link"
            onClick={handleResend}
            disabled={isLoading || resendCountdown > 0}
            className="text-sm"
          >
            {resendCountdown > 0 
              ? `Resend in ${resendCountdown}s` 
              : 'Resend verification code'
            }
          </Button>
        </div>

        <div className="text-center text-xs text-muted-foreground">
          <p>
            Make sure to check your spam folder if you don't see the email in your inbox.
          </p>
        </div>
      </CardContent>
    </Card>
  );
} 