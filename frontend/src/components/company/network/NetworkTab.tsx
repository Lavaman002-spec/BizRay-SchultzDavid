"use client";

import type { CompanyWithDetails } from "@/types/company";
import NetworkVisualization from "./NetworkVisualization";

interface NetworkTabProps {
  company: CompanyWithDetails;
}

export default function NetworkTab({ company }: NetworkTabProps) {
  return <NetworkVisualization company={company} />;
}
