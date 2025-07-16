"use client";
import React, { createContext, useContext, useState, useEffect } from "react";
import { apiService } from "../lib/api";

interface UserContextType {
  user: any;
  loading: boolean;
  login: (credentials: { username: string; password: string }) => Promise<void>;
  signup: (data: { username: string; password: string; email?: string }) => Promise<void>;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Load user info if token exists
  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("authToken") : null;
    if (token) {
      apiService.getCurrentUser()
        .then(response => {
          if (response.success && response.data) {
            setUser(response.data);
          } else {
            setUser(null);
          }
        })
        .catch(() => setUser(null))
        .finally(() => setLoading(false));
    } else {
      setUser(null);
      setLoading(false);
    }
  }, []);

  // Login function
  const login = async (credentials: { username: string; password: string }) => {
    setLoading(true);
    try {
      const response = await apiService.login(credentials);
      if (response.success && response.data && response.data.access_token) {
        localStorage.setItem("authToken", response.data.access_token);
        const userResponse = await apiService.getCurrentUser();
        if (userResponse.success && userResponse.data) {
          setUser(userResponse.data);
        } else {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
      // Optionally, handle error (e.g., show notification)
    } finally {
      setLoading(false);
    }
  };

  // Signup function
  const signup = async (data: { username: string; password: string; email?: string }) => {
    setLoading(true);
    try {
      const response = await apiService.signup(data);
      if (response.success) {
        // Auto-login after signup
        await login({ username: data.username, password: data.password });
      }
    } catch (error) {
      console.error('Signup failed:', error);
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem("authToken");
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