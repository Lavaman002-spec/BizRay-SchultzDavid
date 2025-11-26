import type { CompanyWithDetails, Filing } from '@/types/company';

const DAY_MS = 24 * 60 * 60 * 1000;

type StatsSource = 'filings' | 'synthetic';

type ComplianceTone = 'good' | 'attention';

export interface ReportingStats {
  lastFiling: {
    date: Date | null;
    label: string;
    type: string;
    status: string;
  };
  nextDue: {
    date: Date | null;
    label: string;
    isOverdue: boolean;
    dueInDays: number | null;
  };
  compliance: {
    statusLabel: string;
    badgeLabel: string;
    tone: ComplianceTone;
  };
  documents: {
    count: number;
    issuesText: string;
  };
  source: StatsSource;
}

function hash(n: number) {
  const x = Math.abs(Math.sin(n) * 10000);
  return Math.floor(x);
}

function parseFilingDate(value?: string | null): Date | null {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function addYears(date: Date, years: number) {
  const copy = new Date(date);
  copy.setFullYear(copy.getFullYear() + years);
  return copy;
}

function issuesText(openIssues: number) {
  return openIssues > 0 ? `${openIssues} issues flagged` : 'No issues';
}

function fallbackStats(company: CompanyWithDetails): ReportingStats {
  const baseSeed = Number.isFinite(company.id)
    ? (company.id as number)
    : parseInt(company.fnr ?? '1', 10) || 1;
  const base = hash(baseSeed);
  const now = Date.now();
  const lastFilingDaysAgo = 200 + (base % 180);
  const lastFilingDate = new Date(now - lastFilingDaysAgo * DAY_MS);
  const nextDueDate = addYears(lastFilingDate, 1);
  const isOverdue = nextDueDate.getTime() < now;
  const dueInDays = Math.max(
    0,
    Math.ceil((nextDueDate.getTime() - now) / DAY_MS)
  );
  const docsCount = 5 + (base % 12);
  const openIssues = base % 3 === 0 ? 2 : base % 2;

  return {
    lastFiling: {
      date: lastFilingDate,
      label: 'Annual report',
      type: 'Annual report',
      status: 'Filed',
    },
    nextDue: {
      date: nextDueDate,
      label: 'Annual report deadline',
      isOverdue,
      dueInDays,
    },
    compliance: {
      statusLabel: isOverdue ? 'Attention' : 'Good',
      badgeLabel: isOverdue ? 'Action needed' : `in ${dueInDays} days`,
      tone: isOverdue ? 'attention' : 'good',
    },
    documents: {
      count: docsCount,
      issuesText: issuesText(openIssues),
    },
    source: 'synthetic',
  };
}

function compareDatesDesc(a: Filing, b: Filing) {
  const aDate = parseFilingDate(a.date);
  const bDate = parseFilingDate(b.date);
  if (aDate && bDate) return bDate.getTime() - aDate.getTime();
  if (aDate) return -1;
  if (bDate) return 1;
  return 0;
}

export function getReportingStats(company: CompanyWithDetails): ReportingStats {
  const filings = (company.filings ?? []).slice().sort(compareDatesDesc);
  if (filings.length === 0) {
    return fallbackStats(company);
  }

  const now = Date.now();
  const lastFiling = filings[0];
  const lastFilingDate = parseFilingDate(lastFiling.date);
  const nextDueDate = lastFilingDate ? addYears(lastFilingDate, 1) : null;
  const isOverdue = nextDueDate ? nextDueDate.getTime() < now : false;
  const dueInDays = nextDueDate
    ? Math.max(0, Math.ceil((nextDueDate.getTime() - now) / DAY_MS))
    : null;

  const openIssues = filings.filter((filing) => {
    const status = (filing.status ?? '').toLowerCase();
    return status && status !== 'filed';
  }).length;

  const docsCount = filings.length;
  const tone: ComplianceTone =
    isOverdue || openIssues > 0 ? 'attention' : 'good';

  return {
    lastFiling: {
      date: lastFilingDate,
      label: lastFiling.description || lastFiling.filing_type || 'Filing',
      type: lastFiling.filing_type || 'Filing',
      status: lastFiling.status || 'Unknown',
    },
    nextDue: {
      date: nextDueDate,
      label: lastFiling.filing_type
        ? `${lastFiling.filing_type} deadline`
        : 'Next due date',
      isOverdue,
      dueInDays,
    },
    compliance: {
      statusLabel: tone === 'attention' ? 'Attention' : 'Good',
      badgeLabel:
        tone === 'attention'
          ? openIssues > 0
            ? `${openIssues} issues`
            : 'Overdue'
          : dueInDays !== null
          ? `in ${dueInDays} days`
          : 'On track',
      tone,
    },
    documents: {
      count: docsCount,
      issuesText: issuesText(openIssues),
    },
    source: 'filings',
  };
}
