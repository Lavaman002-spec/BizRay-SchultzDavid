import {
  Building2,
  MapPin,
  Calendar,
  Globe,
  TrendingUp,
  Share2,
  Download,
} from 'lucide-react';
import BrandButton from '@/components/commons/BrandButton';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { CompanyWithDetails } from '@/types/company';

// Define the props interface
interface CompanyHeaderProps {
  company: CompanyWithDetails;
}

export default function CompanyHeader({ company }: CompanyHeaderProps) {
  const primaryAddress = company.addresses?.[0];
  const addressString = primaryAddress
    ? [primaryAddress.street, primaryAddress.house_number, primaryAddress.city]
        .filter(Boolean)
        .join(' ')
    : null;

  return (
    <Card className="bg-white border border-gray-200 rounded-2xl p-8 mb-6">
      <div className="flex items-start justify-between mb-6">
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
        <div className="flex gap-3">
          <BrandButton variant="secondary" text="Share" leftIcon={Share2} />
          <BrandButton variant="primary" text="Export" leftIcon={Download} />
        </div>
      </div>

      {/* Company Info Grid */}
      <div className="grid grid-cols-4 gap-6">
        {/* Address */}
        <div className="flex gap-3">
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

        {/* Founded */}
        <div className="flex gap-3">
          <Calendar className="w-5 h-5 text-gray-600 mt-0.5" />
          <div>
            <p className="text-sm text-gray-600 mb-1">Founded</p>
            <p className="text-base text-gray-900">
              {company.created_at
                ? new Date(company.created_at).getFullYear()
                : '2015'}
            </p>
          </div>
        </div>

        {/* Website */}
        <div className="flex gap-3">
          <Globe className="w-5 h-5 text-gray-600 mt-0.5" />
          <div>
            <p className="text-sm text-gray-600 mb-1">Website</p>
            <a href="#" className="text-base text-blue-600 hover:underline">
              www.example.com
            </a>
          </div>
        </div>

        {/* Industry */}
        <div className="flex gap-3">
          <TrendingUp className="w-5 h-5 text-gray-600 mt-0.5" />
          <div>
            <p className="text-sm text-gray-600 mb-1">Industry</p>
            <p className="text-base text-gray-900">Technology</p>
          </div>
        </div>
      </div>
    </Card>
  );
}
