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

export default function AnalyticsPage() {
  // Mock data for demonstration
  const monthlyApplications = [
    { month: "Jan", applications: 12, interviews: 2, offers: 0 },
    { month: "Feb", applications: 18, interviews: 3, offers: 1 },
    { month: "Mar", applications: 25, interviews: 4, offers: 1 },
    { month: "Apr", applications: 32, interviews: 6, offers: 2 },
    { month: "May", applications: 28, interviews: 5, offers: 1 },
    { month: "Jun", applications: 35, interviews: 7, offers: 3 },
  ];

  const applicationStatus = [
    { name: "Applied", value: 45, color: "#3B82F6" },
    { name: "Under Review", value: 25, color: "#F59E0B" },
    { name: "Interview", value: 15, color: "#10B981" },
    { name: "Rejected", value: 12, color: "#EF4444" },
    { name: "Offer", value: 3, color: "#8B5CF6" },
  ];

  const topCompanies = [
    { company: "Google", applications: 8, interviews: 2 },
    { company: "Microsoft", applications: 6, interviews: 1 },
    { company: "Apple", applications: 5, interviews: 1 },
    { company: "Amazon", applications: 4, interviews: 0 },
    { company: "Meta", applications: 3, interviews: 1 },
  ];

  const jobTypes = [
    { type: "Full-time", applications: 65 },
    { type: "Contract", applications: 20 },
    { type: "Part-time", applications: 10 },
    { type: "Remote", applications: 5 },
  ];

  const stats = [
    {
      title: "Total Applications",
      value: "150",
      change: "+23%",
      trend: "up",
      icon: FileText,
      color: "text-blue-600"
    },
    {
      title: "Interview Rate",
      value: "18.7%",
      change: "+5.2%",
      trend: "up",
      icon: Users,
      color: "text-green-600"
    },
    {
      title: "Response Rate",
      value: "34.5%",
      change: "-2.1%",
      trend: "down",
      icon: Target,
      color: "text-purple-600"
    },
    {
      title: "Avg. Response Time",
      value: "5.2 days",
      change: "-0.8 days",
      trend: "up",
      icon: Clock,
      color: "text-orange-600"
    }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Job Application Analytics</h1>
        <p className="text-blue-100">
          Track your job search progress and identify areas for improvement
        </p>
      </div>

      {/* Key Metrics */}
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
              <div className="flex items-center mt-1">
                {stat.trend === "up" ? (
                  <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                ) : (
                  <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                )}
                <span className={`text-xs ${stat.trend === "up" ? "text-green-600" : "text-red-600"}`}>
                  {stat.change}
                </span>
                <span className="text-xs text-gray-500 ml-1">vs last month</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Applications Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Application Trends</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={monthlyApplications}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="applications" fill="#3B82F6" name="Applications" />
                <Bar dataKey="interviews" fill="#10B981" name="Interviews" />
                <Bar dataKey="offers" fill="#8B5CF6" name="Offers" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Application Status Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Application Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={applicationStatus}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {applicationStatus.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Job Types Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Applications by Job Type</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={jobTypes}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="applications" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top Companies */}
        <Card>
          <CardHeader>
            <CardTitle>Top Companies Applied To</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topCompanies.map((company, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-blue-600">
                        {company.company.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{company.company}</p>
                      <p className="text-sm text-gray-500">
                        {company.applications} applications
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {company.interviews} interviews
                    </p>
                    <p className="text-xs text-gray-500">
                      {((company.interviews / company.applications) * 100).toFixed(1)}% rate
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="h-4 w-4 text-green-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Interview scheduled with TechCorp</p>
                <p className="text-xs text-gray-500">2 hours ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <FileText className="h-4 w-4 text-blue-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Applied to Senior Developer at StartupXYZ</p>
                <p className="text-xs text-gray-500">5 hours ago</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                <AlertCircle className="h-4 w-4 text-yellow-600" />
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">Follow-up reminder for Google application</p>
                <p className="text-xs text-gray-500">1 day ago</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 