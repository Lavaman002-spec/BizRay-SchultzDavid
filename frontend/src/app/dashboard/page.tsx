import StatsCards from '@/components/StatsCards';

export default function DashboardPage() {
  return (
    <div>
      {/* Hero Section */}
      <section className="flex container mx-auto px-4 py-12 md:py-16">
        <div className="mx-auto max-w-6xl w-full">
          <div className="mb-8 text-center">
            <h1 className="mb-4 text-4xl font-bold tracking-tight md:text-5xl">
              Dashboard
            </h1>
            <p className="text-muted-foreground text-lg md:text-xl">
              Comprehensive company data, network analysis, and business
              intelligence to help you make informed decisions.
            </p>
          </div>

          <div className="mt-12">
            <StatsCards />
          </div>
        </div>
      </section>
    </div>
  );
}
