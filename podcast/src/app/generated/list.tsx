"use client";

import { Badge } from "@/components/ui/badge";
import { GeneratedAd } from "@/lib/types";
import { useEffect, useState } from "react";
import { useReadLocalStorage } from "usehooks-ts";

const AudioPlayer = ({ src }: { src: string }) => {
  return (
    <audio controls className="w-full">
      <source src={src} type="audio/mpeg" />
      Your browser does not support the audio element.
    </audio>
  );
};

const GeneratedAdsList = () => {
  const result = useReadLocalStorage<GeneratedAd[]>("generated_ads") || [];
  const [isClient, setIsClient] = useState(false);

  const groupedAds = result.reduce((acc, ad) => {
    const title = ad.advertisement.title;
    if (!acc[title]) {
      acc[title] = [];
    }
    acc[title].push(ad);
    return acc;
  }, {} as Record<string, GeneratedAd[]>);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return null;
  }

  return (
    <div className="h-full flex w-full mx-auto items-center justify-center overflow-auto">
      <ul className="w-full">
        {Object.entries(groupedAds).map(([title, ads]) => (
          <li key={title} className="p-4 border border-border rounded-md mb-4">
            <h2 className="text-xl font-bold">{title}</h2>
            <div className="mt-2">
              {ads[0].advertisement.tags.map((tag) => (
                <Badge key={tag} className="mr-2">
                  {tag}
                </Badge>
              ))}
            </div>
            <div className="mt-4 space-y-4">
              {ads.map((ad) => (
                <AudioPlayer
                  src={`http://localhost:4001/generated-ad/${ad.id}`}
                />
              ))}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default GeneratedAdsList;
