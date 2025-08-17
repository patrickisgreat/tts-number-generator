# TTS Number Generator

A comprehensive Python tool that generates high-quality WAV audio files for numbers 1-8000 using both **OpenAI's Text-to-Speech API** and **ElevenLabs AI**. Perfect for creating number pronunciation files for applications, games, educational content, or any project requiring spoken numbers with customizable emotional delivery.

## Features

### 🎵 Dual TTS Engine Support
- **OpenAI TTS**: 6 distinct voices with vibe prompts (alloy, echo, fable, onyx, nova, shimmer)
- **ElevenLabs**: 25+ premium voices with advanced emotional control and ultra-realistic speech

### 🎭 Advanced Emotional Control
- **OpenAI**: Custom vibe prompts for tone control
- **ElevenLabs**: Emotional context system using narrative descriptions ("he whispered nervously", "she said excitedly")
- **Voice Settings**: Fine-tune stability, similarity, and style parameters

### 🔧 Smart Processing
- **Smart Number Pronunciation**: Converts numbers to words for natural pronunciation (e.g., "101" becomes "one oh one")
- **Rate Limit Handling**: Built-in retry logic and configurable delays to respect API limits
- **Batch Processing**: Generate thousands of files with progress tracking
- **Resume Capability**: Skip already generated files when restarting
- **Automatic Archiving**: Creates zip files of generated audio
- **Comprehensive Logging**: Detailed logs and summary reports

### 🛡️ Security & Configuration
- **Secure API Key Management**: Environment variables and config files (never committed to git)
- **Flexible Configuration**: Support for both `.env` and `config.env` files
- **Multiple Models**: Support for various TTS models and quality levels

## Installation

### Prerequisites

- Python 3.8 or higher
- API key from either OpenAI or ElevenLabs (or both)

### Using Poetry (Recommended)

```bash
git clone <repository-url>
cd tts-number-generator
poetry install
```

### Using pip

```bash
# Install dependencies
pip install openai elevenlabs tqdm

# Or install from requirements (if available)
pip install -r requirements.txt
```

### Quick Setup

```bash
# Clone and install
git clone <repository-url>
cd tts-number-generator
pip3 install openai elevenlabs tqdm

# Set up configuration
cp .env.example config.env
# Edit config.env with your API keys
```

## Configuration

### API Keys Setup

1. **OpenAI API Key**: Get from https://platform.openai.com/api-keys
2. **ElevenLabs API Key**: Get from https://elevenlabs.io/

### Configuration Methods

**Option 1: Config File (Recommended)**
```bash
# Copy template and edit
cp .env.example config.env

# Add your API keys to config.env
OPENAI_API_KEY=sk-your_openai_key_here
ELEVENLABS_API_KEY=sk_your_elevenlabs_key_here
```

**Option 2: Environment Variables**
```bash
export OPENAI_API_KEY="sk-your_openai_key_here"
export ELEVENLABS_API_KEY="sk_your_elevenlabs_key_here"
```

### Security Note
⚠️ **IMPORTANT**: Never commit API keys to git! The `.gitignore` file is configured to exclude `config.env` and `.env` files.

## Usage

### OpenAI TTS (generate_numbers.py)

**Basic Usage:**
```bash
python generate_numbers.py
```
Generates audio files for numbers 1-8000 using default settings (nova voice, tts-1 model).

**Advanced Usage:**
```bash
# Use different voice and model
python generate_numbers.py --voice shimmer --model tts-1-hd

# Generate specific range with custom delay
python generate_numbers.py --start 100 --end 500 --delay 15

# Use voice customization with vibe prompts
python generate_numbers.py --model gpt-4o-mini-tts --vibe "Speak with excitement and energy like a game show host"

# Use predefined vibe from JSON file
python generate_numbers.py --model gpt-4o-mini-tts --vibe-file vibe_prompts.json --vibe-key excited
```

### ElevenLabs TTS (generate_numbers_elevenlabs.py)

**Basic Usage:**
```bash
# List available voices first
python3 generate_numbers_elevenlabs.py --list-voices

# Interactive voice selection
python3 generate_numbers_elevenlabs.py

# Use specific voice
python3 generate_numbers_elevenlabs.py --voice-id 21m00Tcm4TlvDq8ikWAM --start 1 --end 100
```

**Advanced Emotional Control:**
```bash
# Terrified/nervous delivery
python3 generate_numbers_elevenlabs.py --voice-id 21m00Tcm4TlvDq8ikWAM --style-prompt "she whispered in terror"

# Calm and peaceful
python3 generate_numbers_elevenlabs.py --voice-id SAz9YHcvj6GT2YYXdXww --style-prompt "he said calmly and peacefully"

# Excited and energetic
python3 generate_numbers_elevenlabs.py --voice-id 21m00Tcm4TlvDq8ikWAM --style-prompt "she exclaimed excitedly"

# Angry delivery
python3 generate_numbers_elevenlabs.py --voice-id GBv7mTt0atIp3Br8iCZE --style-prompt "he shouted angrily"

# Different model and custom range
python3 generate_numbers_elevenlabs.py --voice-id pFZP5JQG7iQjIQuC4Bku --model eleven_multilingual_v2 --start 1000 --end 2000 --delay 0.5
```

## Voice Options

### OpenAI Voices

- **alloy**: Neutral, balanced voice
- **echo**: Male voice with clear pronunciation  
- **fable**: British accent, sophisticated
- **onyx**: Deep, authoritative voice
- **nova**: Young female voice (default)
- **shimmer**: Soft, gentle female voice

### ElevenLabs Voices (Popular Options)

- **Rachel** (`21m00Tcm4TlvDq8ikWAM`): Clear, professional female voice
- **Clyde** (`2EiwWnXFnvU5JabPnv8n`): Warm male voice
- **Aria** (`9BWtsMINqrJLrRacOk9x`): Expressive female voice
- **River** (`SAz9YHcvj6GT2YYXdXww`): Laid-back, chill delivery
- **Charlie** (`IKne3meq5aSn9XLyUdCD`): Calm, gentle voice
- **Sarah** (`EXAVITQu4vr4xnSDxMaL`): Gentle, soothing tone
- **Thomas** (`GBv7mTt0atIp3Br8iCZE`): Deep, authoritative male

*Use `--list-voices` to see all 25+ available ElevenLabs voices*

## Model Options

### OpenAI Models
- **tts-1**: Standard quality, faster generation
- **tts-1-hd**: High definition quality  
- **gpt-4o-mini-tts**: Supports voice customization with vibe prompts

### ElevenLabs Models
- **eleven_monolingual_v1**: English-optimized, stable (default)
- **eleven_multilingual_v1**: Multi-language support
- **eleven_multilingual_v2**: Advanced multi-language with emotion

## Cost Estimation

### For 8000 Audio Files (~145,000 characters)

**ElevenLabs Pricing:**
- **Starter**: $5/month (30K chars) - ❌ Insufficient
- **Creator**: $22/month (100K chars) - ❌ Insufficient  
- **Pro**: $99/month (500K chars) - ✅ Required for full generation

**OpenAI Pricing:**
- **tts-1**: ~$0.015/1K chars = ~$2.18 total
- **tts-1-hd**: ~$0.030/1K chars = ~$4.35 total

*Note: Prices as of 2024. Check current pricing on respective platforms.*

## Voice Customization

### OpenAI Vibe Prompts

The OpenAI generator includes a comprehensive set of vibe prompts for different tones and emotions:

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

### ElevenLabs Emotional Context

ElevenLabs uses narrative descriptions to control emotion without speaking them aloud:

**Calm/Peaceful:**
- `"he said calmly and peacefully"`
- `"she whispered gently"`
- `"in a meditative tone"`

**Excited/Energetic:**
- `"she exclaimed excitedly"`
- `"he shouted with enthusiasm"`
- `"she said with energy"`

**Nervous/Scared:**
- `"she whispered in terror"`
- `"he said nervously"`
- `"she stammered fearfully"`

**Angry/Aggressive:**
- `"he shouted angrily"`
- `"she said with fury"`
- `"he growled menacingly"`

**Sleepy/Tired:**
- `"she said drowsily"`
- `"he mumbled sleepily"`
- `"in a tired voice"`

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

### OpenAI Examples

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

### ElevenLabs Examples

```bash
# Test setup with Rachel's voice (numbers 1-5)
python3 generate_numbers_elevenlabs.py --voice-id 21m00Tcm4TlvDq8ikWAM --start 1 --end 5

# Chill meditation numbers with River voice
python3 generate_numbers_elevenlabs.py --voice-id SAz9YHcvj6GT2YYXdXww --style-prompt "he said in a calm, meditative tone" --start 1 --end 100

# Dramatic announcement style with Thomas voice
python3 generate_numbers_elevenlabs.py --voice-id GBv7mTt0atIp3Br8iCZE --style-prompt "he announced dramatically" --start 1000 --end 1100

# Gentle whisper with Sarah voice (slower generation)
python3 generate_numbers_elevenlabs.py --voice-id EXAVITQu4vr4xnSDxMaL --style-prompt "she whispered softly" --start 1 --end 50 --delay 2

# Full generation with advanced model
python3 generate_numbers_elevenlabs.py --voice-id 21m00Tcm4TlvDq8ikWAM --model eleven_multilingual_v2 --style-prompt "she said clearly and professionally" --start 1 --end 8000
```

## Troubleshooting

### API Key Issues
- **OpenAI**: Verify your API key is correct and has sufficient credits
- **ElevenLabs**: Check your subscription tier and character limits
- Ensure keys are properly set in environment variable or `config.env` file

### Rate Limit Errors
- **OpenAI**: Increase delay with `--delay 30`, consider higher tier plan
- **ElevenLabs**: Use `--delay 1` or `--delay 2` for rate limiting

### Generation Failures
- Check the log file `tts_generation.log` for detailed error messages
- Use the retry functionality - both tools automatically retry failed generations
- For persistent failures, try a different voice or model

### ElevenLabs Specific Issues
- **Voice not found**: Use `--list-voices` to see available voices
- **Emotion not working**: Try narrative descriptions like "she said angrily" instead of just "angry"
- **Import errors**: Ensure `elevenlabs` package is installed: `pip3 install elevenlabs`

### VS Code Issues
- **Import errors in VS Code**: Update `.vscode/settings.json` to point to correct Python interpreter
- **Python path issues**: Use `python3` instead of `python` on macOS

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]