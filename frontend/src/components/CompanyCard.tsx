import { Card } from '@/components/ui/card';
import { Company, CompanyWithDetails } from '@/types/company';
import Link from 'next/link';
import { MapPin, Info } from 'lucide-react';

interface CompanyCardProps {
  company: Company | CompanyWithDetails;
  riskScore?: number;
  riskLevel?: 'Low Risk' | 'Medium Risk' | 'High Risk';
  address?: string;
}
export default function CompanyCard({
  // riskScore,
  // riskLevel,
  company,
  address,
}: CompanyCardProps) {
  const {
    id: companyId,
    fnr: companyFnr,
    name: companyName,
    state: companyState,
  } = company;

  // get employee count
  const employeeCount = (company as CompanyWithDetails).officers?.length;

  // get company activity
  const companyIndustry = (company as CompanyWithDetails).activities
    ?.map((activity) => activity.description)
    .join(', ');

  // get address
  const primaryAddress = (company as CompanyWithDetails).addresses?.find(
    (addr) => addr.is_active
  );
  const displayAddress = address || (primaryAddress
    ? `${primaryAddress.street} ${primaryAddress.house_number}, ${primaryAddress.postal_code} ${primaryAddress.city}`
    : undefined);

  return (
    <Link key={companyId} href={`/company/${companyId}`}>
      <Card className="bg-white border border-[#e9eaeb] p-6 rounded-2xl hover:shadow-md transition-all hover:border-zinc-300 cursor-pointer flex flex-col gap-6">
        {/* Header: Company Name & Badge */}
        <div className="flex gap-8 items-start w-full">
          <div className="flex-1 flex flex-col gap-0.5 min-w-0">
            <h3 className="font-semibold text-base leading-6 text-[#101828] tracking-[-0.3125px]">
              {companyName}
            </h3>
            <p className="font-normal text-sm leading-5 text-[#6a7282] tracking-[-0.1504px]">
              FN {companyFnr}
            </p>
          </div>
          {companyState && (
            <div className="bg-white border border-[#e9eaeb] rounded px-2 py-0.5 shrink-0">
              <p className="font-medium text-xs leading-4 text-[#101828] whitespace-nowrap">
                {companyState.charAt(0).toUpperCase() + companyState.slice(1)}
              </p>
            </div>
          )}
        </div>

        {/* Address */}
        <div className="flex gap-2 items-start">
          <MapPin className="w-4 h-4 text-[#4a5565] shrink-0 mt-0.5" />
          <p className="font-normal text-sm leading-5 text-[#4a5565] tracking-[-0.1504px]">
            {displayAddress || 'Address not available'}
          </p>
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

          <div className="flex-1 flex flex-col gap-1 min-w-0">
            <p className="font-normal text-xs leading-4 text-[#6a7282]">
              Description
            </p>
            <p className="font-normal text-sm leading-5 text-[#101828] tracking-[-0.1504px] truncate">
              {companyIndustry || 'N/A'}
            </p>
          </div>
        </div>

        {/* Risk Score */}
        {/* {(riskScore !== undefined || riskLevel) && (
          <div className="flex items-center justify-between w-full">
            <div className="flex gap-2 items-center">
              <Info className="w-4 h-4 text-[#4a5565]" />
              <p className="font-normal text-sm leading-5 text-[#4a5565] tracking-[-0.1504px]">
                Risk Score
              </p>
            </div>
            <div className="flex gap-2 items-center">
              {riskScore !== undefined && (
                <p className="font-semibold text-sm leading-5 text-[#101828] tracking-[-0.1504px]">
                  {riskScore}
                </p>
              )}
              {riskLevel && (
                <div className="bg-white border border-[#e9eaeb] rounded px-1.5 py-0.5">
                  <p className="font-medium text-xs leading-4 text-[#101828] whitespace-nowrap">
                    {riskLevel}
                  </p>
                </div>
              )}
            </div>
          </div>
        )} */}
      </Card>
    </Link>
  );
}
