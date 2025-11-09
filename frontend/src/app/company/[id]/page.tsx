'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Building2,
  MapPin,
  Calendar,
  Globe,
  TrendingUp,
  Users2,
  Share2,
  Download,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { getCompany } from '@/lib/api';
import type { CompanyWithDetails } from '@/types/company';
import CompanyHeader from '@/components/company/CompanyHeader';

export default function CompanyPage() {
  const params = useParams();
  const id = params.id as string;

  const [company, setCompany] = useState<CompanyWithDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCompany() {
      try {
        setLoading(true);
        const data = await getCompany(parseInt(id));
        setCompany(data);
      } catch (err) {
        setError('Failed to load company data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchCompany();
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
    <div className="min-h-screen bg-gray-100">
      {/* Main Content */}
      <div className="max-w-4xl mx-auto">
        {/* Company Header Card */}
        <CompanyHeader company={company} />
        {/* Tabs Section */}
        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="bg-white border border-gray-200 rounded-lg p-1 mb-6 h-auto">
            <TabsTrigger
              value="profile"
              className="rounded-2xl px-3 py-1 text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm"
            >
              Profile
            </TabsTrigger>
            <TabsTrigger
              value="risk"
              className="rounded-2xl px-3 py-1 text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm"
            >
              Risk Indicators
            </TabsTrigger>
            <TabsTrigger
              value="reporting"
              className="rounded-2xl px-3 py-1 text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm"
            >
              Reporting
            </TabsTrigger>
            <TabsTrigger
              value="graph"
              className="rounded-2xl px-3 py-1 text-sm font-medium data-[state=active]:bg-white data-[state=active]:shadow-sm"
            >
              Node Graph
            </TabsTrigger>
          </TabsList>

          <TabsContent value="profile" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-2 gap-4">
              {/* Revenue Card */}
              <Card className="bg-white border border-gray-200 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-base text-gray-600">Revenue</p>
                  <TrendingUp className="w-5 h-5 text-green-600" />
                </div>
                <p className="text-3xl font-semibold text-gray-900 mb-2">
                  €12.5M
                </p>
                <p className="text-sm text-green-600">+12% YoY</p>
              </Card>

              {/* Employees Card */}
              <Card className="bg-white border border-gray-200 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <p className="text-base text-gray-600">Employees</p>
                  <Users2 className="w-5 h-5 text-blue-600" />
                </div>
                <p className="text-3xl font-semibold text-gray-900 mb-2">
                  {company.officers?.length || 85}
                </p>
                <p className="text-sm text-gray-600">Full-time staff</p>
              </Card>
            </div>

            {/* Officers & Management */}
            <Card className="bg-white border border-gray-200 rounded-2xl p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                Officers & Management
              </h3>

              {company.officers && company.officers.length > 0 ? (
                <div className="space-y-4">
                  {/* CEO Section */}
                  <div>
                    <p className="text-xs text-gray-500 uppercase mb-3">
                      CEO(S)
                    </p>
                    {company.officers.slice(0, 1).map((officer, index) => (
                      <div key={index} className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                          <Users2 className="w-5 h-5 text-gray-600" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {officer.full_name ||
                              `${officer.first_name} ${officer.last_name}`.trim()}
                          </p>
                          <p className="text-xs text-gray-500">
                            {officer.role || 'CEO'}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="border-t border-gray-200" />

                  {/* Officers Section */}
                  <div>
                    <p className="text-xs text-gray-500 uppercase mb-3">
                      Officers
                    </p>
                    <div className="space-y-4">
                      {company.officers.slice(1).map((officer, index) => (
                        <div key={index} className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                            <Users2 className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {officer.full_name ||
                                `${officer.first_name} ${officer.last_name}`.trim()}
                            </p>
                            <p className="text-xs text-gray-500">
                              {officer.role || 'Officer'}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500 text-sm">
                  No officers information available
                </p>
              )}
            </Card>
          </TabsContent>

          <TabsContent value="risk">
            <Card className="bg-white border border-gray-200 rounded-2xl p-6">
              <p className="text-gray-500">
                Risk indicators content coming soon...
              </p>
            </Card>
          </TabsContent>

          <TabsContent value="reporting">
            <Card className="bg-white border border-gray-200 rounded-2xl p-6">
              <p className="text-gray-500">Reporting content coming soon...</p>
            </Card>
          </TabsContent>

          <TabsContent value="graph">
            <Card className="bg-white border border-gray-200 rounded-2xl p-6">
              <p className="text-gray-500">
                Node graph visualization coming soon...
              </p>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
