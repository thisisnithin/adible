import LinkInput from "./link-input";

export default function Home() {
  return (
    <div className="h-screen flex flex-col items-center justify-center">
      <h1 className="text-4xl font-bold mb-2">Adible</h1>
      <p className="text-lg text-muted-foreground mb-6">
        The audio ad database for your favourite podcasts, blogs, and more.
      </p>
      <LinkInput />
    </div>
  );
}
