import os
import sys
import signal
import platform
import ffmpeg
import openai
import tiktoken
import torch
import whisper
from dotenv import load_dotenv

# Configuration
whisper_model = "base"
command_prompt = "Create clear and concise bullet points summarizing key information, with timestamps if possible."

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")

# Set API keys
if OPENAI_API_KEY is None:
    print("Missing OpenAI API key in environment. Exiting...")
    sys.exit(1)

openai.api_key = OPENAI_API_KEY


def get_ffmpeg_input_source():
    """Determines the appropriate input source for FFmpeg based on the operating system."""
    if platform.system() == "Windows":
        return "audio=Stereo Mix"  # Adjust this if Stereo Mix is not available
    elif platform.system() == "Darwin":  # macOS
        return "default"
    elif platform.system() == "Linux":
        return "default"
    else:
        print("Unsupported operating system.")
        sys.exit(1)


def record_audio(output_filename):
    try:
        input_source = get_ffmpeg_input_source()

        stream = (
            ffmpeg.input(
                input_source,
                f=(
                    "dshow"
                    if platform.system() == "Windows"
                    else "pulse" if platform.system() == "Linux" else "avfoundation"
                ),
            )
            .output(output_filename, acodec="libmp3lame", format="mp3")
            .overwrite_output()
        )

        process = ffmpeg.run_async(stream, pipe_stdin=True, pipe_stderr=True)

        print("Recording started. Press Ctrl+C to stop.")
        try:
            process.wait()
        except KeyboardInterrupt:
            os.kill(process.pid, signal.SIGINT)
            print("\nRecording stopped.")
            process.wait()
    except Exception as e:
        print(f"Error recording audio: {e}")


def transcribe_audio(filename):
    devices = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model(whisper_model, device=devices)

    audio = whisper.load_audio(filename)

    print("Beginning transcription...")
    result = model.transcribe(audio, verbose=False, fp16=False)

    return result["text"]


def summarize_transcript(transcript):
    def generate_summary(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes text to small paragraphs",
                },
                {"role": "user", "content": f"{command_prompt}: {prompt}"},
            ],
            temperature=0.5,
        )
        return response.choices[0].message["content"].strip()

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


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} [record|summarize] output.mp3")
        sys.exit(1)

    action = sys.argv[1]
    output_filename = sys.argv[2]

    if action == "record":
        record_audio(output_filename)
    elif action == "summarize":
        transcript = transcribe_audio(output_filename)
        summary = summarize_transcript(transcript)
        print(f"TRANSCRIPT:\n{transcript}\n")
        print(f"SUMMARY:\n{summary}\n")
    else:
        print(
            f"Invalid action. Usage: python {sys.argv[0]} [record|summarize] output.mp3"
        )
        sys.exit(1)
