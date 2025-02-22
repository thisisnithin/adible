"use client";

import { useReadLocalStorage } from "usehooks-ts";
import { crawlForAds } from "../crawl";
import { useEffect, useState } from "react";

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
    <div key={index} className="p-4 border-b last:border-b-0 space-y-6">
      <h2 className="text-lg font-bold">{ad.title}</h2>
      <a href={ad.url} target="_blank" className="underline">
        {ad.url}
      </a>
      <p className="text-muted-foreground">{ad.content}</p>
    </div>
  ));
}
