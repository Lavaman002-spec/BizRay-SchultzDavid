'use client';

import { useEffect, useState } from 'react';
import { Building2, Users, TrendingUp } from 'lucide-react';
import { checkHealth, getStats } from '@/lib/api';

interface StatsCardsProps {
  className?: string;
}

export default function StatsCards({ className = '' }: StatsCardsProps) {
  const [stats, setStats] = useState({
    totalCompanies: 0,
    totalOfficers: 0,
    activeCompanies: 0,
    dbStatus: 'checking...',
    loading: true,
  });

  useEffect(() => {
    async function loadStats() {
      try {
        const [health, statsData] = await Promise.all([
          checkHealth(),
          getStats(),
        ]);

        setStats({
          totalCompanies: statsData.total_companies,
          totalOfficers: statsData.total_officers,
          activeCompanies: statsData.active_companies,
          dbStatus: health.database,
          loading: false,
        });
      } catch (error) {
        console.error('Failed to load stats:', error);
        setStats({
          totalCompanies: 0,
          totalOfficers: 0,
          activeCompanies: 0,
          dbStatus: 'error',
          loading: false,
        });
      }
    }

    loadStats();
  }, []);

  const statItems = [
    {
      label: 'Total Companies',
      value: stats.totalCompanies,
      icon: Building2,
    },
    {
      label: 'Active Companies',
      value: stats.activeCompanies,
      icon: TrendingUp,
    },
    {
      label: 'Officers',
      value: stats.totalOfficers,
      icon: Users,
    },
  ];

  if (stats.loading) {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-3 gap-4 ${className}`}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-zinc-200 rounded-2xl p-6 animate-pulse">
            <div className="h-4 bg-zinc-300 rounded w-20 mb-4"></div>
            <div className="h-8 bg-zinc-300 rounded w-24"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div
      className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ${className}`}
    >
      {statItems.map((stat) => {
        const Icon = stat.icon;
        const displayValue = stat.value;

        return (
          <div
            key={stat.label}
            className="bg-zinc-200 rounded-2xl p-6 flex flex-col gap-2"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm text-zinc-600">{stat.label}</span>
              <div className="p-2 bg-zinc-300 rounded-lg">
                <Icon className="w-4 h-4 text-zinc-700" />
              </div>
            </div>
            <p className={`text-3xl font-semibold`}>{displayValue}</p>
          </div>
        );
      })}
    </div>
  );
}
