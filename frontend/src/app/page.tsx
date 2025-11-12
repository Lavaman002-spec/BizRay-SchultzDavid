'use client';

import { useState } from 'react';
import { ChevronLeft } from 'lucide-react';
import CompanySearchResults from '@/components/search/CompanySearchResults';
import CompanyPreview from '@/components/search/CompanyPreview';
import CompanySearch from '@/components/search/CompanySearch';
import StatsCards from '@/components/StatsCards';
import { type Company } from '@/types/company';

import Image from 'next/image';

export default function Home() {
  const [results, setResults] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [loading] = useState(false); // Optional addition: setLoading
  const [hasSearched, setHasSearched] = useState(false);
  const [isSearchActive, setIsSearchActive] = useState(false);

  const handleResults = (companies: Company[], count: number) => {
    setResults(companies);
    setTotal(count);
    setHasSearched(true);
    setIsSearchActive(true);
  };

  const handleClearSearch = () => {
    setResults([]);
    setTotal(0);
    setHasSearched(false);
    setIsSearchActive(false);
  };

  return (
    <div className="">
      <div
        className={`flex flex-col place-items-center gap-16 transition-all duration-500 ${
          isSearchActive ? 'min-h-fit py-24' : 'py-32 justify-center'
        }`}
      >
        {/* Hero Section */}
        <section className="flex flex-col w-full max-w-4xl">
          <div className="flex flex-col gap-8 text-left items-left">
            <Image
              src={'/Bizray-icon.svg'}
              width={64}
              height={64}
              alt="Bizray Logo"
              className={`transition-opacity duration-500 ${
                isSearchActive ? 'opacity-0 h-0' : 'opacity-100'
              }`}
            />
            <h2
              className={`text-5xl font-medium text-zinc-950 transition-opacity duration-500 ${
                isSearchActive ? 'opacity-0 h-0' : 'opacity-100'
              }`}
            >
              Welcome to Bizray.
            </h2>
            <p
              className={`text-base text-zinc-700 transition-opacity duration-500 ${
                isSearchActive ? 'opacity-0 h-0' : 'opacity-100'
              }`}
            >
              Aggregate Austrian register data into rich company profiles,
              network graphs, and actionable risk indicators—fast.
            </p>

            {/* Search Box */}
            <div className="w-full flex flex-col gap-4">
              {isSearchActive && (
                <button
                  onClick={handleClearSearch}
                  className="flex items-center gap-2 text-sm text-zinc-600 hover:text-zinc-900 transition-colors w-fit"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Back to home
                </button>
              )}
              <CompanySearch
                onResults={handleResults}
                onClear={handleClearSearch}
              />
              <StatsCards
                className={`transition-opacity duration-500 ${
                  isSearchActive ? 'opacity-0 h-0' : 'opacity-100'
                }`}
              />
            </div>

            {/* Search Results - Show below search when active and results exist */}
            {isSearchActive && hasSearched && (
              <div className="w-full mt-8 animate-in fade-in duration-500">
                <CompanySearchResults
                  results={results}
                  total={total}
                  loading={loading}
                />
              </div>
            )}
          </div>
        </section>
      </div>

      {/* Company Preview or Search Results - Hidden when search is active */}
      {!isSearchActive && (
        <section className="flex flex-col place-items-center justify-center py-24">
          <div className="flex flex-col w-full max-w-4xl">
            {hasSearched ? (
              <CompanySearchResults
                results={results}
                total={total}
                loading={loading}
              />
            ) : (
              <CompanyPreview maxCompanies={12} />
            )}
          </div>
        </section>
      )}
    </div>
  );
}
