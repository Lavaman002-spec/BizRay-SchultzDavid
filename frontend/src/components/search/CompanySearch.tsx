'use client';

import { useState, FormEvent, useEffect, useRef } from 'react';
import { ArrowRightIcon, XIcon } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import LocationDropdown from '@/components/commons/LocationDropdown';
import { searchCompanies, getCompanySuggestions } from '@/lib/api';
import type { Company } from '@/types/company';

interface CompanySearchProps {
  onResults?: (companies: Company[], total: number) => void;
  onClear?: () => void;
  loading?: boolean;
  placeholder?: string;
}

export default function CompanySearch({
  onResults,
  // onClear,
  loading = false,
  placeholder = 'Search by company name or FN number...',
}: CompanySearchProps) {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!query.trim()) {
      setError('Please enter a search term');
      return;
    }

    setIsSearching(true);
    setError(null);

    try {
      const response = await searchCompanies(query, 50, 0, location);
      onResults?.(response.results, response.total);
    } catch (err) {
      // Parse error and show user-friendly message
      let errorMessage = 'Failed to search companies';

      if (err instanceof Error) {
        const message = err.message.toLowerCase();

        if (
          message.includes('state does not exist') ||
          message.includes('column')
        ) {
          errorMessage =
            'Search is temporarily unavailable. Please try again later or contact support.';
        } else if (message.includes('network') || message.includes('fetch')) {
          errorMessage =
            'Unable to connect to the server. Please check your internet connection.';
        } else if (message.includes('timeout')) {
          errorMessage = 'Search is taking too long. Please try again.';
        } else {
          errorMessage = 'Something went wrong. Please try again.';
        }
      }

      setError(errorMessage);
      onResults?.([], 0);
    } finally {
      setIsSearching(false);
    }
  };

  const handleClearInput = () => {
    setQuery('');
    setError(null);
    setSuggestions([]);
    setShowSuggestions(false);
  };

  // Fetch suggestions as user types (with debounce)
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.trim().length < 2) {
        setSuggestions([]);
        setShowSuggestions(false);
        return;
      }

      try {
        const results = await getCompanySuggestions(query, 10);
        setSuggestions(results);
        setShowSuggestions(results.length > 0);
      } catch (err) {
        console.error('Failed to fetch suggestions:', err);
        setSuggestions([]);
      }
    };

    // Debounce the suggestions fetch
    const timeoutId = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    setSelectedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) =>
        prev < suggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      handleSuggestionClick(suggestions[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
      setSelectedIndex(-1);
    }
  };

  const isLoading = loading || isSearching;

  return (
    <div className="w-full flex flex-col gap-3">
      <div className="relative w-full">
        <form onSubmit={handleSubmit} className="w-full">
          <div
            ref={containerRef}
            className="flex flex-col bg-white rounded-2xl border border-zinc-200 overflow-hidden"
          >
            {/* Search Input Row */}
            <div className="flex items-center gap-2 p-4">
              <div className="relative flex-1">
                <Input
                  ref={inputRef}
                  type="text"
                  placeholder={placeholder}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={handleKeyDown}
                  onFocus={() => {
                    if (suggestions.length > 0) setShowSuggestions(true);
                  }}
                  className="border-none shadow-none focus-visible:ring-0 text-base px-0 pr-8"
                  disabled={isLoading}
                  autoComplete="off"
                />
                {query && !isLoading && (
                  <button
                    type="button"
                    onClick={handleClearInput}
                    className="absolute right-0 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 rounded-full transition-colors"
                    aria-label="Clear input"
                  >
                    <XIcon className="w-4 h-4 text-gray-500" />
                  </button>
                )}
              </div>
            </div>

            {/* Location Selector and Submit Button Row */}
            <div className="w-full flex items-center justify-between px-4 pb-4">
              <div className="flex items-center gap-4 flex-1">
                <LocationDropdown
                  value={location}
                  onValueChangeAction={setLocation}
                  disabled={isLoading}
                />
              </div>
              <div>
                <Button
                  type="submit"
                  size="icon"
                  disabled={isLoading || !query.trim()}
                  className="rounded-lg w-10 h-10 bg-black hover:bg-gray-800 disabled:bg-gray-300"
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <ArrowRightIcon className="w-5 h-5" />
                  )}
                </Button>
              </div>
            </div>
          </div>
        </form>

        {/* Suggestions Dropdown - Outside search container */}
        {showSuggestions && suggestions.length > 0 && (
          <div
            ref={suggestionsRef}
            className="absolute left-0 right-0 top-full mt-4 bg-white border border-zinc-200 rounded-2xl shadow-lg max-h-64 overflow-y-auto z-50"
            style={{ width: containerRef.current?.offsetWidth }}
          >
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                onClick={() => handleSuggestionClick(suggestion)}
                className={`w-full text-left px-4 py-3 text-sm hover:bg-zinc-50 transition-colors border-b border-zinc-100 last:border-b-0 first:rounded-t-2xl last:rounded-b-2xl ${
                  index === selectedIndex ? 'bg-zinc-100' : ''
                }`}
              >
                <span className="text-zinc-900 font-medium">{suggestion}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Error Message Card */}
      {error && (
        <div className="w-full bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <svg
            className="w-5 h-5 text-red-600 mt-0.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <div className="flex-1">
            <p className="text-sm font-medium text-red-800">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
}
