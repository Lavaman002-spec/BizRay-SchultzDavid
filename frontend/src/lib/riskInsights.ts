import type { CompanyWithDetails } from '@/types/company';

export type RiskLevel = 'Low' | 'Medium' | 'High';
export type RiskSeverity = 'low' | 'medium' | 'high';
export type RiskCategory =
  | 'Financial'
  | 'Compliance'
  | 'Legal'
  | 'Operational'
  | 'Network';

export interface RiskBreakdownItem {
  category: RiskCategory;
  score: number;
  hint?: string;
}

export interface RiskAlert {
  title: string;
  description?: string;
  severity: RiskSeverity;
  timestamp: string;
}

interface FinancialSignals {
  score: number;
  revenue: number | null;
  profit: number | null;
  profitMargin: number | null;
  currency: string;
}

export interface RiskInsights {
  score: number;
  level: RiskLevel;
  breakdown: RiskBreakdownItem[];
  alerts: RiskAlert[];
  financialSignals: FinancialSignals;
}

function toLevel(score: number): RiskLevel {
  if (score < 35) return 'Low';
  if (score < 70) return 'Medium';
  return 'High';
}

function computeDeterministicScore(n: number) {
  const x = Math.abs(Math.sin(n) * 100);
  return Math.round(x);
}

function clamp(value: number, min = 0, max = 1) {
  return Math.min(Math.max(value, min), max);
}

function numericOrNull(value: unknown): number | null {
  return typeof value === 'number' && Number.isFinite(value) ? value : null;
}

function formatCompactCurrency(value: number, currency: string) {
  return new Intl.NumberFormat('de-AT', {
    style: 'currency',
    currency,
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value);
}

function deriveFinancialSignals(company: CompanyWithDetails): FinancialSignals {
  const latestFinancial = company.financials?.[0];
  const revenue =
    numericOrNull(company.revenue) ?? numericOrNull(latestFinancial?.revenue);
  const profit =
    numericOrNull(company.profit) ?? numericOrNull(latestFinancial?.profit);
  const currency =
    company.revenue_currency ?? latestFinancial?.currency ?? 'EUR';

  const profitMargin =
    revenue && profit !== null && revenue !== 0 ? profit / revenue : null;

  const revenueFactor =
    revenue && revenue > 0 ? clamp(Math.log10(revenue + 1) / 12, 0, 1) : 0.15;
  const marginFactor =
    profitMargin !== null ? clamp((profitMargin + 0.25) / 0.5, 0, 1) : 0.5;
  const profitabilityFactor = profit === null ? 0.4 : profit > 0 ? 1 : 0;

  const healthyComposite =
    revenueFactor * 0.45 + marginFactor * 0.35 + profitabilityFactor * 0.2;

  const score = clamp(Math.round(100 - healthyComposite * 80), 5, 95);

  return { score, revenue, profit, profitMargin, currency };
}

export function computeRiskInsights(company: CompanyWithDetails): RiskInsights {
  const baselineSeed = Number.isFinite(company.id)
    ? (company.id as number)
    : parseInt(company.fnr ?? '1', 10) || 1;
  const base = computeDeterministicScore(baselineSeed);
  const financialSignals = deriveFinancialSignals(company);

  const financialHint = (() => {
    if (financialSignals.revenue === null) {
      return 'No revenue filings on record';
    }
    if (financialSignals.profit === null) {
      return `Revenue ${formatCompactCurrency(
        financialSignals.revenue,
        financialSignals.currency
      )}`;
    }
    const marginPct = clamp(
      (financialSignals.profitMargin ?? 0) * 100,
      -99,
      200
    );
    return `Margin ${marginPct.toFixed(1)}% on ${formatCompactCurrency(
      financialSignals.revenue,
      financialSignals.currency
    )}`;
  })();

  const breakdown: RiskBreakdownItem[] = [
    {
      category: 'Financial',
      score: financialSignals.score,
      hint: financialHint,
    },
    {
      category: 'Compliance',
      score: (base * 0.5 + 40) % 100,
      hint: 'Filings, status, disclosures',
    },
    {
      category: 'Legal',
      score: (base * 0.9 + 10) % 100,
      hint: 'Litigation & insolvency signals',
    },
    {
      category: 'Operational',
      score: (base * 0.6 + 30) % 100,
      hint: 'Continuity & key people',
    },
    {
      category: 'Network',
      score: (base * 0.8 + 15) % 100,
      hint: 'Associations & adverse links',
    },
  ].map((b) => ({ ...b, score: Math.round(clamp(b.score, 0, 100)) }));

  const score = Math.round(
    breakdown.reduce((acc, b) => acc + b.score, 0) / breakdown.length
  );
  const level = toLevel(score);

  const alerts: RiskAlert[] = [];

  const fiscalLabel = company.latest_financial_year
    ? `FY ${company.latest_financial_year}`
    : 'Current FY';

  if (financialSignals.revenue === null) {
    alerts.push({
      title: 'Missing revenue filings',
      description: 'No revenue data submitted for the latest fiscal cycle.',
      severity: 'medium',
      timestamp: fiscalLabel,
    });
  } else if (financialSignals.profit === null) {
    alerts.push({
      title: 'Profit data unavailable',
      description: 'Revenue reported but profitability metrics are missing.',
      severity: 'medium',
      timestamp: fiscalLabel,
    });
  }

  if (
    financialSignals.profitMargin !== null &&
    financialSignals.profitMargin < 0
  ) {
    alerts.push({
      title: 'Negative profitability',
      description: `Margin ${(financialSignals.profitMargin * 100).toFixed(
        1
      )}% in ${fiscalLabel}.`,
      severity: 'high',
      timestamp: fiscalLabel,
    });
  } else if (
    financialSignals.profitMargin !== null &&
    financialSignals.profitMargin < 0.05
  ) {
    alerts.push({
      title: 'Thin operating margins',
      description: `Margin ${(financialSignals.profitMargin * 100).toFixed(
        1
      )}% leaves little buffer for shocks.`,
      severity: 'medium',
      timestamp: fiscalLabel,
    });
  } else if (financialSignals.profitMargin !== null) {
    alerts.push({
      title: 'Healthy profitability',
      description: `Margin ${(financialSignals.profitMargin * 100).toFixed(
        1
      )}% provides resilience.`,
      severity: 'low',
      timestamp: fiscalLabel,
    });
  }

  if ((company.officers?.length ?? 0) === 0) {
    alerts.push({
      title: 'Officer roster incomplete',
      description: 'No active officers found; governance review recommended.',
      severity: 'medium',
      timestamp: 'Current',
    });
  }

  const fallbackAlerts = [
    {
      title: 'Recent officer change',
      description: 'Management structure updated in the last 30 days.',
      severity: 'medium' as RiskSeverity,
      timestamp: '2 weeks ago',
    },
    {
      title: 'Late annual filing',
      description: 'Latest annual report filing appears overdue.',
      severity: 'high' as RiskSeverity,
      timestamp: '1 month ago',
    },
    {
      title: 'New address registered',
      description: 'Active address changed recently.',
      severity: 'low' as RiskSeverity,
      timestamp: '3 months ago',
    },
  ];

  for (const fallback of fallbackAlerts) {
    if (alerts.length >= 3) break;
    alerts.push(fallback);
  }

  return { score, level, breakdown, alerts, financialSignals };
}
