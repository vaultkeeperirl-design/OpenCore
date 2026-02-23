import type { Metadata } from "next";
import { Orbitron, Share_Tech_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";

const orbitron = Orbitron({
  variable: "--font-orbitron",
  subsets: ["latin"],
  weight: ["400", "500", "700", "900"],
});

const shareTechMono = Share_Tech_Mono({
  variable: "--font-share-tech-mono",
  weight: "400",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "OpenCore | Neural OS",
  description: "Advanced Multi-Agent System Interface",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${orbitron.variable} ${shareTechMono.variable}`}>
      <body className="antialiased bg-[#050510] text-white font-mono">
        {children}
        <Toaster theme="dark" position="top-right" />
      </body>
    </html>
  );
}
