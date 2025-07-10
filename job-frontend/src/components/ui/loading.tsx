import * as React from "react"
import { cn } from "@/lib/utils"
import { Loader2, Loader } from "lucide-react"

// Spinner component
interface SpinnerProps extends React.ComponentProps<"div"> {
  size?: "sm" | "md" | "lg"
  variant?: "default" | "primary" | "secondary"
}

export function Spinner({ 
  size = "md", 
  variant = "default", 
  className,
  ...props 
}: SpinnerProps) {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6", 
    lg: "h-8 w-8"
  }

  const variantClasses = {
    default: "text-muted-foreground",
    primary: "text-primary",
    secondary: "text-secondary-foreground"
  }

  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn("flex items-center justify-center", className)}
      {...props}
    >
      <Loader2 
        className={cn(
          "animate-spin",
          sizeClasses[size],
          variantClasses[variant]
        )} 
      />
      <span className="sr-only">Loading...</span>
    </div>
  )
}

// Pulse loader
export function PulseLoader({ 
  size = "md", 
  className,
  ...props 
}: Omit<SpinnerProps, "variant">) {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8"
  }

  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn("flex items-center justify-center", className)}
      {...props}
    >
      <div className={cn(
        "animate-pulse rounded-full bg-muted-foreground/20",
        sizeClasses[size]
      )} />
      <span className="sr-only">Loading...</span>
    </div>
  )
}

// Dots loader
export function DotsLoader({ 
  size = "md", 
  className,
  ...props 
}: Omit<SpinnerProps, "variant">) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn("flex items-center justify-center space-x-1", className)}
      {...props}
    >
      <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.3s]" />
      <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.15s]" />
      <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/60" />
      <span className="sr-only">Loading...</span>
    </div>
  )
}

// Progress bar
interface ProgressBarProps extends React.ComponentProps<"div"> {
  value: number
  max?: number
  variant?: "default" | "success" | "warning" | "error"
  showLabel?: boolean
}

export function ProgressBar({ 
  value, 
  max = 100, 
  variant = "default",
  showLabel = false,
  className,
  ...props 
}: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100)
  
  const variantClasses = {
    default: "bg-primary",
    success: "bg-green-500",
    warning: "bg-yellow-500", 
    error: "bg-red-500"
  }

  return (
    <div className={cn("w-full", className)} {...props}>
      {showLabel && (
        <div className="flex justify-between text-sm text-muted-foreground mb-1">
          <span>Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
        <div
          className={cn(
            "h-full transition-all duration-300 ease-out",
            variantClasses[variant]
          )}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  )
}

// Skeleton loader
interface SkeletonProps extends React.ComponentProps<"div"> {
  variant?: "text" | "circular" | "rectangular"
  width?: string | number
  height?: string | number
}

export function Skeleton({ 
  variant = "rectangular",
  width,
  height,
  className,
  ...props 
}: SkeletonProps) {
  const baseClasses = "animate-pulse bg-muted-foreground/20"
  
  const variantClasses = {
    text: "h-4 rounded",
    circular: "rounded-full",
    rectangular: "rounded-md"
  }

  const style = {
    width: width,
    height: height,
  }

  return (
    <div
      className={cn(
        baseClasses,
        variantClasses[variant],
        className
      )}
      style={style}
      {...props}
    />
  )
}

// Loading overlay
interface LoadingOverlayProps extends React.ComponentProps<"div"> {
  loading: boolean
  text?: string
  spinner?: React.ReactNode
}

export function LoadingOverlay({ 
  loading, 
  text = "Loading...",
  spinner,
  children,
  className,
  ...props 
}: LoadingOverlayProps) {
  if (!loading) return <>{children}</>

  return (
    <div className={cn("relative", className)} {...props}>
      {children}
      <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="flex flex-col items-center space-y-2">
          {spinner || <Spinner size="lg" />}
          {text && (
            <p className="text-sm text-muted-foreground">{text}</p>
          )}
        </div>
      </div>
    </div>
  )
}

// Page loader
export function PageLoader({ 
  text = "Loading page...",
  className,
  ...props 
}: React.ComponentProps<"div"> & { text?: string }) {
  return (
    <div 
      className={cn(
        "min-h-screen flex items-center justify-center",
        className
      )}
      {...props}
    >
      <div className="flex flex-col items-center space-y-4">
        <Spinner size="lg" />
        <p className="text-muted-foreground">{text}</p>
      </div>
    </div>
  )
} 