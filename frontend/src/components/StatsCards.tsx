'use client';

import { useEffect, useState } from 'react';
import { Building2, Briefcase, Link2 } from 'lucide-react';
import { listCompanies } from '@/lib/api';

export default function StatsCards() {
  const [stats, setStats] = useState({
    companies: 0,
    officers: 0,
    links: 0,
    loading: true,
  });

  useEffect(() => {
    async function loadStats() {
      try {
        // Fetch just one company to get the total count
        const data = await listCompanies(1, 0);
        setStats({
          companies: data.total,
          officers: 558, // This would ideally come from an API endpoint
          links: 3, // This would ideally come from an API endpoint
          loading: false,
        });
      } catch (error) {
        console.error('Failed to load stats:', error);
        setStats({
          companies: 0,
          officers: 0,
          links: 0,
          loading: false,
        });
      }
    }

    loadStats();
  }, []);

  const statItems = [
    {
      label: 'Companies',
      value: stats.companies,
      icon: Building2,
    },
    {
      label: 'Offices',
      value: stats.officers,
      icon: Briefcase,
    },
    {
      label: 'Links',
      value: stats.links,
      icon: Link2,
    },
  ];

  if (stats.loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {statItems.map((stat) => {
        const Icon = stat.icon;
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
            <p className="text-3xl font-semibold text-zinc-950">
              {stat.value.toLocaleString()}
            </p>
          </div>
        );
      })}
    </div>
  );
}
