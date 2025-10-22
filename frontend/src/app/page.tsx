'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';
import { CompanyList } from '@/components/companies/company-list';

export default function Home() {
  return (
    <div>
      {/* Hero Section */}
      <section className="flex container mx-auto px-4 py-128 md:py-24">
        <div className="mx-auto max-w-3xl text-center flex flex-col content-center">
          <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-6xl">
            Welcome to Bizray - the Xray for Businesses
          </h1>
          <p className="text-muted-foreground mb-8 text-lg md:text-xl">
            Comprehensive company data, network analysis, and business
            intelligence to help you make informed decisions.
          </p>
          <div className="flex flex-col justify-center gap-4 sm:flex-row">
            <Button asChild size="lg">
              <Link href="/search">
                <Search className="mr-2 h-4 w-4" />
                Search Companies
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/dashboard">View Dashboard</Link>
            </Button>
          </div>
        </div>
      </section>
      {/* Data Table */}
      <section className="flex flex-col items-center w-[800px] mx-auto px-4 py-16">
        <div className="mb-8 text-center">
          <h2 className="mb-2 text-3xl font-bold">Explore Businesses</h2>
          <p className="text-muted-foreground">
            Research businesses located in Austria
          </p>
        </div>
        <CompanyList showSearch={true} autoLoad={true} defaultQuery="GmbH" />
      </section>
    </div>
  );
}
