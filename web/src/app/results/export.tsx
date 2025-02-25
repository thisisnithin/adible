"use client";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Tag, TagInput } from "@/components/ui/tag-input/tag-input";
import { zodResolver } from "@hookform/resolvers/zod";
import React from "react";
import { useForm } from "react-hook-form";
import { useReadLocalStorage } from "usehooks-ts";
import { z } from "zod";
import { crawlForAds } from "../crawl";
import { exportAds } from "./export-ads";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { useParams, useSearchParams } from "next/navigation";

const FormSchema = z.object({
  topics: z
    .array(
      z.object({
        id: z.string(),
        text: z.string(),
      })
    )
    .min(1),
});

export default function Export() {
  const result =
    useReadLocalStorage<Awaited<ReturnType<typeof crawlForAds>>>("result");

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });

  const [tags, setTags] = React.useState<Tag[]>([]);
  const [activeTagIndex, setActiveTagIndex] = React.useState<number | null>(
    null
  );

  const { setValue } = form;

  const [loading, setLoading] = React.useState(false);
  const router = useRouter();
  const params = useSearchParams();
  const url = params.get("url");

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    setLoading(true);
    try {
      const tags = data.topics.map((topic) => topic.text);
      await exportAds(result!, tags);
      router.push(`/success?url=${url}`);
    } catch (error) {
      toast.error("Failed to export ads");
    }
    setLoading(false);
  }

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="space-y-8 flex flex-col items-start"
      >
        <FormField
          control={form.control}
          name="topics"
          render={({ field }) => (
            <FormItem className="flex flex-col items-start w-full">
              <FormLabel className="text-left">Topics</FormLabel>
              <FormControl>
                <TagInput
                  {...field}
                  placeholder="Enter topics"
                  tags={tags}
                  styleClasses={{
                    inlineTagsContainer: "h-12",
                  }}
                  setTags={(newTags) => {
                    setTags(newTags);
                    setValue("topics", newTags as [Tag, ...Tag[]]);
                  }}
                  activeTagIndex={activeTagIndex}
                  setActiveTagIndex={setActiveTagIndex}
                  delimiterList={[" ", ",", "Enter"]}
                />
              </FormControl>
              <FormDescription className="text-left">
                These are the topics where your ads will be placed.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button disabled={tags.length === 0 || loading} type="submit">
          Submit
        </Button>
      </form>
    </Form>
  );
}
