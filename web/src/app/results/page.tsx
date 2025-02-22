import { Badge } from "@/components/ui/badge";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import Export from "./export";
import List from "./list";
import Image from "next/image";

export default async function Results({
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

      <div className="border w-full h-full my-12 overflow-auto">
        <List />
      </div>
      <Export />
    </div>
  );
}
