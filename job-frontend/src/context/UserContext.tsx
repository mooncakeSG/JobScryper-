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
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (token) {
      apiService.getCurrentUser()
        .then(setUser)
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
      // Ensure apiService is defined/imported at the top of the file
      const data = await apiService.login(credentials);
      if (data && data.access_token) {
        localStorage.setItem("token", data.access_token);
        const userInfo = await apiService.getCurrentUser();
        setUser(userInfo);
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
    await apiService.signup(data);
    // Auto-login after signup
    await login({ username: data.username, password: data.password });
    setLoading(false);
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