"use client";

import { Filter } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import type { NetworkFilters as NetworkFiltersType } from "./types";

interface NetworkFiltersProps {
  filters: NetworkFiltersType;
  onChange: (filters: NetworkFiltersType) => void;
}

export default function NetworkFilters({ filters, onChange }: NetworkFiltersProps) {
  const handleConnectionTypeChange = (type: 'ownership' | 'management', checked: boolean) => {
    onChange({
      ...filters,
      connectionTypes: {
        ...filters.connectionTypes,
        [type]: checked
      }
    });
  };

  const handleHopDistanceChange = (value: number[]) => {
    onChange({
      ...filters,
      hopDistance: value[0]
    });
  };

  const handleRiskLevelChange = (level: 'low' | 'medium' | 'high', checked: boolean) => {
    onChange({
      ...filters,
      riskLevels: {
        ...filters.riskLevels,
        [level]: checked
      }
    });
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-6 w-80">
      <div className="flex items-center gap-2 mb-6">
        <Filter className="w-5 h-5 text-gray-600" />
        <h3 className="text-base font-semibold text-gray-900">Graph Filters</h3>
      </div>

      {/* Connection Type */}
      <div className="mb-6">
        <label className="text-sm text-gray-700 mb-3 block">Connection Type</label>
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Checkbox
              id="ownership"
              checked={filters.connectionTypes.ownership}
              onCheckedChange={(checked) => handleConnectionTypeChange('ownership', checked as boolean)}
              className="border-gray-300"
            />
            <label htmlFor="ownership" className="text-sm text-gray-600 cursor-pointer">
              Ownership
            </label>
          </div>

          <div className="flex items-center gap-2">
            <Checkbox
              id="management"
              checked={filters.connectionTypes.management}
              onCheckedChange={(checked) => handleConnectionTypeChange('management', checked as boolean)}
              className="border-gray-300"
            />
            <label htmlFor="management" className="text-sm text-gray-600 cursor-pointer">
              Management
            </label>
          </div>
        </div>
      </div>

      {/* Hop Distance */}
      <div className="mb-6">
        <label className="text-sm text-gray-700 mb-3 block">
          Hop Distance: {filters.hopDistance}
        </label>
        <Slider
          value={[filters.hopDistance]}
          onValueChange={handleHopDistanceChange}
          min={1}
          max={4}
          step={1}
          className="mb-2"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>1 hop</span>
          <span>4 hops</span>
        </div>
      </div>

      {/* Show Risk Level */}
      <div>
        <label className="text-sm text-gray-700 mb-3 block">Show Risk Level</label>
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Checkbox
              id="risk-low"
              checked={filters.riskLevels.low}
              onCheckedChange={(checked) => handleRiskLevelChange('low', checked as boolean)}
              className="border-gray-300"
            />
            <label htmlFor="risk-low" className="text-sm text-gray-600 cursor-pointer">
              Low (0-30)
            </label>
          </div>

          <div className="flex items-center gap-2">
            <Checkbox
              id="risk-medium"
              checked={filters.riskLevels.medium}
              onCheckedChange={(checked) => handleRiskLevelChange('medium', checked as boolean)}
              className="border-gray-300"
            />
            <label htmlFor="risk-medium" className="text-sm text-gray-600 cursor-pointer">
              Medium (30-70)
            </label>
          </div>

          <div className="flex items-center gap-2">
            <Checkbox
              id="risk-high"
              checked={filters.riskLevels.high}
              onCheckedChange={(checked) => handleRiskLevelChange('high', checked as boolean)}
              className="border-gray-300"
            />
            <label htmlFor="risk-high" className="text-sm text-gray-600 cursor-pointer">
              High (70-100)
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
