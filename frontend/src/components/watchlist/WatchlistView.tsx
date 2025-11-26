'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { Bell, BellOff, Loader2, Mail, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';
import type { WatchlistEntry } from '@/types/company';
import {
  getWatchlistEntries,
  removeFromWatchlist,
  updateWatchlistPreferences,
} from '@/lib/api';

export default function WatchlistView() {
  const { session } = useAuth();
  const [entries, setEntries] = useState<WatchlistEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const accessToken = session?.access_token;

  const title = useMemo(
    () =>
      entries.length === 0
        ? 'No companies tracked yet'
        : `${entries.length} compan${
            entries.length === 1 ? 'y' : 'ies'
          } tracked`,
    [entries.length]
  );

  useEffect(() => {
    if (!accessToken) {
      setLoading(false);
      setEntries([]);
      return;
    }

    let isMounted = true;

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getWatchlistEntries(accessToken);
        if (isMounted) {
          setEntries(data);
        }
      } catch (err) {
        if (!isMounted) return;
        console.error(err);
        setError('Failed to load watchlist');
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    load();
    return () => {
      isMounted = false;
    };
  }, [accessToken]);

  const handleRemove = async (companyId: number) => {
    if (!accessToken) {
      toast.error('Please log in to manage your watchlist');
      return;
    }

    try {
      await removeFromWatchlist(companyId, accessToken);
      setEntries((prev) =>
        prev.filter((entry) => entry.company_id !== companyId)
      );
      toast.success('Removed from watchlist');
    } catch (err) {
      console.error(err);
      toast.error('Unable to remove company');
    }
  };

  const handleToggleNotifications = async (entry: WatchlistEntry) => {
    if (!accessToken) {
      toast.error('Please log in to update notifications');
      return;
    }

    const desired = !entry.notify_via_email;

    try {
      await updateWatchlistPreferences(entry.company_id, accessToken, {
        notify_via_email: desired,
      });
      setEntries((prev) =>
        prev.map((item) =>
          item.id === entry.id ? { ...item, notify_via_email: desired } : item
        )
      );
      toast.success(
        desired
          ? 'Email alerts enabled for this company'
          : 'Email alerts disabled'
      );
    } catch (err) {
      console.error(err);
      toast.error('Failed to update email alerts');
    }
  };

  if (!session) {
    return (
      <Card className="p-8">
        <h1 className="text-2xl font-semibold mb-2">Watchlist</h1>
        <p className="text-muted-foreground">
          Sign in to monitor companies and receive change alerts.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-semibold text-gray-900">Watchlist</h1>
        <p className="text-muted-foreground">{title}</p>
      </div>

      {loading && (
        <Card className="p-8 flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-gray-500" />
          <span className="text-sm text-gray-600">Loading companies…</span>
        </Card>
      )}

      {error && !loading && (
        <Card className="p-6 border-red-200 bg-red-50 text-red-700">
          {error}
        </Card>
      )}

      {!loading && entries.length === 0 && !error && (
        <Card className="p-8 flex flex-col items-center text-center gap-3">
          <Bell className="h-10 w-10 text-gray-400" />
          <p className="text-base text-gray-700">
            No companies here yet. Browse companies and tap “Watch” to follow
            updates.
          </p>
          <Link href="/explore">
            <Button variant="secondary">Discover companies</Button>
          </Link>
        </Card>
      )}

      {entries.length > 0 && (
        <div className="space-y-4">
          {entries.map((entry) => {
            const company = entry.company;
            return (
              <Card key={entry.id} className="p-6 flex flex-col gap-4">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <Link
                      href={`/company/${entry.company_id}`}
                      className="text-lg font-semibold text-gray-900 hover:underline"
                    >
                      {company?.name || 'Company record'}
                    </Link>
                    <p className="text-sm text-gray-500">
                      FN {company?.fnr ?? '—'} •{' '}
                      {company?.city ?? 'Unknown city'}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Watching since{' '}
                      {entry.created_at
                        ? new Date(entry.created_at).toLocaleDateString()
                        : '—'}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <Link href={`/company/${entry.company_id}`}>
                      <Button variant="outline">View</Button>
                    </Link>
                    <Button
                      variant="ghost"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => handleRemove(entry.company_id)}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Remove
                    </Button>
                  </div>
                </div>
                <div className="flex flex-wrap items-center gap-3 text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Mail className="h-4 w-4" />
                    <span>Email alerts:</span>
                    <strong>{entry.notify_via_email ? 'On' : 'Off'}</strong>
                  </div>
                  <Button
                    variant={entry.notify_via_email ? 'secondary' : 'outline'}
                    size="sm"
                    onClick={() => handleToggleNotifications(entry)}
                    className="flex items-center gap-2"
                  >
                    {entry.notify_via_email ? (
                      <BellOff className="h-4 w-4" />
                    ) : (
                      <Bell className="h-4 w-4" />
                    )}
                    {entry.notify_via_email
                      ? 'Disable alerts'
                      : 'Enable alerts'}
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
