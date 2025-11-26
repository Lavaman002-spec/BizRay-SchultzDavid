'use client';

import { TrendingUp, Users2 } from 'lucide-react';
import { Card } from '@/components/ui/card';
import type { CompanyWithDetails } from '@/types/company';

interface OverviewProps {
  company: CompanyWithDetails;
}

export default function RevenueCard({ company }: OverviewProps) {
  const financials = company.financials?.[0];
  const revenueValue =
    typeof company.revenue === 'number'
      ? company.revenue
      : typeof financials?.revenue === 'number'
      ? financials.revenue
      : null;
  const hasRevenue = revenueValue !== null;
  const revenueCurrency =
    company.revenue_currency || financials?.currency || 'EUR';
  const revenueYear =
    company.latest_financial_year?.toString() ??
    financials?.year?.toString() ??
    '—';
  const revenueDisplay = hasRevenue
    ? new Intl.NumberFormat('de-AT', {
        style: 'currency',
        currency: revenueCurrency,
        maximumFractionDigits: 0,
      }).format(revenueValue as number)
    : 'No financial data';

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-4">
        {/* Revenue Card */}
        <Card className="bg-white border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <p className="text-base text-gray-600">Revenue</p>
            <TrendingUp className="w-5 h-5 text-green-600" />
          </div>
          <p className="text-3xl font-semibold text-gray-900 mb-2">
            {revenueDisplay}
          </p>
          <p
            className={`text-sm ${
              hasRevenue ? 'text-green-600' : 'text-gray-400'
            }`}
          >
            {hasRevenue ? '+12% YoY' : 'Awaiting latest filing'}
          </p>
          <p className="text-sm text-gray-600">FY {revenueYear}</p>
        </Card>

        {/* Employees Card */}
        <Card className="bg-white border border-gray-200 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-4">
            <p className="text-base text-gray-600">Employees</p>
            <Users2 className="w-5 h-5 text-blue-600" />
          </div>
          <p className="text-3xl font-semibold text-gray-900 mb-2">
            {company.officers?.length || 'N/A'}
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
              <p className="text-xs text-gray-500 uppercase mb-3">CEO(S)</p>
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
              <p className="text-xs text-gray-500 uppercase mb-3">Officers</p>
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
    </div>
  );
}
