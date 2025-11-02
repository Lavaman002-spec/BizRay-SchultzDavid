'use client';

import { useEffect, useState } from 'react';
import { listCompanies } from '@/lib/api';

export function useStats() {
  const [stats, setStats] = useState({
    companies: 0,
    loading: true,
  });

  useEffect(() => {
    async function loadStats() {
      try {
        // Fetch just one company to get the total count
        const data = await listCompanies(1, 0);
        setStats({
          companies: data.total,
          loading: false,
        });
      } catch (error) {
        console.error('Failed to load stats:', error);
        setStats({
          companies: 0,
          loading: false,
        });
      }
    }

    loadStats();
  }, []);

  return stats;
}
