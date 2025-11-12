'use client';

import { useState, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { getCities } from '@/lib/api';

interface LocationDropdownProps {
  value: string;
  onValueChangeAction: (value: string) => void;
  disabled?: boolean;
}

export default function LocationDropdown({
  value,
  onValueChangeAction,
  disabled = false,
}: LocationDropdownProps) {
  const [cities, setCities] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCities = async () => {
      try {
        const fetchedCities = await getCities();
        setCities(fetchedCities);
      } catch (error) {
        console.error('Failed to fetch cities:', error);
        setCities([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCities();
  }, []);

  const selectedCity = value || 'All locations';

  return (
    <div className="flex items-center gap-2">
      <span className="text-base text-zinc-500">in</span>
      <DropdownMenu>
        <DropdownMenuTrigger
          disabled={disabled || loading}
          className="flex items-center gap-1 bg-white border border-zinc-200 rounded-md px-2 py-0.5 text-sm font-medium text-zinc-700 hover:bg-zinc-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Loading...' : selectedCity}
          <ChevronDown className="w-3 h-3 text-zinc-500" />
        </DropdownMenuTrigger>
        <DropdownMenuContent
          align="start"
          className="w-64 max-h-80 overflow-y-auto"
        >
          {/* All locations option */}
          <DropdownMenuItem
            onClick={() => onValueChangeAction('')}
            className={value === '' ? 'bg-zinc-100 font-medium' : ''}
          >
            All locations
          </DropdownMenuItem>

          {/* Separator */}
          {cities.length > 0 && <div className="h-px bg-zinc-200 my-1" />}

          {/* City options */}
          {cities.map((city) => (
            <DropdownMenuItem
              key={city}
              onClick={() => onValueChangeAction(city)}
              className={city === value ? 'bg-zinc-100 font-medium' : ''}
            >
              {city}
            </DropdownMenuItem>
          ))}

          {/* No cities message */}
          {!loading && cities.length === 0 && (
            <div className="px-2 py-4 text-sm text-zinc-500 text-center">
              No cities found
            </div>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
