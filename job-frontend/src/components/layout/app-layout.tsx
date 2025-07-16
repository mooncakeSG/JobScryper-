"use client";

import { useUser } from "@/context/UserContext";
import Link from "next/link";
import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Menu, User, Home, Upload, Search, BarChart3, Settings } from "lucide-react";

const navigation = [
  { name: "Dashboard", href: "/", icon: Home },
  { name: "Upload Resume", href: "/upload", icon: Upload },
  { name: "Job Matching", href: "/match", icon: Search },
  { name: "Analytics", href: "/analytics", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading, logout } = useUser();

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="fixed inset-0 bg-black opacity-30" onClick={() => setSidebarOpen(false)} />
          <div className="relative w-64 bg-white shadow-lg z-50">
            <div className="flex flex-col h-full">
              <div className="flex items-center justify-between p-4">
                <h1 className="text-xl font-bold text-blue-600">{process.env.NEXT_PUBLIC_APP_NAME}</h1>
                <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(false)}>
                  <Menu className="h-5 w-5" />
                </Button>
              </div>
              <nav className="flex-1 px-2 py-4">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`block px-4 py-2 rounded-md mb-2 ${pathname === item.href ? "bg-blue-100 text-blue-700" : "text-gray-700 hover:bg-gray-100"}`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <item.icon className="inline-block mr-2 h-5 w-5 align-text-bottom" />
                    {item.name}
                  </Link>
                ))}
              </nav>
            </div>
          </div>
        </div>
      )}

      {/* Top nav */}
      <div className="flex items-center justify-between p-4 bg-white shadow-sm lg:hidden">
        <Button variant="ghost" size="icon" onClick={() => setSidebarOpen(true)}>
          <Menu className="h-5 w-5" />
        </Button>
        <h1 className="text-xl font-bold text-blue-600">{process.env.NEXT_PUBLIC_APP_NAME}</h1>
        {user ? (
          <Button variant="ghost" size="icon" onClick={logout} title="Logout">
            <User className="h-5 w-5" />
          </Button>
        ) : (
          <Button variant="ghost" size="icon" onClick={() => router.push("/login")} title="Login">
            <User className="h-5 w-5" />
          </Button>
        )}
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-72 lg:flex-col">
        <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-sm">
          <div className="flex h-16 shrink-0 items-center">
            <h1 className="text-2xl font-bold text-blue-600">{process.env.NEXT_PUBLIC_APP_NAME}</h1>
          </div>
          <nav className="flex flex-1 flex-col">
            <ul role="list" className="flex flex-1 flex-col gap-y-7">
              <li>
                <ul role="list" className="-mx-2 space-y-1">
                  {navigation.map((item) => (
                    <li key={item.name}>
                      <Link
                        href={item.href}
                        className={`group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold ${pathname === item.href ? "bg-blue-50 text-blue-600" : "text-gray-700 hover:text-blue-600 hover:bg-gray-50"}`}
                        aria-current={pathname === item.href ? "page" : undefined}
                      >
                        <item.icon className="h-6 w-6 shrink-0" aria-hidden="true" />
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

      {/* Main content */}
      <div className="lg:pl-72">
        {/* Desktop header/navbar */}
        <div className="hidden lg:flex lg:h-16 lg:shrink-0 lg:items-center lg:justify-between lg:px-6 lg:bg-white lg:shadow-sm">
          <div className="flex items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              {navigation.find((item) => item.href === pathname)?.name || "Dashboard"}
            </h2>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-gray-700 font-medium">{user.username}</span>
                <Button variant="ghost" size="icon" onClick={logout} title="Logout">
                  <User className="h-5 w-5" />
                </Button>
              </>
            ) : (
              <Button variant="ghost" size="icon" onClick={() => router.push("/login")} title="Login">
                <User className="h-5 w-5" />
              </Button>
            )}
          </div>
        </div>
        <main id="main-content" className="py-6">
          <div className="px-4 sm:px-6 lg:px-8">{children}</div>
        </main>
      </div>
    </div>
  );
} 