'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Building2,
  MapPin,
  ArrowLeft,
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
import { getCompany } from '@/lib/api';
import type { CompanyWithDetails } from '@/types/company';

export default function CompanyPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [company, setCompany] = useState<CompanyWithDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCompany() {
      try {
        setLoading(true);
        const data = await getCompany(parseInt(id));
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

  if (error || !company) {
    return (
      <div className="min-h-screen">
        <header className="border-b bg-white/80 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-4">
            <Button variant="ghost" onClick={() => router.push('/search')}>
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

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <Button variant="ghost" onClick={() => router.push('/search')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Search
          </Button>
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
              <h1 className="text-4xl font-bold mb-2">{company.name}</h1>
              <div className="flex items-center gap-4 text-white/80">
                <span className="font-mono text-lg">FN {company.fnr}</span>
                {company.legal_form && <span>{company.legal_form}</span>}
                {company.state && (
                  <Badge
                    variant="secondary"
                    className="bg-white/20 text-white border-white/30"
                  >
                    {company.state}
                  </Badge>
                )}
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
                Officers ({company.officers?.length || 0})
              </TabsTrigger>
              <TabsTrigger value="addresses">
                <MapPin className="h-4 w-4 mr-2" />
                Addresses ({company.addresses?.length || 0})
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
                      <div className="text-sm text-muted-foreground">Name</div>
                      <div className="font-medium">{company.name}</div>
                    </div>
                    <Separator />
                    <div>
                      <div className="text-sm text-muted-foreground">
                        Legal Form
                      </div>
                      <div className="font-medium">
                        {company.legal_form || 'Not specified'}
                      </div>
                    </div>
                    <Separator />
                    <div>
                      <div className="text-sm text-muted-foreground">
                        FN Number
                      </div>
                      <div className="font-mono">{company.fnr}</div>
                    </div>
                    <Separator />
                    <div>
                      <div className="text-sm text-muted-foreground">
                        Status
                      </div>
                      <Badge>{company.state || 'Unknown'}</Badge>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Timeline</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {company.created_at && (
                      <>
                        <div>
                          <div className="text-sm text-muted-foreground">
                            Created
                          </div>
                          <div className="font-medium">
                            {new Date(company.created_at).toLocaleDateString()}
                          </div>
                        </div>
                        <Separator />
                      </>
                    )}
                    {company.updated_at && (
                      <>
                        <div>
                          <div className="text-sm text-muted-foreground">
                            Last Updated
                          </div>
                          <div className="font-medium">
                            {new Date(company.updated_at).toLocaleDateString()}
                          </div>
                        </div>
                        <Separator />
                      </>
                    )}
                    {company.last_fetched_at && (
                      <div>
                        <div className="text-sm text-muted-foreground">
                          Last Fetched
                        </div>
                        <div className="font-medium">
                          {new Date(
                            company.last_fetched_at
                          ).toLocaleDateString()}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Officers Tab */}
            <TabsContent value="officers">
              {!company.officers || company.officers.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No officers found for this company.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {company.officers.map((officer, index) => (
                    <Card key={index}>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                          <Users className="h-5 w-5 text-blue-600" />
                          {officer.full_name}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {officer.role && (
                            <div>
                              <div className="text-sm text-muted-foreground">
                                Role
                              </div>
                              <Badge variant="secondary">{officer.role}</Badge>
                            </div>
                          )}
                          {officer.title && (
                            <div>
                              <div className="text-sm text-muted-foreground">
                                Title
                              </div>
                              <div className="text-sm">{officer.title}</div>
                            </div>
                          )}
                          {officer.vnr && (
                            <div>
                              <div className="text-sm text-muted-foreground">
                                VNR
                              </div>
                              <div className="font-mono text-sm">
                                {officer.vnr}
                              </div>
                            </div>
                          )}
                          {officer.birth_date && (
                            <div>
                              <div className="text-sm text-muted-foreground">
                                Birth Date
                              </div>
                              <div className="text-sm">
                                {new Date(
                                  officer.birth_date
                                ).toLocaleDateString()}
                              </div>
                            </div>
                          )}
                          <div>
                            <Badge
                              variant={
                                officer.is_active ? 'default' : 'secondary'
                              }
                            >
                              {officer.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Addresses Tab */}
            <TabsContent value="addresses">
              {!company.addresses || company.addresses.length === 0 ? (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    No addresses found for this company.
                  </AlertDescription>
                </Alert>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {company.addresses.map((address, index) => (
                    <Card key={index}>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center gap-2">
                          <MapPin className="h-5 w-5 text-blue-600" />
                          Address {index + 1}
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          {address.street && (
                            <div>
                              <div className="text-sm text-muted-foreground">
                                Street
                              </div>
                              <div>{address.street}</div>
                            </div>
                          )}
                          {address.city && (
                            <div>
                              <div className="text-sm text-muted-foreground">
                                City
                              </div>
                              <div>{address.city}</div>
                            </div>
                          )}
                          {address.postal_code && (
                            <div>
                              <div className="text-sm text-muted-foreground">
                                Postal Code
                              </div>
                              <div>{address.postal_code}</div>
                            </div>
                          )}
                          {address.country && (
                            <div>
                              <div className="text-sm text-muted-foreground">
                                Country
                              </div>
                              <div>{address.country}</div>
                            </div>
                          )}
                          <div className="flex gap-2 pt-2">
                            {address.is_active && (
                              <Badge variant="default">Active</Badge>
                            )}
                            {address.is_deliverable && (
                              <Badge variant="secondary">Deliverable</Badge>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </section>
    </div>
  );
}
