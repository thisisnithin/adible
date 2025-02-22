import Image from "next/image";
import GeneratedAdsList from "./list";

export default function Generated() {
  return (
    <div className="flex flex-col py-12 h-screen">
      <h1 className="flex items-center gap-x-2 text-3xl font-black mb-8 -ml-2">
        <Image src="/headphone.png" width={64} height={64} alt="Adible logo" />
        Adible Podcasts
      </h1>
      <GeneratedAdsList />
    </div>
  );
}
