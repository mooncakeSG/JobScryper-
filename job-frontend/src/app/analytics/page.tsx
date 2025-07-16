"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from "recharts";
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  FileText, 
  Clock,
  Target,
  CheckCircle,
  AlertCircle
} from "lucide-react";
import { FadeIn } from "@/components/ui/animation";
import { Skeleton } from "@/components/ui/skeleton";
import { useState, useEffect } from "react";
import { apiService } from "@/lib/api";
import { useUser } from "@/context/UserContext";

export default function AnalyticsPage() {
  const { user } = useUser();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any[]>([]);
  const [monthlyApplications, setMonthlyApplications] = useState<any[]>([]);
  const [applicationStatus, setApplicationStatus] = useState<any[]>([]);
  const [jobTypes, setJobTypes] = useState<any[]>([]);

  const themeColors = {
    blue: 'rgb(37, 99, 235)', // Tailwind blue-600
    yellow: 'rgb(245, 158, 11)', // Tailwind yellow-500
    green: 'rgb(16, 185, 129)', // Tailwind green-500
    red: 'rgb(239, 68, 68)', // Tailwind red-500
    purple: 'rgb(139, 92, 246)', // Tailwind purple-500
  };

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }
    setLoading(true);
    apiService.getAnalytics()
      .then((data) => {
        setStats([
          {
            title: "Total Applications",
            value: data.total_applications || 0,
            change: `+${data.monthly_applications?.[0]?.applications || 0}`,
            trend: "up",
            icon: FileText,
            color: "text-blue-600"
          },
          {
            title: "Interview Rate",
            value: `${data.interview_rate || 0}%`,
            change: `+${data.interview_rate || 0}%`,
            trend: "up",
            icon: Users,
            color: "text-green-600"
          },
          {
            title: "Response Rate",
            value: `${data.response_rate || 0}%`,
            change: `+${data.response_rate || 0}%`,
            trend: "up",
            icon: Target,
            color: "text-purple-600"
          },
          {
            title: "Avg. Response Time",
            value: `${data.avg_response_time || 0} days`,
            change: "",
            trend: "up",
            icon: Clock,
            color: "text-orange-600"
          }
        ]);
        setMonthlyApplications(data.monthly_applications || []);
        setApplicationStatus((data.application_status || []).map((s: any) => ({
          name: s.name,
          value: s.value,
          color: themeColors[s.name.toLowerCase()] || themeColors.blue
        })));
        // Optionally set jobTypes if available in backend response
      })
      .catch(() => setStats([]))
      .finally(() => setLoading(false));
  }, [user]);

  if (!user) {
    return <div className="flex justify-center items-center h-screen">Please log in to view analytics.</div>;
  }

  return (
    <FadeIn>
      <div className="space-y-8">
        <div className="bg-white rounded-xl shadow-sm px-8 py-8 mb-8 flex flex-col md:flex-row md:items-center md:justify-between border-b border-gray-100">
          <div className="mb-4 md:mb-0">
            <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-2">Job Application Analytics</h1>
            <p className="text-lg text-gray-500">Track your job search progress and identify areas for improvement</p>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {loading
            ? Array.from({ length: 4 }).map((_, i) => (
                <Card key={i} className="rounded-2xl shadow-sm border border-gray-100 bg-white">
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <Skeleton className="h-5 w-24" />
                    <Skeleton className="h-6 w-6 rounded-full" />
                  </CardHeader>
                  <CardContent>
                    <Skeleton className="h-8 w-20 mb-1" />
                    <Skeleton className="h-4 w-16 mt-1" />
                  </CardContent>
                </Card>
              ))
            : stats.length === 0
            ? <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white col-span-4 text-center p-8">
                <CardContent>
                  <div className="flex flex-col items-center justify-center">
                    <FileText className="h-12 w-12 text-gray-300 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No stats available</h3>
                    <p className="text-gray-500">Stats will appear here as you use the app.</p>
                  </div>
                </CardContent>
              </Card>
            : stats.map((stat, index) => (
                <Card key={index} className="rounded-2xl shadow-sm border border-gray-100 bg-white transition-all hover:shadow-lg group">
                  <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-semibold text-gray-700">
                      {stat.title}
                    </CardTitle>
                    <stat.icon className={`h-6 w-6 ${stat.color}`} />
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-extrabold text-gray-900 mb-1">{stat.value}</div>
                    <div className="flex items-center mt-1">
                      {stat.trend === "up" ? (
                        <TrendingUp className="h-5 w-5 text-green-500 mr-1" />
                      ) : (
                        <TrendingDown className="h-5 w-5 text-red-500 mr-1" />
                      )}
                      <span className={`text-xs font-semibold ${stat.trend === "up" ? "text-green-600" : "text-red-600"}`}>{stat.change}</span>
                      <span className="text-xs text-gray-500 ml-1">vs last month</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
        </div>

        {/* Charts Grid */}
        <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-gray-900">Monthly Application Trends</CardTitle>
          </CardHeader>
          <CardContent className="pt-2 pb-4">
            {loading
              ? <Skeleton className="h-[300px] w-full rounded-xl" />
              : monthlyApplications.length === 0
              ? <div className="flex flex-col items-center justify-center h-[300px]">
                  <BarChart className="h-12 w-12 text-gray-300 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No data</h3>
                  <p className="text-gray-500">Monthly application trends will appear here.</p>
                </div>
              : <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={monthlyApplications}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="applications" fill={themeColors.blue} name="Applications" />
                    <Bar dataKey="interviews" fill={themeColors.green} name="Interviews" />
                    <Bar dataKey="offers" fill={themeColors.purple} name="Offers" />
                  </BarChart>
                </ResponsiveContainer>}
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-gray-900">Application Status Distribution</CardTitle>
          </CardHeader>
          <CardContent className="pt-2 pb-4">
            {loading
              ? <Skeleton className="h-[300px] w-full rounded-xl" />
              : applicationStatus.length === 0
              ? <div className="flex flex-col items-center justify-center h-[300px]">
                  <PieChart className="h-12 w-12 text-gray-300 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No data</h3>
                  <p className="text-gray-500">Application status distribution will appear here.</p>
                </div>
              : <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={applicationStatus}
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      dataKey="value"
                      label={({ name, percent }) =>
                        percent !== undefined
                          ? `${name} ${(percent * 100).toFixed(0)}%`
                          : name
                      }
                    >
                      {applicationStatus.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>}
          </CardContent>
        </Card>

        {/* Job Types Chart (optional, still mock for now) */}
      </div>
    </FadeIn>
  );
} 