"use client";

import { Calendar, FileText, ShieldCheck, AlertTriangle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { CompanyWithDetails } from "@/types/company";

interface ReportingKpisProps {
  company: CompanyWithDetails;
}

function hash(n: number) {
  const x = Math.abs(Math.sin(n) * 10000);
  return Math.floor(x);
}

function formatDate(d: Date) {
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export default function ReportingKpis({ company }: ReportingKpisProps) {
  // Derive deterministic sample data from company id (placeholder for real API data)
  const base = hash(company.id);
  const lastFilingDaysAgo = 200 + (base % 180); // 200-379 days ago
  const lastFiling = new Date(Date.now() - lastFilingDaysAgo * 24 * 3600 * 1000);
  const nextDue = new Date(lastFiling);
  nextDue.setFullYear(nextDue.getFullYear() + 1);
  const now = new Date();
  const isOverdue = nextDue < now;
  const dueInDays = Math.max(0, Math.ceil((nextDue.getTime() - now.getTime()) / (24 * 3600 * 1000)));

  const docsCount = 5 + (base % 12);
  const openIssues = (base % 3) === 0 ? 2 : (base % 2);

  return (
    <div className="grid grid-cols-4 gap-4">
      {/* Last Filing */}
      <Card className="bg-white border border-gray-200 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-gray-600">Last Filing</p>
          <FileText className="w-5 h-5 text-gray-500" />
        </div>
        <p className="text-xl font-semibold text-gray-900">{formatDate(lastFiling)}</p>
        <p className="text-xs text-gray-500 mt-1">Annual report</p>
      </Card>

      {/* Next Due */}
      <Card className="bg-white border border-gray-200 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-gray-600">Next Due</p>
          <Calendar className="w-5 h-5 text-gray-500" />
        </div>
        <div className="flex items-center gap-2">
          <p className="text-xl font-semibold text-gray-900">{formatDate(nextDue)}</p>
          {isOverdue ? (
            <Badge className="bg-red-100 text-red-700 border-red-200 text-xs">Overdue</Badge>
          ) : (
            <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200 text-xs">{`in ${dueInDays} days`}</Badge>
          )}
        </div>
        <p className="text-xs text-gray-500 mt-1">Annual report deadline</p>
      </Card>

      {/* Compliance */}
      <Card className="bg-white border border-gray-200 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-gray-600">Compliance</p>
          <ShieldCheck className="w-5 h-5 text-gray-500" />
        </div>
        <div className="flex items-center gap-2">
          <p className="text-xl font-semibold text-gray-900">{isOverdue ? "Attention" : "Good"}</p>
          <Badge className={`${isOverdue ? "bg-amber-100 text-amber-700 border-amber-200" : "bg-emerald-100 text-emerald-700 border-emerald-200"} text-xs`}>
            {isOverdue ? "Action needed" : "On track"}
          </Badge>
        </div>
        <p className="text-xs text-gray-500 mt-1">Filing & disclosure status</p>
      </Card>

      {/* Documents */}
      <Card className="bg-white border border-gray-200 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-gray-600">Documents</p>
          <AlertTriangle className="w-5 h-5 text-gray-500" />
        </div>
        <p className="text-xl font-semibold text-gray-900">{docsCount}</p>
        <p className="text-xs text-gray-500 mt-1">{openIssues > 0 ? `${openIssues} issues flagged` : "No issues"}</p>
      </Card>
    </div>
  );
}

