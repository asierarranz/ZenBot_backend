import requests
import os
import random
from datetime import datetime
from pydub import AudioSegment
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys and settings
GPT_API_KEY = os.getenv('GPT_API_KEY')
ELEVEN_LABS_API_KEY = os.getenv('ELEVEN_LABS_API_KEY')
TEST_MODE = os.getenv('TEST_MODE', 'False').lower() in ('true', '1', 't')
CHUNK_SIZE = 1024

# Function to generate meditation script using OpenAI GPT-4
def generate_meditation_script(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GPT_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert in generating Yoga Nidra meditation scripts. Use your skills to create a very calm and tranquil script with many pauses and ellipses."
            },
            {
                "role": "user",
                "content": f"Generate a Yoga Nidra meditation based on the following: {prompt}. Return the meditation as a calm and tranquil script with many pauses, using ellipses. This script will be transcribed by an AI, so provide the script as the meditation guide would directly say it, with no intro or outro. Only include what the guide says from the beginning to the end of the meditation."
            }
        ]
    }
    print(f"Sending request to OpenAI with prompt: {prompt}")
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Received response from OpenAI")
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', '').strip()
    else:
        print(f"Failed to generate meditation script. Status code: {response.status_code}")
        print(f"Response content: {response.content}")
        return None

# Function to generate audio using Eleven Labs
def generate_audio(script, prompt):
    if TEST_MODE:
        script = script[:200]
        print("TEST_MODE is enabled. Truncated script to first 200 characters.")

    url = "https://api.elevenlabs.io/v1/text-to-speech/LcfcDJNUP1GQjkzn1xUU"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }
    data = {
        "text": script,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    print(f"Sending request to Eleven Labs with script: {script}")
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        first_words = "_".join(prompt.split()[:4])
        filename = f"meditation_{first_words}_{timestamp}.mp3" if first_words else f"meditation_{timestamp}.mp3"
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        audio_path = os.path.join(static_dir, filename)
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        print("Received response from Eleven Labs, writing audio to file")
        with open(audio_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        print(f"Audio file written to {audio_path}")

        # Mix with background music
        mixed_audio_path = mix_with_background_music(audio_path, static_dir, filename)
        return mixed_audio_path
    else:
        print(f"Failed to generate audio. Status code: {response.status_code}")
        print(f"Response content: {response.content}")
        return None

# Function to mix generated audio with background music
def mix_with_background_music(audio_path, output_dir, filename):
    # Load the generated audio and randomly select one of the background music files
    generated_audio = AudioSegment.from_file(audio_path)
    background_music_files = [f'genai_music{i}.mp3' for i in range(1, 6)]
    selected_music_file = random.choice(background_music_files)
    background_music_path = os.path.join(output_dir, selected_music_file)
    background_music = AudioSegment.from_file(background_music_path)

    # Set background music volume to 10%
    background_music = background_music - 20  # Reduces the volume by 20 dB (10% of original volume)

    # Loop the background music to match the length of the generated audio
    while len(background_music) < len(generated_audio):
        background_music += background_music

    # Trim the background music to match the length of the generated audio
    background_music = background_music[:len(generated_audio)]

    # Mix the audio
    mixed_audio = generated_audio.overlay(background_music)

    # Save the mixed audio
    mixed_audio_path = os.path.join(output_dir, f"mixed_{filename}")
    mixed_audio.export(mixed_audio_path, format="mp3")
    print(f"Mixed audio file saved to {mixed_audio_path}")

    return mixed_audio_path
