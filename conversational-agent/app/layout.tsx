import type { Metadata } from "next";
import "./globals.css";
import { BackgroundWave } from "@/components/background-wave";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Adible Agent",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={"h-full w-full"}>
      <body className={`antialiased w-full h-full lex flex-col`}>
        <div className="flex flex-col flex-grow w-full items-center justify-center sm:px-4">
          <nav
            className={
              "sm:fixed w-full top-0 left-0 grid grid-cols-2 py-4 px-8"
            }
          >
            <div className="text-xl font-bold">Adible</div>
          </nav>
          {children}
          <BackgroundWave />
        </div>
      </body>
    </html>
  );
}
