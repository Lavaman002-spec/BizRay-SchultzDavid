import { Input } from '@/components/ui/input';
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuIndicator,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  NavigationMenuViewport,
} from '@/components/ui/navigation-menu';

export default function Home() {
  return (
    <div className="w-dvw h-dvh felx gap-6 p-6 ">
      <nav className="fixed m-0 w-dvw">
        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuTrigger>Businesses</NavigationMenuTrigger>
              {/* <NavigationMenuContent>
                <NavigationMenuLink>Link</NavigationMenuLink>
              </NavigationMenuContent> */}
            </NavigationMenuItem>
          </NavigationMenuList>
        </NavigationMenu>
      </nav>
      <main className="flex flex-col mt-[64px]">
        <div className="flex flex-col gap-[24px]">
          <h1 className="text-2xl"> Homepage</h1>
          <Input placeholder="Search for a business..." />
        </div>
      </main>
    </div>
  );
}
