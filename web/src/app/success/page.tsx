import { Badge } from "@/components/ui/badge";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { CheckCircle2Icon } from "lucide-react";
import Image from "next/image";

export default async function Success({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const url = (await searchParams).url;

  return (
    <div className="flex flex-col py-12 h-screen">
      <h1 className="flex items-center gap-x-2 text-3xl font-black mb-8 -ml-2">
        <Image src="/headphone.png" width={64} height={64} alt="Adible logo" />
        Adible
      </h1>
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink href="/">Home</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          <BreadcrumbItem>
            <BreadcrumbPage>
              <Badge>{url}</Badge>
            </BreadcrumbPage>
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>

      <div className="flex flex-col items-center justify-center h-full space-y-4">
        <CheckCircle2Icon size={64} className="text-green-500" />
        <span className="text-lg font-bold">Success!</span>
        <p className="text-muted-foreground">
          Your ads have been successfully submitted to our collection.
        </p>
      </div>
    </div>
  );
}
