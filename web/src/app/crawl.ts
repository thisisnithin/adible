"use server";

import FirecrawlApp from "@mendable/firecrawl-js";
import { Mistral } from "@mistralai/mistralai";
import { ParsedChatCompletionResponse } from "@mistralai/mistralai/extra/structChat";
import { z } from "zod";

const extractads = async (pages: { url: string; markdown: string }[]) => {
  const client = new Mistral({ apiKey: process.env.MISTRAL_API_KEY! });
  const shape = z.object({
    title: z.string(),
    content: z.string(),
  });

  const ads = [];

  for (const page of pages) {
    const chatResponse: ParsedChatCompletionResponse<typeof shape> =
      await client.chat.parse({
        model: "ministral-8b-latest",
        messages: [
          {
            role: "user",
            content: page.markdown,
          },
          {
            role: "user",
            content:
              "Give me in detail 2 things in 2 paragraphs with title for each that can be advertised from the provided website content",
          },
        ],
        responseFormat: shape,
        maxTokens: 256,
        temperature: 0,
      });

    ads.push({
      url: page.url,
      ...chatResponse.choices![0].message!.parsed!,
    });
  }

  return ads;
};

const crawl = async (url: string) => {
  const app = new FirecrawlApp({ apiKey: process.env.FIRECRAWL_API_KEY! });

  const crawlResponse = await app.crawlUrl(url, {
    limit: 1,
    maxDepth: 1,
    ignoreSitemap: true,
    scrapeOptions: {
      formats: ["markdown", "html"],
    },
  });

  if (!crawlResponse.success) {
    throw new Error(`Failed to crawl: ${crawlResponse.error}`);
  }

  const pages = crawlResponse.data
    .filter((page) => !!page.metadata && !!page.markdown)
    .map((page) => {
      return {
        url: page.metadata!.sourceURL!,
        markdown: page.markdown!,
      };
    });

  return pages;
};

export const crawlForAds = async (url: string) => {
  try {
    const pages = await crawl(url);
    const ads = await extractads(pages);

    return ads;
  } catch (error) {
    console.error(error);
  }
};
