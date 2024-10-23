import os
import sys
import time
import threading
import discord
import signal
import subprocess
import asyncio
import ffmpeg
import openai
import tiktoken
import torch
import whisper
from dotenv import load_dotenv

# Configuration
whisper_model = "turbo"
command_prompt = "Create clear and concise bullet points summarizing key information, with timestamps if possible."

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_KEY = os.getenv('OPEN_API_KEY')

# Set API keys
if OPENAI_API_KEY is None or DISCORD_TOKEN is None:
    print("Missing API keys in environment. Exiting...")
    sys.exit(1)

openai.api_key = OPENAI_API_KEY

# Discord client setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def join_and_record_voice_channel(guild_id, channel_id, output_filename):
    try:
        guild = client.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        if channel is None:
            print("Channel not found!")
            return

        # Connect to the voice channel
        voice_client = await channel.connect()

        print("Connected to voice channel. Recording...")
        record_audio(output_filename)

        await asyncio.sleep(10)  # Example duration, change as needed

        await voice_client.disconnect()
        print("Disconnected and recording stopped.")

    except Exception as e:
        print(f"Error during recording: {e}")

def record_audio(output_filename):
    try:
        stream = (
            ffmpeg
            .input("default", f="avfoundation", video_size=None)  # Cross-platform support: use 'default'
            .output(output_filename, acodec="libmp3lame", format="mp3")
            .overwrite_output()
        )

        process = ffmpeg.run_async(stream, pipe_stdin=True, pipe_stderr=True)

        print("Recording started. Press Ctrl+C to stop.")
        process.wait()
    except Exception as e:
        print(f"Error recording audio: {e}")

def transcribe_audio(filename):
    devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(whisper_model, device=devices)

    audio = whisper.load_audio(filename)

    print("Beginning transcription...")
    result = model.transcribe(audio, verbose=False, fp16=False, task="translate")

    return result['text']

def summarize_transcript(transcript):
    def generate_summary(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes text to small paragraphs"},
                {"role": "user", "content": f"{command_prompt}: {prompt}"}
            ],
            temperature=0.5,
        )
        return response.choices[0].message['content'].strip()

    chunks = []
    prompt = "Please summarize the following text:\n\n"
    text = prompt + transcript
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    while tokens:
        chunk_tokens = tokens[:2000]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
        tokens = tokens[2000:]

    summary = "\n".join([generate_summary(chunk) for chunk in chunks])

    return summary

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: python {sys.argv[0]} [record|summarize] output.mp3 guild_id channel_id")
        sys.exit(1)

    action = sys.argv[1]
    output_filename = sys.argv[2]
    guild_id = int(sys.argv[3])
    channel_id = int(sys.argv[4])

    if action == "record":
        client.loop.create_task(join_and_record_voice_channel(guild_id, channel_id, output_filename))
        client.run(DISCORD_TOKEN)
    elif action == "summarize":
        transcript = transcribe_audio(output_filename)
        summary = summarize_transcript(transcript)
        print(f"TRANSCRIPT:\n{transcript}\n")
        print(f"SUMMARY:\n{summary}\n")
    else:
        print(f"Invalid action. Usage: python {sys.argv[0]} [record|summarize] output.mp3 guild_id channel_id")
        sys.exit(1)
