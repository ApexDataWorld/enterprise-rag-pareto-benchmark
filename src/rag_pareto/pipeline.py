"""End-to-end benchmark pipeline."""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

from .chunking import chunk_documents
from .data import load_documents, load_queries
from .generation import estimate_cost_latency, generate_answer
from .metrics import aggregate, generation_metrics, retrieval_metrics
from .plots import write_line_svg, write_scatter_svg
from .retrieval import Retriever
from .stats import benjamini_hochberg, bootstrap_ci, paired_sign_test
from .text import tokenize
from .tracking import write_run_metadata


def run_benchmark(config: dict[str, Any], output_dir_override: str | None = None) -> dict[str, Path]:
    seed = int(config.get("seed", 42))
    random.seed(seed)
    output_dir = Path(output_dir_override or config["output_dir"])
    figures_dir = output_dir / "figures"
    tables_dir = output_dir / "tables"
    traces_dir = output_dir / "traces"
    for directory in (figures_dir, tables_dir, traces_dir):
        directory.mkdir(parents=True, exist_ok=True)

    documents = load_documents(config["corpus_path"])
    queries = load_queries(config["questions_path"])
    chunk_cfg = config["chunk"]
    chunks = chunk_documents(documents, int(chunk_cfg["size_tokens"]), int(chunk_cfg["overlap_tokens"]))

    query_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    traces: dict[str, Any] = {"chunks": len(chunks), "queries": []}

    for variant in config["variants"]:
        retriever = Retriever(
            chunks,
            variant["retriever"],
            embedding_provider_config=config.get("embedding_provider"),
            hybrid_weights=config.get("hybrid_weights"),
        )
        variant_rows = []
        for query in queries:
            top_k = int(variant["top_k"])
            retrieved_scored = retriever.search(query.question, top_k=top_k, rerank=bool(variant["rerank"]))
            retrieved = [chunk for chunk, _ in retrieved_scored]
            answer = generate_answer(query, retrieved, variant["generator"])
            input_tokens = len(tokenize(query.question)) + sum(len(tokenize(chunk.text)) for chunk in retrieved)
            estimate = estimate_cost_latency(
                top_k,
                bool(variant["rerank"]),
                variant["generator"],
                len(chunks),
                input_tokens,
                variant["retriever"],
                config.get("cost_model", {}),
            )
            row = {
                "variant": variant["name"],
                "query_id": query.id,
                "query_type": query.query_type,
                "top_k": float(top_k),
                "rerank": str(bool(variant["rerank"])).lower(),
                "retriever": variant["retriever"],
                "retrieval_cost": estimate.retrieval_cost,
                "rerank_cost": estimate.rerank_cost,
                "generation_cost": estimate.generation_cost,
                "total_cost": estimate.total_cost,
                "cost_usd": estimate.total_cost,
                "retrieval_latency_ms": estimate.retrieval_latency_ms,
                "rerank_latency_ms": estimate.rerank_latency_ms,
                "generation_latency_ms": estimate.generation_latency_ms,
                "total_latency_ms": estimate.total_latency_ms,
                "latency_ms": estimate.total_latency_ms,
            }
            row.update(retrieval_metrics(query, retrieved, top_k))
            row.update(generation_metrics(query, answer, retrieved))
            variant_rows.append(row)
            query_rows.append(row)
            traces["queries"].append(
                {
                    "variant": variant["name"],
                    "query_id": query.id,
                    "query_type": query.query_type,
                    "retrieved_chunk_ids": [chunk.id for chunk in retrieved],
                    "retrieved_doc_ids": [chunk.doc_id for chunk in retrieved],
                    "expected_doc_ids": list(query.relevant_doc_ids),
                    "expected_chunk_ids": list(query.relevant_chunk_ids),
                    "answer": answer,
                }
            )
        summary = {"variant": variant["name"], **aggregate(variant_rows)}
        summary["pareto_optimal"] = False
        summary_rows.append(summary)

    _mark_pareto(summary_rows)
    stats_rows = _comparison_rows(query_rows, baseline=str(config["variants"][0]["name"]))
    ci_rows = _confidence_interval_rows(query_rows, seed)
    query_type_rows = _query_type_summary_rows(query_rows)
    pareto_rows = _pareto_rows(summary_rows)

    query_path = tables_dir / "query_metrics.csv"
    summary_path = tables_dir / "summary_metrics.csv"
    stats_path = tables_dir / "statistical_comparisons.csv"
    ci_path = tables_dir / "confidence_intervals.csv"
    query_type_path = tables_dir / "query_type_summary.csv"
    pareto_path = tables_dir / "pareto_frontier_data.csv"
    latex_path = tables_dir / "final_latex_table_values.tex"
    final_summary_path = output_dir / "final_result_summary.md"
    consistency_path = output_dir / "v3_consistency_notes.md"
    traces_path = traces_dir / "retrieval_traces.json"
    _write_csv(query_path, query_rows)
    _write_csv(summary_path, summary_rows)
    _write_csv(stats_path, stats_rows)
    _write_csv(ci_path, ci_rows)
    _write_csv(query_type_path, query_type_rows)
    _write_csv(pareto_path, pareto_rows)
    _write_latex_table(latex_path, summary_rows)
    _write_final_summary(final_summary_path, summary_rows, stats_rows, config)
    _write_consistency_notes(consistency_path, summary_rows, config)
    traces_path.write_text(json.dumps(traces, indent=2), encoding="utf-8")

    plot_rows = [{key: str(value).lower() if isinstance(value, bool) else str(value) for key, value in row.items()} for row in summary_rows]
    write_scatter_svg(plot_rows, "cost_usd", "hallucination_risk", "variant", figures_dir / "pareto_frontier.svg", "Pareto Frontier: Cost vs Hallucination Risk")
    write_scatter_svg(plot_rows, "latency_ms", "faithfulness", "variant", figures_dir / "latency_vs_quality.svg", "Latency vs Faithfulness")
    write_scatter_svg(plot_rows, "cost_usd", "faithfulness", "variant", figures_dir / "cost_vs_quality.svg", "Cost vs Faithfulness")
    write_scatter_svg(plot_rows, "hallucination_risk", "faithfulness", "variant", figures_dir / "risk_vs_faithfulness.svg", "Hallucination Risk vs Faithfulness")
    rerank_rows = [row for row in plot_rows if row["variant"] in {"lexical_k5", "lexical_k5_rerank", "dense_hash_k5", "dense_hash_k5_rerank"}]
    write_scatter_svg(rerank_rows, "latency_ms", "hallucination_risk", "variant", figures_dir / "reranker_impact.svg", "Reranker Impact")
    topk_rows = [row for row in plot_rows if "hybrid" in row["variant"]]
    write_line_svg(topk_rows, "top_k", "context_precision", figures_dir / "topk_sensitivity.svg", "Top-k Sensitivity")
    qt_plot_rows = [
        {key: str(value) for key, value in row.items()}
        for row in query_type_rows
        if row["variant"] == "hybrid_dense_hash_k5_rerank"
    ]
    write_scatter_svg(qt_plot_rows, "query_type_index", "faithfulness", "query_type", figures_dir / "query_type_performance.svg", "Query Type Performance")

    artifact_paths = [
        query_path,
        summary_path,
        stats_path,
        ci_path,
        query_type_path,
        pareto_path,
        latex_path,
        final_summary_path,
        consistency_path,
        traces_path,
        *(figures_dir.glob("*.*")),
    ]
    write_run_metadata(output_dir, config, artifact_paths)
    return {
        "output_dir": output_dir,
        "query_metrics": query_path,
        "summary_metrics": summary_path,
        "statistical_comparisons": stats_path,
        "confidence_intervals": ci_path,
        "query_type_summary": query_type_path,
        "pareto_frontier_data": pareto_path,
        "final_summary": final_summary_path,
        "consistency_notes": consistency_path,
        "traces": traces_path,
    }


def _mark_pareto(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        dominated = False
        for other in rows:
            if other is row:
                continue
            better_or_equal = (
                other["recall_at_k"] >= row["recall_at_k"]
                and other["faithfulness"] >= row["faithfulness"]
                and other["total_latency_ms"] <= row["total_latency_ms"]
                and other["total_cost"] <= row["total_cost"]
                and other["hallucination_risk"] <= row["hallucination_risk"]
            )
            strictly_better = (
                other["recall_at_k"] > row["recall_at_k"]
                or other["faithfulness"] > row["faithfulness"]
                or other["total_latency_ms"] < row["total_latency_ms"]
                or other["total_cost"] < row["total_cost"]
                or other["hallucination_risk"] < row["hallucination_risk"]
            )
            dominated = dominated or (better_or_equal and strictly_better)
        row["pareto_optimal"] = not dominated


def _comparison_rows(query_rows: list[dict[str, Any]], baseline: str) -> list[dict[str, Any]]:
    variants = sorted({str(row["variant"]) for row in query_rows})
    metrics = ["recall_at_k", "mrr", "ndcg_at_k", "faithfulness", "hallucination_risk", "latency_ms", "cost_usd"]
    rows = []
    by_variant = {variant: [row for row in query_rows if row["variant"] == variant] for variant in variants}
    for variant in variants:
        if variant == baseline:
            continue
        for metric in metrics:
            base_values = [float(row[metric]) for row in by_variant[baseline]]
            candidate_values = [float(row[metric]) for row in by_variant[variant]]
            result = paired_sign_test(base_values, candidate_values)
            rows.append({"baseline": baseline, "candidate": variant, "metric": metric, **result})
    return benjamini_hochberg(rows)


def _confidence_interval_rows(query_rows: list[dict[str, Any]], seed: int) -> list[dict[str, Any]]:
    metrics = ["faithfulness", "hallucination_risk", "context_precision", "latency_ms", "cost_usd"]
    rows = []
    variants = sorted({str(row["variant"]) for row in query_rows})
    for variant_index, variant in enumerate(variants):
        variant_rows = [row for row in query_rows if row["variant"] == variant]
        for metric_index, metric in enumerate(metrics):
            values = [float(row[metric]) for row in variant_rows]
            ci = bootstrap_ci(values, seed + variant_index * 97 + metric_index)
            rows.append({"variant": variant, "metric": metric, **ci})
    return rows


def _query_type_summary_rows(query_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics = ["recall_at_k", "mrr", "ndcg_at_k", "context_precision", "faithfulness", "hallucination_risk", "latency_ms", "cost_usd"]
    rows = []
    query_types = sorted({str(row["query_type"]) for row in query_rows})
    variants = sorted({str(row["variant"]) for row in query_rows})
    query_type_index = {query_type: index + 1 for index, query_type in enumerate(query_types)}
    for variant in variants:
        for query_type in query_types:
            group = [row for row in query_rows if row["variant"] == variant and row["query_type"] == query_type]
            if not group:
                continue
            row = {
                "variant": variant,
                "query_type": query_type,
                "query_type_index": float(query_type_index[query_type]),
                "count": float(len(group)),
            }
            for metric in metrics:
                row[metric] = sum(float(item[metric]) for item in group) / len(group)
            rows.append(row)
    return rows


def _pareto_rows(summary_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for row in summary_rows:
        if row["pareto_optimal"]:
            reason = _pareto_reason(row, summary_rows)
        else:
            dominators = [
                other["variant"]
                for other in summary_rows
                if other is not row and _dominates(other, row)
            ]
            reason = "dominated_by=" + "|".join(dominators)
        rows.append(
            {
                "variant": row["variant"],
                "pareto_optimal": row["pareto_optimal"],
                "recall_at_k": row["recall_at_k"],
                "faithfulness": row["faithfulness"],
                "hallucination_risk": row["hallucination_risk"],
                "total_latency_ms": row["total_latency_ms"],
                "total_cost": row["total_cost"],
                "reason": reason,
            }
        )
    return rows


def _dominates(other: dict[str, Any], row: dict[str, Any]) -> bool:
    better_or_equal = (
        other["recall_at_k"] >= row["recall_at_k"]
        and other["faithfulness"] >= row["faithfulness"]
        and other["total_latency_ms"] <= row["total_latency_ms"]
        and other["total_cost"] <= row["total_cost"]
        and other["hallucination_risk"] <= row["hallucination_risk"]
    )
    strictly_better = (
        other["recall_at_k"] > row["recall_at_k"]
        or other["faithfulness"] > row["faithfulness"]
        or other["total_latency_ms"] < row["total_latency_ms"]
        or other["total_cost"] < row["total_cost"]
        or other["hallucination_risk"] < row["hallucination_risk"]
    )
    return better_or_equal and strictly_better


def _pareto_reason(row: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    best_latency = min(rows, key=lambda item: item["total_latency_ms"])["variant"]
    best_cost = min(rows, key=lambda item: item["total_cost"])["variant"]
    best_recall = max(rows, key=lambda item: item["recall_at_k"])["variant"]
    best_faithfulness = max(rows, key=lambda item: item["faithfulness"])["variant"]
    best_risk = min(rows, key=lambda item: item["hallucination_risk"])["variant"]
    labels = []
    if row["variant"] == best_latency:
        labels.append("lowest_latency")
    if row["variant"] == best_cost:
        labels.append("lowest_cost")
    if row["variant"] == best_recall:
        labels.append("highest_recall")
    if row["variant"] == best_faithfulness:
        labels.append("highest_faithfulness")
    if row["variant"] == best_risk:
        labels.append("lowest_hallucination_risk")
    return "|".join(labels) if labels else "non_dominated_tradeoff"


def _write_latex_table(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "% Auto-generated by rag_pareto.pipeline. Do not edit values manually.",
        "\\begin{tabular}{lrrrrrr}",
        "\\toprule",
        "Configuration & Recall@k & MRR & NDCG@k & Faithfulness & Latency ms & Cost USD \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f"{row['variant']} & {row['recall_at_k']:.3f} & {row['mrr']:.3f} & "
            f"{row['ndcg_at_k']:.3f} & {row['faithfulness']:.3f} & "
            f"{row['total_latency_ms']:.1f} & {row['total_cost']:.8f} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_final_summary(path: Path, rows: list[dict[str, Any]], stats_rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    lines = [
        "# Final V3 Result Summary",
        "",
        "This file is generated by `python -m rag_pareto.cli run --config configs/default.yaml`.",
        "",
        f"- Configurations executed: {len(rows)}",
        f"- Dense-hash retrieval provider: {config.get('dense_retrieval', {}).get('provider', 'not_configured')}",
        f"- Dense embedding dimension: {config.get('dense_retrieval', {}).get('embedding_dimension', 'not_configured')}",
        f"- Dense similarity/index: {config.get('dense_retrieval', {}).get('similarity', 'not_configured')} / {config.get('dense_retrieval', {}).get('index', 'not_configured')}",
        "",
        "## Summary Metrics",
        "",
        "| Configuration | Recall@k | MRR | NDCG@k | Context Precision | Faithfulness | Hallucination Risk | Latency ms | Cost USD | Pareto |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['variant']} | {row['recall_at_k']:.4f} | {row['mrr']:.4f} | {row['ndcg_at_k']:.4f} | "
            f"{row['context_precision']:.4f} | {row['faithfulness']:.4f} | {row['hallucination_risk']:.4f} | "
            f"{row['total_latency_ms']:.1f} | {row['total_cost']:.8f} | {row['pareto_optimal']} |"
        )
    dense_stats = [
        row
        for row in stats_rows
        if row["candidate"] in {"dense_hash_k5", "dense_hash_k5_rerank", "hybrid_dense_hash_k5_rerank"}
        and row["metric"] in {"faithfulness", "latency_ms", "cost_usd"}
    ]
    lines.extend(["", "## Dense Variant Statistical Comparisons", ""])
    for row in dense_stats:
        lines.append(
            f"- {row['candidate']} vs {row['baseline']} on {row['metric']}: "
            f"delta={float(row['mean_delta']):.6f}, raw_p={float(row['raw_p_value']):.6g}, "
            f"BH_p={float(row['bh_adjusted_p_value']):.6g}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_consistency_notes(path: Path, rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    variants = [row["variant"] for row in rows]
    dense = config.get("dense_retrieval", {})
    pareto_count = sum(1 for row in rows if row["pareto_optimal"])
    lines = [
        "# V3 Consistency Notes",
        "",
        "## Experiment Scope",
        "",
        f"The generated benchmark executes {len(variants)} configurations: {', '.join(variants)}.",
        "The current repo does not contain LaTeX source, so this run cannot directly edit or validate manuscript tables.",
        "The uploaded PDF should be treated as stale if it still says six configurations or lists dense-hash retrieval as future work.",
        "",
        "## Dense Retrieval Implementation",
        "",
        f"- Model/provider: `{dense.get('model_name', 'local_hashing_embedding_v1')}`.",
        f"- Dimension: `{dense.get('embedding_dimension', 96)}`.",
        f"- Similarity: `{dense.get('similarity', 'cosine')}`.",
        f"- Index: `{dense.get('index', 'local_in_memory_exhaustive_scan')}`.",
        "- External dependencies/API keys: none.",
        "- Important: this is a deterministic local hashing-embedding provider, not Sentence Transformers, MiniLM, or FAISS.",
        f"- Hybrid dense fusion: `{dense.get('score_fusion', 'see retrieval.py')}`.",
        "- Reranking: exact token overlap plus title-hit bonus over the expanded candidate set.",
        "- Dense latency includes the configured `dense_embedding_latency_ms` estimate in `configs/default.yaml`.",
        "",
        "## Pareto Verification",
        "",
        f"Pareto-optimal configurations after recomputation: {pareto_count} of {len(rows)}.",
        "Dominated and non-dominated labels are written to `tables/pareto_frontier_data.csv`.",
        "A configuration is dominated only if another configuration has greater-or-equal recall and faithfulness, lower-or-equal latency/cost/risk, and is strictly better on at least one of those objectives.",
        "",
        "## Paper-Side Required Fixes",
        "",
        "- Table I and appendix config should list all 9 generated configurations.",
        "- Methods should describe deterministic hashing embeddings, 96 dimensions, cosine similarity, and local exhaustive scan unless the code is changed to use MiniLM/FAISS.",
        "- Figure references should use the generated PDFs, not SVGs.",
        "- Dense-hash retrieval should not be described as future work in V3.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
