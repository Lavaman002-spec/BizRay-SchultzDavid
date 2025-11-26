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

import { useAuth } from '@/context/AuthContext';
import { LogOut, User as UserIcon } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function AppNav() {
  const { user, signOut } = useAuth();

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
              {/* <NavigationMenuItem>
                <NavigationMenuLink asChild>
                  <Link href="/dashboard">Dashboard</Link>
                </NavigationMenuLink>
              </NavigationMenuItem> */}
              {/* <NavigationMenuItem>
                <NavigationMenuLink asChild>
                  <Link href="/explore">Explore</Link>
                </NavigationMenuLink>
              </NavigationMenuItem> */}
              {user && (
                <>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild>
                      <Link href="/watchlist">Watchlist</Link>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem>
                    <NavigationMenuLink asChild>
                      <Link href="/settings">Settings</Link>
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                </>
              )}
            </NavigationMenu>
          </div>
        </div>

        {/* CTAs */}
        <div className="flex gap-2">
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  <UserIcon />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">Account</p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => signOut()}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <>
              <Link href="/login">
                <Button variant={'secondary'}>Log In</Button>
              </Link>
              <Link href="/signup">
                <Button>Create Account</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
