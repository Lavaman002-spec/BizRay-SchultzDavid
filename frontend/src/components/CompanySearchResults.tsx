'use client';

import { Building2, MapPin, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import Link from 'next/link';
import type { Company } from '@/lib/api';

interface CompanySearchResultsProps {
  results: Company[];
  total: number;
  loading: boolean;
  query: string;
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

      <div className="grid gap-4">
        {results.map((company) => (
          <Link key={company.id} href={`/company/${company.id}`}>
            <Card className="hover:shadow-lg transition-all hover:scale-[1.01] cursor-pointer">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="flex items-center gap-2 mb-2">
                      <Building2 className="h-5 w-5 text-blue-600" />
                      {company.name}
                    </CardTitle>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span className="font-mono">{company.register_id}</span>
                      {company.city && (
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          {company.city}
                        </div>
                      )}
                    </div>
                  </div>
                  <Badge
                    variant={
                      company.status === 'AKTIV' || company.status === 'active'
                        ? 'default'
                        : 'secondary'
                    }
                  >
                    {company.status || 'Unknown'}
                  </Badge>
                </div>
              </CardHeader>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
