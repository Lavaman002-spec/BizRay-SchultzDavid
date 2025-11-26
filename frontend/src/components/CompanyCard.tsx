import { Card } from '@/components/ui/card';
import { CompanyWithDetails } from '@/types/company';
import Link from 'next/link';
import { MapPin } from 'lucide-react';

interface CompanyCardProps {
  company: CompanyWithDetails;
  riskScore?: number;
  riskLevel?: 'Low Risk' | 'Medium Risk' | 'High Risk';
  address?: string;
}
export default function CompanyCard({ company }: CompanyCardProps) {
  // get employee count
  const employeeCount = company.officers?.length;

  const primaryAddress = company.addresses?.[0];
  const addressString = primaryAddress
    ? [primaryAddress.street, primaryAddress.house_number, primaryAddress.city]
        .filter(Boolean)
        .join(' ')
    : null;

  // get company activity
  const companyIndustry = company.activities
    ?.map((activity) => activity.description)
    .join(', ');

  return (
    <Link key={company.id} href={`/company/${company.id}`}>
      <Card className="bg-white border border-[#e9eaeb] p-6 rounded-2xl hover:shadow-md transition-all hover:border-zinc-300 cursor-pointer flex flex-col gap-6">
        {/* Header: Company Name & Badge */}
        <div className="flex gap-8 items-start w-full">
          <div className="flex-1 flex flex-col gap-0.5 min-w-0">
            <h3 className="font-semibold text-base leading-6 text-[#101828] tracking-[-0.3125px]">
              {company.name}
            </h3>
            <p className="font-normal text-sm leading-5 text-[#6a7282] tracking-[-0.1504px]">
              FN {company.fnr}
            </p>
          </div>
          {company.legal_form && (
            <div className="bg-white border border-[#e9eaeb] rounded px-2 py-0.5 shrink-0">
              <p className="font-medium text-xs leading-4 text-[#101828] whitespace-nowrap">
                {company.legal_form.charAt(0).toUpperCase() +
                  company.legal_form.slice(1)}
              </p>
            </div>
          )}
        </div>

        {/* Address */}
        <div className="flex gap-1 items-start">
          <MapPin className="w-4 h-4 text-[#4a5565] " />

          <p className="text-sm text-gray-600 mb-1"></p>
          {addressString ? (
            <>
              <p className="text-sm text-gray-600 mb-1">
                {primaryAddress?.street} {primaryAddress?.house_number}
              </p>
              <p className="text-sm text-gray-600 mb-1">
                {primaryAddress?.city}
              </p>
            </>
          ) : (
            <p className="text-sm text-gray-600 mb-1">Not available</p>
          )}
        </div>

        {/* Stats Grid */}
        <div className="flex gap-4 items-center pt-6 border-t border-[#e9eaeb] w-full">
          <div className="flex-1 flex flex-col gap-1 min-w-0">
            <p className="font-normal text-xs leading-4 text-[#6a7282]">
              Employees
            </p>
            <p className="font-normal text-sm leading-5 text-[#101828] tracking-[-0.1504px]">
              {employeeCount || 'N/A'}
            </p>
          </div>

          {/* <div className="flex-1 flex flex-col gap-1 min-w-0">
            <p className="font-normal text-xs leading-4 text-[#6a7282]">
              Industry
            </p>
            <p className="font-normal text-sm leading-5 text-[#101828] tracking-[-0.1504px] truncate">
              {companyIndustry || 'N/A'}
            </p>
          </div> */}
          <div className="flex-1 flex flex-col gap-1 min-w-0">
            <p className="font-normal text-xs leading-4 text-[#6a7282]">
              Revenue
            </p>
            <p className="font-normal text-sm leading-5 text-[#101828] tracking-[-0.1504px] truncate">
              {company.revenue || 'N/A'}
            </p>
          </div>
        </div>
      </Card>
    </Link>
  );
}
