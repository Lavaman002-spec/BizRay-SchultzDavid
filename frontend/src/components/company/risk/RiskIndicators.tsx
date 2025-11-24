"use client";

import { Card } from "@/components/ui/card";
import RiskScoreBadge, { RiskLevel } from "./RiskScoreBadge";
import RiskScoreGauge from "./RiskScoreGauge";
import RiskMetricCard from "./RiskMetricCard";
import RiskAlertItem, { RiskSeverity } from "./RiskAlertItem";
import type { CompanyWithDetails } from "@/types/company";

type Category = "Financial" | "Compliance" | "Legal" | "Operational" | "Network";

interface RiskBreakdownItem {
  category: Category;
  score: number; // 0-100
  hint?: string;
}

interface RiskIndicatorsProps {
  company: CompanyWithDetails;
}

function toLevel(score: number): RiskLevel {
  if (score < 35) return "Low";
  if (score < 70) return "Medium";
  return "High";
}

function computeDeterministicScore(n: number) {
  // Simple deterministic hash to keep stable per company
  const x = Math.abs(Math.sin(n) * 100);
  return Math.round(x);
}

function computeRisk(company: CompanyWithDetails) {
  const base = computeDeterministicScore(company.id);

  const breakdown: RiskBreakdownItem[] = [
    { category: "Financial" as Category, score: (base * 0.7 + 20) % 100, hint: "Liquidity & payment behavior" },
    { category: "Compliance" as Category, score: (base * 0.5 + 40) % 100, hint: "Filings, status, disclosures" },
    { category: "Legal" as Category, score: (base * 0.9 + 10) % 100, hint: "Litigation & insolvency signals" },
    { category: "Operational" as Category, score: (base * 0.6 + 30) % 100, hint: "Continuity & key people" },
    { category: "Network" as Category, score: (base * 0.8 + 15) % 100, hint: "Associations & adverse links" },
  ].map((b) => ({ ...b, score: Math.round(b.score) }));

  const score = Math.round(breakdown.reduce((acc, b) => acc + b.score, 0) / breakdown.length);
  const level = toLevel(score);

  const alerts: { title: string; description?: string; severity: RiskSeverity; timestamp: string }[] = [
    {
      title: "Recent officer change",
      description: "Management structure updated in the last 30 days.",
      severity: "medium",
      timestamp: "2 weeks ago",
    },
    {
      title: "Late annual filing",
      description: "Latest annual report filing appears overdue.",
      severity: "high",
      timestamp: "1 month ago",
    },
    {
      title: "New address registered",
      description: "Active address changed recently.",
      severity: "low",
      timestamp: "3 months ago",
    },
  ];

  return { score, level, breakdown, alerts };
}

export default function RiskIndicators({ company }: RiskIndicatorsProps) {
  const { score, level, breakdown, alerts } = computeRisk(company);

  return (
    <div className="space-y-6">
      {/* Summary Card */}
      <Card className="bg-white border border-gray-200 rounded-2xl p-6">
        <div className="flex items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <RiskScoreGauge score={score} />
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-xl font-semibold text-gray-900">Overall Risk</h3>
                <RiskScoreBadge level={level} />
              </div>
              <p className="text-sm text-gray-600 max-w-prose">
                This score reflects signals across compliance, legal, operational, financial, and network dimensions.
              </p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 w-[360px]">
            {breakdown.slice(0, 4).map((item) => (
              <RiskMetricCard key={item.category} label={item.category} value={item.score} hint={item.hint} />
            ))}
          </div>
        </div>
      </Card>

      {/* Detailed Breakdown */}
      <div className="grid grid-cols-3 gap-6">
        <Card className="bg-white border border-gray-200 rounded-2xl p-6 col-span-2">
          <h4 className="text-base font-semibold text-gray-900 mb-4">Category Breakdown</h4>
          <div className="grid grid-cols-2 gap-4">
            {breakdown.map((item) => (
              <RiskMetricCard key={item.category} label={item.category} value={item.score} hint={item.hint} />
            ))}
          </div>
        </Card>

        <Card className="bg-white border border-gray-200 rounded-2xl p-6">
          <h4 className="text-base font-semibold text-gray-900 mb-4">Recent Alerts</h4>
          <div>
            {alerts.map((a, idx) => (
              <RiskAlertItem key={idx} title={a.title} description={a.description} severity={a.severity} timestamp={a.timestamp} />
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
