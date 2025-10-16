import Link from 'next/link';
import { Input } from '@/components/ui/input';
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuIndicator,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  NavigationMenuViewport,
} from '@/components/ui/navigation-menu';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Search, Network, BarChart3, FileText } from 'lucide-react';
import { AppNav } from '@/components/layout/AppNav';

export default function Home() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24 min-h-screen">
        <div className="mx-auto max-w-3xl text-center flex flex-col content-center">
          <h1 className="mb-6 text-4xl font-bold tracking-tight md:text-6xl">
            B2B Company Intelligence
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

      {/* Features Section */}
      <section className="bg-muted/50 border-t py-16">
        <div className="container mx-auto px-4">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader>
                <Search className="text-primary mb-2 h-8 w-8" />
                <CardTitle>Search & Discovery</CardTitle>
                <CardDescription>
                  Find companies with advanced search and filters
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <FileText className="text-primary mb-2 h-8 w-8" />
                <CardTitle>Company Profiles</CardTitle>
                <CardDescription>
                  Detailed information, filings, and financials
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Network className="text-primary mb-2 h-8 w-8" />
                <CardTitle>Network Analysis</CardTitle>
                <CardDescription>
                  Visualize relationships and ownership structures
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <BarChart3 className="text-primary mb-2 h-8 w-8" />
                <CardTitle>Financial Insights</CardTitle>
                <CardDescription>
                  Track metrics and trends over time
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
}
