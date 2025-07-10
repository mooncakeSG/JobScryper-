import { useEffect, useRef, useCallback, useState } from 'react';

interface UseKeyboardNavigationOptions {
  onEscape?: () => void;
  onEnter?: () => void;
  onSpace?: () => void;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  onTab?: (event: KeyboardEvent) => void;
  enabled?: boolean;
}

export function useKeyboardNavigation({
  onEscape,
  onEnter,
  onSpace,
  onArrowUp,
  onArrowDown,
  onArrowLeft,
  onArrowRight,
  onTab,
  enabled = true
}: UseKeyboardNavigationOptions = {}) {
  const elementRef = useRef<HTMLElement>(null);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled) return;

    switch (event.key) {
      case 'Escape':
        if (onEscape) {
          event.preventDefault();
          onEscape();
        }
        break;
      case 'Enter':
        if (onEnter) {
          event.preventDefault();
          onEnter();
        }
        break;
      case ' ':
        if (onSpace) {
          event.preventDefault();
          onSpace();
        }
        break;
      case 'ArrowUp':
        if (onArrowUp) {
          event.preventDefault();
          onArrowUp();
        }
        break;
      case 'ArrowDown':
        if (onArrowDown) {
          event.preventDefault();
          onArrowDown();
        }
        break;
      case 'ArrowLeft':
        if (onArrowLeft) {
          event.preventDefault();
          onArrowLeft();
        }
        break;
      case 'ArrowRight':
        if (onArrowRight) {
          event.preventDefault();
          onArrowRight();
        }
        break;
      case 'Tab':
        if (onTab) {
          onTab(event);
        }
        break;
    }
  }, [enabled, onEscape, onEnter, onSpace, onArrowUp, onArrowDown, onArrowLeft, onArrowRight, onTab]);

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    element.addEventListener('keydown', handleKeyDown);
    return () => {
      element.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  return elementRef;
}

// Hook for managing focus in lists
export function useListNavigation<T>(
  items: T[],
  onSelect?: (item: T, index: number) => void
) {
  const [focusedIndex, setFocusedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setFocusedIndex(prev => 
          prev < items.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        event.preventDefault();
        setFocusedIndex(prev => prev > 0 ? prev - 1 : prev);
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (focusedIndex >= 0 && focusedIndex < items.length && onSelect) {
          onSelect(items[focusedIndex], focusedIndex);
        }
        break;
      case 'Home':
        event.preventDefault();
        setFocusedIndex(0);
        break;
      case 'End':
        event.preventDefault();
        setFocusedIndex(items.length - 1);
        break;
    }
  }, [items, focusedIndex, onSelect]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('keydown', handleKeyDown);
    return () => {
      container.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleKeyDown]);

  const focusItem = useCallback((index: number) => {
    setFocusedIndex(index);
    const container = containerRef.current;
    if (container) {
      const focusableElement = container.querySelector(`[data-index="${index}"]`) as HTMLElement;
      if (focusableElement) {
        focusableElement.focus();
      }
    }
  }, []);

  return {
    focusedIndex,
    setFocusedIndex,
    containerRef,
    focusItem
  };
}

// Hook for managing modal focus
export function useModalFocus(open: boolean) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (open) {
      // Store the currently focused element
      previousFocusRef.current = document.activeElement as HTMLElement;
      
      // Focus the modal
      const modal = modalRef.current;
      if (modal) {
        const focusableElements = modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstFocusable = focusableElements[0] as HTMLElement;
        if (firstFocusable) {
          firstFocusable.focus();
        }
      }
    } else {
      // Restore focus when modal closes
      if (previousFocusRef.current) {
        previousFocusRef.current.focus();
      }
    }
  }, [open]);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      // This should be handled by the modal component
      return;
    }

    if (event.key === 'Tab') {
      const modal = modalRef.current;
      if (!modal) return;

      const focusableElements = Array.from(
        modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )
      ) as HTMLElement[];

      if (focusableElements.length === 0) return;

      const firstElement = focusableElements[0];
      const lastElement = focusableElements[focusableElements.length - 1];

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
  }, []);

  useEffect(() => {
    if (open) {
      document.addEventListener('keydown', handleKeyDown);
      return () => {
        document.removeEventListener('keydown', handleKeyDown);
      };
    }
  }, [open, handleKeyDown]);

  return modalRef;
} 