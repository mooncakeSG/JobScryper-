"use client";

import { useState } from "react";
import { apiService } from "@/lib/api";

export default function DebugPage() {
  const [results, setResults] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  const addResult = (message: string) => {
    setResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const testBackendHealth = async () => {
    setLoading(true);
    try {
      addResult("Testing backend health...");
      const health = await apiService.healthCheck();
      addResult(`✅ Backend health: ${JSON.stringify(health)}`);
    } catch (error: any) {
      addResult(`❌ Backend health failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testSignup = async () => {
    setLoading(true);
    try {
      addResult("Testing signup...");
      const signupData = {
        username: `testuser${Date.now()}`,
        password: "testpass123",
        email: `test${Date.now()}@example.com`
      };
      addResult(`Signup data: ${JSON.stringify(signupData)}`);
      
      const result = await apiService.signup(signupData);
      addResult(`✅ Signup successful: ${JSON.stringify(result)}`);
      
      // Store the credentials for login test
      localStorage.setItem('debug_credentials', JSON.stringify(signupData));
    } catch (error: any) {
      addResult(`❌ Signup failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const testLogin = async () => {
    setLoading(true);
    try {
      addResult("Testing login...");
      const credentials = localStorage.getItem('debug_credentials');
      if (!credentials) {
        addResult("❌ No credentials found. Run signup first.");
        return;
      }
      
      const { username, password } = JSON.parse(credentials);
      addResult(`Login with: ${username}`);
      
      const result = await apiService.login({ username, password });
      addResult(`✅ Login successful: ${JSON.stringify(result)}`);
    } catch (error: any) {
      addResult(`❌ Login failed: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Frontend-Backend Debug</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Test Controls</h2>
          <div className="space-y-4">
            <button
              onClick={testBackendHealth}
              disabled={loading}
              className="w-full bg-blue-500 text-white p-3 rounded hover:bg-blue-600 disabled:opacity-50"
            >
              Test Backend Health
            </button>
            
            <button
              onClick={testSignup}
              disabled={loading}
              className="w-full bg-green-500 text-white p-3 rounded hover:bg-green-600 disabled:opacity-50"
            >
              Test Signup
            </button>
            
            <button
              onClick={testLogin}
              disabled={loading}
              className="w-full bg-purple-500 text-white p-3 rounded hover:bg-purple-600 disabled:opacity-50"
            >
              Test Login
            </button>
            
            <button
              onClick={clearResults}
              className="w-full bg-gray-500 text-white p-3 rounded hover:bg-gray-600"
            >
              Clear Results
            </button>
          </div>
        </div>
        
        <div>
          <h2 className="text-xl font-semibold mb-4">Results</h2>
          <div className="bg-gray-100 p-4 rounded h-96 overflow-y-auto">
            {results.length === 0 ? (
              <p className="text-gray-500">No results yet. Run a test to see output.</p>
            ) : (
              <div className="space-y-2">
                {results.map((result, index) => (
                  <div key={index} className="text-sm font-mono bg-white p-2 rounded border">
                    {result}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 