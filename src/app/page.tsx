"use client";

import React, { useEffect, useState } from "react";
import { useUser } from "../context/UserContext";
import { apiService } from "@/lib/api";

export default function Dashboard() {
  const { user, loading } = useUser();
  const [analytics, setAnalytics] = useState(null);
  const [applications, setApplications] = useState([]);
  const [dataLoading, setDataLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (user) {
      // Fetch real user data when user is authenticated
      setDataLoading(true);
      setError("");
      
      Promise.all([
        apiService.getAnalytics(),
        apiService.getApplications()
      ])
      .then(([analyticsData, applicationsData]) => {
        setAnalytics(analyticsData);
        setApplications(applicationsData);
      })
      .catch((err) => {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      })
      .finally(() => setDataLoading(false));
    }
  }, [user]);

  // Wait for auth loading to complete
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div>Loading...</div>
      </div>
    );
  }
  
  // Show login prompt if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Welcome to Job Scraper</h1>
          <p className="mb-4">Please log in to access your dashboard</p>
          <a href="/login" className="text-blue-600 hover:underline">
            Go to Login
          </a>
        </div>
      </div>
    );
  }
  
  // Show dashboard loading
  if (dataLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div>Loading dashboard...</div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-bold text-red-600 mb-2">Error</h2>
          <p className="text-gray-600">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Welcome back, {user.username}!</h1>
        <p className="text-gray-600">Here's your job application dashboard</p>
      </div>
      
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold">Total Applications</h3>
            <p className="text-3xl font-bold text-blue-600">{analytics.total_applications || 0}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold">Interview Rate</h3>
            <p className="text-3xl font-bold text-green-600">{analytics.interview_rate || 0}%</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold">Response Rate</h3>
            <p className="text-3xl font-bold text-orange-600">{analytics.response_rate || 0}%</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold">Avg Response Time</h3>
            <p className="text-3xl font-bold text-purple-600">{analytics.avg_response_time || 0} days</p>
          </div>
        </div>
      )}

      {applications && applications.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4">Recent Applications</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-semibold">Your Applications ({applications.length})</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {applications.slice(0, 5).map((app, index) => (
                  <div key={app.id || index} className="flex justify-between items-center p-4 border rounded">
                    <div>
                      <h4 className="font-semibold">{app.job_title}</h4>
                      <p className="text-gray-600">{app.company}</p>
                    </div>
                    <div className="text-right">
                      <span className="px-2 py-1 rounded text-sm bg-blue-100 text-blue-800">
                        {app.status}
                      </span>
                      <p className="text-sm text-gray-500 mt-1">{app.application_date}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <a href="/applications" className="block p-6 bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold mb-2">View Applications</h3>
            <p className="text-gray-600">Manage your job applications</p>
          </a>
          <a href="/analytics" className="block p-6 bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold mb-2">Analytics</h3>
            <p className="text-gray-600">View detailed analytics</p>
          </a>
          <a href="/upload" className="block p-6 bg-white rounded-lg shadow hover:shadow-lg transition-shadow">
            <h3 className="text-lg font-semibold mb-2">Upload Resume</h3>
            <p className="text-gray-600">Analyze your resume</p>
          </a>
        </div>
      </div>
    </div>
  );
} 