"use client";
import React, { createContext, useContext, useState, useEffect } from "react";
// @ts-ignore: Suppress import error if module is missing during build
import { apiService } from "@/lib/api";

interface UserContextType {
  user: any;
  loading: boolean;
  login: (credentials: { username: string; password: string }) => Promise<boolean>;
  signup: (data: { username: string; password: string; email?: string }) => Promise<boolean>;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Load user info if token exists on mount
  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (token) {
      apiService.getCurrentUser()
        .then(userData => {
          setUser(userData);
          setLoading(false);
        })
        .catch(() => {
          setUser(null);
          setLoading(false);
        });
    } else {
      setUser(null);
      setLoading(false);
    }
  }, []);

  // Login function - stores token, fetches user, sets context
  const login = async (credentials: { username: string; password: string }): Promise<boolean> => {
    try {
      // Step 1: Login and get token
      const data = await apiService.login(credentials);
      
      if (data && data.access_token) {
        // Step 2: Store token
        localStorage.setItem("token", data.access_token);
        
        // Step 3: Immediately fetch user info
        const userInfo = await apiService.getCurrentUser();
        
        // Step 4: Set user in context
        setUser(userInfo);
        return true;
      } else {
        setUser(null);
        return false;
      }
    } catch (error) {
      console.error('Login failed:', error);
      setUser(null);
      return false;
    }
  };

  // Signup function - registers user then auto-logs in
  const signup = async (data: { username: string; password: string; email?: string }): Promise<boolean> => {
    try {
      await apiService.signup(data);
      // Auto-login after signup
      return await login({ username: data.username, password: data.password });
    } catch (error) {
      console.error('Signup failed:', error);
      return false;
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    window.location.href = "/login";
  };

  return (
    <UserContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within a UserProvider");
  return ctx;
} 