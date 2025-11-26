'use client';

import { Badge } from '@/components/ui/badge';
import type { RiskLevel } from '@/lib/riskInsights';

export default function RiskScoreBadge({ level }: { level: RiskLevel }) {
  const styles: Record<RiskLevel, string> = {
    Low: 'bg-green-100 text-green-700 border-green-200',
    Medium: 'bg-amber-100 text-amber-700 border-amber-200',
    High: 'bg-red-100 text-red-700 border-red-200',
  };

  return (
    <Badge
      className={`${styles[level]} text-xs px-2 py-0.5 font-medium`}
    >{`${level} Risk`}</Badge>
  );
}
