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
import io

from domain.advertisement import AdvertisementDb
from voices import AVAILABLE_VOICES

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
)

class Advertisement(BaseModel):
    id: str
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
    determined_advertisement: AdvertisementDb

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
    3. Do not restrict to a single language in a multiple language audio recording.


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
        ad_id = placement.find('advertisement').get('id')

        transcription_segment = transcription_segments[segment_no]
        determined_advertisement = next(ad for ad in available_ads if ad.id == ad_id)

        ad_placements.append(AdvertisementPlacement(
            transcription_segment=transcription_segment,
            determined_advertisement=determined_advertisement
        ))

    return ad_placements


def determine_ad_placement(transcription_segments: list[TranscriptionSegment], available_ads: list[Advertisement]) -> List[AdvertisementPlacement]:
    print("Determining ad placement...")
    print(f"Total transcription segments: {len(transcription_segments)}")
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
Considering how much everything else has gone up over the last few years<break time="0.1s" /> like haircuts I guess we shouldn't be too surprised even if it is a tough pill to swallow like today's segue to our sponsor,<break time="0.1s" /> The Big Thunder Game.. (advertisement content here)
</segue>
<content>
The Big Thunder Game brings an exciting new way to play MMORPGs with friends regardless of their ability to play.
</content>
<exit>
(add some context here that continues to the next segment),<break time="0.2s" /> now back to the show.
</exit>
</advertisement>
<advertisement>
<segue>
if you're planning your next PC build<break time="0.1s" /> then consider checking out our sponsor VIP SCD key
</segue>
<content>
Their Windows 10 and 11 OEM Keys sell for a fraction of retail <break time="0.1s" /> and will unlock the full potential of your OS it'll also remove.. (more content here)
</content>
<exit>
use VIP SCD key on your next PC build <break time="0.2s" /> and now lets get back to this PC.
</exit>
</advertisement>
<advertisement>
<segue>
क्या आप रचनात्मकता और मज़े की तलाश में हैं? <break time="0.1s" /> तो आइए जानते हैं हमारे प्रायोजक LEGO के बारे में
</segue>
<content>
LEGO के नए साहसिक सेट्स के साथ अपनी कल्पना को उड़ान दें। <break time="0.1s" /> हर सेट में उच्च गुणवत्ता वाले ब्रिक्स, विस्तृत निर्देश पुस्तिका, और असीमित रचनात्मक संभावनाएं हैं। चाहे आप शुरुआती बिल्डर हों या अनुभवी LEGO प्रेमी, हमारे पास हर कौशल स्तर के लिए सेट हैं। इस महीने के विशेष ऑफर में सभी LEGO सिटी और LEGO टेकनिक सेट्स पर 20% की छूट पाएं। साथ ही, <break time="0.1s" /> VIP सदस्यों के लिए अतिरिक्त बोनस प्वाइंट्स!
</content>
<exit>
LEGO के साथ अपनी रचनात्मक यात्रा शुरू करें,<break time="0.1s" /> और अब वापस लौटते हैं हमारी मुख्य कहानी की ओर।
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
5. Try to match the language used by the segments.

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

def determine_optimal_voice_id(advertisement_text: str, transcription_segments: list[TranscriptionSegment], ad_placement: AdvertisementPlacement) -> str:
    voices_xml = "\n".join([
        f"<voice id='{voice.id}'>"
        f"<description>{voice.description}</description>"
        f"<language>{voice.language}</language>"
        f"</voice>"
    for voice in AVAILABLE_VOICES])

    surrounding_segments: list[TranscriptionSegment] = []
    segment_nos = {segment.no: segment for segment in transcription_segments}

    for offset in [-2, -1, 0, 1, 2]:
        target_no = ad_placement.transcription_segment.no + offset
        if target_no in segment_nos:
            surrounding_segments.append(segment_nos[target_no])

    surrounding_segments_xml = "\n".join([
        f"<transcription_segment no='{segment.no}'>"
        f"<text>{segment.text}</text>"
        f"</transcription_segment>"
    for segment in surrounding_segments])

    prompt = f"""You are a marketing expert agent. You know your way around selecting the right voice for an advertisement.
You will be given an advertisement text, the surrounding segments of the audio recording, and the advertisement placement.
Your job is to select the optimal voice for the advertisement.

Here are the surrounding segments of the audio recording:
<surrounding_segments>
{surrounding_segments_xml}
</surrounding_segments>

Here is the advertisement text:
<advertisement_text>
{advertisement_text}
</advertisement_text>

The available voices are:
<available_voices>
{voices_xml}
</available_voices>

Please follow the below rules when selecting the voice:
1. The voice should match the tone of the surrounding segments.
2. The conversation pace should be optimal for the selected voice.
3. The voice should be able to speak the advertisement text naturally.
4. When no voice is a good fit, return the voice with id 'default'.

Please respond in the format provided between the <example></example> tags.
<example>
<response>
<voice_determination>
<thinking>
This conversation seems to be between two people, they seem to be interested in an sports car.
Both people interested seem to be males in their 30s.
</thinking>
<voice id='voice id'/> <!-- The voice that should be used for the advertisement -->
</voice_determination>
</response>
</example>
"""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}, {"role": "assistant", "content": "<response>"}],
        stop=["</response>"]
    )

    try:
        xml_response = response.choices[0].message.content
        print(f"LLM Response for determining optimal voice:\n{xml_response}")
        root = ET.fromstring(f"<response>{xml_response}</response>")
        voice_element = root.find('.//voice')
        voice_id = voice_element.get('id') if voice_element is not None else "default"
    except Exception as e:
        print(f"Error parsing voice determination response: {e}")
        voice_id = "default"
    return voice_id
    

def generate_advertisement_audio(advertisement_text: str, voice_id: str = "UgBBYS2sOqTuMpoF3BR0", file_path: str = None) -> str:
    elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio_response = elevenlabs_client.text_to_speech.convert(
        text=advertisement_text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )
    
    save_file_path = f"{uuid.uuid4()}.mp3"
    if file_path:
        save_file_path = file_path
    
    with open(save_file_path, "wb") as f:
        for chunk in audio_response:
            if chunk:
                f.write(chunk)
    
    print(f"Audio file saved at {save_file_path}")
    
    return save_file_path


def insert_advertisement_audio(original_audio_bytes: bytes, ad_audio_bytes: bytes, segment_after: TranscriptionSegment, output_path: str = None) -> str:
    print(f"Inserting ad after segment ending at {segment_after.end} seconds")
    
    original_audio = AudioSegment.from_file(io.BytesIO(original_audio_bytes))
    ad_audio = AudioSegment.from_file(io.BytesIO(ad_audio_bytes))
    
    insert_point_ms = int(segment_after.end * 1000)
    
    first_part = original_audio[:insert_point_ms]
    second_part = original_audio[insert_point_ms:]
    final_audio = first_part + ad_audio + second_part
    
    if not output_path:
        output_path = f"output_{uuid.uuid4()}.mp3"
    
    final_audio.export(output_path, format="mp3")
    print(f"Combined audio saved to {output_path}")
    
    return output_path

def generate_ad_audio_with_nearby_audio(generated_ad_bytes: bytes, transcription_segment: TranscriptionSegment, original_audio_bytes: bytes) -> bytes:
    original_audio = AudioSegment.from_file(io.BytesIO(original_audio_bytes))
    ad_audio = AudioSegment.from_file(io.BytesIO(generated_ad_bytes))

    start_ms = max(0, int((transcription_segment.start - 5) * 1000))  # 5 sec before
    end_ms = int((transcription_segment.end + 10) * 1000)  # 10 sec after
    insert_point_ms = int(transcription_segment.end * 1000)

    before_segment = original_audio[start_ms:insert_point_ms]
    after_segment = original_audio[insert_point_ms:end_ms]
    final_audio = before_segment + ad_audio + after_segment

    buffer = io.BytesIO()
    final_audio.export(buffer, format="mp3")
    return buffer.getvalue()