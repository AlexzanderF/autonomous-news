/**
 * Formats a date string into a human-readable "time ago" format
 * @param dateString - ISO date string or valid date string
 * @returns Formatted string like "Just Now", "5M ago", "2h ago", "3d ago"
 */
export function formatTimeAgo(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (seconds < 60) return 'Just Now';

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}M ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;

  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
