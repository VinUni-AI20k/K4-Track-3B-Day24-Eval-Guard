from __future__ import annotations

"""Phase A: RAGAS Production Evaluation — 50q, 3 distributions, cluster analysis."""

import json
import os
import sys
from dataclasses import asdict, dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH, ANSWERS_PATH, ARTIFACTS_DIR
from src.experiment_support import write_json

Distribution = str  # "factual" | "multi_hop" | "adversarial"

DIAGNOSTIC_TREE = {
    "faithfulness":      ("LLM hallucinating", "Tighten system prompt, lower temperature"),
    "context_recall":    ("Missing relevant chunks", "Improve chunking or add BM25"),
    "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
    "answer_relevancy":  ("Answer doesn't match question", "Improve prompt template"),
}


@dataclass
class RagasResult:
    question_id: int
    distribution: Distribution
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float

    @property
    def avg_score(self) -> float:
        return (self.faithfulness + self.answer_relevancy +
                self.context_precision + self.context_recall) / 4

    @property
    def worst_metric(self) -> str:
        scores = {
            "faithfulness":      self.faithfulness,
            "answer_relevancy":  self.answer_relevancy,
            "context_precision": self.context_precision,
            "context_recall":    self.context_recall,
        }
        return min(scores, key=scores.get)


# ─── Đã implement sẵn ────────────────────────────────────────────────────────

@dataclass
class RagasEvaluation:
    """Task 2 output: measured rows plus model identifiers reported by m4."""
    results: list[RagasResult]
    evaluator_models: list[str]

def load_test_set_50q(path: str = TEST_SET_PATH) -> list[dict]:
    """Load 50q test set với 3 distributions."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_answers(path: str = ANSWERS_PATH) -> list[dict]:
    """Load pre-generated answers từ setup_answers.py."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"answers_50q.json không tìm thấy tại {path}\n"
            "→ Chạy trước: python scripts/setup_answers.py --live"
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict]) -> dict:
    """Provided exporter: preserve the student-produced Task 3 rows verbatim."""
    per_dist: dict[str, dict] = {}
    for dist in ["factual", "multi_hop", "adversarial"]:
        subset = [r for r in results if r.distribution == dist]
        if subset:
            per_dist[dist] = {
                "count": len(subset),
                "faithfulness":      sum(r.faithfulness for r in subset) / len(subset),
                "answer_relevancy":  sum(r.answer_relevancy for r in subset) / len(subset),
                "context_precision": sum(r.context_precision for r in subset) / len(subset),
                "context_recall":    sum(r.context_recall for r in subset) / len(subset),
                "avg_score":         sum(r.avg_score for r in subset) / len(subset),
            }

    report = {
        "total_questions": len(results),
        "per_question": [asdict(r) for r in results],
        "per_distribution": per_dist,
        "failure_clusters": clusters,
        "bottom_10": bottom,
    }
    return report


def save_phase_a_report(results: list[RagasResult], clusters: dict, bottom: list[dict],
                        path: str = os.path.join(ARTIFACTS_DIR, "ragas_50q.json")) -> None:
    write_json(path, build_phase_a_report(results, clusters, bottom))



# ─── Tasks 1-4: Sinh viên implement ──────────────────────────────────────────

DISTRIBUTIONS = ("factual", "multi_hop", "adversarial")
METRICS = tuple(DIAGNOSTIC_TREE)

# Ghi chú bổ sung cho bẫy adversarial: version conflict (v2023/v2024, mật khẩu v1/v2)
# và negation trap. Điểm thấp ở nhóm này cần đọc answer/contexts trước khi kết luận.
ADVERSARIAL_NOTE = ("Câu adversarial: kiểm tra pipeline có dùng đúng phiên bản chính sách "
                    "hiện hành và giữ đúng phủ định/điều kiện không")
ADVERSARIAL_FIX = ("Thêm metadata version/effective_date khi chunking, lọc hoặc ưu tiên "
                   "bản hiện hành khi rerank, và yêu cầu prompt nêu rõ phiên bản áp dụng")


def group_by_distribution(test_set: list[dict]) -> dict[str, list[dict]]:
    """Task 1: Nhóm 50 câu hỏi theo 3 distributions.

    Returns:
        {"factual": [...], "multi_hop": [...], "adversarial": [...]}
    """
    groups: dict[str, list[dict]] = {d: [] for d in DISTRIBUTIONS}
    for item in test_set:
        dist = item["distribution"]
        if dist not in groups:
            raise ValueError(f"Unknown distribution {dist!r} for question {item.get('id')}.")
        groups[dist].append(item)
    return groups


def run_ragas_50q(answers: list[dict]) -> RagasEvaluation:
    """Task 2: Chạy RAGAS 4 metrics trên toàn bộ 50 câu hỏi qua m4.evaluate_ragas().

    Kết quả giữ đúng thứ tự answers; evaluator_models lấy trực tiếp từ metadata m4.
    """
    from src.m4_eval import evaluate_ragas

    questions = [a["question"] for a in answers]
    ans_texts = [a["answer"] for a in answers]
    contexts = [a["contexts"] for a in answers]
    ground_truths = [a["ground_truth"] for a in answers]

    raw = evaluate_ragas(questions, ans_texts, contexts, ground_truths)
    per_q = raw.get("per_question", [])
    if len(per_q) != len(answers):
        raise ValueError(f"m4 returned {len(per_q)} rows for {len(answers)} answers.")
    evaluator_models = raw.get("metadata", {}).get("evaluator_models")
    if not evaluator_models:
        raise ValueError("m4 must report metadata.evaluator_models; no JUDGE_MODEL fallback.")

    results = []
    for a, pq in zip(answers, per_q):
        scores = {m: float(getattr(pq, m)) for m in METRICS}
        for m, v in scores.items():
            if not (0.0 <= v <= 1.0):  # also rejects NaN
                raise ValueError(f"Question {a['id']}: {m}={v} is not a finite score in [0, 1].")
        results.append(RagasResult(
            question_id=a["id"], distribution=a["distribution"],
            question=a["question"], answer=a["answer"],
            contexts=a["contexts"], ground_truth=a["ground_truth"],
            faithfulness=scores["faithfulness"], answer_relevancy=scores["answer_relevancy"],
            context_precision=scores["context_precision"], context_recall=scores["context_recall"],
        ))
    return RagasEvaluation(results, list(evaluator_models))


def bottom_10(results: list[RagasResult]) -> list[dict]:
    """Task 3: Lấy 10 câu hỏi có avg_score thấp nhất, kèm diagnosis/suggested_fix.

    Returns:
        [{"rank": 1, "question_id": ..., "distribution": ...,
          "question": ..., "avg_score": ..., "worst_metric": ...,
          "diagnosis": ..., "suggested_fix": ...}, ...]
    """
    ordered = sorted(results, key=lambda r: (r.avg_score, r.question_id))[:10]
    output = []
    for rank, r in enumerate(ordered, 1):
        worst = r.worst_metric
        diagnosis, fix = DIAGNOSTIC_TREE[worst]
        diagnosis = f"{diagnosis} ({worst}={getattr(r, worst):.2f})"
        if r.distribution == "adversarial":
            diagnosis = f"{diagnosis}. {ADVERSARIAL_NOTE}"
            fix = f"{fix}; {ADVERSARIAL_FIX}"
        output.append({
            "rank": rank,
            "question_id": r.question_id,
            "distribution": r.distribution,
            "question": r.question,
            "avg_score": round(r.avg_score, 6),
            "worst_metric": worst,
            "diagnosis": diagnosis,
            "suggested_fix": fix,
        })
    return output


def cluster_analysis(results: list[RagasResult]) -> dict:
    """Task 4: Phân tích failure clusters theo (worst_metric × distribution).

    Matrix thống kê worst_metric của mọi câu, không coi mọi câu là một failure.
    Nhóm yếu nhất = distribution có avg_score trung bình thấp nhất (bỏ nhóm rỗng).
    Tổng matrix theo cột chỉ là kích thước nhóm 20/20/10, không đo chất lượng.
    """
    matrix = {m: {d: 0 for d in DISTRIBUTIONS} for m in METRICS}
    for r in results:
        matrix[r.worst_metric][r.distribution] += 1

    means = {}
    for d in DISTRIBUTIONS:
        subset = [r.avg_score for r in results if r.distribution == d]
        if subset:  # nhóm rỗng bị bỏ, không gán 0
            means[d] = sum(subset) / len(subset)
    if not means:
        return {"matrix": matrix, "distribution_avg_scores": {},
                "dominant_failure_distribution": None, "dominant_failure_metric": None,
                "insight": "Không có kết quả để phân tích."}

    dominant_dist = min(means, key=means.get)
    totals = {m: sum(matrix[m].values()) for m in METRICS}
    dominant_metric = max(METRICS, key=lambda m: totals[m])
    metric_in_weakest = max(METRICS, key=lambda m: matrix[m][dominant_dist])
    ranking = ", ".join(f"{d}={means[d]:.3f}" for d in sorted(means, key=means.get))
    insight = (
        f"Điểm trung bình theo nhóm (thấp→cao): {ranking}. Nhóm yếu nhất là "
        f"'{dominant_dist}'; trong nhóm này worst_metric hay gặp nhất là "
        f"'{metric_in_weakest}' ({matrix[metric_in_weakest][dominant_dist]} câu). "
        f"Trên toàn bộ {len(results)} câu, '{dominant_metric}' là worst_metric phổ biến nhất "
        f"({totals[dominant_metric]} câu) → {DIAGNOSTIC_TREE[dominant_metric][0]}; "
        f"gợi ý: {DIAGNOSTIC_TREE[dominant_metric][1]}."
    )
    return {"matrix": matrix, "distribution_avg_scores": means,
            "dominant_failure_distribution": dominant_dist,
            "dominant_failure_metric": dominant_metric, "insight": insight}


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from scripts.run_experiments import main
    raise SystemExit(main(["--phase", "a", *sys.argv[1:]]))
