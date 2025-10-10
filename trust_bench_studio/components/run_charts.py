"""Visualization helpers for run metrics."""

from __future__ import annotations

from typing import Optional, Sequence

import streamlit as st

from trust_bench_studio.utils import RunSummary, diff_metrics


def _format_value(value: Optional[float]) -> str:
    if value is None:
        return "-"
    absolute = abs(value)
    if absolute >= 100:
        formatted = f"{value:.0f}"
    elif absolute >= 10:
        formatted = f"{value:.1f}"
    elif absolute >= 1:
        formatted = f"{value:.2f}"
    else:
        formatted = f"{value:.3f}"
    return formatted.rstrip("0").rstrip(".") if "." in formatted else formatted


def _format_delta(value: Optional[float]) -> str:
    if value is None:
        return "-"
    formatted = _format_value(value)
    return formatted if value <= 0 else f"+{formatted}"


def _find_baseline_index(
    summaries: Sequence[Optional[RunSummary]], active_index: int
) -> Optional[int]:
    for idx, summary in enumerate(summaries):
        if idx == active_index or not summary or not summary.metrics:
            continue
        return idx
    return None


def render_run_panels(
    run_names: Sequence[str],
    active_index: int,
    summaries: Sequence[Optional[RunSummary]],
) -> None:
    """Render summary charts and comparison tables."""
    st.subheader("Evaluation Metrics")

    if not run_names:
        st.info("No evaluation runs available yet. Trigger an evaluation to begin.")
        return

    if active_index >= len(summaries):
        st.warning("Selected run index is outside the known summaries.")
        return

    active_summary = summaries[active_index]
    if not active_summary or not active_summary.metrics:
        st.warning("Selected run does not expose numeric metrics.")
        return

    baseline_index = _find_baseline_index(summaries, active_index)
    baseline_summary = summaries[baseline_index] if baseline_index is not None else None

    if baseline_summary:
        st.caption(
            f"Comparing `{run_names[active_index]}` against `{run_names[baseline_index]}`."
        )
    else:
        st.caption(f"Showing metrics for `{run_names[active_index]}`.")

    metrics = diff_metrics(
        baseline=baseline_summary.metrics if baseline_summary else None,
        candidate=active_summary.metrics,
    )

    if not metrics:
        st.info("Metrics discovered, but nothing comparable across runs yet.")
        return

    progress_metric = None
    for key, value in active_summary.metrics.items():
        if not isinstance(value, (int, float)):
            continue
        normalized_key = str(key).lower()
        if "progress" in normalized_key and 0.0 <= float(value) <= 1.0:
            progress_metric = (key, float(value))
            break

    if progress_metric:
        metric_label, metric_value = progress_metric
        st.progress(
            metric_value,
            text=f"{metric_label}: {int(metric_value * 100)}%",
        )

    key_metrics = list(active_summary.metrics.items())[: min(3, len(active_summary.metrics))]
    if key_metrics:
        columns = st.columns(len(key_metrics))
        for (metric_name, metric_value), column in zip(key_metrics, columns):
            delta = metrics.get(metric_name, (None, None, None))[2]
            column.metric(
                metric_name,
                _format_value(metric_value),
                _format_delta(delta),
            )

    rows = []
    for metric, (base, cand, delta) in metrics.items():
        rows.append(
            {
                "metric": metric,
                "baseline": _format_value(base),
                "selected": _format_value(cand),
                "delta": _format_delta(delta),
            }
        )

    st.dataframe(rows, hide_index=True, use_container_width=True)
