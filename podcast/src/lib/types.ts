export type GeneratedAd = {
  id: string;
  segue: string;
  content: string;
  exit: string;
  transcription_segment_id: string;
  advertisement: {
    id: string;
    url: string;
    title: string;
    content: string;
    tags: string[];
  };
};
