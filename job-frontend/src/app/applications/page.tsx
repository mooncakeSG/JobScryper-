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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogClose } from "@/components/ui/dialog";

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
  const [showAddModal, setShowAddModal] = useState(false);
  const [newApp, setNewApp] = useState({
    job_title: "",
    company: "",
    location: "",
    status: "applied",
    application_date: new Date().toISOString().slice(0, 10),
    salary_min: "",
    salary_max: "",
    job_url: "",
    interview_date: "",
    notes: ""
  });
  const [adding, setAdding] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editApp, setEditApp] = useState<JobApplication | null>(null);
  const [editing, setEditing] = useState(false);

  useEffect(() => {
    fetchApplications();
  }, []);

  useEffect(() => {
    filterApplications();
  }, [applications, searchTerm, statusFilter, sortBy]);

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

  const deleteApplication = async (applicationId: number) => {
    try {
      const response = await fetch(`/api/applications/${applicationId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setApplications(prev => prev.filter(app => app.id !== applicationId));
        toast({
          title: "Deleted",
          description: "Application deleted successfully",
          variant: "success",
        });
      } else {
        toast({
          title: "Delete Failed",
          description: "Failed to delete application",
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Network Error",
        description: "Unable to delete application",
        variant: "destructive",
      });
    }
  };

  const handleAddChange = (e: any) => {
    const { name, value } = e.target;
    setNewApp(prev => ({ ...prev, [name]: value }));
  };

  const handleAddApplication = async (e: any) => {
    e.preventDefault();
    setAdding(true);
    try {
      const response = await fetch('/api/applications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newApp,
          salary_min: newApp.salary_min ? Number(newApp.salary_min) : undefined,
          salary_max: newApp.salary_max ? Number(newApp.salary_max) : undefined,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setApplications(prev => [data.application, ...prev]);
        toast({ title: "Application Added", description: "New application added successfully", variant: "success" });
        setShowAddModal(false);
        setNewApp({
          job_title: "",
          company: "",
          location: "",
          status: "applied",
          application_date: new Date().toISOString().slice(0, 10),
          salary_min: "",
          salary_max: "",
          job_url: "",
          interview_date: "",
          notes: ""
        });
      } else {
        toast({ title: "Add Failed", description: "Failed to add application", variant: "destructive" });
      }
    } catch (error) {
      toast({ title: "Network Error", description: "Unable to add application", variant: "destructive" });
    } finally {
      setAdding(false);
    }
  };

  const openEditModal = (app: JobApplication) => {
    setEditApp({ ...app });
    setShowEditModal(true);
  };

  const handleEditChange = (e: any) => {
    const { name, value } = e.target;
    setEditApp(prev => prev ? { ...prev, [name]: value } : null);
  };

  const handleEditStatusChange = (val: string) => {
    setEditApp(prev => prev ? { ...prev, status: val } : null);
  };

  const handleEditApplication = async (e: any) => {
    e.preventDefault();
    if (!editApp) return;
    setEditing(true);
    try {
      const response = await fetch(`/api/applications/${editApp.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_title: editApp.job_title,
          company: editApp.company,
          location: editApp.location,
          status: editApp.status,
          application_date: editApp.application_date,
          salary_min: editApp.salary_min ? Number(editApp.salary_min) : undefined,
          salary_max: editApp.salary_max ? Number(editApp.salary_max) : undefined,
          job_url: editApp.job_url,
          interview_date: editApp.interview_date,
          notes: editApp.notes,
        }),
      });
      if (response.ok) {
        const data = await response.json();
        setApplications(prev => prev.map(app => app.id === editApp.id ? data.application : app));
        toast({ title: "Application Updated", description: "Application updated successfully", variant: "success" });
        setShowEditModal(false);
        setEditApp(null);
      } else {
        toast({ title: "Update Failed", description: "Failed to update application", variant: "destructive" });
      }
    } catch (error) {
      toast({ title: "Network Error", description: "Unable to update application", variant: "destructive" });
    } finally {
      setEditing(false);
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
      <div className="bg-white rounded-xl shadow-sm px-8 py-8 mb-8 flex flex-col md:flex-row md:items-center md:justify-between border-b border-gray-100">
        <div className="mb-4 md:mb-0">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight mb-2">Applications</h1>
          <p className="text-lg text-gray-500">Track your job applications and manage your career progress</p>
        </div>
        <Button className="flex items-center gap-2 h-12 px-6 text-base font-semibold shadow-md" onClick={() => setShowAddModal(true)}>
          <Plus className="h-5 w-5" />
          Add Application
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 mb-8">
        <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white">
          <CardContent className="p-6 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Total Applications</p>
              <p className="text-3xl font-bold text-gray-900">{applications.length}</p>
            </div>
            <div className="h-12 w-12 bg-blue-50 rounded-xl flex items-center justify-center">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white">
          <CardContent className="p-6 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Active Applications</p>
              <p className="text-3xl font-bold text-gray-900">
                {applications.filter(app => 
                  ['pending', 'applied', 'screening', 'interview_scheduled', 'interviewed', 'technical_test'].includes(app.status)
                ).length}
              </p>
            </div>
            <div className="h-12 w-12 bg-green-50 rounded-xl flex items-center justify-center">
              <Clock className="h-6 w-6 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white">
          <CardContent className="p-6 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Interviews</p>
              <p className="text-3xl font-bold text-gray-900">
                {applications.filter(app => 
                  ['interview_scheduled', 'interviewed'].includes(app.status)
                ).length}
              </p>
            </div>
            <div className="h-12 w-12 bg-purple-50 rounded-xl flex items-center justify-center">
              <Calendar className="h-6 w-6 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white">
          <CardContent className="p-6 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500 mb-1">Success Rate</p>
              <p className="text-3xl font-bold text-gray-900">
                {applications.length > 0 
                  ? Math.round((applications.filter(app => app.status === 'offer_accepted').length / applications.length) * 100)
                  : 0}%
              </p>
            </div>
            <div className="h-12 w-12 bg-orange-50 rounded-xl flex items-center justify-center">
              <TrendingUp className="h-6 w-6 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="rounded-2xl shadow-sm border border-gray-100 bg-white mb-8">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  id="search"
                  placeholder="Search jobs, companies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all">
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
                <SelectTrigger className="focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all">
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
                className="w-full h-10 border-gray-300 hover:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
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
          filteredApplications.map((application, idx) => (
            <Card
              key={`${application.id}-${application.job_title}-${idx}`}
              className="rounded-2xl shadow-sm border border-gray-100 bg-white transition-all hover:shadow-lg group"
            >
              <CardContent className="p-6">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2">
                      <div className="min-w-0">
                        <h3 className="text-xl font-bold text-gray-900 truncate mb-1">{application.job_title}</h3>
                        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-1">
                          <div className="flex items-center gap-1">
                            <Building className="h-4 w-4" />
                            <span className="truncate max-w-[120px]">{application.company}</span>
                          </div>
                          {application.location && (
                            <div className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              <span className="truncate max-w-[100px]">{application.location}</span>
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
                      <span
                        className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold border ${statusColors[application.status as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'} shadow-sm`}
                        title={application.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      >
                        {getStatusIcon(application.status)}
                        {application.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-4 text-xs text-gray-500 mt-2">
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
                      <div className="mt-3 p-3 bg-gray-50 rounded-lg border text-sm text-gray-700">
                        {application.notes}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-row md:flex-col gap-2 md:items-end md:justify-between min-w-fit">
                    {application.job_url && (
                      <Button
                        variant="ghost"
                        size="icon"
                        asChild
                        className="hover:bg-blue-50"
                        title="View Job Posting"
                        aria-label="View Job Posting"
                      >
                        <a href={application.job_url} target="_blank" rel="noopener noreferrer">
                          <Eye className="h-5 w-5" />
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
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => openEditModal(application)}
                      title="Edit Application"
                      aria-label="Edit Application"
                      className="hover:bg-yellow-50"
                    >
                      <Edit className="h-5 w-5" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this application?')) {
                          deleteApplication(application.id);
                        }
                      }}
                      title="Delete Application"
                      aria-label="Delete Application"
                      className="hover:bg-red-50"
                    >
                      <Trash2 className="h-5 w-5" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <Dialog open={showAddModal} onOpenChange={setShowAddModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Application</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddApplication} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="job_title">Job Title</Label>
                <Input id="job_title" name="job_title" value={newApp.job_title} onChange={handleAddChange} required />
              </div>
              <div>
                <Label htmlFor="company">Company</Label>
                <Input id="company" name="company" value={newApp.company} onChange={handleAddChange} required />
              </div>
              <div>
                <Label htmlFor="location">Location</Label>
                <Input id="location" name="location" value={newApp.location} onChange={handleAddChange} />
              </div>
              <div>
                <Label htmlFor="status">Status</Label>
                <Select value={newApp.status} onValueChange={val => setNewApp(prev => ({ ...prev, status: val }))}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {statusOptions.slice(1).map(option => (
                      <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="application_date">Application Date</Label>
                <Input id="application_date" name="application_date" type="date" value={newApp.application_date} onChange={handleAddChange} />
              </div>
              <div>
                <Label htmlFor="salary_min">Salary Min</Label>
                <Input id="salary_min" name="salary_min" type="number" value={newApp.salary_min} onChange={handleAddChange} />
              </div>
              <div>
                <Label htmlFor="salary_max">Salary Max</Label>
                <Input id="salary_max" name="salary_max" type="number" value={newApp.salary_max} onChange={handleAddChange} />
              </div>
              <div>
                <Label htmlFor="job_url">Job URL</Label>
                <Input id="job_url" name="job_url" value={newApp.job_url} onChange={handleAddChange} />
              </div>
              <div>
                <Label htmlFor="interview_date">Interview Date</Label>
                <Input id="interview_date" name="interview_date" type="date" value={newApp.interview_date} onChange={handleAddChange} />
              </div>
              <div className="md:col-span-2">
                <Label htmlFor="notes">Notes</Label>
                <Input id="notes" name="notes" value={newApp.notes} onChange={handleAddChange} />
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" disabled={adding}>{adding ? "Adding..." : "Add Application"}</Button>
              <DialogClose asChild>
                <Button type="button" variant="outline">Cancel</Button>
              </DialogClose>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Application</DialogTitle>
          </DialogHeader>
          {editApp && (
            <form onSubmit={handleEditApplication} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="edit_job_title">Job Title</Label>
                  <Input id="edit_job_title" name="job_title" value={editApp.job_title} onChange={handleEditChange} required />
                </div>
                <div>
                  <Label htmlFor="edit_company">Company</Label>
                  <Input id="edit_company" name="company" value={editApp.company} onChange={handleEditChange} required />
                </div>
                <div>
                  <Label htmlFor="edit_location">Location</Label>
                  <Input id="edit_location" name="location" value={editApp.location} onChange={handleEditChange} />
                </div>
                <div>
                  <Label htmlFor="edit_status">Status</Label>
                  <Select value={editApp.status} onValueChange={handleEditStatusChange}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {statusOptions.slice(1).map(option => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="edit_application_date">Application Date</Label>
                  <Input id="edit_application_date" name="application_date" type="date" value={editApp.application_date} onChange={handleEditChange} />
                </div>
                <div>
                  <Label htmlFor="edit_salary_min">Salary Min</Label>
                  <Input id="edit_salary_min" name="salary_min" type="number" value={editApp.salary_min ?? ""} onChange={handleEditChange} />
                </div>
                <div>
                  <Label htmlFor="edit_salary_max">Salary Max</Label>
                  <Input id="edit_salary_max" name="salary_max" type="number" value={editApp.salary_max ?? ""} onChange={handleEditChange} />
                </div>
                <div>
                  <Label htmlFor="edit_job_url">Job URL</Label>
                  <Input id="edit_job_url" name="job_url" value={editApp.job_url ?? ""} onChange={handleEditChange} />
                </div>
                <div>
                  <Label htmlFor="edit_interview_date">Interview Date</Label>
                  <Input id="edit_interview_date" name="interview_date" type="date" value={editApp.interview_date ?? ""} onChange={handleEditChange} />
                </div>
                <div className="md:col-span-2">
                  <Label htmlFor="edit_notes">Notes</Label>
                  <Input id="edit_notes" name="notes" value={editApp.notes ?? ""} onChange={handleEditChange} />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" disabled={editing}>{editing ? "Saving..." : "Save Changes"}</Button>
                <DialogClose asChild>
                  <Button type="button" variant="outline">Cancel</Button>
                </DialogClose>
              </DialogFooter>
            </form>
          )}
        </DialogContent>
      </Dialog>
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