"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { GeneratedAd } from "@/lib/types";
import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";
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
  const [selectedAdId, setSelectedAdId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const audioId = useSearchParams().get("audioId");

  // Group ads by their title.
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

  // Set default selection to the first ad's id if available.
  useEffect(() => {
    if (result.length > 0 && !selectedAdId) {
      setSelectedAdId(result[0].id);
    }
  }, [result, selectedAdId]);

  if (!isClient) {
    return null;
  }

  const handleSubmit = async () => {
    const selectedAd = result.find((ad) => ad.id === selectedAdId);

    if (!selectedAd) {
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(
        "http://localhost:4001/insert-advertisement-audio",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            audio_file_id: audioId,
            generated_ad_id: selectedAdId,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        router.push(`/result?id=${data.id}`);
      } else {
        throw new Error("Failed to submit the advertisement audio");
      }
    } catch (error) {
      toast.error("Failed to submit the advertisement audio");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="h-full flex flex-col w-full mx-auto items-end justify-center overflow-auto">
        <ul className="w-full">
          {Object.entries(groupedAds).map(([title, ads]) => (
            <li
              key={title}
              className="p-4 border border-border rounded-md mb-4"
            >
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
                  <div key={ad.id} className="flex items-center space-x-4">
                    <input
                      type="radio"
                      name="selectedAd"
                      value={ad.id}
                      checked={selectedAdId === ad.id}
                      onChange={() => setSelectedAdId(ad.id)}
                    />
                    <AudioPlayer
                      src={`http://localhost:4001/generated-ad/${ad.id}`}
                    />
                  </div>
                ))}
              </div>
            </li>
          ))}
        </ul>
      </div>
      <Button disabled={loading} className="w-max" onClick={handleSubmit}>
        Submit
      </Button>
    </>
  );
};

export default GeneratedAdsList;
