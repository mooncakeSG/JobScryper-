"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Sidebar, SidebarContent, SidebarProvider } from "@/components/ui/sidebar";
import { 
  Menu, 
  Upload, 
  Search, 
  BarChart3, 
  Settings, 
  User, 
  Home
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

interface AppLayoutProps {
  children: React.ReactNode;
}

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Upload Resume", href: "/upload", icon: Upload },
  { name: "Job Matching", href: "/match", icon: Search },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setIsLoggedIn(!!localStorage.getItem("token"));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsLoggedIn(false);
    router.push("/login");
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen bg-gray-50">
        {/* Mobile sidebar */}
        <div className="lg:hidden">
          <div className="flex items-center justify-between p-4 bg-white shadow-sm">
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSidebarOpen(!sidebarOpen)}
              >
                <Menu className="h-5 w-5" />
              </Button>
              <h1 className="text-xl font-bold text-blue-600">
                {process.env.NEXT_PUBLIC_APP_NAME}
              </h1>
            </div>
            {isLoggedIn ? (
              <Button variant="ghost" size="icon" onClick={handleLogout} title="Logout">
                <User className="h-5 w-5" />
              </Button>
            ) : (
              <Button variant="ghost" size="icon" onClick={() => router.push("/login")} title="Login">
                <User className="h-5 w-5" />
              </Button>
            )}
          </div>
        </div>

        <div className="flex">
          {/* Desktop sidebar */}
          <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
            <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-sm">
              <div className="flex h-16 shrink-0 items-center">
                <h1 className="text-2xl font-bold text-blue-600">
                  {process.env.NEXT_PUBLIC_APP_NAME}
                </h1>
              </div>
              <nav className="flex flex-1 flex-col">
                <ul role="list" className="flex flex-1 flex-col gap-y-7">
                  <li>
                    <ul role="list" className="-mx-2 space-y-1">
                      {navigation.map((item) => (
                        <li key={item.name}>
                          <Link
                            href={item.href}
                            className={cn(
                              pathname === item.href
                                ? "bg-blue-50 text-blue-600"
                                : "text-gray-700 hover:text-blue-600 hover:bg-gray-50",
                              "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                            )}
                            aria-current={pathname === item.href ? "page" : undefined}
                          >
                            <item.icon
                              className={cn(
                                pathname === item.href
                                  ? "text-blue-600"
                                  : "text-gray-400 group-hover:text-blue-600",
                                "h-6 w-6 shrink-0"
                              )}
                              aria-hidden="true"
                            />
                            {item.name}
                          </Link>
                        </li>
                      ))}
                    </ul>
                  </li>
                </ul>
              </nav>
            </div>
          </div>

          {/* Mobile sidebar */}
          {sidebarOpen && (
            <div className="lg:hidden">
              <div className="fixed inset-0 z-50 bg-gray-900/80" onClick={() => setSidebarOpen(false)} />
              <div className="fixed inset-y-0 left-0 z-50 w-72 bg-white px-6 pb-4 shadow-xl">
                <div className="flex h-16 shrink-0 items-center">
                  <h1 className="text-2xl font-bold text-blue-600">
                    {process.env.NEXT_PUBLIC_APP_NAME}
                  </h1>
                </div>
                <nav className="mt-5">
                  <ul role="list" className="space-y-1">
                    {navigation.map((item) => (
                                              <li key={item.name}>
                          <Link
                            href={item.href}
                            onClick={() => setSidebarOpen(false)}
                            className={cn(
                              pathname === item.href
                                ? "bg-blue-50 text-blue-600"
                                : "text-gray-700 hover:text-blue-600 hover:bg-gray-50",
                              "group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                            )}
                            aria-current={pathname === item.href ? "page" : undefined}
                          >
                            <item.icon
                              className={cn(
                                pathname === item.href
                                  ? "text-blue-600"
                                  : "text-gray-400 group-hover:text-blue-600",
                                "h-6 w-6 shrink-0"
                              )}
                              aria-hidden="true"
                            />
                            {item.name}
                          </Link>
                        </li>
                    ))}
                  </ul>
                </nav>
              </div>
            </div>
          )}

          {/* Main content */}
          <div className="lg:pl-72">
            <div className="hidden lg:flex lg:h-16 lg:shrink-0 lg:items-center lg:justify-between lg:px-6 lg:bg-white lg:shadow-sm">
              <div className="flex items-center">
                <h2 className="text-xl font-semibold text-gray-900">
                  {navigation.find((item) => item.href === pathname)?.name || "Dashboard"}
                </h2>
              </div>
              <div className="flex items-center space-x-4">
                {isLoggedIn ? (
                  <Button variant="ghost" size="icon" onClick={handleLogout} title="Logout">
                    <User className="h-5 w-5" />
                  </Button>
                ) : (
                  <Button variant="ghost" size="icon" onClick={() => router.push("/login")} title="Login">
                    <User className="h-5 w-5" />
                  </Button>
                )}
              </div>
            </div>

            {/* Page content */}
            <main id="main-content" className="py-6">
              <div className="px-4 sm:px-6 lg:px-8">
                {children}
              </div>
            </main>
          </div>
        </div>
      </div>
    </SidebarProvider>
  );
} 