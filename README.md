# Meeting Summarizer

A Python-based application that records, transcribes, and summarizes meetings from Discord voice channels. The application uses OpenAI Whisper for transcription and GPT-3.5 for summarization. The GUI is built using PyQt5 for a user-friendly interface.

## Features

- **Record Meetings**: Capture audio directly from Discord voice channels or your system's default input.
- **Transcribe and Summarize**: Automatically transcribe recorded audio and generate concise summaries using OpenAI's GPT-3.5.
- **User-Friendly GUI**: Intuitive interface built with PyQt5 for easy recording, transcribing, and summarizing operations.
- **Cross-Platform Compatibility**: Works on Windows, macOS, and Linux.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/meeting-summarizer.git
   cd meeting-summarizer
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the environment variables by creating a `.env` file:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   OPEN_API_KEY=your_openai_api_key
   ```

## Usage

1. **Run the Application**:
   ```bash
   python gui.py
   ```

2. **Recording a Meeting**:
   - Click "Start Recording" and select a file name to save the recording.
   - Click "Stop Recording" when done.

3. **Transcribing and Summarizing**:
   - Click "Summarize" and select an existing MP3 file for transcription and summarization.
   - The transcript and summary will appear in the respective sections.

## Requirements

- Python 3.8+
- Dependencies: PyQt5, discord.py, ffmpeg-python, openai, whisper-python, tiktoken, torch, python-dotenv

## Notes

- Make sure you have FFmpeg installed on your system for recording functionality. You can download it [here](https://ffmpeg.org/download.html).
- Ensure your Discord bot has the necessary permissions to access voice channels.
- You must have valid API keys for OpenAI and Discord set in your `.env` file.

## Contributing

Feel free to open issues or submit pull requests. Any contributions to improve the application are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Happy summarizing!


### Notes:
- Make sure to replace `https://github.com/yourusername/meeting-summarizer.git` with your actual repository URL if you plan to host it on GitHub.
- This README provides clear instructions for installation, usage, and setup, ensuring anyone can quickly get started with your project.