"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { JobCardSkeletonList } from "@/components/ui/job-card-skeleton";
import { useToast } from "@/hooks/use-toast";
import { 
  Search, 
  Filter, 
  Plus, 
  Calendar,
  Building,
  MapPin,
  DollarSign,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Eye,
  Edit,
  Trash2,
  FileText,
  TrendingUp
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface JobApplication {
  id: number;
  job_title: string;
  company: string;
  location: string;
  status: string;
  application_date: string;
  salary_min?: number;
  salary_max?: number;
  job_url?: string;
  interview_date?: string;
  notes?: string;
}

const statusColors = {
  pending: "bg-yellow-100 text-yellow-800",
  applied: "bg-blue-100 text-blue-800",
  screening: "bg-purple-100 text-purple-800",
  interview_scheduled: "bg-orange-100 text-orange-800",
  interviewed: "bg-indigo-100 text-indigo-800",
  technical_test: "bg-pink-100 text-pink-800",
  offer_received: "bg-green-100 text-green-800",
  offer_accepted: "bg-emerald-100 text-emerald-800",
  offer_rejected: "bg-red-100 text-red-800",
  rejected: "bg-red-100 text-red-800",
  withdrawn: "bg-gray-100 text-gray-800"
};

const statusOptions = [
  { value: "all", label: "All Statuses" },
  { value: "pending", label: "Pending" },
  { value: "applied", label: "Applied" },
  { value: "screening", label: "Screening" },
  { value: "interview_scheduled", label: "Interview Scheduled" },
  { value: "interviewed", label: "Interviewed" },
  { value: "technical_test", label: "Technical Test" },
  { value: "offer_received", label: "Offer Received" },
  { value: "offer_accepted", label: "Offer Accepted" },
  { value: "offer_rejected", label: "Offer Rejected" },
  { value: "rejected", label: "Rejected" },
  { value: "withdrawn", label: "Withdrawn" }
];

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [filteredApplications, setFilteredApplications] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState("application_date");
  const { toast } = useToast();

  useEffect(() => {
    fetchApplications();
  }, []);

  useEffect(() => {
    filterApplications();
  }, [applications, searchTerm, statusFilter]);

  const fetchApplications = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/applications?user_id=demo');
      if (response.ok) {
        const data = await response.json();
        setApplications(data.applications || []);
        toast({
          title: "Applications loaded",
          description: `Successfully loaded ${data.applications?.length || 0} applications`,
          variant: "success",
        });
      } else {
        console.error('Failed to fetch applications');
        toast({
          title: "Error",
          description: "Failed to load applications. Using demo data.",
          variant: "destructive",
        });
        // For demo purposes, use mock data
        setApplications(mockApplications);
      }
    } catch (error) {
      console.error('Error fetching applications:', error);
      toast({
        title: "Network Error",
        description: "Unable to connect to server. Using demo data.",
        variant: "destructive",
      });
      // For demo purposes, use mock data
      setApplications(mockApplications);
    } finally {
      setLoading(false);
    }
  };

  const filterApplications = () => {
    let filtered = applications;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(app => 
        app.job_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        app.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        app.location.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== "all") {
      filtered = filtered.filter(app => app.status === statusFilter);
    }

    // Sort applications
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "application_date":
          return new Date(b.application_date).getTime() - new Date(a.application_date).getTime();
        case "company":
          return a.company.localeCompare(b.company);
        case "status":
          return a.status.localeCompare(b.status);
        default:
          return 0;
      }
    });

    setFilteredApplications(filtered);
  };

  const updateApplicationStatus = async (applicationId: number, newStatus: string) => {
    try {
      const response = await fetch(`/api/applications/${applicationId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        setApplications(prev => 
          prev.map(app => 
            app.id === applicationId 
              ? { ...app, status: newStatus }
              : app
          )
        );
        toast({
          title: "Status Updated",
          description: `Application status updated to ${newStatus.replace('_', ' ')}`,
          variant: "success",
        });
      } else {
        toast({
          title: "Update Failed",
          description: "Failed to update application status",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error updating application status:', error);
      toast({
        title: "Network Error",
        description: "Unable to update application status",
        variant: "destructive",
      });
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'offer_accepted':
        return <CheckCircle className="h-4 w-4" />;
      case 'rejected':
      case 'offer_rejected':
        return <XCircle className="h-4 w-4" />;
      case 'interview_scheduled':
      case 'interviewed':
        return <Calendar className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return "Not specified";
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    if (min) return `$${min.toLocaleString()}+`;
    if (max) return `Up to $${max.toLocaleString()}`;
    return "Not specified";
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-10 w-32" />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>

        <Skeleton className="h-32 w-full" />

        <JobCardSkeletonList count={5} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Applications</h1>
          <p className="text-gray-600 mt-1">
            Track your job applications and manage your career progress
          </p>
        </div>
        <Button className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Application
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Applications</p>
                <p className="text-2xl font-bold text-gray-900">{applications.length}</p>
              </div>
              <div className="h-8 w-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <FileText className="h-4 w-4 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Applications</p>
                <p className="text-2xl font-bold text-gray-900">
                  {applications.filter(app => 
                    ['pending', 'applied', 'screening', 'interview_scheduled', 'interviewed', 'technical_test'].includes(app.status)
                  ).length}
                </p>
              </div>
              <div className="h-8 w-8 bg-green-100 rounded-lg flex items-center justify-center">
                <Clock className="h-4 w-4 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Interviews</p>
                <p className="text-2xl font-bold text-gray-900">
                  {applications.filter(app => 
                    ['interview_scheduled', 'interviewed'].includes(app.status)
                  ).length}
                </p>
              </div>
              <div className="h-8 w-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <Calendar className="h-4 w-4 text-purple-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-gray-900">
                  {applications.length > 0 
                    ? Math.round((applications.filter(app => app.status === 'offer_accepted').length / applications.length) * 100)
                    : 0}%
                </p>
              </div>
              <div className="h-8 w-8 bg-orange-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="h-4 w-4 text-orange-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  id="search"
                  placeholder="Search jobs, companies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="sort">Sort By</Label>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger>
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="application_date">Application Date</SelectItem>
                  <SelectItem value="company">Company</SelectItem>
                  <SelectItem value="status">Status</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button 
                variant="outline" 
                onClick={() => {
                  setSearchTerm("");
                  setStatusFilter("all");
                  setSortBy("application_date");
                }}
                className="w-full"
              >
                Clear Filters
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Applications List */}
      <div className="space-y-4">
        {filteredApplications.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <div className="text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <h3 className="text-lg font-medium mb-2">No applications found</h3>
                <p className="text-sm">
                  {applications.length === 0 
                    ? "Start by adding your first job application"
                    : "Try adjusting your search or filter criteria"
                  }
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredApplications.map((application) => (
            <Card key={application.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-3">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {application.job_title}
                        </h3>
                        <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Building className="h-4 w-4" />
                            {application.company}
                          </div>
                          {application.location && (
                            <div className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              {application.location}
                            </div>
                          )}
                          {(application.salary_min || application.salary_max) && (
                            <div className="flex items-center gap-1">
                              <DollarSign className="h-4 w-4" />
                              {formatSalary(application.salary_min, application.salary_max)}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium flex items-center gap-1 ${statusColors[application.status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'}`}>
                          {getStatusIcon(application.status)}
                          {application.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        Applied: {formatDate(application.application_date)}
                      </div>
                      {application.interview_date && (
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          Interview: {formatDate(application.interview_date)}
                        </div>
                      )}
                    </div>

                    {application.notes && (
                      <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                        {application.notes}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    {application.job_url && (
                      <Button variant="outline" size="sm" asChild>
                        <a href={application.job_url} target="_blank" rel="noopener noreferrer">
                          <Eye className="h-4 w-4" />
                        </a>
                      </Button>
                    )}
                    <Select 
                      value={application.status} 
                      onValueChange={(value) => updateApplicationStatus(application.id, value)}
                    >
                      <SelectTrigger className="w-32">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {statusOptions.slice(1).map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button variant="outline" size="sm">
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this application?')) {
                          // Add delete functionality here
                          toast({
                            title: "Delete",
                            description: "Delete functionality coming soon",
                            variant: "info",
                          });
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

// Mock data for demonstration
const mockApplications: JobApplication[] = [
  {
    id: 1,
    job_title: "Senior Software Engineer",
    company: "TechCorp",
    location: "San Francisco, CA",
    status: "interview_scheduled",
    application_date: "2024-01-15",
    salary_min: 120000,
    salary_max: 180000,
    job_url: "https://example.com/job1",
    interview_date: "2024-01-25",
    notes: "Phone interview scheduled with hiring manager"
  },
  {
    id: 2,
    job_title: "Full Stack Developer",
    company: "StartupXYZ",
    location: "Remote",
    status: "applied",
    application_date: "2024-01-14",
    salary_min: 90000,
    salary_max: 130000,
    job_url: "https://example.com/job2"
  },
  {
    id: 3,
    job_title: "Frontend Engineer",
    company: "BigTech Inc",
    location: "New York, NY",
    status: "rejected",
    application_date: "2024-01-10",
    salary_min: 110000,
    salary_max: 160000,
    notes: "Rejected after technical interview"
  },
  {
    id: 4,
    job_title: "DevOps Engineer",
    company: "CloudSolutions",
    location: "Austin, TX",
    status: "offer_received",
    application_date: "2024-01-08",
    salary_min: 100000,
    salary_max: 140000,
    notes: "Great offer! Considering acceptance"
  },
  {
    id: 5,
    job_title: "Product Manager",
    company: "Innovation Labs",
    location: "Seattle, WA",
    status: "pending",
    application_date: "2024-01-12",
    salary_min: 130000,
    salary_max: 190000
  }
]; 