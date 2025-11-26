'use client';

import { Calendar, FileText, ShieldCheck, AlertTriangle } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { CompanyWithDetails } from '@/types/company';
import { getReportingStats } from '@/lib/reportingStats';

interface ReportingKpisProps {
  company: CompanyWithDetails;
}

function formatDate(date: Date | null) {
  if (!date) {
    return 'Not available';
  }
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export default function ReportingKpis({ company }: ReportingKpisProps) {
  // Derive reporting stats (falls back to deterministic values when filings are missing)
  const stats = getReportingStats(company);
  const lastFilingDate = stats.lastFiling.date;
  const nextDueDate = stats.nextDue.date;
  const isOverdue = stats.nextDue.isOverdue;
  const dueInDays = stats.nextDue.dueInDays;
  const docsCount = stats.documents.count;
  const issuesText = stats.documents.issuesText;
  const complianceTone = stats.compliance.tone;

  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Last Filing */}
      <Card className="bg-white border border-gray-200 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-gray-600">Last Filing</p>
          <FileText className="w-5 h-5 text-gray-500" />
        </div>
        <p className="text-xl font-semibold text-gray-900">
          {formatDate(lastFilingDate)}
        </p>
        <p className="text-xs text-gray-500 mt-1">{stats.lastFiling.label}</p>
      </Card>

      {/* Next Due */}
      <Card className="bg-white border border-gray-200 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-gray-600">Next Due</p>
          <Calendar className="w-5 h-5 text-gray-500" />
        </div>
        <div className="flex items-center gap-2">
          <p className="text-xl font-semibold text-gray-900">
            {formatDate(nextDueDate)}
          </p>
          {isOverdue ? (
            <Badge className="bg-red-100 text-red-700 border-red-200 text-xs">
              Overdue
            </Badge>
          ) : (
            <Badge className="bg-emerald-100 text-emerald-700 border-emerald-200 text-xs">
              {dueInDays !== null ? `in ${dueInDays} days` : 'On track'}
            </Badge>
          )}
        </div>
        <p className="text-xs text-gray-500 mt-1">{stats.nextDue.label}</p>
      </Card>

      {/* Compliance */}
      <Card className="bg-white border border-gray-200 rounded-2xl p-5">
        <div className="flex items-center justify-between mb-3">
          <p className="text-sm text-gray-600">Compliance</p>
          <ShieldCheck className="w-5 h-5 text-gray-500" />
        </div>
        <div className="flex items-center gap-2">
          <p className="text-xl font-semibold text-gray-900">
            {stats.compliance.statusLabel}
          </p>
          <Badge
            className={`${
              complianceTone === 'attention'
                ? 'bg-amber-100 text-amber-700 border-amber-200'
                : 'bg-emerald-100 text-emerald-700 border-emerald-200'
            } text-xs`}
          >
            {stats.compliance.badgeLabel}
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
        <p className="text-xs text-gray-500 mt-1">{issuesText}</p>
      </Card>
    </div>
  );
}
