"use client";

import React, { useEffect, useState } from "react";
import { apiService } from "@/lib/api";

const mockAnalytics = {
  total_applications: 5,
  interview_rate: 20,
  response_rate: 40,
  avg_response_time: 5.2,
  monthly_applications: [
    { month: "2024-06", applications: 2, interviews: 1, offers: 0 },
    { month: "2024-05", applications: 3, interviews: 0, offers: 0 },
  ],
  application_status: [
    { name: "Applied", value: 3 },
    { name: "Interviewed", value: 1 },
    { name: "Rejected", value: 1 },
  ],
};

function useAutoAnalytics() {
  const [analytics, setAnalytics] = useState<any>(mockAnalytics);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (token) {
      apiService.getAnalytics()
        .then((data) => setAnalytics(data))
        .catch(() => setAnalytics(mockAnalytics))
        .finally(() => setLoading(false));
    } else {
      setAnalytics(mockAnalytics);
      setLoading(false);
    }
  }, []);

  return { analytics, loading };
}

export default function AnalyticsDashboard() {
  const { analytics, loading } = useAutoAnalytics();

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto", padding: 24, background: "#fff", borderRadius: 12, boxShadow: "0 2px 8px #eee" }}>
      <h2 style={{ fontSize: 28, fontWeight: 700, marginBottom: 16 }}>Analytics</h2>
      <div style={{ marginBottom: 12 }}>Total Applications: <b>{analytics.total_applications}</b></div>
      <div style={{ marginBottom: 12 }}>Interview Rate: <b>{analytics.interview_rate}%</b></div>
      <div style={{ marginBottom: 12 }}>Response Rate: <b>{analytics.response_rate}%</b></div>
      <div style={{ marginBottom: 12 }}>Avg. Response Time: <b>{analytics.avg_response_time} days</b></div>
      <h3 style={{ marginTop: 24, fontWeight: 600 }}>Monthly Applications</h3>
      <ul>
        {analytics.monthly_applications.map((m: any) => (
          <li key={m.month}>{m.month}: {m.applications} apps, {m.interviews} interviews, {m.offers} offers</li>
        ))}
      </ul>
      <h3 style={{ marginTop: 24, fontWeight: 600 }}>Status Breakdown</h3>
      <ul>
        {analytics.application_status.map((s: any) => (
          <li key={s.name}>{s.name}: {s.value}</li>
        ))}
      </ul>
    </div>
  );
} 