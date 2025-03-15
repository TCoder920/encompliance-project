/**
 * Utility functions for handling and formatting dates throughout the application
 */

/**
 * Checks if a date string is in the future (likely indicating an incorrect date)
 * @param dateString - The date string to check
 * @returns True if the date is in the future, false otherwise
 */
export function isDateInFuture(dateString: string): boolean {
  try {
    const inputDate = new Date(dateString);
    const now = new Date();
    return inputDate > now;
  } catch (error) {
    console.error('Error checking if date is in future:', error);
    return false;
  }
}

/**
 * Formats a date string into a standardized readable format
 * @param dateString - The date string to format
 * @param includeTime - Whether to include time in the formatted output (default: true)
 * @returns Formatted date string
 */
export function formatDate(dateString: string, includeTime: boolean = true): string {
  try {
    // Check for future dates and correct them (display current date instead)
    const inputDate = new Date(dateString);
    const now = new Date();
    
    // If date is in the future (indicating a data issue), use current date
    const dateToUse = isDateInFuture(dateString) ? now : inputDate;
    
    // Format options for consistent display
    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    };
    
    // Add time options if requested
    if (includeTime) {
      options.hour = '2-digit';
      options.minute = '2-digit';
      options.hour12 = true;
    }
    
    return dateToUse.toLocaleString('en-US', options);
  } catch (error) {
    console.error('Error formatting date:', error, dateString);
    return dateString || 'Unknown date';
  }
}

/**
 * Formats a date relative to now (e.g., "2 hours ago")
 * @param dateString - The date string to format
 * @returns Formatted relative time string
 */
export function formatRelativeTime(dateString: string): string {
  try {
    // Check for future dates and correct them (display current date instead)
    const inputDate = new Date(dateString);
    const now = new Date();
    
    // If date is in the future (indicating a data issue), use current date
    const dateToUse = isDateInFuture(dateString) ? now : inputDate;
    
    const diffMs = now.getTime() - dateToUse.getTime();
    const diffSec = Math.round(diffMs / 1000);
    const diffMin = Math.round(diffSec / 60);
    const diffHour = Math.round(diffMin / 60);
    const diffDay = Math.round(diffHour / 24);
    
    if (diffSec < 60) {
      return 'just now';
    } else if (diffMin < 60) {
      return `${diffMin} ${diffMin === 1 ? 'minute' : 'minutes'} ago`;
    } else if (diffHour < 24) {
      return `${diffHour} ${diffHour === 1 ? 'hour' : 'hours'} ago`;
    } else if (diffDay < 30) {
      return `${diffDay} ${diffDay === 1 ? 'day' : 'days'} ago`;
    } else {
      // For older dates, use the standard format
      return formatDate(dateString);
    }
  } catch (error) {
    console.error('Error formatting relative time:', error, dateString);
    return dateString || 'Unknown date';
  }
}

/**
 * Safely attempts to format a date string, returning a fallback value if parsing fails
 * @param dateString - The date string to format
 * @param fallback - Fallback value to return if formatting fails
 * @returns Formatted date string or fallback
 */
export function safeFormatDate(dateString: string | null | undefined, fallback: string = 'N/A'): string {
  if (!dateString) return fallback;
  
  try {
    return formatDate(dateString);
  } catch (error) {
    console.error('Error in safeFormatDate:', error);
    return fallback;
  }
}

/**
 * Universal date and time formatter that can handle both Date objects and string dates
 * This is the recommended function to use for all date/time formatting across the application
 * 
 * @param timestamp - The date to format (can be Date object or string)
 * @param options - Optional formatting options (defaults to standard date and time format)
 * @returns Formatted date and time string or 'Unknown' if invalid
 */
export function formatDateTime(timestamp: Date | string | null | undefined, options?: Intl.DateTimeFormatOptions): string {
  try {
    if (!timestamp) return 'Unknown';
    
    // If timestamp is a string, convert it to a Date object
    const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
    
    // Check if the date is valid
    if (isNaN(date.getTime())) {
      return 'Unknown';
    }
    
    // If date is in the future (indicating a data issue), use current date
    const dateToUse = date > new Date() ? new Date() : date;
    
    // Default formatting options if none provided
    const defaultOptions: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    // Use provided options or defaults
    return dateToUse.toLocaleString(undefined, options || defaultOptions);
  } catch (error) {
    console.error('Error formatting timestamp:', error);
    return 'Unknown';
  }
}

export default {
  formatDate,
  formatRelativeTime,
  safeFormatDate,
  isDateInFuture,
  formatDateTime
}; 