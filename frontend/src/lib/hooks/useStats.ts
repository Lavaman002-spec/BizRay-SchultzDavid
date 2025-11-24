'use client';

import { useEffect, useState } from 'react';
import { getStats } from '@/lib/api';

export function useStats() {
  const [stats, setStats] = useState({
    companies: 0,
    loading: true,
  });

  useEffect(() => {
    async function loadStats() {
      try {
        const data = await getStats();
        setStats({
          companies: data.total_companies,
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
