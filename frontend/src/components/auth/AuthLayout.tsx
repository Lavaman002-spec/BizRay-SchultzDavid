import Link from "next/link";
import Image from "next/image";

interface AuthLayoutProps {
    children: React.ReactNode;
    title: string;
    description: string;
    footerText: string;
    footerLinkText: string;
    footerLinkHref: string;
}

export function AuthLayout({
    children,
    title,
    description,
    footerText,
    footerLinkText,
    footerLinkHref,
}: AuthLayoutProps) {
    return (
        <div className="w-full lg:grid lg:min-h-screen lg:grid-cols-2">
            <div className="flex items-center justify-center py-12">
                <div className="mx-auto grid w-[350px] gap-6">
                    <div className="grid gap-2 text-center">
                        <h1 className="text-3xl font-bold">{title}</h1>
                        <p className="text-balance text-muted-foreground">
                            {description}
                        </p>
                    </div>
                    {children}
                    <div className="mt-4 text-center text-sm">
                        {footerText}{" "}
                        <Link href={footerLinkHref} className="underline">
                            {footerLinkText}
                        </Link>
                    </div>
                </div>
            </div>
            <div className="hidden bg-muted lg:block relative">
                {/* Placeholder for the image/branding section */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-900 flex items-center justify-center text-white p-10">
                    <div className="max-w-md space-y-4">
                        <h2 className="text-4xl font-bold">BizRay</h2>
                        <p className="text-lg opacity-90">Discover and analyze business networks with ease.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
