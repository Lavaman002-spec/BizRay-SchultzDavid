'use client';

import { useEffect, useState } from 'react';
import { Building2, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CompanyWithDetails, listCompanies } from '@/lib/api';
import CompanyCard from '@/components/CompanyCard';

interface CompanyPreviewProps {
  maxCompanies?: number;
}

export default function CompanyPreview({
  maxCompanies = 12,
}: CompanyPreviewProps) {
  const [companies, setCompanies] = useState<CompanyWithDetails[]>([]);
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
            <div className="h-4 bg-white rounded "></div>
            <div className="h-3 bg-white rounded "></div>
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
        {companies.map((company) => (
          <CompanyCard key={company.id} company={company} />
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
