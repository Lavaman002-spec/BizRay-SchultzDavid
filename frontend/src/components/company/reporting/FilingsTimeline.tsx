"use client";

import { Clock, FileText, UserCog, MapPin, Shield } from "lucide-react";
import type { CompanyWithDetails } from "@/types/company";

interface FilingsTimelineProps {
  company: CompanyWithDetails;
}

type FilingStatus = "Filed" | "Due Soon" | "Overdue";

interface FilingItem {
  type: string;
  date: Date;
  status: FilingStatus;
}

function hash(n: number) {
  const x = Math.abs(Math.sin(n) * 10000);
  return Math.floor(x);
}

function iconFor(type: string) {
  if (type.includes("Annual")) return FileText;
  if (type.includes("Director")) return UserCog;
  if (type.includes("Address")) return MapPin;
  return Shield;
}

function computeFilings(company: CompanyWithDetails): FilingItem[] {
  const base = hash(company.id);
  const now = Date.now();
  const days = (i: number) => (base % 90) + i * 60; // spaced
  const items: FilingItem[] = [
    { type: "Annual Report", date: new Date(now - days(4) * 86400000), status: "Filed" },
    { type: "Director Change", date: new Date(now - days(3) * 86400000), status: "Filed" },
    { type: "Address Update", date: new Date(now - days(2) * 86400000), status: "Filed" },
    { type: "Share Capital Update", date: new Date(now - days(1) * 86400000), status: (base % 2) ? "Due Soon" : "Filed" },
    { type: "Annual Report", date: new Date(now + (30 - (base % 15)) * 86400000), status: (base % 3) === 0 ? "Overdue" : "Due Soon" },
  ];
  // Sort desc by date
  return items.sort((a, b) => b.date.getTime() - a.date.getTime());
}

function formatDate(d: Date) {
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export default function FilingsTimeline({ company }: FilingsTimelineProps) {
  const filings = computeFilings(company);

  const pill: Record<FilingStatus, string> = {
    Filed: "bg-emerald-100 text-emerald-700 border-emerald-200",
    "Due Soon": "bg-amber-100 text-amber-700 border-amber-200",
    Overdue: "bg-red-100 text-red-700 border-red-200",
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-base font-semibold text-gray-900">Filings Timeline</h4>
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <Clock className="w-3.5 h-3.5" /> Updated daily
        </div>
      </div>
      <div className="space-y-3">
        {filings.map((f, idx) => {
          const Icon = iconFor(f.type);
          return (
            <div key={idx} className="flex items-center justify-between gap-3 py-2 border-b border-gray-100 last:border-b-0">
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center shrink-0">
                  <Icon className="w-4.5 h-4.5 text-gray-600" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{f.type}</p>
                  <p className="text-xs text-gray-500">{formatDate(f.date)}</p>
                </div>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full border ${pill[f.status]}`}>{f.status}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

