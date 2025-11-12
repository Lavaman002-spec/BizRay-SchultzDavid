"use client";

import { TrendingUp } from "lucide-react";
import type { CompanyWithDetails } from "@/types/company";

interface FinancialTrendProps {
  company: CompanyWithDetails;
}

function hash(n: number) {
  const x = Math.abs(Math.sin(n) * 10000);
  return Math.floor(x);
}

function generateSeries(seed: number) {
  // Generate 6-year revenue series in millions
  const base = 5 + (seed % 8); // 5-12
  const series: number[] = [];
  for (let i = 0; i < 6; i++) {
    const variance = ((seed >> i) % 5) - 2; // -2..2
    const value = Math.max(2, base + i * 0.8 + variance * 0.2);
    series.push(parseFloat(value.toFixed(2)));
  }
  return series;
}

function Sparkline({ data, width = 260, height = 80 }: { data: number[]; width?: number; height?: number }) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const px = (i: number) => (i / (data.length - 1)) * (width - 8) + 4;
  const py = (v: number) => height - 4 - ((v - min) / (max - min || 1)) * (height - 8);
  const d = data.map((v, i) => `${i === 0 ? "M" : "L"}${px(i)},${py(v)}`).join(" ");
  return (
    <svg width={width} height={height} aria-label="Revenue trend">
      <polyline
        fill="none"
        stroke="#e5e7eb"
        strokeWidth="2"
        points={`4,${height - 4} ${width - 4},${height - 4}`}
      />
      <path d={d} fill="none" stroke="#16a34a" strokeWidth="2" />
    </svg>
  );
}

export default function FinancialTrend({ company }: FinancialTrendProps) {
  const seed = hash(company.id);
  const series = generateSeries(seed);
  const last = series[series.length - 1];
  const prev = series[series.length - 2] || last;
  const yoy = ((last - prev) / (prev || 1)) * 100;

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: series.length }, (_, i) => currentYear - series.length + 1 + i);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-base font-semibold text-gray-900">Financial Trend</h4>
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <TrendingUp className="w-3.5 h-3.5" /> Revenue (est.)
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <p className="text-2xl font-semibold text-gray-900">€{last.toFixed(1)}M</p>
          <p className="text-xs text-gray-500">{years[0]}–{years[years.length - 1]}</p>
        </div>
        <div className={`text-sm font-medium ${yoy >= 0 ? "text-emerald-600" : "text-red-600"}`}>
          {yoy >= 0 ? "+" : ""}{yoy.toFixed(1)}% YoY
        </div>
      </div>

      <div className="mt-3">
        <Sparkline data={series} />
      </div>
    </div>
  );
}

