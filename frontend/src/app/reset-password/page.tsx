'use client';

import { FormEvent, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

import { useAuth } from '@/context/AuthContext';
import { supabase } from '@/lib/supabase';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';

export default function ResetPasswordPage() {
  const { session, loading } = useAuth();
  const router = useRouter();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!session) {
      toast.error('Open the reset link from your email first.');
      return;
    }
    if (!password || !confirmPassword) {
      toast.error('Enter and confirm your new password');
      return;
    }
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setSubmitting(true);
    try {
      const { error } = await supabase.auth.updateUser({ password });
      if (error) throw error;
      toast.success('Password updated. Please log in again.');
      router.push('/login');
    } catch (error: unknown) {
      const message =
        error instanceof Error ? error.message : 'Unable to reset password';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto max-w-lg py-24">
        <Card className="p-8 text-center text-muted-foreground">
          Checking your reset link…
        </Card>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="container mx-auto max-w-lg py-24">
        <Card className="p-8 space-y-4 text-center">
          <div className="space-y-1">
            <h1 className="text-2xl font-semibold">Reset password</h1>
            <p className="text-muted-foreground">
              Use the reset link in your inbox to open this page with a valid
              session, then choose a new password.
            </p>
          </div>
          <Link href="/login">
            <Button variant="outline">Back to login</Button>
          </Link>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-lg py-24">
      <Card className="p-8 space-y-6">
        <div className="space-y-2">
          <h1 className="text-3xl font-semibold">Choose a new password</h1>
          <p className="text-muted-foreground">
            Enter a new password for {session.user?.email ?? 'your account'}.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="password">New password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              minLength={8}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm">Confirm password</Label>
            <Input
              id="confirm"
              type="password"
              value={confirmPassword}
              minLength={8}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
            />
          </div>
          <Button type="submit" className="w-full" disabled={submitting}>
            {submitting ? 'Updating…' : 'Update password'}
          </Button>
        </form>
      </Card>
    </div>
  );
}
