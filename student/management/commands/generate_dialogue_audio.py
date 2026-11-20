"""Generate the Dialogue listening-practice audio files.

For every topic/level version in student/dialogue_data.py, each dialogue line
is synthesized with the OpenAI TTS API using the speaker's assigned voice,
speed and age/style instruction (plus the site's standard-Mandarin verbatim
rule), then the lines are joined with short pauses into one MP3 per version:

    student/static/student/dialogues/<topic-slug>-<l2|l3>.mp3

Runs on the server (needs OPENAI_API_KEY from the environment, like the AI
conversation speech). Idempotent: existing files are skipped unless --force.
After generating, it runs collectstatic so the files are served immediately.

Usage:
    python manage.py generate_dialogue_audio [--only SLUG ...] [--level l2|l3]
                                             [--force] [--speed-scale 1.0]
"""
import subprocess
import tempfile
import time
from pathlib import Path

import requests
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from student.ai_conversation_views import MANDARIN_SPEECH_CONVERTER, _api_key
from student.dialogue_data import TOPICS
from student.dialogue_views import LEVEL_SUFFIX

MANDARIN_RULE = (
    'Read the supplied Chinese text verbatim in Standard Mandarin Chinese '
    '(Putonghua / 標準國語) pronunciation. The language is Mandarin Chinese, '
    'not Cantonese. Use standard Mandarin phonology and tones for every '
    'Chinese character. Do NOT use Cantonese pronunciation, Cantonese '
    'readings, Cantonese particles, Taiwanese Hokkien, or any other regional '
    'reading. Do not translate, paraphrase, add, omit, or explain any words.'
)
PAUSE_SECONDS = 0.35


def _tts(text, voice, speed, style, model, api_key):
    instructions = f'You are {style}. Speak naturally, like a real person in a conversation. ' + MANDARIN_RULE
    payload = {
        'model': model,
        'voice': voice,
        'input': MANDARIN_SPEECH_CONVERTER.convert(text),
        'instructions': instructions,
        'response_format': 'mp3',
        'speed': round(speed, 2),
    }
    last_error = None
    for attempt in range(3):
        try:
            r = requests.post(
                'https://api.openai.com/v1/audio/speech',
                headers={'Authorization': f'Bearer {api_key}',
                         'Content-Type': 'application/json'},
                json=payload, timeout=60)
            r.raise_for_status()
            return r.content
        except requests.RequestException as exc:  # retry transient failures
            last_error = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f'TTS failed for voice {voice}: {last_error}')


def _has(tool):
    return subprocess.run(['which', tool], capture_output=True).returncode == 0


def _join(line_files, out_path):
    """Join line MP3s with a short pause; fall back to raw concatenation."""
    if _has('ffmpeg'):
        with tempfile.TemporaryDirectory() as tmp:
            silence = Path(tmp) / 'silence.mp3'
            subprocess.run(
                ['ffmpeg', '-y', '-f', 'lavfi', '-i',
                 'anullsrc=r=24000:cl=mono', '-t', str(PAUSE_SECONDS),
                 '-c:a', 'libmp3lame', '-b:a', '128k', str(silence)],
                capture_output=True, check=True)
            listing = Path(tmp) / 'list.txt'
            entries = []
            for i, f in enumerate(line_files):
                if i:
                    entries.append(f"file '{silence}'")
                entries.append(f"file '{f}'")
            listing.write_text('\n'.join(entries))
            subprocess.run(
                ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(listing),
                 '-c:a', 'libmp3lame', '-b:a', '128k', str(out_path)],
                capture_output=True, check=True)
    else:
        with open(out_path, 'wb') as out:
            for f in line_files:
                out.write(Path(f).read_bytes())


def _duration(path):
    if not _has('ffprobe'):
        return None
    r = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


class Command(BaseCommand):
    help = 'Generate Dialogue listening audio (one MP3 per topic and level).'

    def add_arguments(self, parser):
        parser.add_argument('--only', nargs='*', default=None,
                            help='Only these topic slugs.')
        parser.add_argument('--level', choices=['l2', 'l3'], default=None)
        parser.add_argument('--force', action='store_true',
                            help='Regenerate files that already exist.')
        parser.add_argument('--speed-scale', type=float, default=1.0,
                            help='Multiply every speaker speed (duration calibration).')
        parser.add_argument('--no-collectstatic', action='store_true')

    def handle(self, *args, **options):
        import os
        model = os.getenv('OPENAI_AI_TTS_MODEL', 'gpt-4o-mini-tts')
        api_key = _api_key()
        out_dir = (Path(settings.BASE_DIR) / 'student' / 'static' / 'student'
                   / 'dialogues')
        out_dir.mkdir(parents=True, exist_ok=True)
        generated, skipped = [], []
        for topic in TOPICS:
            if options['only'] and topic['slug'] not in options['only']:
                continue
            for level_key, suffix in LEVEL_SUFFIX.items():
                if options['level'] and options['level'] != suffix:
                    continue
                version = topic['versions'].get(level_key)
                if version is None:
                    continue
                out_path = out_dir / f"{topic['slug']}-{suffix}.mp3"
                if out_path.exists() and not options['force']:
                    skipped.append(out_path.name)
                    continue
                with tempfile.TemporaryDirectory() as tmp:
                    line_files = []
                    for i, (speaker_key, text) in enumerate(version['lines']):
                        speaker = topic['speakers'][speaker_key]
                        audio = _tts(
                            text, speaker['voice'],
                            speaker['speed'] * options['speed_scale'],
                            speaker['style'], model, api_key)
                        line_path = Path(tmp) / f'line{i:02d}.mp3'
                        line_path.write_bytes(audio)
                        line_files.append(line_path)
                    _join(line_files, out_path)
                dur = _duration(out_path)
                chars = sum(len(t) for _, t in version['lines'])
                generated.append(
                    f"{out_path.name}: {len(version['lines'])} lines, "
                    f"{chars} chars, "
                    f"{dur:.1f}s" if dur else f"{out_path.name}: duration n/a")
                self.stdout.write(generated[-1])
        self.stdout.write(
            f'Generated {len(generated)}, skipped {len(skipped)} existing.')
        if generated and not options['no_collectstatic']:
            call_command('collectstatic', '--noinput', verbosity=0)
            self.stdout.write('collectstatic done.')
