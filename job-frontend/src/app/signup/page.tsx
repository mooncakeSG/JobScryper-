"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SignupPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const response = await fetch("/api/auth/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, email, fullName }),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Signup failed");
      }
      setSuccess(true);
      setTimeout(() => router.push("/login"), 1200);
    } catch (err: any) {
      setError(err.message || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-gray-50 to-white px-4">
      <Card className="w-full max-w-md rounded-2xl shadow-lg border border-gray-100 bg-white p-8">
        <CardHeader>
          <CardTitle className="text-2xl font-extrabold text-gray-900 mb-2">Sign Up</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSignup} className="space-y-6">
            <div>
              <Label htmlFor="fullName" className="text-sm font-semibold text-gray-700">Full Name</Label>
              <Input
                id="fullName"
                value={fullName}
                onChange={e => setFullName(e.target.value)}
                required
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="email" className="text-sm font-semibold text-gray-700">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="username" className="text-sm font-semibold text-gray-700">Username</Label>
              <Input
                id="username"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                autoFocus
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="password" className="text-sm font-semibold text-gray-700">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                className="mt-1"
              />
            </div>
            {error && <div className="text-red-600 text-sm font-medium">{error}</div>}
            {success && <div className="text-green-600 text-sm font-medium">Signup successful! Redirecting...</div>}
            <Button type="submit" className="w-full h-12 text-lg font-semibold shadow-md" disabled={loading}>
              {loading ? "Signing up..." : "Sign Up"}
            </Button>
            <div className="text-center text-sm mt-2">
              Already have an account? <a href="/login" className="text-blue-600 hover:underline font-semibold">Login</a>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
} 