'use client';

import { Card } from '@/components/ui/card';
import RiskScoreBadge from './RiskScoreBadge';
import RiskScoreGauge from './RiskScoreGauge';
import RiskMetricCard from './RiskMetricCard';
import RiskAlertItem from './RiskAlertItem';
import type { CompanyWithDetails } from '@/types/company';
import { computeRiskInsights } from '@/lib/riskInsights';

interface RiskIndicatorsProps {
  company: CompanyWithDetails;
}

export default function RiskIndicators({ company }: RiskIndicatorsProps) {
  const { score, level, breakdown, alerts } = computeRiskInsights(company);

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card className="bg-white border border-gray-200 rounded-2xl p-6">
        <div className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <RiskScoreGauge score={score} />
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-xl font-semibold text-gray-900">
                  Overall Risk
                </h3>
                <RiskScoreBadge level={level} />
              </div>
              <p className="text-sm text-gray-600 max-w-prose">
                This score reflects signals across compliance, legal,
                operational, financial, and network dimensions.
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-3 gap-6">
        <Card className="bg-white border border-gray-200 rounded-2xl p-6 col-span-2">
          <h4 className="text-base font-semibold text-gray-900 mb-4">
            Category Breakdown
          </h4>
          <div className="grid grid-cols-2 gap-4">
            {breakdown.map((item) => (
              <RiskMetricCard
                key={item.category}
                label={item.category}
                value={item.score}
                hint={item.hint}
              />
            ))}
          </div>
        </Card>

        <Card className="bg-white border border-gray-200 rounded-2xl p-6">
          <h4 className="text-base font-semibold text-gray-900 mb-4">
            Recent Alerts
          </h4>
          <div>
            {alerts.map((a, idx) => (
              <RiskAlertItem
                key={idx}
                title={a.title}
                description={a.description}
                severity={a.severity}
                timestamp={a.timestamp}
              />
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
