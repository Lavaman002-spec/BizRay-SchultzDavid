'use client';

import { useState } from 'react';
import {
  Building2,
  MapPin,
  Calendar,
  TrendingUp,
  Share2,
  Download,
  Bell,
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '@/context/AuthContext';
import { useEffect } from 'react';
import BrandButton from '@/components/commons/BrandButton';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { CompanyWithDetails } from '@/types/company';
import { generateCompanyPDF } from '@/lib/pdfExport';
import { createExport } from '@/lib/api';

// Define the props interface
interface CompanyHeaderProps {
  company: CompanyWithDetails;
  isRefreshing?: boolean;
}

export default function CompanyHeader({
  company,
  isRefreshing = false,
}: CompanyHeaderProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [isWatched, setIsWatched] = useState(false);
  const [isLoadingWatch, setIsLoadingWatch] = useState(true);
  const { session } = useAuth();

  useEffect(() => {
    const checkWatchlist = async () => {
      if (!session?.access_token) return;
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/watchlist/check/${company.id}`,
          {
            headers: { Authorization: `Bearer ${session.access_token}` },
          }
        );
        if (res.ok) {
          const data = await res.json();
          setIsWatched(data.is_watched);
        }
      } catch (error) {
        console.error('Failed to check watchlist', error);
      } finally {
        setIsLoadingWatch(false);
      }
    };
    checkWatchlist();
  }, [company.id, session]);

  const handleWatchToggle = async () => {
    if (!session) {
      toast.error('Please login to watch companies');
      return;
    }

    const originalState = isWatched;
    setIsWatched(!isWatched); // Optimistic update

    try {
      const method = originalState ? 'DELETE' : 'POST';
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/watchlist/${company.id}`,
        {
          method,
          headers: { Authorization: `Bearer ${session.access_token}` },
        }
      );

      if (!res.ok) throw new Error('Failed to update watchlist');

      toast.success(
        originalState ? 'Removed from watchlist' : 'Added to watchlist'
      );
    } catch (error) {
      console.error(error);
      setIsWatched(originalState); // Revert
      toast.error('Failed to update watchlist');
    }
  };

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast.success('Link copied to clipboard!');
    } catch (err) {
      console.error(err);
      toast.error('Failed to copy link');
    }
  };

  const handleExport = async () => {
    try {
      setIsExporting(true);

      // Generate and download the PDF
      generateCompanyPDF(company);

      // Create export record in database
      await createExport({
        company_id: company.id,
        export_type: 'pdf',
      });

      console.log('Export completed successfully');
    } catch (error) {
      console.error('Failed to export company data:', error);
      alert('Failed to export company data. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };
  const primaryAddress = company.addresses?.[0];
  const addressString = primaryAddress
    ? [primaryAddress.street, primaryAddress.house_number, primaryAddress.city]
        .filter(Boolean)
        .join(' ')
    : null;

  return (
    <Card className="bg-white border border-gray-200 rounded-2xl p-8 mb-6">
      {isRefreshing && (
        <span className="text-xs text-gray-500 animate-pulse">
          Refreshing data…
        </span>
      )}
      <div className="flex flex-col items-start gap-4 mb-6">
        {/* Left: Company Info */}
        <div className="flex gap-4">
          {/* Company Icon */}
          <div className="bg-gray-100 rounded-2xl p-4 w-16 h-16 flex items-center justify-center">
            <Building2 className="w-8 h-8 text-gray-600" />
          </div>

          {/* Company Details */}
          <div>
            <h1 className="text-4xl font-semibold text-gray-900 mb-2">
              {company.name}
            </h1>
            <div className="flex items-center gap-3 text-gray-600">
              <span className="text-base">{company.legal_form || 'GmbH'}</span>
              <span className="text-base">•</span>
              <span className="text-base">FN {company.fnr}</span>
              <Badge className="bg-blue-100 text-blue-600 border-blue-200 text-xs px-2 py-0.5 font-medium">
                Active
              </Badge>
            </div>
          </div>
        </div>

        {/* Right: Action Buttons */}
        <div className="flex gap-3 items-center">
          <BrandButton
            variant="secondary"
            text={isWatched ? 'Watching' : 'Watch'}
            leftIcon={Bell}
            onClick={handleWatchToggle}
            className={
              isWatched ? 'bg-blue-50 text-blue-600 border-blue-200' : ''
            }
          />
          <BrandButton
            variant="secondary"
            text="Share"
            leftIcon={Share2}
            onClick={handleShare}
          />
          <BrandButton
            variant="primary"
            text={isExporting ? 'Exporting...' : 'Export'}
            leftIcon={Download}
            onClick={handleExport}
            disabled={isExporting}
          />
        </div>
      </div>

      {/* Company Info Grid */}
      <div className="flex gap-6 w-full">
        {/* Address */}
        <div className="flex gap-3 w-full">
          <MapPin className="w-5 h-5 text-gray-600 mt-0.5" />
          <div>
            <p className="text-sm text-gray-600 mb-1">Address</p>
            {addressString ? (
              <>
                <p className="text-base text-gray-900">
                  {primaryAddress?.street} {primaryAddress?.house_number}
                </p>
                <p className="text-base text-gray-900">
                  {primaryAddress?.city}
                </p>
              </>
            ) : (
              <p className="text-base text-gray-400">Not available</p>
            )}
          </div>
        </div>

        {/* Industry */}
        <div className="flex gap-3 w-full">
          <TrendingUp className="w-5 h-5 text-gray-600 mt-0.5" />
          <div>
            <p className="text-sm text-gray-600 mb-1">Industry</p>
            <p className="text-base text-gray-900">Technology</p>
          </div>
        </div>

        {/* Last Updates */}
        <div className="flex gap-3 w-full">
          <Calendar className="w-5 h-5 text-gray-600 mt-0.5" />
          <div>
            <p className="text-sm text-gray-600 mb-1">Last Updated</p>
            <p className="text-base text-gray-900">
              {company.created_at
                ? new Date(company.created_at).getFullYear()
                : '2015'}
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
}
