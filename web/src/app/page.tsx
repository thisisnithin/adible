import Image from "next/image";
import LinkInput from "./link-input";

export default function Home() {
  return (
    <div className="h-screen flex flex-col items-center justify-center">
      <Image src="/headphone.png" width={200} height={200} alt="Adible logo" />
      <h1 className="text-4xl font-black mb-2">Adible</h1>
      <p className="text-muted-foreground mb-6">
        The advertisement database for all forms of audio content
      </p>
      <LinkInput />
    </div>
  );
}
