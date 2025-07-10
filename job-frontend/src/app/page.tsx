import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  Upload, 
  Search, 
  BarChart3, 
  FileText, 
  Users, 
  TrendingUp 
} from "lucide-react";
import Link from "next/link";

export default function Dashboard() {
  const stats = [
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
  ];

  const quickActions = [
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
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">
          Welcome to {process.env.NEXT_PUBLIC_APP_NAME}
        </h1>
        <p className="text-blue-100">
          Your AI-powered job application assistant. Track applications, optimize your resume, and land your dream job.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
              <p className="text-xs text-gray-500 mt-1">{stat.change}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {quickActions.map((action, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center mb-4`}>
                  <action.icon className="h-6 w-6" />
                </div>
                <CardTitle className="text-lg">{action.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">{action.description}</p>
                <Link href={action.href}>
                  <Button variant="outline" className="w-full">
                    Get Started
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">Resume uploaded and analyzed</p>
                <p className="text-xs text-gray-500">2 hours ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">Applied to Software Engineer at TechCorp</p>
                <p className="text-xs text-gray-500">5 hours ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-gray-900">Found 15 new job matches</p>
                <p className="text-xs text-gray-500">1 day ago</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
