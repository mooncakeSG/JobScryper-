"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { 
  Search, 
  MapPin, 
  Building2, 
  Clock, 
  Star,
  ExternalLink,
  Filter,
  Loader2
} from "lucide-react";
import { apiService, JobMatch } from "@/lib/api";

// Add a simple toast/snackbar for feedback
function Toast({ message, onClose }: { message: string, onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 2500);
    return () => clearTimeout(timer);
  }, [onClose]);
  return (
    <div className="fixed bottom-6 right-6 bg-blue-600 text-white px-4 py-2 rounded shadow-lg z-50">
      {message}
    </div>
  );
}

export default function MatchPage() {
  const [jobs, setJobs] = useState<JobMatch[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [location, setLocation] = useState("");
  const [filters, setFilters] = useState({
    jobType: "all",
    minSalary: "",
    company: ""
  });
  const [toast, setToast] = useState<string | null>(null);
  const [applyingId, setApplyingId] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [savedJobs, setSavedJobs] = useState<{ [id: string]: boolean }>({});
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Mock data for demonstration
  const mockJobs: JobMatch[] = [
    {
      id: "1",
      title: "Senior Software Engineer",
      company: "TechCorp Inc.",
      location: "San Francisco, CA",
      salary: "$120,000 - $180,000",
      description: "Join our team to build scalable web applications using React, Node.js, and cloud technologies. We're looking for someone with 5+ years of experience in full-stack development.",
      matchScore: 95,
      datePosted: "2 days ago",
      jobType: "Full-time",
      source: "LinkedIn",
      url: "https://example.com/job1"
    },
    {
      id: "2",
      title: "Frontend Developer",
      company: "StartupXYZ",
      location: "Remote",
      salary: "$80,000 - $120,000",
      description: "Remote position for a passionate frontend developer. Experience with React, TypeScript, and modern UI frameworks required.",
      matchScore: 88,
      datePosted: "1 week ago",
      jobType: "Full-time",
      source: "Indeed",
      url: "https://example.com/job2"
    },
    {
      id: "3",
      title: "Full Stack Developer",
      company: "InnovateLabs",
      location: "New York, NY",
      salary: "$100,000 - $150,000",
      description: "Looking for a full-stack developer to join our innovative team. Must have experience with Python, JavaScript, and database design.",
      matchScore: 82,
      datePosted: "3 days ago",
      jobType: "Full-time",
      source: "Glassdoor",
      url: "https://example.com/job3"
    },
    {
      id: "4",
      title: "DevOps Engineer",
      company: "CloudFirst",
      location: "Austin, TX",
      salary: "$110,000 - $160,000",
      description: "Join our DevOps team to manage CI/CD pipelines and cloud infrastructure. Experience with AWS, Docker, and Kubernetes required.",
      matchScore: 78,
      datePosted: "5 days ago",
      jobType: "Full-time",
      source: "RemoteOK",
      url: "https://example.com/job4"
    }
  ];

  useEffect(() => {
    // Initialize with mock data
    setJobs(mockJobs);
  }, []);

  useEffect(() => {
    // Fetch saved jobs on mount
    apiService.getSavedJobs('demo').then((saved) => {
      const savedMap: { [id: string]: boolean } = {};
      saved.forEach((job: any) => {
        if (job.id) savedMap[job.id] = true;
        else if (job.url) savedMap[job.url] = true;
      });
      setSavedJobs(savedMap);
    });
    setIsLoggedIn(!!localStorage.getItem("token"));
  }, []);

  const searchJobs = async () => {
    setLoading(true);
    
    try {
      const result = await apiService.searchJobs({
        query: searchTerm,
        location: location,
        jobType: filters.jobType,
        minSalary: filters.minSalary,
        company: filters.company
      });
      
      setJobs(result);
    } catch (error) {
      console.error('Search error:', error);
      // Use mock data if API fails
      setJobs(mockJobs);
    } finally {
      setLoading(false);
    }
  };

  const getMatchColor = (score: number) => {
    if (score >= 90) return "bg-green-100 text-green-800";
    if (score >= 80) return "bg-blue-100 text-blue-800";
    if (score >= 70) return "bg-yellow-100 text-yellow-800";
    return "bg-gray-100 text-gray-800";
  };

  // Map backend jobs to frontend format
  const mappedJobs = jobs.map((job: any) => ({
    id: job.id || job.job_id || job._id || Math.random().toString(),
    title: job.title || job.job_title || "Untitled",
    company: job.company || job.company_name || "Unknown Company",
    location: job.location || job.city || job.place || "Unknown Location",
    salary: job.salary,
    description: job.description || job.desc || "No description provided.",
    matchScore: job.matchScore || job.match_score || 0,
    datePosted: job.datePosted || job.date_posted || "",
    jobType: job.jobType || job.job_type || "",
    source: job.source,
    url: job.url || job.job_url || "",
  }));

  console.log("Mapped jobs from API:", mappedJobs);

  // Temporarily show all jobs without filtering
  const filteredJobs = mappedJobs;

  // Handle Apply
  const handleApply = async (job: any) => {
    setApplyingId(job.id);
    try {
      await apiService.createApplication({
        job_title: job.title,
        company: job.company,
        location: job.location,
        job_description: job.description,
        job_url: job.url,
        source: job.source,
        job_type: job.jobType,
        match_score: job.matchScore,
      });
      setToast("Application submitted!");
    } catch (err) {
      setToast("Failed to apply. Try again.");
    } finally {
      setApplyingId(null);
    }
  };

  // Update handleSave to use backend
  const handleSave = async (job: any) => {
    setSavingId(job.id);
    try {
      await apiService.saveJob(job, 'demo');
      setSavedJobs(prev => ({ ...prev, [job.id]: true }));
      setToast("Job saved!");
    } catch (err) {
      setToast("Failed to save job.");
    } finally {
      setSavingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
        <h1 className="text-2xl font-bold mb-2">Find Your Perfect Job Match</h1>
        <p className="text-blue-100">
          Discover opportunities that match your skills and preferences
        </p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Search Jobs</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="search">Job Title or Keywords</Label>
              <Input
                id="search"
                placeholder="e.g., Software Engineer, React Developer"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="location">Location</Label>
              <Input
                id="location"
                placeholder="e.g., San Francisco, Remote"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="jobType">Job Type</Label>
              <select
                id="jobType"
                className="w-full p-2 border border-gray-300 rounded-md"
                value={filters.jobType}
                onChange={(e) => setFilters({...filters, jobType: e.target.value})}
              >
                <option value="all">All Types</option>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="remote">Remote</option>
              </select>
            </div>
            <div>
              <Label htmlFor="minSalary">Minimum Salary</Label>
              <Input
                id="minSalary"
                placeholder="e.g., 80000"
                value={filters.minSalary}
                onChange={(e) => setFilters({...filters, minSalary: e.target.value})}
              />
            </div>
            <div>
              <Label htmlFor="company">Company</Label>
              <Input
                id="company"
                placeholder="e.g., Google, Microsoft"
                value={filters.company}
                onChange={(e) => setFilters({...filters, company: e.target.value})}
              />
            </div>
          </div>

          <Button onClick={searchJobs} disabled={loading} className="w-full">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Searching...
              </>
            ) : (
              <>
                <Search className="mr-2 h-4 w-4" />
                Search Jobs
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            {filteredJobs.length} Jobs Found
          </h2>
          <Button variant="outline" size="sm">
            <Filter className="mr-2 h-4 w-4" />
            More Filters
          </Button>
        </div>

        {filteredJobs.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <Search className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <p className="text-gray-500">No jobs found matching your criteria</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {filteredJobs.map((job) => (
              <Card key={job.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">{job.title}</CardTitle>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                        <div className="flex items-center space-x-1">
                          <Building2 className="h-4 w-4" />
                          <span>{job.company}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MapPin className="h-4 w-4" />
                          <span>{job.location}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="h-4 w-4" />
                          <span>{job.datePosted}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getMatchColor(job.matchScore)}`}>
                        {job.matchScore}% Match
                      </span>
                      <Star className="h-4 w-4 text-yellow-500" />
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 mb-4">{job.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-sm">
                      <span className="bg-gray-100 px-2 py-1 rounded">{job.jobType}</span>
                      {job.salary && (
                        <span className="text-green-600 font-medium">{job.salary}</span>
                      )}
                      <span className="text-gray-500">via {job.source}</span>
                    </div>
                    
                    <div className="flex space-x-2">
                      {isLoggedIn ? (
                        <>
                          <Button onClick={() => handleSave(job)} variant="outline" size="sm" disabled={!!savedJobs[job.id] || savingId === job.id}>
                            {savedJobs[job.id] ? "Saved" : savingId === job.id ? "Saving..." : "Save"}
                          </Button>
                          <Button
                            onClick={async () => {
                              try {
                                await apiService.createApplication({
                                  job_title: job.title,
                                  company: job.company,
                                  location: job.location,
                                  job_description: job.description,
                                  job_url: job.url,
                                  source: job.source,
                                  job_type: job.jobType,
                                  match_score: job.matchScore,
                                });
                              } catch (err) {}
                              if (job.url) {
                                window.open(job.url, '_blank', 'noopener,noreferrer');
                              }
                            }}
                            size="sm"
                            disabled={!job.url}
                          >
                            <ExternalLink className="mr-1 h-4 w-4" />
                            Apply
                          </Button>
                        </>
                      ) : (
                        <Button variant="outline" size="sm" onClick={() => window.location.href = '/login'}>
                          Login to Save/Apply
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  );
} 