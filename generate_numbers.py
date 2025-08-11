#!/usr/bin/env python3
"""
OpenAI TTS Number Generator
Generates WAV files for numbers 1-8000 using OpenAI's Text-to-Speech API
"""

import argparse
import json
import logging
import sys
import time
import zipfile
from pathlib import Path

from openai import OpenAI
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


class TTSNumberGenerator:
    """TTS Number Generator for creating voice files from numbers."""

    def __init__(self, api_key=None, voice="alloy", model="tts-1", vibe_prompt=None):
        """
        Initialize the TTS Number Generator

        Args:
            api_key: OpenAI API key (if None, will use OPENAI_API_KEY env var)
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: Model to use (tts-1, tts-1-hd, or gpt-4o-mini-tts for voice customization)
            vibe_prompt: Optional prompt to customize voice tone/emotion (only works with gpt-4o-mini-tts)
        """
        self.client = OpenAI(api_key=api_key)
        self.voice = voice
        self.model = model
        self.vibe_prompt = vibe_prompt
        self.output_dir = Path("number_audio_files")
        self.failed_numbers = []

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Validate model and vibe prompt combination
        if vibe_prompt and model != "gpt-4o-mini-tts":
            logger.warning("Vibe prompt specified but model is %s. Voice customization only works with gpt-4o-mini-tts", model)

        logger.info("Initialized TTS Generator with voice: %s, model: %s%s",
                   voice, model, f", vibe: {vibe_prompt[:50]}..." if vibe_prompt else "")

    @staticmethod
    def load_vibe_prompts(json_file_path):
        """Load vibe prompts from a JSON file."""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info("Loaded vibe prompts from %s", json_file_path)
            return data
        except FileNotFoundError:
            logger.error("Vibe prompts file not found: %s", json_file_path)
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in vibe prompts file %s: %s", json_file_path, str(e))
            sys.exit(1)

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
                
                # Add vibe customization to text if specified
                if self.vibe_prompt and self.model == "gpt-4o-mini-tts":
                    text = f"[Voice direction: {self.vibe_prompt}] {text}"

                # Generate speech
                response = self.client.audio.speech.create(
                    model=self.model,
                    voice=self.voice,
                    input=text,
                    response_format="wav"
                )

                # Save to file
                output_file = self.output_dir / f"{number:05d}.wav"
                with open(output_file, "wb") as f:
                    f.write(response.content)

                return True, None

            except Exception as e:
                error_msg = str(e).lower()

                # Handle rate limit errors specifically
                if "rate limit" in error_msg or "429" in error_msg:
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

    def generate_batch(self, start_num, end_num, delay_between_requests=20):
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

    def create_zip_archive(self, zip_filename="number_audio_files.zip"):
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
    """Main function to run the TTS generator."""
    parser = argparse.ArgumentParser(
        description='Generate TTS audio files for numbers 1-8000')
    parser.add_argument(
        '--voice', default='nova',
        choices=['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'],
        help='Voice to use for TTS (alloy=neutral, echo=male, '
             'fable=british, onyx=deep, nova=young female, '
             'shimmer=soft female)')
    parser.add_argument(
        '--model', default='tts-1',
        choices=['tts-1', 'tts-1-hd', 'gpt-4o-mini-tts'],
        help='TTS model to use (gpt-4o-mini-tts supports voice customization)')
    parser.add_argument('--start', type=int, default=1,
                       help='Starting number')
    parser.add_argument('--end', type=int, default=8000,
                       help='Ending number')
    parser.add_argument(
        '--delay', type=int, default=20,
        help='Delay in seconds between API requests '
             '(default: 20s for rate limiting)')
    parser.add_argument('--zip-name', default='number_audio_files.zip',
                       help='Name for the output zip file')
    parser.add_argument(
        '--vibe', type=str,
        help='Voice customization prompt to control tone/emotion '
             '(only works with gpt-4o-mini-tts model). '
             'Example: "Speak with excitement and energy" or '
             '"Use a calm, soothing tone"')
    parser.add_argument(
        '--vibe-file', type=str,
        help='JSON file containing vibe prompts. Use with --vibe-key to select a prompt')
    parser.add_argument(
        '--vibe-key', type=str,
        help='Key from JSON vibe file to use (e.g., "excited", "calm", "professional")')
    parser.add_argument(
        '--list-vibes', action='store_true',
        help='List available vibe prompts from JSON file and exit')

    args = parser.parse_args()

    # Handle vibe prompt loading and listing
    vibe_prompt = args.vibe
    
    if args.vibe_file:
        vibe_data = TTSNumberGenerator.load_vibe_prompts(args.vibe_file)
        
        # List available vibes and exit
        if args.list_vibes:
            print("Available vibe prompts:")
            print("\n=== General Prompts ===")
            for key, prompt in vibe_data.get("prompts", {}).items():
                print(f"  {key}: {prompt}")
            
            if "number_specific" in vibe_data:
                print("\n=== Number-Specific Prompts ===")
                for category, numbers in vibe_data["number_specific"].items():
                    print(f"  {category}:")
                    for num, prompt in numbers.items():
                        print(f"    {num}: {prompt}")
            
            if "range_specific" in vibe_data:
                print("\n=== Range-Specific Prompts ===")
                for range_key, prompt in vibe_data["range_specific"].items():
                    print(f"  {range_key}: {prompt}")
            
            sys.exit(0)
        
        # Use vibe key to select prompt
        if args.vibe_key:
            if args.vibe_key in vibe_data.get("prompts", {}):
                vibe_prompt = vibe_data["prompts"][args.vibe_key]
                logger.info("Using vibe prompt '%s': %s", args.vibe_key, vibe_prompt[:50] + "...")
            else:
                logger.error("Vibe key '%s' not found in JSON file", args.vibe_key)
                logger.info("Use --list-vibes to see available keys")
                sys.exit(1)
        elif not args.vibe:
            logger.error("When using --vibe-file, you must specify either --vibe-key or --vibe")
            sys.exit(1)

    # Load configuration and check for API key
    config = Config()
    if not config.is_configured():
        logger.error("OpenAI API key not found. Please:")
        logger.error("1. Set OPENAI_API_KEY environment variable, or")
        logger.error("2. Create a config.env file with: "
                    "OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)

    api_key = config.openai_api_key

    logger.info("Starting TTS Number Generator")
    logger.info("Range: %s to %s", args.start, args.end)
    logger.info("Voice: %s, Model: %s", args.voice, args.model)

    try:
        # Initialize generator
        generator = TTSNumberGenerator(api_key=api_key, voice=args.voice,
                                      model=args.model, vibe_prompt=vibe_prompt)

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