import React, { useState } from "react";
import { JobCard } from "./job-card";
import { JobMatch } from "@/lib/api";

// Sample job data that matches the structure from the image
const sampleJobs: (JobMatch & {
  commitment?: string;
  compensationType?: string;
  startDate?: string;
  website?: string;
  highlights?: string[];
  matchExplanation?: string;
})[] = [
  {
    id: "1",
    title: "Full Stack Lead Developer (Intern-to-Hire)",
    company: "Maskd AI - Rhesto Division",
    location: "Remote",
    salary: "$48,877 - $89,667",
    description: "About the Role Rhesto — the hospitality tech subsidiary of **Maskd AI** — is revolutionizing how restaurants and hotels handle front-of-house operations using realistic voice and AI automation.",
    matchScore: 80,
    datePosted: "2 days ago",
    jobType: "Full-Time",
    source: "JobSpy",
    url: "https://example.com/job1",
    commitment: "Full-Time (3)-Month Unpaid Internship → Paid Role)",
    compensationType: "Internship",
    startDate: "Immediate",
    website: "www.maskdai.com",
    highlights: [
      "Increased Efficiency: AI-powered automation reduces manual tasks by 60%",
      "Cost Savings: Average 40% reduction in operational costs",
      "Improved Customer Experience: 24/7 availability with personalized interactions",
      "Scalable Solution: Easy integration with existing systems"
    ],
    matchExplanation: `Job Summary: Full Stack Lead Developer position at Maskd AI's Rhesto Division, focusing on hospitality tech and AI automation.

Your Profile Highlights:
1. **Technical Skills**: Proficiency in full-stack development (Python, JavaScript, React, FastAPI, etc.), machine learning, and AI tools (OpenAI, IBM WatsonX, Groq).
2. **Experience**: Current involvement in an AI bootcamp, experience as an IT Support Associate, and development of production-ready projects (e.g., IntelliAssist, Sentiment Analysis Dashboard, AI Resume Builder).
3. **Unique Perspective**: Combines technical skills with a legal background, emphasizing ethical tech solutions, digital safety, and privacy.

Match Score: 80

Explanation: Strong alignment in technical skills and AI experience. The role's focus on AI automation matches your expertise. The internship-to-hire structure provides a good entry point. Consider highlighting your AI project experience in your application.`
  },
  {
    id: "2",
    title: "Senior React Developer",
    company: "TechCorp Inc.",
    location: "San Francisco, CA",
    salary: "$120,000 - $180,000",
    description: "Join our team to build scalable web applications using React, Node.js, and cloud technologies. We're looking for someone with 5+ years of experience in full-stack development.",
    matchScore: 95,
    datePosted: "1 day ago",
    jobType: "Full-time",
    source: "LinkedIn",
    url: "https://example.com/job2",
    commitment: "Full-Time",
    compensationType: "Salary",
    startDate: "ASAP",
    website: "www.techcorp.com",
    highlights: [
      "Competitive salary and equity package",
      "Flexible work arrangements",
      "Professional development opportunities",
      "Health, dental, and vision insurance"
    ],
    matchExplanation: "Excellent match! Your React experience and full-stack skills align perfectly with this role."
  },
  {
    id: "3",
    title: "Frontend Developer",
    company: "StartupXYZ",
    location: "Remote",
    salary: "$80,000 - $120,000",
    description: "Remote position for a passionate frontend developer. Experience with React, TypeScript, and modern UI frameworks required.",
    matchScore: 88,
    datePosted: "3 days ago",
    jobType: "Full-time",
    source: "Indeed",
    url: "https://example.com/job3",
    commitment: "Full-Time",
    compensationType: "Salary",
    startDate: "Flexible",
    website: "www.startupxyz.com",
    highlights: [
      "100% remote work environment",
      "Flexible hours and unlimited PTO",
      "Stock options in a growing company",
      "Modern tech stack and learning opportunities"
    ],
    matchExplanation: "Great match for your frontend skills and remote work preference."
  }
];

export function JobCardExample() {
  const [savedJobs, setSavedJobs] = useState<{ [id: string]: boolean }>({});
  const [applyingJobs, setApplyingJobs] = useState<{ [id: string]: boolean }>({});
  const [isLoggedIn, setIsLoggedIn] = useState(true);

  const handleSave = (job: JobMatch) => {
    setSavedJobs(prev => ({ ...prev, [job.id]: true }));
    console.log("Saving job:", job.title);
  };

  const handleApply = (job: JobMatch) => {
    setApplyingJobs(prev => ({ ...prev, [job.id]: true }));
    console.log("Applying to job:", job.title);
    
    // Simulate application process
    setTimeout(() => {
      setApplyingJobs(prev => ({ ...prev, [job.id]: false }));
      if (job.url) {
        window.open(job.url, '_blank', 'noopener,noreferrer');
      }
    }, 2000);
  };

  return (
    <div className="space-y-6 p-6">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Job Card Component Example
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Demonstrating the JobCard component with sample data from the /api/match response
        </p>
      </div>

      {/* Login Toggle */}
      <div className="flex justify-center mb-6">
        <button
          onClick={() => setIsLoggedIn(!isLoggedIn)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          {isLoggedIn ? "Logout" : "Login"}
        </button>
      </div>

      {/* Job Cards */}
      <div className="space-y-6">
        {sampleJobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            onSave={handleSave}
            onApply={handleApply}
            isSaved={savedJobs[job.id]}
            isSaving={false}
            isApplying={applyingJobs[job.id]}
            isLoggedIn={isLoggedIn}
          />
        ))}
      </div>

      {/* Instructions */}
      <div className="mt-8 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
          Component Features:
        </h3>
        <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
          <li>• Responsive design with clean card layout</li>
          <li>• Match score badge with color coding</li>
          <li>• Salary range displayed as green badge</li>
          <li>• Company website link when available</li>
          <li>• Highlights displayed as bullet points</li>
          <li>• Save and Apply functionality</li>
          <li>• Dark mode support</li>
          <li>• Accessible HTML structure</li>
        </ul>
      </div>
    </div>
  );
} 