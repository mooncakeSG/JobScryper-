import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

export function JobCardSkeleton() {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-3">
            <div className="flex items-start justify-between">
              <div className="space-y-2">
                <Skeleton className="h-6 w-3/4" />
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-1">
                    <Skeleton className="h-4 w-4" />
                    <Skeleton className="h-4 w-24" />
                  </div>
                  <div className="flex items-center gap-1">
                    <Skeleton className="h-4 w-4" />
                    <Skeleton className="h-4 w-32" />
                  </div>
                  <div className="flex items-center gap-1">
                    <Skeleton className="h-4 w-4" />
                    <Skeleton className="h-4 w-28" />
                  </div>
                </div>
              </div>
              <Skeleton className="h-8 w-24 rounded-full" />
            </div>

            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1">
                <Skeleton className="h-4 w-4" />
                <Skeleton className="h-4 w-20" />
              </div>
              <div className="flex items-center gap-1">
                <Skeleton className="h-4 w-4" />
                <Skeleton className="h-4 w-24" />
              </div>
            </div>

            <Skeleton className="h-16 w-full" />
          </div>

          <div className="flex items-center gap-2 ml-4">
            <Skeleton className="h-8 w-8" />
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-8 w-8" />
            <Skeleton className="h-8 w-8" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function JobCardSkeletonList({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <JobCardSkeleton key={index} />
      ))}
    </div>
  );
} 