"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowRight, GlobeIcon, LoaderIcon } from "lucide-react";
import { useState } from "react";
import { crawlForAds } from "./crawl";
import { toast } from "sonner";
import { useLocalStorage } from "usehooks-ts";
import { useRouter } from "next/navigation";
import { TextLoop } from "@/components/ui/text-loop";

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
    <form
      onSubmit={(e) => {
        e.preventDefault();
        handleCrawl();
      }}
      className="relative w-full max-w-xl"
    >
      <div className="absolute top-2 left-0 flex items-center pl-3 pointer-events-none">
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
          type="submit"
          variant="ghost"
          size="icon"
          className="absolute inset-y-0 right-0 flex items-center"
          disabled={!url}
        >
          <ArrowRight className="w-5 h-5" />
          <span className="sr-only">Search</span>
        </Button>
      ) : (
        <LoaderIcon className="absolute top-2 right-2 w-5 h-5 animate-spin text-gray-400" />
      )}
      {loading && (
        <TextLoop
          interval={4}
          transition={{
            duration: 0.5,
          }}
          className="text-sm mt-4 mx-auto w-full text-center text-muted-foreground"
        >
          <span>Crawling website...</span>
          <span>Fetching page content...</span>
          <span>Extracting markdown...</span>
          <span>Parsing HTML structure...</span>
          <span>Analyzing site metadata...</span>
          <span>Scraping internal links...</span>
          <span>Compiling page data...</span>
          <span>Processing page data...</span>
          <span>Generating ad suggestions...</span>
          <span>Processing ad copy...</span>
          <span>Validating results...</span>
          <span>Aggregating ad ideas...</span>
          <span>Optimizing crawl data...</span>
        </TextLoop>
      )}
    </form>
  );
};

export default LinkInput;
