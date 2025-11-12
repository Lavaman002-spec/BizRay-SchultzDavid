"use client";

import { AlertTriangle, Info, Clock } from "lucide-react";
import type { CompanyWithDetails } from "@/types/company";

interface ComplianceAlertsProps {
  company: CompanyWithDetails;
}

type Severity = "low" | "medium" | "high";

interface AlertItem {
  title: string;
  description?: string;
  severity: Severity;
  timestamp?: string;
}

function hash(n: number) {
  const x = Math.abs(Math.sin(n) * 10000);
  return Math.floor(x);
}

function computeAlerts(company: CompanyWithDetails): AlertItem[] {
  const base = hash(company.id);
  const alerts: AlertItem[] = [
    {
      title: "Annual report deadline approaching",
      description: "Submit by the statutory deadline to avoid penalties.",
      severity: (base % 3) === 0 ? "high" : "medium",
      timestamp: "due in 14 days",
    },
    {
      title: "Director appointment updated",
      description: "Recent officer change filed.",
      severity: "low",
      timestamp: "2 weeks ago",
    },
    {
      title: "Registered address updated",
      description: "Ensure public records reflect the change.",
      severity: (base % 2) === 0 ? "low" : "medium",
      timestamp: "1 month ago",
    },
  ];
  return alerts;
}

export default function ComplianceAlerts({ company }: ComplianceAlertsProps) {
  const alerts = computeAlerts(company);

  const color: Record<Severity, string> = {
    low: "text-emerald-600",
    medium: "text-amber-600",
    high: "text-red-600",
  };
  const dot: Record<Severity, string> = {
    low: "bg-emerald-100",
    medium: "bg-amber-100",
    high: "bg-red-100",
  };

  return (
    <div>
      <h4 className="text-base font-semibold text-gray-900 mb-4">Compliance Alerts</h4>
      <div>
        {alerts.map((a, idx) => (
          <div key={idx} className="flex items-start gap-3 py-3 border-b border-gray-100 last:border-b-0">
            <div className={`w-8 h-8 rounded-full ${dot[a.severity]} flex items-center justify-center shrink-0`}>
              {a.severity === "high" ? (
                <AlertTriangle className={`w-4 h-4 ${color[a.severity]}`} />
              ) : (
                <Info className={`w-4 h-4 ${color[a.severity]}`} />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-medium text-gray-900 truncate">{a.title}</p>
                {a.timestamp && (
                  <div className="flex items-center gap-1 text-xs text-gray-500 shrink-0">
                    <Clock className="w-3.5 h-3.5" /> {a.timestamp}
                  </div>
                )}
              </div>
              {a.description && <p className="text-sm text-gray-600 mt-0.5">{a.description}</p>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

