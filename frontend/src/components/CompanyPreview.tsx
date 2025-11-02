'use client';

import { useEffect, useState } from 'react';
import { Building2, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { listCompanies, type Company } from '@/lib/api';
import Link from 'next/link';

interface CompanyPreviewProps {
  maxCompanies?: number;
}

export default function CompanyPreview({
  maxCompanies = 12,
}: CompanyPreviewProps) {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const companiesPerPage = maxCompanies;
  const totalPages = Math.ceil(total / companiesPerPage);

  const loadCompanies = async () => {
    setLoading(true);
    try {
      const offset = (currentPage - 1) * companiesPerPage;
      const data = await listCompanies(companiesPerPage, offset);
      setCompanies(data);
      // Backend doesn't return total count, so we estimate based on results
      // If we get a full page, there might be more
      if (data.length === companiesPerPage) {
        setTotal(offset + data.length + 1); // At least one more page
      } else {
        setTotal(offset + data.length); // Last page
      }
    } catch (error) {
      console.error('Failed to load companies:', error);
      setCompanies([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCompanies();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage]);

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
    }
  };

  if (loading && companies.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
        {Array.from({ length: maxCompanies }).map((_, i) => (
          <Card key={i} className="p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3"></div>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Company Directory</h2>
          <p className="text-muted-foreground">
            Showing {companies.length} of {total.toLocaleString()} companies
          </p>
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrevPage}
              disabled={currentPage === 1 || loading}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <span className="text-sm text-muted-foreground px-4">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNextPage}
              disabled={currentPage === totalPages || loading}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>

      {/* Company Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {companies.map((company) => (
          <Link key={company.id} href={`/company/${company.id}`}>
            <Card className="p-6 hover:shadow-lg transition-all hover:border-blue-300 cursor-pointer h-full">
              <div className="flex items-start gap-3 mb-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Building2 className="h-5 w-5 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm line-clamp-2 mb-1">
                    {company.name}
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    FN {company.fnr}
                  </p>
                </div>
              </div>

              <div className="space-y-2 text-sm">
                {company.legal_form && (
                  <div className="text-xs text-muted-foreground truncate">
                    {company.legal_form}
                  </div>
                )}

                {company.state && (
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        company.state === 'active'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {company.state}
                    </span>
                  </div>
                )}
              </div>
            </Card>
          </Link>
        ))}
      </div>

      {companies.length === 0 && !loading && (
        <div className="text-center py-12">
          <Building2 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <p className="text-muted-foreground">No companies found</p>
        </div>
      )}

      {/* Bottom Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center pt-4">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handlePrevPage}
              disabled={currentPage === 1 || loading}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            <span className="text-sm text-muted-foreground px-4">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleNextPage}
              disabled={currentPage === totalPages || loading}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
