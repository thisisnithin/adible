"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

export const Poll = () => {
  const id = useSearchParams().get("id");

  const [processingStatus, setProcessingStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const interval = setInterval(async () => {
      try {
        const response = await fetch(
          `http://localhost:4001/stitched-audio/${id}`
        );
        const data = await response.json();
        setProcessingStatus(data.processing_status);

        if (data.processing_status === "COMPLETE") {
          clearInterval(interval);
        }
      } catch (error) {
        console.error("Error fetching processing status:", error);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [id]);

  return (
    <div className="flex flex-col items-center justify-center w-full">
      {processingStatus !== "COMPLETE" ? (
        <div className="flex items-center justify-center h-full">
          <p className="text-2xl">{processingStatus}</p>
        </div>
      ) : (
        <audio
          className="w-full"
          controls
          src={`http://localhost:4001/stitched-audio/${id}/bytes`}
        />
      )}
    </div>
  );
};
