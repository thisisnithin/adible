"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowRight, GlobeIcon, LoaderIcon } from "lucide-react";
import { useState } from "react";
import { crawlForAds } from "./crawl";
import { toast } from "sonner";
import { useLocalStorage } from "usehooks-ts";
import { useRouter } from "next/navigation";

const LinkInput = () => {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [, setValue] = useLocalStorage<Awaited<ReturnType<typeof crawlForAds>>>(
    "result",
    undefined
  );

  const router = useRouter();

  const handleCrawl = async () => {
    setLoading(true);
    try {
      const ads = await crawlForAds(url);
      setValue(ads);
      router.push(`/results?url=${url}`);
    } catch (error) {
      toast.error("Failed to crawl website");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative w-full max-w-md">
      <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
        <GlobeIcon className="w-5 h-5 text-gray-400" />
      </div>
      <Input
        type="text"
        placeholder="Enter your website to get started"
        className="pl-10 pr-10"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      {!loading ? (
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="absolute inset-y-0 right-0 flex items-center"
          disabled={!url}
          onClick={() => handleCrawl()}
        >
          <ArrowRight className="w-5 h-5" />
          <span className="sr-only">Search</span>
        </Button>
      ) : (
        <LoaderIcon className="absolute inset-y-2 right-2 w-5 h-5 animate-spin text-gray-400" />
      )}
    </div>
  );
};

export default LinkInput;
