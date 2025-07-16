import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "./badge";
import { 
  Building2, 
  MapPin, 
  Clock, 
  Star, 
  ExternalLink,
  Calendar,
  DollarSign,
  Briefcase,
  Globe
} from "lucide-react";
import { JobMatch } from "@/lib/api";
import { CurrencyDisplay } from "./currency-display";

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

export function JobCard({
  job,
  onSave,
  onApply,
  isSaved = false,
  isSaving = false,
  isApplying = false,
  isLoggedIn = true
}: JobCardProps) {
  const getMatchColor = (score: number) => {
    if (score >= 90) return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
    if (score >= 80) return "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400";
    if (score >= 70) return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400";
    return "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300";
  };

  const getSalaryColor = () => {
    return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400";
  };

  const formatSalary = (salary?: string) => {
    if (!salary) return null;
    // If salary is already formatted, return as is
    if (salary.includes('/')) return salary;
    // If it's a range, format it
    if (salary.includes('-')) {
      return `${salary}/year`;
    }
    return salary;
  };

  const parseSalaryForDisplay = (salary?: string) => {
    if (!salary) return null;
    
    // Extract numbers from salary string
    const numbers = salary.match(/\d+/g);
    if (!numbers || numbers.length === 0) return salary;
    
    // If it's a range (e.g., "80000-150000")
    if (numbers.length >= 2) {
      const min = parseInt(numbers[0], 10);
      const max = parseInt(numbers[1], 10);
      return { min, max, isRange: true };
    }
    
    // If it's a single value
    const amount = parseInt(numbers[0], 10);
    return { amount, isRange: false };
  };

  const handleWebsiteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (job.website) {
      window.open(job.website, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <Card className="group hover:shadow-lg transition-all duration-200 ease-in-out hover:scale-[1.01] transform-gpu border border-gray-200 dark:border-gray-700">
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between gap-4">
          {/* Left side - Job info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-3">
              <CardTitle className="text-xl font-bold text-gray-900 dark:text-gray-100 leading-tight">
                {job.title}
              </CardTitle>
              {/* Match Score Badge */}
              <Badge 
                className={`${getMatchColor(job.matchScore)} font-semibold text-sm px-3 py-1 rounded-full shadow-sm`}
                title={`${job.matchScore}% match with your profile`}
              >
                {job.matchScore}% Match
              </Badge>
            </div>

            {/* Company and Location */}
            <div className="space-y-2 mb-3">
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <Building2 className="h-4 w-4 flex-shrink-0" />
                <span className="font-medium">{job.company}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <MapPin className="h-4 w-4 flex-shrink-0" />
                <span>{job.location}</span>
              </div>
            </div>

            {/* Commitment and Compensation Type */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
              {job.commitment && (
                <div className="flex items-center gap-1">
                  <Briefcase className="h-4 w-4" />
                  <span><strong>Commitment:</strong> {job.commitment}</span>
                </div>
              )}
              {job.compensationType && (
                <div className="flex items-center gap-1">
                  <span><strong>Compensation:</strong> {job.compensationType}</span>
                </div>
              )}
            </div>

            {/* Start Date */}
            {job.startDate && (
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-3">
                <Calendar className="h-4 w-4" />
                <span><strong>Start Date:</strong> {job.startDate}</span>
              </div>
            )}

            {/* Website */}
            {job.website && (
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-3">
                <Globe className="h-4 w-4" />
                <span><strong>Website:</strong> {job.website}</span>
              </div>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Description */}
        <div className="mb-4">
          <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
            {job.description}
          </p>
        </div>

        {/* Highlights */}
        {job.highlights && job.highlights.length > 0 && (
          <div className="mb-4">
            <h4 className="font-semibold text-gray-900 dark:text-gray-100 mb-2 text-sm">
              Our Benefits to Industries:
            </h4>
            <ul className="space-y-1">
              {job.highlights.map((highlight, index) => (
                <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                  <span className="text-gray-400 dark:text-gray-500 mt-1">•</span>
                  <span>{highlight}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Bottom section with salary, badges, and actions */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pt-4 border-t border-gray-100 dark:border-gray-700">
          {/* Left side - Salary and badges */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Salary Range */}
            {job.salary && (
              <Badge className={`${getSalaryColor()} font-semibold text-sm px-3 py-1 rounded-full shadow-sm`}>
                <DollarSign className="h-3 w-3 mr-1" />
                {(() => {
                  const parsed = parseSalaryForDisplay(job.salary);
                  if (!parsed || typeof parsed === 'string') {
                    return formatSalary(job.salary);
                  }
                  
                  if (parsed.isRange && parsed.min !== undefined && parsed.max !== undefined) {
                    return (
                      <span className="flex items-center gap-1">
                        <CurrencyDisplay amount={parsed.min} currency="USD" size="sm" />
                        <span>-</span>
                        <CurrencyDisplay amount={parsed.max} currency="USD" size="sm" />
                        <span className="text-xs">/year</span>
                      </span>
                    );
                  } else if (!parsed.isRange && parsed.amount !== undefined) {
                    return (
                      <span className="flex items-center gap-1">
                        <CurrencyDisplay amount={parsed.amount} currency="USD" size="sm" />
                        <span className="text-xs">/year</span>
                      </span>
                    );
                  }
                })()}
              </Badge>
            )}
            
            {/* Job Type Badge */}
            {job.jobType && (
              <Badge variant="secondary" className="text-xs px-2 py-1">
                {job.jobType}
              </Badge>
            )}

            {/* Compensation Type Badges */}
            {job.compensationType && (
              <Badge variant="outline" className="text-xs px-2 py-1">
                {job.compensationType.toLowerCase()}
              </Badge>
            )}

            {/* Source */}
            <span className="text-xs text-gray-500 dark:text-gray-400">
              via {job.source}
            </span>
          </div>

          {/* Right side - Actions */}
          <div className="flex items-center gap-2">
            {/* Visit Company Website */}
            {job.website && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleWebsiteClick}
                className="text-xs"
              >
                <ExternalLink className="h-3 w-3 mr-1" />
                Visit Company Website
              </Button>
            )}

            {/* Save and Apply buttons */}
            {isLoggedIn ? (
              <>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => onSave?.(job)}
                  disabled={isSaving}
                  className={`h-8 w-8 ${isSaved ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' : 'hover:bg-blue-50 dark:hover:bg-blue-900/20'}`}
                  title={isSaved ? "Saved" : "Save Job"}
                  aria-label={isSaved ? "Saved" : "Save Job"}
                >
                  <Star className={`h-4 w-4 ${isSaved ? 'fill-current' : ''}`} />
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  onClick={() => onApply?.(job)}
                  disabled={isApplying || !job.url}
                  className="text-xs"
                >
                  {isApplying ? (
                    <>
                      <Clock className="h-3 w-3 mr-1 animate-spin" />
                      Applying...
                    </>
                  ) : (
                    <>
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Apply
                    </>
                  )}
                </Button>
              </>
            ) : (
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => window.location.href = '/login'}
                className="text-xs"
              >
                Login to Save/Apply
              </Button>
            )}
          </div>
        </div>

        {/* Match Explanation */}
        {job.matchExplanation && (
          <div className="mt-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2 text-sm">
              AI Match Explanation:
            </h4>
            <div className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
              {job.matchExplanation.split('\n').map((line, index) => (
                <p key={index} className="mb-2 last:mb-0">
                  {line}
                </p>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

 