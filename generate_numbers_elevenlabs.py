#!/usr/bin/env python3
"""
ElevenLabs TTS Number Generator
Generates WAV files for numbers 1-8000 using ElevenLabs Text-to-Speech API
"""

import argparse
import logging
import sys
import time
import zipfile
from pathlib import Path

from elevenlabs import VoiceSettings, save
from elevenlabs.client import ElevenLabs
from tqdm import tqdm

from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tts_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ElevenLabsTTSNumberGenerator:
    """ElevenLabs TTS Number Generator for creating voice files from numbers."""

    def __init__(self, api_key=None, voice_id=None, model="eleven_monolingual_v1"):
        """
        Initialize the ElevenLabs TTS Number Generator

        Args:
            api_key: ElevenLabs API key (if None, will use ELEVENLABS_API_KEY env var)
            voice_id: Voice ID to use (if None, will list available voices)
            model: Model to use (eleven_monolingual_v1, eleven_multilingual_v1, etc.)
        """
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.model = model
        self.output_dir = Path("number_audio_files")
        self.failed_numbers = []

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Voice settings for consistent quality
        self.voice_settings = VoiceSettings(
            stability=0.7,
            similarity_boost=0.8,
            style=0.0,
            use_speaker_boost=True
        )

        logger.info("Initialized ElevenLabs TTS Generator with voice_id: %s, model: %s",
                   voice_id, model)

    def list_available_voices(self):
        """List all available voices and their details."""
        try:
            voices = self.client.voices.get_all()
            logger.info("Available voices:")
            for voice in voices.voices:
                logger.info("  ID: %s, Name: %s, Category: %s", 
                           voice.voice_id, voice.name, voice.category)
            return voices.voices
        except Exception as e:
            logger.error("Error fetching voices: %s", str(e))
            return []

    def select_voice_interactive(self):
        """Interactive voice selection."""
        voices = self.list_available_voices()
        if not voices:
            logger.error("No voices available")
            return None

        print("\nAvailable voices:")
        for i, voice in enumerate(voices, 1):
            print(f"{i:2d}. {voice.name} (ID: {voice.voice_id}) - {voice.category}")

        while True:
            try:
                choice = input("\nSelect voice number (1-{}): ".format(len(voices)))
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(voices):
                    selected_voice = voices[choice_idx]
                    logger.info("Selected voice: %s (ID: %s)", 
                               selected_voice.name, selected_voice.voice_id)
                    return selected_voice.voice_id
                else:
                    print("Invalid choice. Please try again.")
            except (ValueError, KeyboardInterrupt):
                print("Invalid input or cancelled.")
                return None

    def number_to_words(self, num):
        """Convert number to words for better TTS pronunciation."""
        # Define word arrays for numbers
        ones = ["", "one", "two", "three", "four", "five", "six", "seven",
                "eight", "nine", "ten", "eleven", "twelve", "thirteen",
                "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
                "nineteen"]
        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty",
                "seventy", "eighty", "ninety"]

        if num == 0:
            return "zero"
        elif num < 20:
            return ones[num]
        elif num < 100:
            result = tens[num // 10]
            if num % 10 != 0:
                result += " " + ones[num % 10]
            return result
        elif num == 100:
            return "one hundred"
        elif num < 200:
            # 101-199: "one oh one", "one oh two", etc.
            remainder = num % 100
            if remainder < 10:
                return "one oh " + ones[remainder]
            else:
                return "one " + self.number_to_words(remainder)
        elif num < 300:
            # 200-299: "two hundred", "two oh one", etc.
            remainder = num % 100
            if remainder == 0:
                return "two hundred"
            elif remainder < 10:
                return "two oh " + ones[remainder]
            else:
                return "two " + self.number_to_words(remainder)
        elif num < 1000:
            # 300-999: handle similarly
            hundreds_digit = num // 100
            remainder = num % 100
            if remainder == 0:
                return ones[hundreds_digit] + " hundred"
            elif remainder < 10:
                return ones[hundreds_digit] + " oh " + ones[remainder]
            else:
                return ones[hundreds_digit] + " " + self.number_to_words(remainder)
        elif num < 1000000:
            thousands = num // 1000
            result = self.number_to_words(thousands) + " thousand"
            remainder = num % 1000
            if remainder != 0:
                result += " " + self.number_to_words(remainder)
            return result
        else:
            return str(num)  # Fallback for numbers > 999,999

    def generate_single_audio(self, number, retry_delay=60):
        """Generate audio for a single number with rate limit handling."""
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            try:
                # Convert number to words for better pronunciation
                text = self.number_to_words(number)

                # Generate speech
                audio = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=self.voice_id,
                    model_id=self.model,
                    voice_settings=self.voice_settings
                )

                # Save to file
                output_file = self.output_dir / f"{number:05d}.wav"
                save(audio, str(output_file))

                return True, None

            except Exception as e:
                error_msg = str(e).lower()

                # Handle rate limit errors specifically
                if "rate limit" in error_msg or "429" in error_msg or "quota" in error_msg:
                    retry_count += 1
                    wait_time = retry_delay * (2 ** (retry_count - 1))
                    logger.warning(
                        "Rate limit hit for %s. Waiting %ss "
                        "(attempt %s/%s)",
                        number, wait_time, retry_count, max_retries)
                    time.sleep(wait_time)
                    continue
                else:
                    # Non-rate-limit error, don't retry
                    error_msg = "Error generating audio for %s: %s"
                    logger.error(error_msg, number, str(e))
                    return False, error_msg

        # All retries exhausted
        error_msg = "Failed to generate audio for %s after %s rate limit retries"
        logger.error(error_msg, number, max_retries)
        return False, error_msg

    def generate_batch(self, start_num, end_num, delay_between_requests=1):
        """Generate audio files with careful rate limiting."""
        logger.info("Generating audio for numbers %s to %s",
                   start_num, end_num)
        logger.info("Using %ss delay between requests to respect rate limits",
                   delay_between_requests)

        total_numbers = end_num - start_num + 1
        successful = 0

        with tqdm(total=total_numbers, desc="Generating audio files") as pbar:
            for i in range(start_num, end_num + 1):
                # Check if file already exists
                output_file = self.output_dir / f"{i:05d}.wav"
                if output_file.exists():
                    logger.debug("File for %s already exists, skipping", i)
                    successful += 1
                    pbar.update(1)
                    continue

                success, error = self.generate_single_audio(i)

                if success:
                    successful += 1
                    logger.debug("Successfully generated audio for %s", i)
                else:
                    self.failed_numbers.append((i, error))

                pbar.update(1)

                # Rate limiting - wait between requests (except for last)
                if i < end_num:
                    time.sleep(delay_between_requests)

        logger.info("Batch complete: %s/%s successful",
                   successful, total_numbers)
        return successful

    def retry_failed(self, max_retries=3):
        """Retry failed generations."""
        if not self.failed_numbers:
            return

        logger.info("Retrying %s failed numbers...",
                   len(self.failed_numbers))

        for retry_count in range(max_retries):
            if not self.failed_numbers:
                break

            logger.info("Retry attempt %s/%s", retry_count + 1, max_retries)
            current_failed = self.failed_numbers.copy()
            self.failed_numbers = []

            for number, _ in tqdm(current_failed,
                                 desc=f"Retry {retry_count + 1}"):
                success, error = self.generate_single_audio(number)
                if not success:
                    self.failed_numbers.append((number, error))
                time.sleep(0.5)  # Longer pause for retries

    def create_zip_archive(self, zip_filename="number_audio_files_elevenlabs.zip"):
        """Create a zip archive of all generated audio files."""
        logger.info("Creating zip archive...")

        zip_path = Path(zip_filename)
        audio_files = list(self.output_dir.glob("*.wav"))

        if not audio_files:
            logger.error("No audio files found to zip!")
            return False

        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for audio_file in tqdm(audio_files, desc="Adding files to zip"):
                    # Add file to zip with relative path
                    zipf.write(audio_file, audio_file.name)

            file_size = zip_path.stat().st_size / (1024 * 1024)  # MB
            logger.info("Zip archive created: %s (%.1fMB)",
                       zip_filename, file_size)
            logger.info("Archive contains %s audio files", len(audio_files))
            return True

        except (OSError, zipfile.BadZipFile) as e:
            logger.error("Error creating zip archive: %s", str(e))
            return False

    def generate_summary_report(self):
        """Generate a summary report of the generation process."""
        total_expected = 8000
        audio_files = list(self.output_dir.glob("*.wav"))
        successful_count = len(audio_files)
        failed_count = len(self.failed_numbers)

        logger.info("\n%s", "="*50)
        logger.info("GENERATION SUMMARY REPORT")
        logger.info("="*50)
        logger.info("Total numbers to process: %s", total_expected)
        logger.info("Successfully generated: %s", successful_count)
        logger.info("Failed: %s", failed_count)
        logger.info("Success rate: %.1f%%",
                   (successful_count/total_expected)*100)

        if self.failed_numbers:
            failed_nums = [num for num, _ in self.failed_numbers[:10]]
            logger.info("Failed numbers: %s", failed_nums)
            if len(self.failed_numbers) > 10:
                logger.info("... and %s more",
                           len(self.failed_numbers) - 10)

        logger.info("="*50)


def main():
    """Main function to run the ElevenLabs TTS generator."""
    parser = argparse.ArgumentParser(
        description='Generate TTS audio files for numbers 1-8000 using ElevenLabs')
    parser.add_argument(
        '--voice-id', type=str,
        help='ElevenLabs voice ID to use. If not provided, will show interactive selection.')
    parser.add_argument(
        '--model', default='eleven_monolingual_v1',
        choices=['eleven_monolingual_v1', 'eleven_multilingual_v1', 'eleven_multilingual_v2'],
        help='ElevenLabs model to use')
    parser.add_argument('--start', type=int, default=1,
                       help='Starting number')
    parser.add_argument('--end', type=int, default=8000,
                       help='Ending number')
    parser.add_argument(
        '--delay', type=int, default=1,
        help='Delay in seconds between API requests '
             '(default: 1s for rate limiting)')
    parser.add_argument('--zip-name', default='number_audio_files_elevenlabs.zip',
                       help='Name for the output zip file')
    parser.add_argument(
        '--list-voices', action='store_true',
        help='List available voices and exit')

    args = parser.parse_args()

    # Load configuration and check for API key
    config = Config()
    
    # Check for ElevenLabs API key
    elevenlabs_api_key = config.elevenlabs_api_key if hasattr(config, 'elevenlabs_api_key') else None
    if not elevenlabs_api_key:
        # Fall back to environment variable
        import os
        elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not elevenlabs_api_key:
        logger.error("ElevenLabs API key not found. Please:")
        logger.error("1. Set ELEVENLABS_API_KEY environment variable, or")
        logger.error("2. Add ELEVENLABS_API_KEY=your_api_key_here to config.env file")
        sys.exit(1)

    try:
        # Initialize generator for voice listing
        temp_generator = ElevenLabsTTSNumberGenerator(api_key=elevenlabs_api_key)
        
        # List voices and exit if requested
        if args.list_voices:
            temp_generator.list_available_voices()
            sys.exit(0)
        
        # Handle voice selection
        voice_id = args.voice_id
        if not voice_id:
            voice_id = temp_generator.select_voice_interactive()
            if not voice_id:
                logger.error("No voice selected. Exiting.")
                sys.exit(1)

        logger.info("Starting ElevenLabs TTS Number Generator")
        logger.info("Range: %s to %s", args.start, args.end)
        logger.info("Voice ID: %s, Model: %s", voice_id, args.model)

        # Initialize generator with selected voice
        generator = ElevenLabsTTSNumberGenerator(
            api_key=elevenlabs_api_key, 
            voice_id=voice_id,
            model=args.model
        )

        # Generate audio files
        start_time = time.time()
        generator.generate_batch(args.start, args.end, args.delay)

        # Retry failed ones
        generator.retry_failed()

        # Create zip archive
        generator.create_zip_archive(args.zip_name)

        # Generate summary
        generator.generate_summary_report()

        end_time = time.time()
        total_time = end_time - start_time
        logger.info("Total execution time: %.1f minutes", total_time/60)

    except KeyboardInterrupt:
        logger.info("Generation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()