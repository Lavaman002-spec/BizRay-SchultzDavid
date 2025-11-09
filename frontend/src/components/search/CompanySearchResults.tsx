'use client';

import { AlertCircle } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { Company } from '@/types/company';
import CompanyCard from '../company/CompanyCard';

interface CompanySearchResultsProps {
  results: Company[];
  total: number;
  loading?: boolean;
  query?: string;
}

// Helper function to format address
function formatAddress(company: Company): string | undefined {
  if (!company.address) return undefined;

  const parts: string[] = [];

  // Add street and house number
  if (company.address.street) {
    let streetPart = company.address.street;
    if (company.address.house_number) {
      streetPart += ` ${company.address.house_number}`;
    }
    parts.push(streetPart);
  }

  // Add city
  if (company.address.city) {
    parts.push(company.address.city);
  }

  return parts.length > 0 ? parts.join(', ') : undefined;
}

export default function CompanySearchResults({
  results,
  total,
  loading,
  query,
}: CompanySearchResultsProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-8 w-64" />
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <Skeleton className="h-6 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/2" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          No companies found{query ? ` for "${query}"` : ''}. Try a different
          search term.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">
          {total} {total === 1 ? 'Company' : 'Companies'} Found
        </h2>
        {query && (
          <p className="text-muted-foreground">
            Results for{' '}
            <span className="font-semibold">&quot;{query}&quot;</span>
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {results.map((company) => (
          <CompanyCard
            key={company.id}
            company={company}
            address={formatAddress(company)}
          />
        ))}
      </div>
    </div>
  );
}
