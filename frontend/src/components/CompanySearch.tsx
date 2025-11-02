'use client';

import { useState, FormEvent } from 'react';
import { ArrowRightIcon } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { searchCompanies } from '@/lib/api';
import type { Company } from '@/types/company';

interface CompanySearchProps {
  onResults?: (companies: Company[], total: number) => void;
  loading?: boolean;
  placeholder?: string;
}

export default function CompanySearch({
  onResults,
  loading = false,
  placeholder = 'Search by company name or FN number...',
}: CompanySearchProps) {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a search term');
      return;
    }

    setIsSearching(true);
    setError(null);

    try {
      const response = await searchCompanies(query, 50, 0);
      onResults?.(response.results, response.total);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to search companies'
      );
      onResults?.([], 0);
    } finally {
      setIsSearching(false);
    }
  };

  const isLoading = loading || isSearching;

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex flex-col bg-white rounded-2xl border border-zinc-200 overflow-hidden">
        {/* Search Input Row */}
        <div className="flex items-center gap-2 p-4">
          <div className="relative flex-1">
            <Input
              type="text"
              placeholder={placeholder}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="border-none shadow-none focus-visible:ring-0 text-base px-0"
              disabled={isLoading}
            />
          </div>
        </div>

        {/* Submit Button Row */}
        <div className="w-full flex items-center justify-between px-4 pb-4">
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className={error ? '' : 'ml-auto'}>
            <Button
              type="submit"
              size="icon"
              disabled={isLoading || !query.trim()}
              className="rounded-lg w-10 h-10 bg-black hover:bg-gray-800 disabled:bg-gray-300"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <ArrowRightIcon className="w-5 h-5" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </form>
  );
}
