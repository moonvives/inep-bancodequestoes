#!/usr/bin/env python3
"""Build PDF page/crop metadata for the 540 Natureza questions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pdfplumber


def question_headers(words: list[dict], page_width: float) -> list[dict]:
    headers: list[dict] = []
    for index, word in enumerate(words):
        number = None
        bottom = word["bottom"]

        joined = re.match(r"^Questão(\d{3})", word["text"])
        if joined:
            number = int(joined.group(1))
        elif word["text"] == "Questão" and index + 1 < len(words):
            separated = re.match(r"^(\d{3})", words[index + 1]["text"])
            if separated and abs(word["top"] - words[index + 1]["top"]) < 2:
                number = int(separated.group(1))
                bottom = max(bottom, words[index + 1]["bottom"])

        if number is not None:
            headers.append(
                {
                    "number": number,
                    "column": 0 if word["x0"] < page_width / 2 else 1,
                    "top": word["top"],
                    "bottom": bottom,
                }
            )
    return headers


def build_regions(pdf_path: Path) -> dict:
    questions: dict[int, dict] = {}

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages, 1):
            # Pages before 30 are editorial; pages after 260 contain answer tables.
            if not 30 <= page_number <= 260:
                continue

            words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
            headers = question_headers(words, page.width)
            has_right_column = any(item["column"] == 1 for item in headers)

            for header in headers:
                number = header["number"]
                if number in questions:
                    continue

                if header["column"] == 0:
                    # Pages with no right-column question use the entire editorial width.
                    left, right = 14.0, 281.0 if has_right_column else 562.0
                else:
                    left, right = page.width / 2 + 10.0, 562.0

                following = [
                    item
                    for item in headers
                    if item["column"] == header["column"] and item["top"] > header["top"]
                ]
                limit = min(item["top"] for item in following) - 6 if following else 805.0
                top = header["bottom"] + 5

                relevant_words = [
                    word
                    for word in words
                    if left - 5 <= word["x0"] <= right + 5
                    and top <= word["top"] < limit
                    and word["text"] != "Página"
                ]
                max_bottom = max((word["bottom"] for word in relevant_words), default=limit - 4)

                for object_type in ("image", "rect", "curve", "line"):
                    for item in page.objects.get(object_type, []):
                        if (
                            item.get("x1", 0) >= left
                            and item.get("x0", 0) <= right
                            and top <= item.get("top", 0) < limit
                            and item.get("bottom", 0) <= limit + 2
                        ):
                            max_bottom = max(max_bottom, item.get("bottom", 0))

                bottom = min(limit, max_bottom + 7)
                questions[number] = {
                    "page": page_number,
                    "rect": [
                        round(left, 2),
                        round(top, 2),
                        round(right - left, 2),
                        round(max(60, bottom - top), 2),
                    ],
                }

    missing = [number for number in range(1, 541) if number not in questions]
    if missing:
        raise RuntimeError(f"Missing question regions: {missing}")

    return {
        "source": "eBook - Naturezas PPL por Habilidades e Dificuldades",
        "total": len(questions),
        "questions": questions,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    data = build_regions(args.pdf)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"Mapped {data['total']} questions to {args.output}")


if __name__ == "__main__":
    main()
