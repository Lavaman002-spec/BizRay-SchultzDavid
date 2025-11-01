'use client';

import { useState, FormEvent } from 'react';
import { ArrowRightIcon } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface CompanySearchProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
  defaultLocation?: string;
}

export default function CompanySearch({
  onSearch,
  loading = false,
  placeholder = 'Search for a company...',
  defaultLocation = 'Wien',
}: CompanySearchProps) {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState(defaultLocation);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex flex-col bg-white rounded-2xl border border-zinc-200 overflow-hidden">
        {/* Search Input Row */}
        <div className="flex items-center gap-2 p-4">
          <div className="relative flex-1">
            <Input
              type="text"
              placeholder={placeholder}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="border-none shadow-none focus-visible:ring-0 text-base px-0"
              disabled={loading}
            />
          </div>

          {/* Location Select */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>in</span>
            <Select
              value={location}
              onValueChange={setLocation}
              disabled={loading}
            >
              <SelectTrigger className="w-40 h-8 border-gray-300">
                <SelectValue placeholder="Select city" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  <SelectItem value="Wien">Wien</SelectItem>
                  <SelectItem value="Graz">Graz</SelectItem>
                  <SelectItem value="Linz">Linz</SelectItem>
                  <SelectItem value="Salzburg">Salzburg</SelectItem>
                  <SelectItem value="Innsbruck">Innsbruck</SelectItem>
                  <SelectItem value="Klagenfurt">Klagenfurt</SelectItem>
                  <SelectItem value="Villach">Villach</SelectItem>
                  <SelectItem value="Wels">Wels</SelectItem>
                  <SelectItem value="Sankt Pölten">Sankt Pölten</SelectItem>
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Submit Button Row */}
        <div className="w-full flex items-center justify-end px-4 pb-4">
          <Button
            type="submit"
            size="icon"
            disabled={loading || !query.trim()}
            className="rounded-lg w-10 h-10 bg-black hover:bg-gray-800 disabled:bg-gray-300"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <ArrowRightIcon className="w-5 h-5" />
            )}
          </Button>
        </div>
      </div>
    </form>
  );
}
