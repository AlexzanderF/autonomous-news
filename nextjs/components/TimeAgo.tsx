'use client';

import { formatTimeAgo } from '@/utils/date';

interface TimeAgoProps {
  dateString: string;
  className?: string;
}

/**
 * Client-side component for accurate local timezone "time ago" display.
 * Uses suppressHydrationWarning since server/client times may differ due to timezone.
 */
export default function TimeAgo({ dateString, className }: TimeAgoProps) {
  return (
    <time dateTime={dateString} className={className} suppressHydrationWarning>
      {formatTimeAgo(dateString)}
    </time>
  );
}
