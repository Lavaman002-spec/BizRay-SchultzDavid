'use client';

import { useState } from 'react';
import CompanySearch from '@/components/CompanySearch';
import CompanySearchResults from '@/components/CompanySearchResults';
import type { Company } from '@/types/company';

export default function SearchPage() {
  const [results, setResults] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [hasSearched, setHasSearched] = useState(false);

  const handleResults = (companies: Company[], count: number) => {
    setResults(companies);
    setTotal(count);
    setHasSearched(true);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold">Search Companies</h1>
          <p className="text-muted-foreground">
            Search the Austrian Business Register (Firmenbuch)
          </p>
        </div>

        <div className="mb-8">
          <CompanySearch onResults={handleResults} />
        </div>

        {hasSearched && (
          <CompanySearchResults results={results} total={total} />
        )}
      </div>
    </div>
  );
}
