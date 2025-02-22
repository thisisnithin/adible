import os
import csv
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from pydub import AudioSegment
import json
from elevenlabs.client import ElevenLabs
import xml.etree.ElementTree as ET
import uuid

from pydub.playback import play as play_audio

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
)

class Advertisement(BaseModel):
    id: int
    url: str
    title: str
    content: str
    tags: list[str]

class TranscriptionSegment(BaseModel):
    no: int
    start: float
    end: float
    text: str

class AdvertisementPlacement(BaseModel):
    transcription_segment: TranscriptionSegment
    determined_advertisement: Advertisement

class GeneratedAdvertisementText(BaseModel):
    segue: str
    content: str
    exit: str

def transcribe_audio_with_timestamps(file_path: str) -> list[TranscriptionSegment]:
    print(f"Starting transcription for file: {file_path}")
    audio = AudioSegment.from_file(file_path)
    
    snippet_duration = 2 * 60 * 1000
    print(f"Processing audio in {snippet_duration/1000} second segments")
    
    transcription_segments = []
    total_time_processed = 0  # Initialize total time processed
    
    for i in range(0, len(audio), snippet_duration):
        print(f"Processing segment {i // snippet_duration + 1}")
        snippet = audio[i:i + snippet_duration]
        
        snippet_file_path = f"temp_snippet_{i // snippet_duration}.mp3"
        snippet.export(snippet_file_path, format="mp3")
        print(f"Exported snippet to {snippet_file_path}")

        segments_created = 0
        
        with open(snippet_file_path, 'rb') as audio_file:
            print("Sending snippet to OpenAI for transcription...")
            transcription_verbose = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"]
            )
        
        for idx, t_segment in enumerate(transcription_verbose.segments):
            start_time = total_time_processed + t_segment.start
            end_time = total_time_processed + t_segment.end
            print(f"Segment from {start_time} to {end_time}: {t_segment.text}")

            transcription_segments.append(TranscriptionSegment(
                no=segments_created + idx,
                start=start_time,
                end=end_time,
                text=t_segment.text
            ))

        segments_created += len(transcription_verbose.segments)
        
        total_time_processed += len(snippet) / 1000
        print(f"Total time processed: {total_time_processed} seconds")  # Print total time processed in seconds

    print("Transcription complete!")
    return transcription_segments


def _load_tsv_as_advertisements(file_path: str) -> List[Advertisement]:

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        ads = [
            Advertisement(
                id=idx,
                url=row['URL'],
                title=row['Title'],
                content=row['Content'],
                tags=row['Tags'].split(',')
            )
            for idx, row in enumerate(reader)
        ]
    return ads

def _determine_ad_placement(transcription_segments: list[TranscriptionSegment], available_ads: list[Advertisement]) -> List[AdvertisementPlacement]:

    transcription_segment_xml = "\n".join([
        f"<transcription_segment no='{segment.no}'>"
        f"<start>{segment.start}</start>"
        f"<end>{segment.end}</end>"
        f"<text>{segment.text}</text>"
        f"</transcription_segment>"
    for segment in transcription_segments])

    available_ad_xml = "\n".join([
        f"<advertisement id='{ad.id}'>"
        f"<url>{ad.url}</url>"
        f"<title>{ad.title}</title>"
        f"<content>{ad.content}</content>"
        f"<tags>{','.join(ad.tags)}</tags>"
        f"</advertisement>"
    for ad in available_ads])

    prompt = f"""You are a natural advertisment placement expert. You will be working with the transcript of a audio recording which might be a podcast, youtube video, or any other recorded audio.
    You will be given the transcript of a audio recording and a list of advertisements that can be placed in the audio recording.
    Your job is to determine the transcription segments along with the advertisement that should be placed in the audio recording.

    Please respond in the format provided between the <example></example> tags.
    <example>
    <response>
    <possible_ad_placements>
    <placement>
    <transcription_segment no='segment number'/> <!-- The segment after which the advertisement should be placed -->
    <advertisement id='advertisement id'/> <!-- The advertisement that should be placed -->
    </placement>
    </possible_ad_placements>
    </response>
    </example>

    Please focus on following the following rules:
    1. You need to determine what ad can be placed in after a segment such that it is a part of the conversation.
    2. If no natural placement is found, then return an empty <possible_ad_placements> tag.


    Here is the transcription of the audio recording:
    <transcription_segments>
    {transcription_segment_xml}
    </transcription_segments>

    Here is the list of advertisements that can be placed in the audio recording:
    <advertisements>
    {available_ad_xml}
    </advertisements>
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}, {"role": "assistant", "content": "<response>"}],
        stop=["</response>"]
    )

    xml_response = response.choices[0].message.content
    print(f"LLM Response for determining ad placement:\n{xml_response}")
    root = ET.fromstring(xml_response)

    ad_placements = []
    for placement in root.findall('.//placement'):
        segment_no = int(placement.find('transcription_segment').get('no'))
        ad_id = int(placement.find('advertisement').get('id'))

        transcription_segment = transcription_segments[segment_no]
        determined_advertisement = next(ad for ad in available_ads if ad.id == ad_id)

        ad_placements.append(AdvertisementPlacement(
            transcription_segment=transcription_segment,
            determined_advertisement=determined_advertisement
        ))

    return ad_placements


def determine_ad_placement(transcription_segments: list[TranscriptionSegment]) -> List[AdvertisementPlacement]:
    print("Determining ad placement...")
    print(f"Total transcription segments: {len(transcription_segments)}")

    available_ads = _load_tsv_as_advertisements("target_ads.tsv")

    print(f"Total available ads: {len(available_ads)}")

    ad_placements = _determine_ad_placement(transcription_segments, available_ads)

    return ad_placements

def generate_audio_ad_placement(transcription_segments: list[TranscriptionSegment], filtered_ad_keywords: list[str]):
    target_ads = _load_tsv_as_advertisements("target_ads.tsv")
    
    filtered_ads = [
        ad for ad in target_ads
        if any(keyword in ad.tags for keyword in filtered_ad_keywords)
    ]

    first_matching_ad = filtered_ads[0] if filtered_ads else None
    if not first_matching_ad:
        raise ValueError("No matching ads found")
    
    pass


def load_transcription_segments(transcription_state_path: str) -> List[TranscriptionSegment]:
    with open(transcription_state_path) as f:
        data = json.load(f)
    
    segments = []
    for segment in data["transcriptions"]["segments"]:
        segments.append(TranscriptionSegment(
            no=segment["no"],
            start=segment["start"],
            end=segment["end"], 
            text=segment["text"]
        ))
    return segments

def parse_advertisement_xml(xml_content: str) -> List[GeneratedAdvertisementText]:
    root = ET.fromstring(xml_content)
    advertisements = []

    for ad in root.findall('.//advertisement'):
        segue = ad.find('segue').text
        content = ad.find('content').text
        exit = ad.find('exit').text
        advertisements.append(GeneratedAdvertisementText(segue=segue, content=content, exit=exit))

    return advertisements

def _generate_advertisement_text(ad_placement: AdvertisementPlacement, surrounding_segments: list[TranscriptionSegment]) -> List[GeneratedAdvertisementText]:

    ad_placement_xml = f"""
<advertisement_placement>
    <transcription_segment no='{ad_placement.transcription_segment.no}'>
        <text>{ad_placement.transcription_segment.text}</text>
    </transcription_segment>
    <advertisement>
        <title>{ad_placement.determined_advertisement.title}</title>
        <content>{ad_placement.determined_advertisement.content}</content>
    </advertisement>
</advertisement_placement>
"""
    
    surrounding_segments_xml = "\n".join([
        f"<transcription_segment no='{segment.no}'>"
        f"<text>{segment.text}</text>"
        f"</transcription_segment>"
    for segment in surrounding_segments])


    prompt = f"""
You are a natural performance marketing expert. You know you way around the ad placment space. The finesse you have with ad placement is such that you can fit any advertisement into a segment of a podcast, youtube video, or any other recorded audio.
You will be given the advertisement placement and the surrounding segments of the audio recording.
Your job is to finnse the advertisement placement such that it is a part of the conversation and is not intrusive.

Here are some examples of how you can finnse the advertisement placement:
<examples>
<advertisement>
<segue>
Considering how much everything else has gone up over the last few years like haircuts I guess we shouldn't be too surprised even if it is a tough pill to swallow like today's segue to our sponsor, The Big Thunder Game.. (advertisement content here)
</segue>
<content>
The Big Thunder Game brings an exciting new way to play MMORPGs with friends regardless of their ability to play.
</content>
<exit>
(add some context here that continues to the next segment), now back to the show.
</exit>
</advertisement>
<advertisement>
<segue>
if you're planning your next PC build then consider checking out our sponsor VIP SCD key
</segue>
<content>
Their Windows 10 and 11 OEM Keys sell for a fraction of retail and will unlock the full potential of your OS it'll also remove.. (more content here)
</content>
<exit>
use VIP SCD key on your next PC build and now lets get back to this PC.
</exit>
</advertisement>
</examples>

Here is the advertisement placement:
<advertisement_placement>
    {ad_placement_xml}
</advertisement_placement>

Here are the surrounding segments of the audio recording:
<surrounding_segments>
{surrounding_segments_xml}
</surrounding_segments>

Please follow the below rules when generating the advertisements:
1. The advertisement should be a part of the conversation and not intrusive.
2. The advertisement content should be very short and to the point.
3. The ending of the advertisement should be a segue back to the show.
4. Always provide three variations of the same advertisement.

Please respond in the format provided between the <example></example> tags.
<example>
<response>
<advertisements>
<advertisement>
<segue>
finnse your way here
</segue>
<content>
keep it short and concise
</content>
<exit>
the exit of the content
</exit>
</advertisement>
</advertisements>
</response>
</example>
"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}, {"role": "assistant", "content": "<response>"}],
        stop=["</response>"]
    )

    return parse_advertisement_xml(response.choices[0].message.content)
    

def generate_advertisements(ad_placement: AdvertisementPlacement, transcription_segments: list[TranscriptionSegment]) -> List[GeneratedAdvertisementText]:  
    surrounding_segments = []
    segment_nos = {segment.no: segment for segment in transcription_segments}

    for offset in [-2, -1, 1, 2]:
        target_no = ad_placement.transcription_segment.no + offset
        if target_no in segment_nos:
            surrounding_segments.append(segment_nos[target_no])

    advertisement_texts = _generate_advertisement_text(ad_placement, surrounding_segments)

    return advertisement_texts

def generate_advertisement_audio(advertisement_text: str) -> str:
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio_response = elevenlabs_client.text_to_speech.convert(
        text=advertisement_text,
        voice_id="JBFqnCBsd6RMkjVDRZzb",
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )
    
    save_file_path = f"{uuid.uuid4()}.mp3"
    
    with open(save_file_path, "wb") as f:
        for chunk in audio_response:
            if chunk:
                f.write(chunk)
    
    print(f"Audio file saved at {save_file_path}")
    
    return save_file_path

# Transcription
# transcribe_audio_with_timestamps("/Users/pradyumnarahulk/Downloads/demo/rogan_chess_preparation_w_magnus.mp3", str(uuid4()))

# Determine Ad Placement
# EXPERIMENTAL
# transcription_segments = load_transcription_segments("transcription_state.json")
# ad_placements = determine_ad_placement(transcription_segments)

# print(f"Possible Ad Placements: {ad_placements}")

# generated_advertisement_texts = generate_advertisements(ad_placements[0], transcription_segments)
# print(f"Generated Advertisement Texts: {generated_advertisement_texts}")

# advertisement_audio_path = generate_advertisement_audio(generated_advertisement_texts[0].segue + " " + generated_advertisement_texts[0].content + " " + generated_advertisement_texts[0].exit)


# EXPERIMENTAL TESTING
# target_segment = ad_placements[0].transcription_segment
# starting_segment = None
# for segment in transcription_segments:
#     if segment.no == target_segment.no - 2:
#         starting_segment = segment
#         break

# next_segment = None
# for segment in transcription_segments:
#     if segment.no == target_segment.no + 1:
#         next_segment = segment
#         break

# original_audio = AudioSegment.from_file("/Users/pradyumnarahulk/Downloads/demo/rogan_chess_preparation_w_magnus.mp3")

# start_time_ms = starting_segment.start * 1000
# end_time_ms = target_segment.end * 1000
# play_audio(original_audio[start_time_ms:end_time_ms])

# ad_audio = AudioSegment.from_file(advertisement_audio_path)
# play_audio(ad_audio)

# next_start_time_ms = next_segment.start * 1000
# play_audio(original_audio[next_start_time_ms:])