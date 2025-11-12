'use client';

import * as React from 'react';
import Link from 'next/link';
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
} from '@/components/ui/navigation-menu';
import Image from 'next/image';
import { Button } from '../ui/button';

export default function AppNav() {
  return (
    <header className="fixed w-dvw z-10 bg-zinc-100 border-b border-zinc-200">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <div className="flex gap-4">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold">
            <Image
              src="/company-logo.svg"
              width={100}
              height={48}
              alt="Company Logo"
            />
          </Link>
          {/* Nav Menu */}
          <div className="flex gap-2">
            <NavigationMenu className="list-none">
              <NavigationMenuItem>
                <NavigationMenuLink asChild>
                  <Link href="/dashboard">Dashboard</Link>
                </NavigationMenuLink>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <NavigationMenuLink asChild>
                  <Link href="/explore">Explore</Link>
                </NavigationMenuLink>
              </NavigationMenuItem>
              <NavigationMenuItem>
                <NavigationMenuLink asChild>
                  <Link href="/settings">Settings</Link>
                </NavigationMenuLink>
              </NavigationMenuItem>
            </NavigationMenu>
          </div>
        </div>

        {/* CTAs */}
        <div className="flex gap-2">
          <Button variant={'secondary'}>Log In</Button>
          <Button>Create Account</Button>
        </div>
      </div>
    </header>
  );
}
