import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { Toaster } from "@/components/ui/Toaster";
import { ReminderToastProvider } from "@/components/reminders/ReminderNotification";
import { ServiceWorkerListener } from "@/components/reminders/ServiceWorkerListener";
import { NotificationPermissionPrompt } from "@/components/reminders/PermissionPrompt";
import { WebVitalsReporter } from "@/components/performance/WebVitals";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Perpetua - AI-Powered Task Management",
  description: "Master your tasks with intelligent prioritization, streak tracking, and focus modes.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-50 dark:bg-gray-950`}
      >
        <Providers>
          <WebVitalsReporter />
          <ServiceWorkerListener />
          <NotificationPermissionPrompt />
          <ReminderToastProvider>
            {children}
            <Toaster />
          </ReminderToastProvider>
        </Providers>
      </body>
    </html>
  );
}
