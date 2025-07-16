"use client";
import * as React from "react"
import { cn } from "@/lib/utils"

// Fade in animation
interface FadeInProps extends React.ComponentProps<"div"> {
  delay?: number
  duration?: number
  children: React.ReactNode
}

export function FadeIn({ 
  delay = 0, 
  duration = 300, 
  children, 
  className,
  ...props 
}: FadeInProps) {
  const [isVisible, setIsVisible] = React.useState(false)

  React.useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  return (
    <div
      className={cn(
        "transition-all duration-300 ease-out",
        isVisible 
          ? "opacity-100 translate-y-0" 
          : "opacity-0 translate-y-4",
        className
      )}
      style={{ transitionDuration: `${duration}ms` }}
      {...props}
    >
      {children}
    </div>
  )
}

// Slide in animation
interface SlideInProps extends React.ComponentProps<"div"> {
  direction?: "up" | "down" | "left" | "right"
  delay?: number
  duration?: number
  children: React.ReactNode
}

export function SlideIn({ 
  direction = "up", 
  delay = 0, 
  duration = 300, 
  children, 
  className,
  ...props 
}: SlideInProps) {
  const [isVisible, setIsVisible] = React.useState(false)

  React.useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  const getTransform = () => {
    switch (direction) {
      case "up":
        return isVisible ? "translateY(0)" : "translateY(20px)"
      case "down":
        return isVisible ? "translateY(0)" : "translateY(-20px)"
      case "left":
        return isVisible ? "translateX(0)" : "translateX(20px)"
      case "right":
        return isVisible ? "translateX(0)" : "translateX(-20px)"
      default:
        return isVisible ? "translateY(0)" : "translateY(20px)"
    }
  }

  return (
    <div
      className={cn(
        "transition-all duration-300 ease-out",
        isVisible ? "opacity-100" : "opacity-0",
        className
      )}
      style={{ 
        transform: getTransform(),
        transitionDuration: `${duration}ms` 
      }}
      {...props}
    >
      {children}
    </div>
  )
}

// Scale in animation
interface ScaleInProps extends React.ComponentProps<"div"> {
  delay?: number
  duration?: number
  children: React.ReactNode
}

export function ScaleIn({ 
  delay = 0, 
  duration = 300, 
  children, 
  className,
  ...props 
}: ScaleInProps) {
  const [isVisible, setIsVisible] = React.useState(false)

  React.useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), delay)
    return () => clearTimeout(timer)
  }, [delay])

  return (
    <div
      className={cn(
        "transition-all duration-300 ease-out transform-gpu",
        isVisible 
          ? "opacity-100 scale-100" 
          : "opacity-0 scale-95",
        className
      )}
      style={{ transitionDuration: `${duration}ms` }}
      {...props}
    >
      {children}
    </div>
  )
}

// Stagger animation for lists
interface StaggerProps extends React.ComponentProps<"div"> {
  staggerDelay?: number
  children: React.ReactNode
}

export function Stagger({ 
  staggerDelay = 100, 
  children, 
  className,
  ...props 
}: StaggerProps) {
  const childrenArray = React.Children.toArray(children)

  return (
    <div className={className} {...props}>
      {childrenArray.map((child, index) => (
        <FadeIn key={index} delay={index * staggerDelay}>
          {child}
        </FadeIn>
      ))}
    </div>
  )
}

// Pulse animation
interface PulseProps extends React.ComponentProps<"div"> {
  children: React.ReactNode
}

export function Pulse({ children, className, ...props }: PulseProps) {
  return (
    <div
      className={cn(
        "animate-pulse",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// Bounce animation
interface BounceProps extends React.ComponentProps<"div"> {
  children: React.ReactNode
}

export function Bounce({ children, className, ...props }: BounceProps) {
  return (
    <div
      className={cn(
        "animate-bounce",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// Shake animation
interface ShakeProps extends React.ComponentProps<"div"> {
  children: React.ReactNode
}

export function Shake({ children, className, ...props }: ShakeProps) {
  return (
    <div
      className={cn(
        "animate-[shake_0.5s_ease-in-out]",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// Hover lift effect
interface HoverLiftProps extends React.ComponentProps<"div"> {
  children: React.ReactNode
}

export function HoverLift({ children, className, ...props }: HoverLiftProps) {
  return (
    <div
      className={cn(
        "transition-all duration-200 ease-out hover:scale-105 hover:shadow-lg transform-gpu",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

// Ripple effect for buttons
interface RippleProps extends React.ComponentProps<"div"> {
  children: React.ReactNode
}

export function Ripple({ children, className, ...props }: RippleProps) {
  const [ripples, setRipples] = React.useState<Array<{ id: number; x: number; y: number }>>([])

  const handleClick = (event: React.MouseEvent) => {
    const rect = event.currentTarget.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top
    const id = Date.now()

    setRipples(prev => [...prev, { id, x, y }])

    setTimeout(() => {
      setRipples(prev => prev.filter(ripple => ripple.id !== id))
    }, 600)
  }

  return (
    <div
      className={cn("relative overflow-hidden", className)}
      onClick={handleClick}
      {...props}
    >
      {children}
      {ripples.map(ripple => (
        <div
          key={ripple.id}
          className="absolute w-2 h-2 bg-white/30 rounded-full animate-[ripple_0.6s_linear] pointer-events-none"
          style={{
            left: ripple.x - 4,
            top: ripple.y - 4,
          }}
        />
      ))}
    </div>
  )
} 