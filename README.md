# OpenAI TTS Numbers Generator

A Python tool that generates high-quality WAV audio files for numbers 1-8000 using OpenAI's Text-to-Speech API. Perfect for creating number pronunciation files for applications, games, or educational content.

## Features

- **Multiple Voice Options**: Choose from 6 distinct voices (alloy, echo, fable, onyx, nova, shimmer)
- **Voice Customization**: Use the `gpt-4o-mini-tts` model with custom vibe prompts to control tone and emotion
- **Smart Number Pronunciation**: Converts numbers to words for natural pronunciation (e.g., "101" becomes "one oh one")
- **Rate Limit Handling**: Built-in retry logic and configurable delays to respect OpenAI API limits
- **Batch Processing**: Generate thousands of files with progress tracking
- **Resume Capability**: Skip already generated files when restarting
- **Automatic Archiving**: Creates zip files of generated audio
- **Comprehensive Logging**: Detailed logs and summary reports

## Installation

### Using Poetry (Recommended)

```bash
git clone <repository-url>
cd openai-tts-numbers-generator
poetry install
```

### Using pip

```bash
pip install openai tqdm
```

## Configuration

1. Get your OpenAI API key from https://platform.openai.com/api-keys

2. Set up your API key using one of these methods:

   **Environment Variable:**
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

   **Config File:**
   ```bash
   cp config.env.example config.env
   # Edit config.env and add your API key
   ```

## Usage

### Basic Usage

```bash
python generate_numbers.py
```

This generates audio files for numbers 1-8000 using the default settings (nova voice, tts-1 model).

### Advanced Usage

```bash
# Use different voice and model
python generate_numbers.py --voice shimmer --model tts-1-hd

# Generate specific range with custom delay
python generate_numbers.py --start 100 --end 500 --delay 15

# Use voice customization with vibe prompts
python generate_numbers.py --model gpt-4o-mini-tts --vibe "Speak with excitement and energy like a game show host"

# Use predefined vibe from JSON file
python generate_numbers.py --model gpt-4o-mini-tts --vibe-file vibe_prompts.json --vibe-key excited

# List all available vibe prompts
python generate_numbers.py --vibe-file vibe_prompts.json --list-vibes
```

### Voice Options

- **alloy**: Neutral, balanced voice
- **echo**: Male voice with clear pronunciation
- **fable**: British accent, sophisticated
- **onyx**: Deep, authoritative voice
- **nova**: Young female voice (default)
- **shimmer**: Soft, gentle female voice

### Model Options

- **tts-1**: Standard quality, faster generation
- **tts-1-hd**: High definition quality
- **gpt-4o-mini-tts**: Supports voice customization with vibe prompts

## Voice Customization

The tool includes a comprehensive set of vibe prompts for different tones and emotions:

- **excited**: Game show host energy
- **calm**: Meditation guide tone
- **professional**: Business presentation style
- **friendly**: Conversational and warm
- **dramatic**: Epic movie trailer narrator
- **robot**: AI assistant tone
- **whisper**: Soft, intimate delivery
- **teacher**: Patient, educational tone
- **newscaster**: Authoritative news anchor
- **sleepy**: Drowsy, relaxed delivery
- **pirate**: Swashbuckling adventure style
- **butler**: Refined, polite English butler
- **surfer**: Laid-back California vibe
- **scientist**: Methodical, precise delivery

## Output

- Audio files are saved as `00001.wav`, `00002.wav`, etc. in the `number_audio_files/` directory
- A zip archive is automatically created for easy distribution
- Comprehensive logging is saved to `tts_generation.log`
- Summary report shows success rates and any failures

## Rate Limiting

The tool includes smart rate limiting to stay within OpenAI's API limits:

- Default 20-second delay between requests
- Automatic retry with exponential backoff for rate limit errors
- Configurable delay settings for different usage tiers

## Examples

```bash
# Quick test with a small range
python generate_numbers.py --start 1 --end 10 --voice nova

# Professional business tone for presentations
python generate_numbers.py --model gpt-4o-mini-tts --vibe-file vibe_prompts.json --vibe-key professional

# Dramatic movie trailer voice
python generate_numbers.py --model gpt-4o-mini-tts --vibe-file vibe_prompts.json --vibe-key dramatic --voice onyx

# High quality with custom excitement
python generate_numbers.py --model tts-1-hd --voice shimmer --start 1 --end 100
```

## Troubleshooting

### API Key Issues
- Verify your API key is correct and has sufficient credits
- Check that the key is properly set in environment variable or config.env file

### Rate Limit Errors
- Increase the delay between requests with `--delay 30`
- Consider using a higher tier OpenAI plan for increased rate limits

### Generation Failures
- Check the log file `tts_generation.log` for detailed error messages
- Use the retry functionality - the tool automatically retries failed generations
- For persistent failures, try a different voice or model

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]