'use client';

import { useEffect, useState } from 'react';
import { DataTable } from '@/components/data-table';
import { companyColumns, Company } from './company-columns';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';

interface CompanyListProps {
  initialQuery?: string;
  autoLoad?: boolean;
  showSearch?: boolean;
}

export function CompanyList({
  initialQuery = '',
  autoLoad = false,
  showSearch = true,
}: CompanyListProps) {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [query, setQuery] = useState(initialQuery);

  useEffect(() => {
    if (autoLoad && initialQuery) {
      fetchCompanies(initialQuery);
    }
  }, [autoLoad, initialQuery]);

  const fetchCompanies = async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setError('Please enter at least 2 characters');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `http://localhost:8000/search?q=${encodeURIComponent(searchQuery)}`
      );

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setCompanies(data.results || []);
    } catch (err) {
      setError('Failed to load companies. Make sure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCompanies(query);
  };

  return (
    <div className="space-y-4">
      {showSearch && (
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1">
            <Input
              type="text"
              placeholder="Search companies by name..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
          </div>
          <Button type="submit" disabled={loading}>
            <Search className="mr-2 h-4 w-4" />
            {loading ? 'Searching...' : 'Search'}
          </Button>
        </form>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      ) : companies.length > 0 ? (
        <div>
          <div className="mb-4 text-sm text-muted-foreground">
            Found {companies.length}{' '}
            {companies.length === 1 ? 'company' : 'companies'}
          </div>
          <DataTable columns={companyColumns} data={companies} />
        </div>
      ) : query && !error ? (
        <div className="rounded-md border border-dashed p-8 text-center">
          <p className="text-muted-foreground">
            No companies found. Try a different search term.
          </p>
        </div>
      ) : null}
    </div>
  );
}
