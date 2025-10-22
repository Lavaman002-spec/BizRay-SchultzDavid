'use client';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { CompanyList } from '@/components/companies/company-list';

export default function SearchPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold">Search Companies</h1>
          <p className="text-muted-foreground">
            Search the Austrian Business Register (Firmenbuch)
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Company Search</CardTitle>
            <CardDescription>
              Enter a company name to search (minimum 2 characters)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CompanyList showSearch={true} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
