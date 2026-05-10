"""Dependency-free SVG plots for paper artifacts."""

from __future__ import annotations

from html import escape
from pathlib import Path


def write_scatter_svg(rows: list[dict[str, str]], x_key: str, y_key: str, label_key: str, path: Path, title: str) -> None:
    width, height = 980, 540
    margin_left, margin_top, margin_bottom = 86, 76, 76
    plot_width, plot_height = 600, 360
    plot_right = margin_left + plot_width
    plot_bottom = margin_top + plot_height
    xs = [float(row[x_key]) for row in rows]
    ys = [float(row[y_key]) for row in rows]
    min_x, max_x = _padded_domain(xs)
    min_y, max_y = _padded_domain(ys)

    def sx(value: float) -> float:
        return margin_left + (value - min_x) / ((max_x - min_x) or 1.0) * plot_width

    def sy(value: float) -> float:
        return plot_bottom - (value - min_y) / ((max_y - min_y) or 1.0) * plot_height

    parts = [_svg_header(width, height), f"<text x='{margin_left}' y='38' class='title'>{escape(title)}</text>"]
    _append_axes(parts, margin_left, margin_top, plot_right, plot_bottom, x_key, y_key)
    for index, row in enumerate(rows):
        x = sx(float(row[x_key]))
        y = sy(float(row[y_key]))
        frontier = row.get("pareto_optimal", "false") == "true"
        css = "frontier" if frontier else f"series-{index % 6}"
        parts.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='7' class='point {css}'/>")
    _append_legend(parts, rows, label_key, plot_right + 42, margin_top + 14)
    parts.append(f"<text x='{(margin_left + plot_right) / 2:.2f}' y='{height - 26}' class='label'>{escape(_label(x_key))}</text>")
    parts.append(f"<text x='24' y='{(margin_top + plot_bottom) / 2:.2f}' class='label' transform='rotate(-90 24 {(margin_top + plot_bottom) / 2:.2f})'>{escape(_label(y_key))}</text>")
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")
    _write_basic_pdf(rows, x_key, y_key, label_key, path.with_suffix(".pdf"), title, chart_type="scatter")


def write_line_svg(rows: list[dict[str, str]], x_key: str, y_key: str, path: Path, title: str) -> None:
    sorted_rows = sorted(rows, key=lambda row: float(row[x_key]))
    width, height = 980, 540
    margin_left, margin_top, margin_bottom = 86, 76, 76
    plot_width, plot_height = 600, 360
    plot_right = margin_left + plot_width
    plot_bottom = margin_top + plot_height
    xs = [float(row[x_key]) for row in sorted_rows]
    ys = [float(row[y_key]) for row in sorted_rows]
    min_x, max_x = _padded_domain(xs)
    min_y, max_y = _padded_domain(ys)

    def sx(value: float) -> float:
        return margin_left + (value - min_x) / ((max_x - min_x) or 1.0) * plot_width

    def sy(value: float) -> float:
        return plot_bottom - (value - min_y) / ((max_y - min_y) or 1.0) * plot_height

    points = " ".join(f"{sx(float(row[x_key])):.2f},{sy(float(row[y_key])):.2f}" for row in sorted_rows)
    parts = [_svg_header(width, height), f"<text x='{margin_left}' y='38' class='title'>{escape(title)}</text>"]
    _append_axes(parts, margin_left, margin_top, plot_right, plot_bottom, x_key, y_key)
    parts.append(f"<polyline points='{points}' class='line'/>")
    for index, row in enumerate(sorted_rows):
        x = sx(float(row[x_key]))
        y = sy(float(row[y_key]))
        parts.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='6' class='point series-{index % 6}'/>")
    _append_legend(parts, sorted_rows, "variant", plot_right + 42, margin_top + 14)
    parts.append(f"<text x='{(margin_left + plot_right) / 2:.2f}' y='{height - 26}' class='label'>{escape(_label(x_key))}</text>")
    parts.append(f"<text x='24' y='{(margin_top + plot_bottom) / 2:.2f}' class='label' transform='rotate(-90 24 {(margin_top + plot_bottom) / 2:.2f})'>{escape(_label(y_key))}</text>")
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")
    _write_basic_pdf(sorted_rows, x_key, y_key, "variant", path.with_suffix(".pdf"), title, chart_type="line")


def _append_axes(parts: list[str], left: int, top: int, right: int, bottom: int, x_key: str, y_key: str) -> None:
    parts.append(f"<rect x='{left}' y='{top}' width='{right-left}' height='{bottom-top}' class='plot-bg'/>")
    parts.append(f"<line x1='{left}' y1='{bottom}' x2='{right}' y2='{bottom}' class='axis'/>")
    parts.append(f"<line x1='{left}' y1='{top}' x2='{left}' y2='{bottom}' class='axis'/>")
    for i in range(1, 5):
        x = left + (right - left) * i / 4
        y = top + (bottom - top) * i / 4
        parts.append(f"<line x1='{x:.2f}' y1='{top}' x2='{x:.2f}' y2='{bottom}' class='grid'/>")
        parts.append(f"<line x1='{left}' y1='{y:.2f}' x2='{right}' y2='{y:.2f}' class='grid'/>")


def _append_legend(parts: list[str], rows: list[dict[str, str]], label_key: str, x: int, y: int) -> None:
    parts.append(f"<text x='{x}' y='{y - 20}' class='legend-title'>Variants</text>")
    for index, row in enumerate(rows):
        item_y = y + index * 30
        css = "frontier" if row.get("pareto_optimal", "false") == "true" else f"series-{index % 6}"
        label = escape(row[label_key])
        suffix = " Pareto" if row.get("pareto_optimal", "false") == "true" else ""
        parts.append(f"<circle cx='{x}' cy='{item_y}' r='7' class='point {css}'/>")
        parts.append(f"<text x='{x + 18}' y='{item_y + 4}' class='legend'>{label}{suffix}</text>")


def _padded_domain(values: list[float]) -> tuple[float, float]:
    min_value, max_value = min(values), max(values)
    spread = (max_value - min_value) or max(abs(max_value), 1.0)
    pad = spread * 0.08
    return min_value - pad, max_value + pad


def _label(key: str) -> str:
    return key.replace("_", " ")


def _svg_header(width: int, height: int) -> str:
    return f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
<style>
  .plot-bg {{ fill: #ffffff; stroke: #d7dde5; stroke-width: 1; }}
  .axis {{ stroke: #27313f; stroke-width: 1.4; }}
  .grid {{ stroke: #e6eaf0; stroke-width: 1; }}
  .point {{ opacity: 0.92; }}
  .frontier {{ fill: #0f766e; opacity: 1; }}
  .series-0 {{ fill: #2563eb; }}
  .series-1 {{ fill: #dc2626; }}
  .series-2 {{ fill: #7c3aed; }}
  .series-3 {{ fill: #ca8a04; }}
  .series-4 {{ fill: #0891b2; }}
  .series-5 {{ fill: #4b5563; }}
  .line {{ fill: none; stroke: #0f766e; stroke-width: 2.5; }}
  .title {{ font: 700 20px Arial, sans-serif; fill: #111827; }}
  .label {{ font: 600 13px Arial, sans-serif; fill: #374151; }}
  .legend-title {{ font: 700 13px Arial, sans-serif; fill: #111827; }}
  .legend {{ font: 12px Arial, sans-serif; fill: #111827; }}
</style>"""


def _write_basic_pdf(
    rows: list[dict[str, str]],
    x_key: str,
    y_key: str,
    label_key: str,
    path: Path,
    title: str,
    chart_type: str,
) -> None:
    if not rows:
        path.write_bytes(_pdf_document(["BT /F1 12 Tf 72 720 Td (No data) Tj ET"]))
        return
    width, height = 980, 540
    left, bottom, plot_width, plot_height = 86, 104, 600, 360
    xs = [float(row[x_key]) for row in rows]
    ys = [float(row[y_key]) for row in rows]
    min_x, max_x = _padded_domain(xs)
    min_y, max_y = _padded_domain(ys)

    def sx(value: float) -> float:
        return left + (value - min_x) / ((max_x - min_x) or 1.0) * plot_width

    def sy(value: float) -> float:
        return bottom + (value - min_y) / ((max_y - min_y) or 1.0) * plot_height

    commands = [
        "0.07 0.09 0.12 rg",
        f"BT /F2 20 Tf 86 502 Td ({_pdf_escape(title)}) Tj ET",
        "0.15 0.19 0.25 RG 1.2 w",
        f"{left} {bottom} m {left + plot_width} {bottom} l S",
        f"{left} {bottom} m {left} {bottom + plot_height} l S",
        "0.90 0.92 0.94 RG 0.6 w",
    ]
    for i in range(1, 5):
        x = left + plot_width * i / 4
        y = bottom + plot_height * i / 4
        commands.append(f"{x:.2f} {bottom} m {x:.2f} {bottom + plot_height} l S")
        commands.append(f"{left} {y:.2f} m {left + plot_width} {y:.2f} l S")
    commands.extend(
        [
            f"BT /F1 13 Tf 346 40 Td ({_pdf_escape(_label(x_key))}) Tj ET",
            f"BT /F1 13 Tf 24 274 Td ({_pdf_escape(_label(y_key))}) Tj ET",
        ]
    )
    if chart_type == "line" and len(rows) > 1:
        commands.append("0.06 0.46 0.43 RG 2.2 w")
        first = rows[0]
        commands.append(f"{sx(float(first[x_key])):.2f} {sy(float(first[y_key])):.2f} m")
        for row in rows[1:]:
            commands.append(f"{sx(float(row[x_key])):.2f} {sy(float(row[y_key])):.2f} l")
        commands.append("S")
    for index, row in enumerate(rows):
        x = sx(float(row[x_key]))
        y = sy(float(row[y_key]))
        red, green, blue = _pdf_color(index, row.get("pareto_optimal", "false") == "true")
        commands.append(f"{red:.3f} {green:.3f} {blue:.3f} rg")
        commands.append(f"{x - 5.5:.2f} {y - 5.5:.2f} 11 11 re f")
    commands.append("0.07 0.09 0.12 rg")
    commands.append("BT /F2 13 Tf 728 470 Td (Variants) Tj ET")
    for index, row in enumerate(rows[:12]):
        red, green, blue = _pdf_color(index, row.get("pareto_optimal", "false") == "true")
        y = 448 - index * 24
        commands.append(f"{red:.3f} {green:.3f} {blue:.3f} rg")
        commands.append(f"722.5 {y - 5.5:.2f} 11 11 re f")
        suffix = " Pareto" if row.get("pareto_optimal", "false") == "true" else ""
        commands.append("0.07 0.09 0.12 rg")
        commands.append(f"BT /F1 11 Tf 746 {y - 4} Td ({_pdf_escape(row[label_key] + suffix)}) Tj ET")
    path.write_bytes(_pdf_document(commands, width=width, height=height))


def _pdf_color(index: int, frontier: bool) -> tuple[float, float, float]:
    if frontier:
        return 0.059, 0.463, 0.431
    colors = [
        (0.145, 0.388, 0.922),
        (0.863, 0.149, 0.149),
        (0.486, 0.227, 0.929),
        (0.792, 0.541, 0.016),
        (0.031, 0.569, 0.698),
        (0.294, 0.333, 0.388),
    ]
    return colors[index % len(colors)]


def _pdf_document(commands: list[str], width: int = 980, height: int = 540) -> bytes:
    stream = "\n".join(commands).encode("latin-1", errors="replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>".encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    chunks = [b"%PDF-1.4\n"]
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(sum(len(chunk) for chunk in chunks))
        chunks.append(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref_offset = sum(len(chunk) for chunk in chunks)
    chunks.append(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        chunks.append(f"{offset:010d} 00000 n \n".encode())
    chunks.append(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode()
    )
    return b"".join(chunks)


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
