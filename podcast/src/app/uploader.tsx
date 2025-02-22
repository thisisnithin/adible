"use client";

import { useLocalStorage } from "usehooks-ts";
import { FileUpIcon } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useDropzone } from "react-dropzone";
import { GeneratedAd } from "@/lib/types";

const Uploader = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processId, setProcessId] = useState(0);

  const onDrop = async (acceptedFiles: File[]) => {
    setFiles(() => acceptedFiles);
    setIsUploading(true);

    const formData = new FormData();
    formData.append("file", acceptedFiles[0]);

    try {
      const res = await fetch("http://localhost:4001/upload-audio", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        throw new Error("Failed to upload file");
      }

      const data = await res.json();
      setIsUploading(false);
      setIsProcessing(true);
      setProcessId(data.id);
    } catch (error) {
      console.error("Error uploading file:", error);
      setIsUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/plain": [".mp3"],
    },
  });

  return (
    <div
      {...getRootProps()}
      className={`cursor-pointer rounded-md w-full border border-dashed border-border bg-background p-8 text-center transition-colors ${
        isDragActive ? "bg-primary/10" : "hover:border-primary/50"
      }`}
    >
      <input {...getInputProps()} />
      {isUploading && <p className="mt-2 text-sm">Uploading...</p>}{" "}
      {!isUploading && !isProcessing && (
        <>
          <FileUpIcon className="mx-auto h-8 w-8 stroke-1 text-muted-foreground" />
          <p className="mt-2 text-sm">Drag and drop podcast audio file here </p>
          <p className="mt-2 text-xs text-muted-foreground">
            Supported format .mp3
          </p>
        </>
      )}
      {isProcessing && <Process processId={processId} />}
    </div>
  );
};

const Process = ({ processId }: { processId: number }) => {
  const [status, setStatus] = useState("PENDING");
  const router = useRouter();

  const [, setValue] = useLocalStorage<GeneratedAd[] | undefined>(
    "generated_ads",
    undefined
  );

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(
          `http://localhost:4001/audio_files/${processId}`
        );
        if (!res.ok) {
          throw new Error("Failed to fetch processing status");
        }

        const data = await res.json();
        setStatus(data.processing_status);

        if (data.processing_status === "COMPLETE") {
          clearInterval(interval);
          setValue(data.generated_ads);
          router.push(`/generated?audioId=${processId}`);
        }
      } catch (error) {
        console.error("Error fetching processing status:", error);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [processId, router]);

  return <div>Processing status: {status}</div>;
};

export default Uploader;
