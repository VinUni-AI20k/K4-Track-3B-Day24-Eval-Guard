from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os, sys, json, re
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


DIAGNOSTIC_TREE = {
    "faithfulness": (
        "LLM tự bịa câu trả lời ngoài tài liệu",
        "Thắt chặt system prompt, giảm nhiệt độ (temperature) về 0"
    ),
    "context_recall": (
        "Hệ thống tìm kiếm bỏ sót đoạn văn đúng",
        "Cải thiện lại bước cắt đoạn hoặc bổ sung từ khóa BM25"
    ),
    "context_precision": (
        "Đoạn văn không liên quan bị xếp lên đầu",
        "Bổ sung tầng Cross-Encoder reranking hoặc lọc theo metadata"
    ),
    "answer_relevancy": (
        "Câu trả lời bị lệch trọng tâm câu hỏi",
        "Viết lại prompt hướng dẫn mô hình trả lời trực tiếp hơn"
    ),
}


METRIC_NAMES = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")
EVALUATOR_LLM_MODEL = "gpt-4o-mini"
EVALUATOR_EMBEDDING_MODEL = "text-embedding-3-small"
NAN_RETRIES = 2


def _score_rows(questions, answers, contexts, ground_truths, llm, embeddings) -> list[dict]:
    """Run RAGAS once and return one dict of 4 raw metric values per input row, in order."""
    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from ragas.run_config import RunConfig
    from datasets import Dataset

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        llm=llm, embeddings=embeddings,
        run_config=RunConfig(max_workers=8, timeout=120),
    )
    df = result.to_pandas()
    if len(df) != len(questions):
        raise ValueError(f"RAGAS returned {len(df)} rows for {len(questions)} questions.")
    return [{m: float(row[m]) for m in METRIC_NAMES} for _, row in df.iterrows()]


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Run real RAGAS evaluation with explicit evaluator models.

    No heuristic fallback: if RAGAS cannot produce a finite score, rows with NaN are
    re-evaluated up to NAN_RETRIES times and otherwise an error is raised.
    """
    import math
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings

    if not (len(questions) == len(answers) == len(contexts) == len(ground_truths)):
        raise ValueError("questions/answers/contexts/ground_truths must have equal length.")

    llm = ChatOpenAI(model=EVALUATOR_LLM_MODEL, temperature=0)
    embeddings = OpenAIEmbeddings(model=EVALUATOR_EMBEDDING_MODEL)

    scores = _score_rows(questions, answers, contexts, ground_truths, llm, embeddings)
    for attempt in range(NAN_RETRIES):
        missing = [i for i, row in enumerate(scores)
                   if not all(math.isfinite(v) for v in row.values())]
        if not missing:
            break
        print(f"  ⚠️  RAGAS NaN ở {len(missing)} câu, chạy lại lần {attempt + 1}...")
        retried = _score_rows([questions[i] for i in missing], [answers[i] for i in missing],
                              [contexts[i] for i in missing], [ground_truths[i] for i in missing],
                              llm, embeddings)
        for i, row in zip(missing, retried):
            # Keep finite values from earlier passes; fill only the metrics that were NaN.
            scores[i] = {m: row[m] if not math.isfinite(scores[i][m]) else scores[i][m]
                         for m in METRIC_NAMES}

    bad = [i for i, row in enumerate(scores) if not all(math.isfinite(v) for v in row.values())]
    if bad:
        raise ValueError(f"RAGAS trả NaN không khắc phục được ở các dòng {bad}; không điền điểm giả.")

    per_question = [
        EvalResult(question=q, answer=a, contexts=list(c), ground_truth=gt, **row)
        for q, a, c, gt, row in zip(questions, answers, contexts, ground_truths, scores)
    ]
    n = len(per_question)
    aggregate = {m: sum(getattr(r, m) for r in per_question) / n if n else 0.0
                 for m in METRIC_NAMES}
    return {
        **aggregate,
        "per_question": per_question,
        "metadata": {"evaluator_models": [EVALUATOR_LLM_MODEL, EVALUATOR_EMBEDDING_MODEL]},
    }


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    if not eval_results:
        return []

    failures = []
    for r in eval_results:
        metric_scores = {
            "faithfulness": r.faithfulness,
            "context_recall": r.context_recall,
            "context_precision": r.context_precision,
            "answer_relevancy": r.answer_relevancy,
        }
        avg_score = sum(metric_scores.values()) / len(metric_scores)
        worst_metric = min(metric_scores, key=metric_scores.get)
        worst_score = metric_scores[worst_metric]
        diagnosis, suggested_fix = DIAGNOSTIC_TREE.get(
            worst_metric,
            ("Lỗi không xác định", "Kiểm tra lại cấu hình pipeline")
        )
        failures.append({
            "question": r.question,
            "worst_metric": worst_metric,
            "score": float(worst_score),
            "avg_score": float(avg_score),
            "diagnosis": diagnosis,
            "suggested_fix": suggested_fix,
        })

    failures.sort(key=lambda x: x["avg_score"])
    return failures[:bottom_n]


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
