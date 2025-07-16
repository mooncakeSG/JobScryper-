import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppLayout } from "@/components/layout/app-layout";
import { Toaster } from "@/components/ui/toaster";
import { SkipToMainContent } from "@/components/ui/accessibility";
import { UserProvider } from "@/context/UserContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "JobScryper - Modern Job Application Platform",
  description: "AI-powered job matching and resume optimization platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <SkipToMainContent />
        <UserProvider>
          <AppLayout>{children}</AppLayout>
        </UserProvider>
        <Toaster />
      </body>
    </html>
  );
}
