"use client";

import type { CompanyWithDetails } from "@/types/company";
import NetworkGraph from "@/components/NetworkGraph";

interface NetworkTabProps {
  company: CompanyWithDetails;
}

export default function NetworkTab({ company }: NetworkTabProps) {
  return <NetworkGraph companyId={company.id} />;
}
