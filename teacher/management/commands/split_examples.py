import re

from django.core.management.base import BaseCommand

from django.db import transaction

from teacher.models import Vocabulary, Idiom

def split_example(text):

    """

    Try to split:

    Chinese sentence + Pinyin sentence + English translation

    Returns:

        (chinese, pinyin, english) or None

    """

    if not text:

        return None

    text = text.strip()

    # Find the end of the Chinese sentence.

    # Supports common Chinese punctuation.

    chinese_match = re.match(

        r"^(.+?[。！？!?])\s*(.+)$",

        text

    )

    if not chinese_match:

        return None

    chinese = chinese_match.group(1).strip()

    remainder = chinese_match.group(2).strip()

    # Make sure the first section actually contains Chinese.

    if not re.search(r"[\u4e00-\u9fff]", chinese):

        return None

    # Find the end of the pinyin sentence.

    # Pinyin is normally followed by ., !, or ? before English begins.

    pinyin_match = re.match(

        r"^(.+?[.!?])\s+([A-Z].+)$",

        remainder

    )

    if not pinyin_match:

        return None

    pinyin = pinyin_match.group(1).strip()

    english = pinyin_match.group(2).strip()

    if not english:

        return None

    return chinese, pinyin, english

class Command(BaseCommand):

    help = "Split old combined vocabulary/expression examples into separate fields."

    def add_arguments(self, parser):

        parser.add_argument(

            "--apply",

            action="store_true",

            help="Actually update the database. Without this flag, only preview changes.",

        )

    def handle(self, *args, **options):

        apply_changes = options["apply"]

        if apply_changes:

            self.stdout.write(

                self.style.WARNING(

                    "\nAPPLY MODE: database records will be changed.\n"

                )

            )

        else:

            self.stdout.write(

                self.style.SUCCESS(

                    "\nDRY RUN: nothing will be changed.\n"

                )

            )

        updated = 0

        skipped = 0

        already_done = 0

        model_configs = [

            (Vocabulary, "word"),

            (Idiom, "idiom"),

        ]

        with transaction.atomic():

            for model, name_field in model_configs:

                self.stdout.write(

                    f"\n--- Checking {model.__name__} ---"

                )

                for item in model.objects.all():

                    name = getattr(item, name_field)

                    # Don't overwrite records already separated.

                    if item.example_pinyin or item.example_translation:

                        already_done += 1

                        continue

                    result = split_example(item.example_sentence)

                    if not result:

                        skipped += 1

                        self.stdout.write(

                            self.style.WARNING(

                                f"SKIPPED [{item.id}] {name}: "

                                f"{item.example_sentence}"

                            )

                        )

                        continue

                    chinese, pinyin, english = result

                    self.stdout.write(

                        self.style.SUCCESS(

                            f"\n[{item.id}] {name}"

                        )

                    )

                    self.stdout.write(

                        f"Chinese: {chinese}"

                    )

                    self.stdout.write(

                        f"Pinyin:  {pinyin}"

                    )

                    self.stdout.write(

                        f"English: {english}"

                    )

                    if apply_changes:

                        item.example_sentence = chinese

                        item.example_pinyin = pinyin

                        item.example_translation = english

                        item.save(

                            update_fields=[

                                "example_sentence",

                                "example_pinyin",

                                "example_translation",

                            ]

                        )

                    updated += 1

            # Dry run must never save anything.

            if not apply_changes:

                transaction.set_rollback(True)

        self.stdout.write("\n==========================")

        self.stdout.write(f"Can be split: {updated}")

        self.stdout.write(f"Skipped: {skipped}")

        self.stdout.write(f"Already separated: {already_done}")

        self.stdout.write("==========================")

        if not apply_changes:

            self.stdout.write(

                self.style.SUCCESS(

                    "\nNothing was changed. "

                    "Run again with --apply when the preview looks correct."

                )

            )

