"use client";

import { Card } from "@/components/ui/card";

interface RiskMetricCardProps {
  label: string;
  value: number; // 0-100
  hint?: string;
}

export default function RiskMetricCard({ label, value, hint }: RiskMetricCardProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const hue = 120 - (clamped * 120) / 100; // green->red
  const color = `hsl(${hue} 80% 45%)`;

  return (
    <Card className="bg-white border border-gray-200 rounded-2xl p-4">
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-gray-600">{label}</p>
        <p className="text-sm font-medium text-gray-900">{clamped}</p>
      </div>
      <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full"
          style={{ width: `${clamped}%`, backgroundColor: color }}
        />
      </div>
      {hint && <p className="text-xs text-gray-500 mt-2">{hint}</p>}
    </Card>
  );
}

