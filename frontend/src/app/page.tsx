'use client';

import { useState } from 'react';
import { Search, Building2, TrendingUp, Database } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import CompanySearchResults from '@/components/CompanySearchResults';
import { searchCompanies, type Company } from '@/lib/api';

export default function Home() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setHasSearched(true);

    try {
      const data = await searchCompanies(query);
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
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Building2 className="h-8 w-8 text-blue-600" />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                BizRay
              </h1>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Database className="h-4 w-4" />
                <span>Austrian Business Register</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 bg-clip-text text-transparent">
            Austrian Business Intelligence
          </h2>
          <p className="text-xl text-muted-foreground mb-12">
            Search and analyze company data from the Austrian Business Register
          </p>

          {/* Search Box */}
          <form onSubmit={handleSearch} className="mb-8">
            <div className="flex gap-2 max-w-2xl mx-auto">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-5 w-5" />
                <Input
                  type="text"
                  placeholder="Search by company name or register ID..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="pl-10 h-12 text-lg"
                />
              </div>
              <Button type="submit" size="lg" disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </div>
          </form>

          {/* Stats Cards */}
          {!hasSearched && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-3xl mx-auto">
              <Card className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Building2 className="h-5 w-5 text-blue-600" />
                  </div>
                  <h3 className="font-semibold">Companies</h3>
                </div>
                <p className="text-3xl font-bold">6</p>
                <p className="text-sm text-muted-foreground">In database</p>
              </Card>

              <Card className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <TrendingUp className="h-5 w-5 text-green-600" />
                  </div>
                  <h3 className="font-semibold">Officers</h3>
                </div>
                <p className="text-3xl font-bold">3</p>
                <p className="text-sm text-muted-foreground">Tracked</p>
              </Card>

              <Card className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Database className="h-5 w-5 text-purple-600" />
                  </div>
                  <h3 className="font-semibold">Links</h3>
                </div>
                <p className="text-3xl font-bold">3</p>
                <p className="text-sm text-muted-foreground">
                  Ownership connections
                </p>
              </Card>
            </div>
          )}
        </div>
      </section>

      {/* Search Results */}
      {hasSearched && (
        <section className="pb-20 px-4">
          <div className="container mx-auto max-w-6xl">
            <CompanySearchResults
              results={results}
              total={total}
              loading={loading}
              query={query}
            />
          </div>
        </section>
      )}
    </div>
  );
}
