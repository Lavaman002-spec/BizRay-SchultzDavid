'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Building2,
  MapPin,
  ArrowLeft,
  Download,
  Users,
  FileText,
  Briefcase,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import { getCompany, exportCompanyCSV, type CompanyProfile } from '@/lib/api';

export default function CompanyPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [company, setCompany] = useState<CompanyProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    async function fetchCompany() {
      try {
        setLoading(true);
        const data = await getCompany(id);
        setCompany(data);
      } catch (err) {
        setError('Failed to load company data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchCompany();
  }, [id]);

  const handleExport = async () => {
    try {
      setExporting(true);
      toast.loading('Preparing export...');

      const blob = await exportCompanyCSV(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `company_${company?.identity.register_id}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success('Export downloaded successfully!');
    } catch (err) {
      toast.error('Failed to export company data');
      console.error(err);
    } finally {
      setExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen">
        <header className="border-b bg-white/80 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-4">
            <Skeleton className="h-8 w-48" />
          </div>
        </header>
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          <Skeleton className="h-12 w-3/4 mb-4" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    );
  }

  if (error || !company) {
    return (
      <div className="min-h-screen">
        <header className="border-b bg-white/80 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-4">
            <Button variant="ghost" onClick={() => router.push('/')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Search
            </Button>
          </div>
        </header>
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || 'Company not found'}</AlertDescription>
          </Alert>
        </div>
      </div>
    );
  }

  const { identity, officers } = company;

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Button variant="ghost" onClick={() => router.push('/')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Search
            </Button>
            <Button onClick={handleExport} disabled={exporting}>
              <Download className="h-4 w-4 mr-2" />
              {exporting ? 'Exporting...' : 'Export CSV'}
            </Button>
          </div>
        </div>
      </header>

      {/* Company Header */}
      <section className="bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-12">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="flex items-start gap-4">
            <div className="p-4 bg-white/10 rounded-lg backdrop-blur-sm">
              <Building2 className="h-12 w-12" />
            </div>
            <div className="flex-1">
              <h1 className="text-4xl font-bold mb-2">{identity.name}</h1>
              <div className="flex items-center gap-4 text-white/80">
                <span className="font-mono text-lg">
                  {identity.register_id}
                </span>
                {identity.city && (
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    {identity.city}
                  </div>
                )}
                <Badge
                  variant="secondary"
                  className="bg-white/20 text-white border-white/30"
                >
                  {identity.status || 'Unknown'}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Company Details */}
      <section className="py-8">
        <div className="container mx-auto px-4 max-w-6xl">
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-8">
              <TabsTrigger value="overview">
                <FileText className="h-4 w-4 mr-2" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="officers">
                <Users className="h-4 w-4 mr-2" />
                Officers ({officers.length})
              </TabsTrigger>
              <TabsTrigger value="ownership">
                <Briefcase className="h-4 w-4 mr-2" />
                Ownership
              </TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview">
              <div className="grid gap-6 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Company Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="text-sm text-muted-foreground">
                        Legal Form
                      </div>
                      <div className="font-medium">
                        {identity.legal_form || 'Not specified'}
                      </div>
                    </div>
                    <Separator />
                    <div>
                      <div className="text-sm text-muted-foreground">
                        Register ID
                      </div>
                      <div className="font-mono">{identity.register_id}</div>
                    </div>
                    <Separator />
                    <div>
                      <div className="text-sm text-muted-foreground">
                        Status
                      </div>
                      <Badge>{identity.status || 'Unknown'}</Badge>
                    </div>
                    <Separator />
                    <div>
                      <div className="text-sm text-muted-foreground">
                        Country
                      </div>
                      <div>{identity.country || 'Austria'}</div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Address Information</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {identity.address_line && (
                      <>
                        <div>
                          <div className="text-sm text-muted-foreground">
                            Street Address
                          </div>
                          <div className="font-medium">
                            {identity.address_line}
                          </div>
                        </div>
                        <Separator />
                      </>
                    )}
                    <div>
                      <div className="text-sm text-muted-foreground">City</div>
                      <div className="font-medium">
                        {identity.city || 'Not specified'}
                      </div>
                    </div>
                    {identity.address_line && identity.city && (
                      <>
                        <Separator />
                        <div className="pt-2">
                          <Button variant="outline" className="w-full" asChild>
                            <a
                              href={`https://www.google.com/maps/search/${encodeURIComponent(
                                `${identity.address_line}, ${identity.city}, Austria`
                              )}`}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <MapPin className="h-4 w-4 mr-2" />
                              View on Map
                            </a>
                          </Button>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Officers Tab */}
            <TabsContent value="officers">
              {officers.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No officers found for this company.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {officers.map((officer, index) => (
                    <Card key={index}>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                          <Users className="h-5 w-5 text-blue-600" />
                          {officer.person_name}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <div>
                            <div className="text-sm text-muted-foreground">
                              Role
                            </div>
                            <Badge variant="secondary">{officer.role}</Badge>
                          </div>
                          {officer.person_id && (
                            <div>
                              <div className="text-sm text-muted-foreground">
                                Person ID
                              </div>
                              <div className="font-mono text-sm">
                                {officer.person_id}
                              </div>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Ownership Tab */}
            <TabsContent value="ownership">
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  Ownership and corporate structure visualization coming soon.
                </AlertDescription>
              </Alert>
            </TabsContent>
          </Tabs>
        </div>
      </section>
    </div>
  );
}
