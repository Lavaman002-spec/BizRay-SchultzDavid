'use client';

import { Card } from '@/components/ui/card';
import type { CompanyWithDetails } from '@/types/company';
import ReportingKpis from './ReportingKpis';
import FilingsTimeline from './FilingsTimeline';
import FinancialTrend from './FinancialTrend';
import ComplianceAlerts from './ComplianceAlerts';

interface ReportingPanelProps {
  company: CompanyWithDetails;
}

export default function ReportingPanel({ company }: ReportingPanelProps) {
  return (
    <div className="space-y-6">
      <ReportingKpis company={company} />

      <div className="grid grid-cols-3 gap-6">
        <Card className="bg-white border border-gray-200 rounded-2xl p-6 col-span-2">
          <FilingsTimeline company={company} />
        </Card>
        <Card className="bg-white border border-gray-200 rounded-2xl p-6">
          <FinancialTrend company={company} />
        </Card>
      </div>

      <Card className="bg-white border border-gray-200 rounded-2xl p-6">
        <ComplianceAlerts company={company} />
      </Card>
    </div>
  );
}
