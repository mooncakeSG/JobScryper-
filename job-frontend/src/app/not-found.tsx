import Link from "next/link";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background text-foreground px-4">
      <div className="flex flex-col items-center gap-4 p-8 rounded-xl shadow-md bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800">
        <AlertCircle className="h-16 w-16 text-red-500 mb-2" />
        <h1 className="text-3xl font-bold mb-2">404 - Page Not Found</h1>
        <p className="text-gray-600 dark:text-gray-300 mb-4 text-center max-w-md">
          Sorry, the page you are looking for does not exist or has been moved.
        </p>
        <Link href="/">
          <Button variant="outline" className="font-semibold">Go to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
} 