"use client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Upload, 
  Search, 
  BarChart3, 
  FileText, 
  Users, 
  TrendingUp,
  AlertCircle
} from "lucide-react";
import Link from "next/link";
import { FadeIn } from "@/components/ui/animation";
import { Skeleton } from "@/components/ui/skeleton";
import { useState, useEffect } from "react";

export default function Dashboard() {
  // Simulate loading and empty states for demonstration
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any[]>([]);
  const [quickActions, setQuickActions] = useState<any[]>([]);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setStats([
        {
          title: "Total Applications",
          value: "24",
          change: "+3 this week",
          icon: FileText,
          color: "text-blue-600"
        },
        {
          title: "Interview Rate",
          value: "12.5%",
          change: "+2.1% from last month",
          icon: TrendingUp,
          color: "text-green-600"
        },
        {
          title: "Jobs Matched",
          value: "156",
          change: "+12 today",
          icon: Users,
          color: "text-purple-600"
        },
        {
          title: "Success Rate",
          value: "8.3%",
          change: "+1.2% from last month",
          icon: BarChart3,
          color: "text-orange-600"
        }
      ]);
      setQuickActions([
        {
          title: "Upload Resume",
          description: "Upload and analyze your resume for ATS optimization",
          icon: Upload,
          href: "/upload",
          color: "bg-blue-50 text-blue-600 hover:bg-blue-100"
        },
        {
          title: "Find Jobs",
          description: "Search and match jobs based on your profile",
          icon: Search,
          href: "/match",
          color: "bg-green-50 text-green-600 hover:bg-green-100"
        },
        {
          title: "Track Applications",
          description: "Manage and track your job applications",
          icon: FileText,
          href: "/applications",
          color: "bg-orange-50 text-orange-600 hover:bg-orange-100"
        },
        {
          title: "View Analytics",
          description: "Track your application progress and insights",
          icon: BarChart3,
          href: "/analytics",
          color: "bg-purple-50 text-purple-600 hover:bg-purple-100"
        }
      ]);
      setRecentActivity([
        {
          color: "bg-blue-500",
          text: "Resume uploaded and analyzed",
          time: "2 hours ago"
        },
        {
          color: "bg-green-500",
          text: "Applied to Software Engineer at TechCorp",
          time: "5 hours ago"
        },
        {
          color: "bg-purple-500",
          text: "Found 15 new job matches",
          time: "1 day ago"
        }
      ]);
      setLoading(false);
    }, 1500);
  }, []);

  return (
    <FadeIn>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="bg-white rounded-xl shadow-sm px-8 py-8 mb-8 flex flex-col md:flex-row md:items-center md:justify-between border-b border-gray-100">
          <div className="mb-4 md:mb-0">
            <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-2">
              Welcome to {process.env.NEXT_PUBLIC_APP_NAME}
            </h1>
            <p className="text-lg text-gray-500">
              Your AI-powered job application assistant. Track applications, optimize your resume, and land your dream job.
            </p>
          </div>
        </div>

        {/* Stats Grid */}
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
                    <stat.icon className={`h-6 w-6 ${stat.color}`} aria-hidden="true" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-extrabold text-gray-900 mb-1">{stat.value}</div>
                    <p className="text-xs text-gray-500 mt-1">{stat.change}</p>
                  </CardContent>
                </Card>
              ))}
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {loading
              ? Array.from({ length: 4 }).map((_, i) => (
                  <Card key={i} className="rounded-2xl shadow-sm border border-gray-100 bg-white">
                    <CardHeader>
                      <Skeleton className="h-12 w-12 rounded-lg mb-4" />
                      <Skeleton className="h-6 w-32 mb-2" />
                    </CardHeader>
                    <CardContent>
                      <Skeleton className="h-4 w-40 mb-4" />
                      <Skeleton className="h-10 w-full" />
                    </CardContent>
                  </Card>
                ))
              : quickActions.length === 0
              ? <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white col-span-4 text-center p-8">
                  <CardContent>
                    <div className="flex flex-col items-center justify-center">
                      <Search className="h-12 w-12 text-gray-300 mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No quick actions</h3>
                      <p className="text-gray-500">Quick actions will appear here as you use the app.</p>
                    </div>
                  </CardContent>
                </Card>
              : quickActions.map((action, index) => (
                  <Card key={index} className="rounded-2xl shadow-sm border border-gray-100 bg-white transition-all hover:shadow-lg group focus-within:shadow-lg focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2">
                    <CardHeader>
                      <div className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center mb-4`}>
                        <action.icon className="h-6 w-6" aria-hidden="true" />
                      </div>
                      <CardTitle className="text-lg font-bold text-gray-900">{action.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-600 mb-4">{action.description}</p>
                      <Link href={action.href} tabIndex={0}>
                        <Button variant="outline" className="w-full font-semibold">
                          Get Started
                        </Button>
                      </Link>
                    </CardContent>
                  </Card>
                ))}
          </div>
        </div>

        {/* Recent Activity */}
        <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-gray-900">Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {loading
              ? <div className="space-y-4">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div key={i} className="flex items-center space-x-4">
                      <Skeleton className="w-2 h-2 rounded-full" />
                      <div className="flex-1">
                        <Skeleton className="h-4 w-48 mb-1" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                    </div>
                  ))}
                </div>
              : recentActivity.length === 0
              ? <div className="flex flex-col items-center justify-center py-8">
                  <AlertCircle className="h-12 w-12 text-gray-300 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No recent activity</h3>
                  <p className="text-gray-500">Your recent activity will show up here as you use the app.</p>
                </div>
              : <div className="space-y-4">
                  {recentActivity.map((item, i) => (
                    <div key={i} className="flex items-center space-x-4">
                      <div className={`w-2 h-2 ${item.color} rounded-full`} aria-hidden="true"></div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-900">{item.text}</p>
                        <p className="text-xs text-gray-500">{item.time}</p>
                      </div>
                    </div>
                  ))}
                </div>}
          </CardContent>
        </Card>
      </div>
    </FadeIn>
  );
}
