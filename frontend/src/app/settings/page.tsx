'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { toast } from 'sonner';

import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/context/AuthContext';
import { supabase } from '@/lib/supabase';

export default function SettingsPage() {
  const { user, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  useEffect(() => {
    if (user?.email) {
      setEmail(user.email);
    }
  }, [user?.email]);

  const disableEmailSubmit = useMemo(() => {
    return !email || email === user?.email || emailLoading;
  }, [email, user?.email, emailLoading]);

  const handleEmailUpdate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!user) {
      toast.error('Please sign in to update your email');
      return;
    }
    if (!email || email === user.email) {
      toast.info('Email unchanged');
      return;
    }

    setEmailLoading(true);
    try {
      const { error } = await supabase.auth.updateUser({ email });
      if (error) {
        throw error;
      }
      toast.success(
        "Check your inbox to verify the change. We'll switch emails once you confirm."
      );
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unable to update email';
      toast.error(message);
    } finally {
      setEmailLoading(false);
    }
  };

  const handlePasswordReset = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!user) {
      toast.error('Please sign in to reset your password');
      return;
    }
    if (!newPassword || !confirmPassword) {
      toast.error('Enter and confirm your new password');
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setPasswordLoading(true);
    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      });
      if (error) {
        throw error;
      }
      toast.success('Password updated');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Unable to reset password';
      toast.error(message);
    } finally {
      setPasswordLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto max-w-2xl py-24">
        <Card className="p-8 text-center text-muted-foreground">
          Loading your settings…
        </Card>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container mx-auto max-w-2xl py-24">
        <Card className="p-10 text-center space-y-4">
          <div className="space-y-1">
            <h1 className="text-3xl font-semibold">Settings</h1>
            <p className="text-muted-foreground">
              Sign in to manage your account email and password.
            </p>
          </div>
          <Link href="/login">
            <Button>Go to login</Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-3xl py-24 space-y-8">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold tracking-tight">Account settings</h1>
        <p className="text-muted-foreground">
          Update your contact email and keep your password secure.
        </p>
      </div>

      <Card className="p-6 md:p-8 space-y-6">
        <div>
          <h2 className="text-xl font-semibold">Contact email</h2>
          <p className="text-sm text-muted-foreground">
            We use this email for alerts and login. Changing it requires
            confirming a verification link that we send to the new address.
          </p>
        </div>
        <form onSubmit={handleEmailUpdate} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email address</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Current: {user.email ?? '—'}</span>
            {user.email && user.email !== email && <span>Pending change</span>}
          </div>
          <Button type="submit" disabled={disableEmailSubmit}>
            {emailLoading ? 'Sending confirmation…' : 'Update email'}
          </Button>
        </form>
      </Card>

      <Card className="p-6 md:p-8 space-y-6">
        <div>
          <h2 className="text-xl font-semibold">Reset password</h2>
          <p className="text-sm text-muted-foreground">
            Set a new password any time. You will stay signed in on this device
            after the change.
          </p>
        </div>
        <form onSubmit={handlePasswordReset} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="new-password">New password</Label>
            <Input
              id="new-password"
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              minLength={8}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm-password">Confirm password</Label>
            <Input
              id="confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              minLength={8}
              required
            />
          </div>
          <Button type="submit" disabled={passwordLoading}>
            {passwordLoading ? 'Updating…' : 'Reset password'}
          </Button>
        </form>
      </Card>
    </div>
  );
}
