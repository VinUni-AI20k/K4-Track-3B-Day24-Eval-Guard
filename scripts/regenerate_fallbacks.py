"""Re-run LLM generation for answers saved as extractive_fallback.

setup_answers.py falls back to the first context when the generation call fails
(e.g. a network outage). This script keeps the contexts that search/rerank
actually retrieved and only repeats the generation step, with the same prompt and
config.GENERATION_MODEL, retrying transient errors. Rows that still fail stay
extractive_fallback.

    python scripts/regenerate_fallbacks.py --live
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import ANSWERS_PATH, GENERATION_MODEL, OPENAI_API_KEY

SYSTEM_PROMPT = "Trả lời CHỈ dựa trên context. Nếu không có → nói 'Không tìm thấy.'"  # same as setup_answers


def generate(client, question: str, contexts: list[str], retries: int = 4) -> tuple[str, str]:
    ctx = "\n\n".join(contexts)
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=GENERATION_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Context:\n{ctx}\n\nCâu hỏi: {question}"},
                ],
            )
            reported = getattr(resp, "model", None)
            model = reported if isinstance(reported, str) and reported.strip() else GENERATION_MODEL
            return resp.choices[0].message.content, model
        except Exception as error:  # report the real cause, then back off
            print(f"    attempt {attempt}/{retries} failed: {type(error).__name__}: {error}")
            if attempt == retries:
                raise
            time.sleep(2 ** attempt)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args(argv)
    if not args.live:
        parser.error("Generation calls the OpenAI API. Pass --live.")
    if not OPENAI_API_KEY:
        parser.error("Set OPENAI_API_KEY in .env.")

    from openai import OpenAI
    client = OpenAI(timeout=60, max_retries=0)
    with open(ANSWERS_PATH, encoding="utf-8") as f:
        answers = json.load(f)

    targets = [row for row in answers if row["generation_mode"] == "extractive_fallback"]
    print(f"{len(targets)} fallback answers to regenerate: {[r['id'] for r in targets]}")
    fixed = 0
    for row in targets:
        if not row["contexts"]:
            print(f"  id {row['id']}: no contexts, keeping fallback")
            continue
        try:
            answer, model = generate(client, row["question"], row["contexts"])
        except Exception:
            print(f"  id {row['id']}: still failing, keeping fallback")
            continue
        row.update(answer=answer, generation_mode="llm", generation_model=model)
        fixed += 1
        print(f"  id {row['id']}: regenerated with {model}")

    with open(ANSWERS_PATH, "w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=2)
    print(f"Regenerated {fixed}/{len(targets)}; saved {ANSWERS_PATH}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
