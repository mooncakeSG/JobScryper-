# JobCard Component

A reusable React component for displaying job information in a clean, accessible card layout. The component is designed to work with data from the `/api/match` endpoint and supports both light and dark themes.

## Features

- **Responsive Design**: Clean card layout that works on all screen sizes
- **Accessibility**: Semantic HTML with proper ARIA labels and keyboard navigation
- **Dark Mode Support**: Full dark mode compatibility with Tailwind CSS
- **Interactive Elements**: Save and Apply functionality with loading states
- **Visual Hierarchy**: Clear organization of job information with proper spacing
- **Color-coded Match Scores**: Visual indicators for job match percentages
- **Company Website Integration**: Direct links to company websites when available

## Props

```typescript
interface JobCardProps {
  job: JobMatch & {
    commitment?: string;
    compensationType?: string;
    startDate?: string;
    website?: string;
    highlights?: string[];
    matchExplanation?: string;
  };
  onSave?: (job: JobMatch) => void;
  onApply?: (job: JobMatch) => void;
  isSaved?: boolean;
  isSaving?: boolean;
  isApplying?: boolean;
  isLoggedIn?: boolean;
}
```

## Usage

### Basic Usage

```tsx
import { JobCard } from "@/components/ui/job-card";

const job = {
  id: "1",
  title: "Full Stack Developer",
  company: "TechCorp Inc.",
  location: "San Francisco, CA",
  salary: "$120,000 - $180,000",
  description: "Join our team to build scalable web applications...",
  matchScore: 95,
  datePosted: "2 days ago",
  jobType: "Full-time",
  source: "LinkedIn",
  url: "https://example.com/job",
  commitment: "Full-Time",
  compensationType: "Salary",
  startDate: "ASAP",
  website: "www.techcorp.com",
  highlights: [
    "Competitive salary and equity package",
    "Flexible work arrangements",
    "Professional development opportunities"
  ],
  matchExplanation: "Excellent match! Your skills align perfectly with this role."
};

function JobList() {
  const handleSave = (job) => {
    console.log("Saving job:", job.title);
  };

  const handleApply = (job) => {
    console.log("Applying to job:", job.title);
  };

  return (
    <JobCard
      job={job}
      onSave={handleSave}
      onApply={handleApply}
      isSaved={false}
      isSaving={false}
      isApplying={false}
      isLoggedIn={true}
    />
  );
}
```

### With API Data

```tsx
import { JobCard } from "@/components/ui/job-card";
import { apiService } from "@/lib/api";

function JobSearchResults() {
  const [jobs, setJobs] = useState([]);
  const [savedJobs, setSavedJobs] = useState({});

  const handleSave = async (job) => {
    try {
      await apiService.saveJob(job, 'user-id');
      setSavedJobs(prev => ({ ...prev, [job.id]: true }));
    } catch (error) {
      console.error("Failed to save job:", error);
    }
  };

  const handleApply = async (job) => {
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
      if (job.url) {
        window.open(job.url, '_blank', 'noopener,noreferrer');
      }
    } catch (error) {
      console.error("Failed to apply:", error);
    }
  };

  return (
    <div className="space-y-6">
      {jobs.map((job) => (
        <JobCard
          key={job.id}
          job={job}
          onSave={handleSave}
          onApply={handleApply}
          isSaved={!!savedJobs[job.id]}
          isSaving={false}
          isApplying={false}
          isLoggedIn={true}
        />
      ))}
    </div>
  );
}
```

## Displayed Fields

The JobCard component displays the following information:

1. **Job Title** - Prominently displayed at the top
2. **Match Score** - Color-coded badge showing percentage match
3. **Company** - Company name with building icon
4. **Location** - Job location with map pin icon
5. **Commitment** - Full-time, part-time, etc. (if available)
6. **Compensation Type** - Salary, contract, internship, etc. (if available)
7. **Start Date** - When the position starts (if available)
8. **Website** - Company website link (if available)
9. **Description** - Job description/summary
10. **Highlights** - Bullet points of benefits/features (if available)
11. **Salary Range** - Green badge with dollar sign icon
12. **Job Type Badge** - Secondary badge showing job type
13. **Source** - Job board source (e.g., "via JobSpy")
14. **Actions** - Save and Apply buttons

## Styling

The component uses Tailwind CSS classes and supports:

- **Light Theme**: Clean white cards with gray borders
- **Dark Theme**: Dark cards with appropriate contrast
- **Hover Effects**: Subtle scaling and shadow changes
- **Color Coding**: 
  - Green for high match scores (90%+)
  - Blue for good match scores (80-89%)
  - Yellow for moderate match scores (70-79%)
  - Gray for low match scores (<70%)
- **Responsive Design**: Adapts to different screen sizes

## Accessibility

- Semantic HTML structure
- Proper ARIA labels for interactive elements
- Keyboard navigation support
- Screen reader friendly
- High contrast ratios
- Focus indicators

## Dependencies

- React
- Tailwind CSS
- Lucide React (for icons)
- Class Variance Authority (for badge variants)

## Example

See `job-card-example.tsx` for a complete example with sample data and interactive functionality. 