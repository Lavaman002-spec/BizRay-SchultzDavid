'use client';

import { useState } from 'react';
import CompanySearchResults from '@/components/CompanySearchResults';
import CompanyPreview from '@/components/CompanyPreview';
import CompanySearch from '@/components/CompanySearch';
import StatsCards from '@/components/StatsCards';
import { searchCompanies, type Company } from '@/lib/api';
import AppNav from '@/components/layout/AppNav';
import Image from 'next/image';

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [fetchFromAPI] = useState(true);

  const handleSearch = async (searchQuery: string) => {
    setQuery(searchQuery);
    setLoading(true);
    setHasSearched(true);

    try {
      const data = await searchCompanies(searchQuery, 20, 0, {
        fetchIfNotFound: fetchFromAPI,
      });
      setResults(data.items);
      setTotal(data.total);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-zinc-100">
      {/* Header */}
      <AppNav />

      <div className="min-h-screen flex flex-col place-items-center justify-center gap-16">
        {/* Hero Section */}
        <section className="flex flex-col w-full max-w-4xl">
          <div className="flex flex-col gap-8 text-left items-left mx-auto">
            <Image
              src={'/Bizray-icon.svg'}
              width={64}
              height={64}
              alt="Bizray Logo"
            />
            <h2 className="text-5xl font-medium text-zinc-950">
              Welcome to Bizray.
            </h2>
            <p className="text-base text-zinc-700">
              Aggregate Austrian register data into rich company profiles,
              network graphs, and actionable risk indicators—fast.
            </p>

            {/* Search Box */}
            <div className="w-full flex flex-col gap-4">
              <CompanySearch onSearch={handleSearch} loading={loading} />
              <StatsCards />
            </div>

            {/* Stats Cards - 16px gap (gap-4 = 16px in Tailwind) */}
          </div>
        </section>
      </div>

      {/* Company Preview or Search Results */}
      <section className="min-h-screen flex flex-col place-items-center justify-center px-4">
        <div className="flex flex-col w-full max-w-4xl">
          {hasSearched ? (
            <CompanySearchResults
              results={results}
              total={total}
              loading={loading}
              query={query}
            />
          ) : (
            <CompanyPreview maxCompanies={12} />
          )}
        </div>
      </section>
    </div>
  );
}
