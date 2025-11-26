'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { AlertCircle } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { getCompany, refreshCompany } from '@/lib/api';
import type { CompanyWithDetails } from '@/types/company';
import CompanyHeader from '@/components/company/CompanyHeader';
import RiskIndicators from '@/components/company/risk/RiskIndicators';
import ReportingPanel from '@/components/company/reporting/ReportingPanel';
import NetworkTab from '@/components/company/network/NetworkTab';
import RevenueCard from '@/components/company/overview/overviewCard';

export default function CompanyPage() {
  const params = useParams();
  const id = params.id as string;

  const [company, setCompany] = useState<CompanyWithDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    if (!id) {
      return;
    }

    const storageKey = `company-cache-${id}`;
    let isMounted = true;

    const loadFromCache = () => {
      if (typeof window === 'undefined') return null;
      try {
        const cached = window.sessionStorage.getItem(storageKey);
        return cached ? (JSON.parse(cached) as CompanyWithDetails) : null;
      } catch (err) {
        console.warn('Failed to parse cached company data', err);
        return null;
      }
    };

    const persistToCache = (data: CompanyWithDetails) => {
      if (typeof window === 'undefined') return;
      try {
        window.sessionStorage.setItem(storageKey, JSON.stringify(data));
      } catch (err) {
        console.warn('Failed to cache company data', err);
      }
    };

    const fetchCompany = async (showSkeleton: boolean, hasPreview: boolean) => {
      try {
        setError(null);
        if (showSkeleton) {
          setLoading(true);
        }

        setIsRefreshing(true);
        const refreshed = await refreshCompany(parseInt(id));
        if (!isMounted) return;
        setCompany(refreshed);
        persistToCache(refreshed);
      } catch (refreshError) {
        console.error('Failed to refresh company data', refreshError);
        try {
          const fallback = await getCompany(parseInt(id));
          if (!isMounted) return;
          setCompany(fallback);
          persistToCache(fallback);
        } catch (err) {
          console.error(err);
          if (showSkeleton || !hasPreview) {
            setError('Failed to load company data');
          }
        }
      } finally {
        if (!isMounted) return;
        setLoading(false);
        setIsRefreshing(false);
      }
    };

    const cachedCompany = loadFromCache();

    if (cachedCompany) {
      setCompany(cachedCompany);
      setLoading(false);
      fetchCompany(false, true);
    } else {
      fetchCompany(true, false);
    }

    return () => {
      isMounted = false;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="bg-gray-100">
        <div className="max-w-[900px] mx-auto px-16 py-8">
          <div className="animate-pulse">
            <div className="bg-white rounded-2xl p-8 h-64 mb-6" />
            <div className="bg-white rounded-2xl p-8 h-96" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !company) {
    return (
      <div>
        <div className="max-w-4xl">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || 'Company not found'}</AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col align-middle items-center">
      <div className="w-[900px] bg-gray-100">
        <CompanyHeader company={company} isRefreshing={isRefreshing} />

        <div>
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-6 bg-zinc-200">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="risk">Risk</TabsTrigger>
              <TabsTrigger value="reporting">Reporting</TabsTrigger>
              <TabsTrigger value="network">Network</TabsTrigger>
            </TabsList>

            <TabsContent value="overview">
              <RevenueCard company={company} />
            </TabsContent>

            <TabsContent value="risk">
              <RiskIndicators company={company} />
            </TabsContent>

            <TabsContent value="reporting">
              <ReportingPanel company={company} />
            </TabsContent>

            <TabsContent value="network">
              <NetworkTab company={company} />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
