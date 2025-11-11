"use client";

import { AlertTriangle, Info, Clock } from "lucide-react";

export type RiskSeverity = "low" | "medium" | "high";

interface RiskAlertItemProps {
  title: string;
  description?: string;
  severity: RiskSeverity;
  timestamp?: string;
}

export default function RiskAlertItem({ title, description, severity, timestamp }: RiskAlertItemProps) {
  const color: Record<RiskSeverity, string> = {
    low: "text-green-600",
    medium: "text-amber-600",
    high: "text-red-600",
  };

  const dot: Record<RiskSeverity, string> = {
    low: "bg-green-100",
    medium: "bg-amber-100",
    high: "bg-red-100",
  };

  return (
    <div className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-b-0">
      <div className={`w-8 h-8 rounded-full ${dot[severity]} flex items-center justify-center shrink-0`}>
        {severity === "high" ? (
          <AlertTriangle className={`w-4 h-4 ${color[severity]}`} />
        ) : (
          <Info className={`w-4 h-4 ${color[severity]}`} />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm font-medium text-gray-900 truncate">{title}</p>
          {timestamp && (
            <div className="flex items-center gap-1 text-xs text-gray-500 shrink-0">
              <Clock className="w-3.5 h-3.5" /> {timestamp}
            </div>
          )}
        </div>
        {description && <p className="text-sm text-gray-600 mt-0.5">{description}</p>}
      </div>
    </div>
  );
}

