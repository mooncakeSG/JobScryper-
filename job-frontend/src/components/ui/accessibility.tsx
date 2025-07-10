import * as React from "react";
import { cn } from "@/lib/utils";

// Skip to main content link
export function SkipToMainContent() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-white focus:px-4 focus:py-2 focus:text-black focus:outline-none focus:ring-2 focus:ring-blue-500 focus:rounded-md"
    >
      Skip to main content
    </a>
  );
}

// Focus trap for modals and dialogs
export function FocusTrap({ children, ...props }: React.ComponentProps<"div">) {
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Tab') {
        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    container.addEventListener('keydown', handleKeyDown);
    firstElement.focus();

    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return (
    <div ref={containerRef} {...props}>
      {children}
    </div>
  );
}

// Live region for announcements
export function LiveRegion({ 
  children, 
  role = "status", 
  "aria-live": ariaLive = "polite",
  className,
  ...props 
}: React.ComponentProps<"div"> & {
  role?: "status" | "alert" | "log";
  "aria-live"?: "polite" | "assertive" | "off";
}) {
  return (
    <div
      role={role}
      aria-live={ariaLive}
      className={cn("sr-only", className)}
      {...props}
    >
      {children}
    </div>
  );
}

// Visually hidden element
export function VisuallyHidden({ 
  children, 
  className,
  ...props 
}: React.ComponentProps<"span">) {
  return (
    <span
      className={cn(
        "absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0",
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}

// Screen reader only text
export function ScreenReaderOnly({ 
  children, 
  className,
  ...props 
}: React.ComponentProps<"span">) {
  return (
    <span
      className={cn("sr-only", className)}
      {...props}
    >
      {children}
    </span>
  );
}

// Accessible button that can be triggered with keyboard
export function AccessibleButton({
  children,
  onClick,
  onKeyDown,
  disabled = false,
  className,
  "aria-label": ariaLabel,
  "aria-describedby": ariaDescribedby,
  ...props
}: React.ComponentProps<"button"> & {
  onClick?: () => void;
  onKeyDown?: (event: React.KeyboardEvent) => void;
}) {
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onClick?.();
    }
    onKeyDown?.(event);
  };

  return (
    <button
      onClick={onClick}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedby}
      className={cn(
        "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background",
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}

// Accessible link that can be triggered with keyboard
export function AccessibleLink({
  children,
  href,
  onClick,
  onKeyDown,
  className,
  "aria-label": ariaLabel,
  "aria-describedby": ariaDescribedby,
  ...props
}: React.ComponentProps<"a"> & {
  onClick?: () => void;
  onKeyDown?: (event: React.KeyboardEvent) => void;
}) {
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onClick?.();
    }
    onKeyDown?.(event);
  };

  return (
    <a
      href={href}
      onClick={onClick}
      onKeyDown={handleKeyDown}
      aria-label={ariaLabel}
      aria-describedby={ariaDescribedby}
      className={cn(
        "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 focus:ring-offset-background",
        className
      )}
      {...props}
    >
      {children}
    </a>
  );
}

// Accessible list with keyboard navigation
export function AccessibleList<T>({
  items,
  renderItem,
  onItemSelect,
  className,
  "aria-label": ariaLabel,
  ...props
}: {
  items: T[];
  renderItem: (item: T, index: number, isSelected: boolean) => React.ReactNode;
  onItemSelect?: (item: T, index: number) => void;
  "aria-label"?: string;
} & Omit<React.ComponentProps<"ul">, "children">) {
  const [selectedIndex, setSelectedIndex] = React.useState(-1);
  const listRef = React.useRef<HTMLUListElement>(null);

  const handleKeyDown = (event: React.KeyboardEvent) => {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setSelectedIndex(prev => 
          prev < items.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        event.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : prev);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < items.length && onItemSelect) {
          onItemSelect(items[selectedIndex], selectedIndex);
        }
        break;
      case 'Home':
        event.preventDefault();
        setSelectedIndex(0);
        break;
      case 'End':
        event.preventDefault();
        setSelectedIndex(items.length - 1);
        break;
    }
  };

  return (
    <ul
      ref={listRef}
      role="listbox"
      aria-label={ariaLabel}
      onKeyDown={handleKeyDown}
      className={cn("focus:outline-none", className)}
      {...props}
    >
      {items.map((item, index) => (
        <li
          key={index}
          role="option"
          aria-selected={index === selectedIndex}
          tabIndex={index === selectedIndex ? 0 : -1}
          className={cn(
            "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
            index === selectedIndex && "bg-accent"
          )}
        >
          {renderItem(item, index, index === selectedIndex)}
        </li>
      ))}
    </ul>
  );
}

// Accessible form field with proper labeling
export function AccessibleFormField({
  label,
  id,
  error,
  required = false,
  children,
  className,
  ...props
}: {
  label: string;
  id: string;
  error?: string;
  required?: boolean;
  children: React.ReactNode;
} & React.ComponentProps<"div">) {
  const errorId = `${id}-error`;
  const describedBy = error ? errorId : undefined;

  return (
    <div className={cn("space-y-2", className)} {...props}>
      <label
        htmlFor={id}
        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
      >
        {label}
        {required && <span className="text-destructive ml-1">*</span>}
      </label>
      {React.cloneElement(children as React.ReactElement, {
        id,
        "aria-describedby": describedBy,
        "aria-invalid": !!error,
        required
      })}
      {error && (
        <p id={errorId} className="text-sm text-destructive" role="alert">
          {error}
        </p>
      )}
    </div>
  );
} 