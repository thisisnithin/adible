"use client";

import { useReadLocalStorage } from "usehooks-ts";
import { crawlForAds } from "../crawl";
import { useEffect, useState } from "react";
import { ExternalLinkIcon } from "lucide-react";

export default function List() {
  const result =
    useReadLocalStorage<Awaited<ReturnType<typeof crawlForAds>>>("result");

  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return null;
  }

  if (!result) {
    return (
      <span className="flex items-center justify-center h-full">
        No results to show
      </span>
    );
  }

  return result.map((ad, index) => (
    <div key={index} className="p-4 border-b last:border-b-0">
      <h2 className="text-lg font-bold">{ad.title}</h2>
      <a
        href={ad.url}
        target="_blank"
        className="underline flex items-center gap-2 mb-6 text-muted-foreground"
      >
        {ad.url}
        <ExternalLinkIcon className="w-4 h-4" />
      </a>
      <p className="text-muted-foreground">{ad.content}</p>
    </div>
  ));
}
