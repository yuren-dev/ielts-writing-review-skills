#!/usr/bin/env python3
"""Create an IELTS Academic Task 1 reviewed HTML report.

The input is the same JSON review plan used by the legacy
``create_task1_review_docx.py`` script; only the rendering layer is HTML.
The chart image(s) are inlined as base64 data URIs so the report stays
self-contained:

{
  "prompt": "...",
  "review_units": [
    {
      "original": "Student sentence or paragraph.",
      "comments": [{"target": "specific phrase", "text": "中文批注：问题 + 改法"}],
      "rewrite": "English Band 7.5 rewrite."
    }
  ],
  "visual_facts": ["中文看图要点。"],
  "scores": {
    "Task Achievement": "6.5",
    "Coherence & Cohesion": "7",
    "Lexical Resource": "6.5",
    "Grammatical Range & Accuracy": "6.5",
    "Overall": "6.5"
  },
  "score_explanation": ["中文评分说明。"],
  "focus_feedback": ["中文优先改进点（3-5 条）。"],
  "model_answer": ["English paragraph 1", "..."]
}

Output is one self-contained HTML file (inline CSS, inlined images, no
external resources).
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import re
from datetime import datetime
from pathlib import Path
from typing import Any

CJK_RE = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
TASK_TITLE = "雅思写作 Task 1 批改报告"
MODEL_SECTION_ID = "model-answer"
MODEL_PLAN_KEY = "model_answer"
MODEL_MIN_WORDS = 150
MODEL_MAX_WORDS = 200
CRITERIA = [
    ("Task Achievement", "任务完成度"),
    ("Coherence & Cohesion", "连贯与衔接"),
    ("Lexical Resource", "词汇资源"),
    ("Grammatical Range & Accuracy", "语法多样性与准确性"),
]
MODEL_STRUCTURE_NOTES = [
    "第 1 段（引言）：改述题目，说明图表类型、对象、单位与时间范围。",
    "第 2 段（概述）：以 Overall 开头，概括最主要的总体特征，通常不堆砌具体数据。",
    "第 3 段（主体一）：按第一组逻辑（如最高与最低、时间起点）报告具体数据并作比较。",
    "第 4 段（主体二）：报告第二组数据，用 respectively、that of 等结构与前文形成对比。",
]

STYLE = """
:root {
  --ink: #1a1a1a;
  --muted: #555555;
  --line: #c9c9c9;
  --mark-bg: #fff2a8;
  --mark-line: #a97c00;
  --accent: #8a1c1c;
  --box: #faf7ea;
}
* { box-sizing: border-box; }
html { background: #f1f1f1; }
body {
  max-width: 920px;
  margin: 0 auto;
  padding: 40px 48px 56px;
  background: #ffffff;
  color: var(--ink);
  font-family: Georgia, "Times New Roman", "Songti SC", SimSun, serif;
  font-size: 16px;
  line-height: 1.75;
}
h1 { margin: 0 0 12px; font-size: 27px; line-height: 1.3; }
h2 {
  margin: 38px 0 14px;
  padding-left: 10px;
  border-left: 5px solid var(--accent);
  font-size: 20px;
  line-height: 1.4;
}
h3 { margin: 20px 0 8px; font-size: 17px; }
p { margin: 0 0 12px; }
ul, ol { margin: 8px 0 14px; padding-left: 26px; }
li { margin: 5px 0; }
.review-header { border-bottom: 2px solid var(--ink); padding-bottom: 18px; }
.meta {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 4px 16px;
  margin: 14px 0 20px;
  font-size: 15px;
}
.meta dt { color: var(--muted); }
.meta dd { margin: 0; }
.prompt-text { padding: 10px 14px; background: #f5f5f5; border: 1px solid var(--line); }
.score-table { width: 100%; margin: 14px 0 10px; border-collapse: collapse; }
.score-table caption { text-align: left; font-weight: bold; padding-bottom: 6px; }
.score-table th, .score-table td { border: 1px solid var(--line); padding: 7px 12px; text-align: left; }
.score-table thead th { background: #efefef; }
.score-table .overall th, .score-table .overall td { font-weight: bold; background: #f7f7f7; }
.score-notes { margin: 8px 0 0; padding-left: 22px; color: var(--muted); font-size: 15px; }
.section-intro { color: var(--muted); font-size: 15px; }
.paragraph-block { margin: 0 0 30px; padding-bottom: 6px; }
p.original { font-size: 16.5px; }
mark.comment {
  background: var(--mark-bg);
  border-bottom: 2px solid var(--mark-line);
  padding: 0 2px;
  color: inherit;
}
sup.comment-ref { color: var(--accent); font-weight: bold; font-size: 0.72em; margin-left: 1px; }
.comment-list {
  margin: 10px 0 14px;
  padding: 10px 16px 10px 36px;
  background: var(--box);
  border: 1px solid #e3d6a4;
  border-radius: 4px;
}
.comment-item { margin: 7px 0; }
.comment-target {
  display: inline-block;
  margin-right: 8px;
  padding: 0 5px;
  border-radius: 3px;
  background: #ece5c8;
  font-family: "Courier New", monospace;
  font-size: 0.92em;
}
.comment-text { font-size: 15.5px; }
.rewrite {
  margin: 14px 0 0;
  padding: 10px 0 10px 16px;
  border-left: 4px solid #8fb0cf;
  background: #f6f9fc;
}
.rewrite-text { font-size: 16px; }
.rewrite-note { margin: 4px 0 0; color: var(--muted); font-size: 14.5px; }
.visual { margin: 6px 0 16px; }
.visual img { max-width: 100%; height: auto; border: 1px solid var(--line); }
.visual figcaption { margin-top: 6px; color: var(--muted); font-size: 14px; }
.visual-points { margin-bottom: 26px; padding: 10px 16px; background: #f7f7f7; border: 1px solid var(--line); }
.visual-points ul { margin-bottom: 0; }
.model-paragraph { font-size: 16.5px; }
.model-wordcount { color: var(--muted); font-size: 14px; }
.model-note {
  margin-top: 22px;
  padding: 12px 16px;
  border: 1px solid var(--line);
  background: #fafafa;
}
.model-note ol { margin-bottom: 0; }
.review-footer {
  margin-top: 42px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 13.5px;
}
@page { margin: 18mm; }
@media print {
  html { background: #ffffff; }
  body { max-width: none; margin: 0; padding: 0; font-size: 12pt; }
  #feedback, #model-essay, #model-answer { break-before: page; }
  .paragraph-block, .rewrite, .comment-list, .score-table, .visual, .model-note { break-inside: avoid; }
  h1, h2, h3 { break-after: avoid; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  mark.comment { background: #fff2a8 !important; border-bottom: 1.5pt solid #a97c00; }
}
"""


def escape_text(text: str) -> str:
    return html.escape(str(text), quote=False)


def escape_attr(text: str) -> str:
    return html.escape(str(text), quote=True)


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)?|\d+", text))


def normalized_with_map(text: str) -> tuple[str, list[int]]:
    chars: list[str] = []
    index_map: list[int] = []
    pending_space = False
    pending_index = 0
    for idx, char in enumerate(text):
        if char.isspace():
            if chars and not pending_space:
                pending_space = True
                pending_index = idx
            continue
        if pending_space:
            chars.append(" ")
            index_map.append(pending_index)
            pending_space = False
        chars.append(char)
        index_map.append(idx)
    return "".join(chars), index_map


def iter_spans(text: str, needle: str):
    """Yield (start, end) spans for needle, exact case first then case-insensitive."""
    needle = needle.strip()
    if not needle or not text:
        return
    start = 0
    while True:
        found = text.find(needle, start)
        if found < 0:
            break
        yield found, found + len(needle)
        start = found + 1
    normalized_text, text_map = normalized_with_map(text)
    normalized_needle = " ".join(needle.split()).lower()
    if not normalized_text or not normalized_needle:
        return
    normalized_text = normalized_text.lower()
    start = 0
    while True:
        found = normalized_text.find(normalized_needle, start)
        if found < 0:
            break
        end_pos = found + len(normalized_needle) - 1
        yield text_map[found], text_map[end_pos] + 1
        start = found + 1


def locate_span(text: str, needle: str, used: list[tuple[int, int]]) -> tuple[int, int] | None:
    for start, end in iter_spans(text, needle):
        if all(end <= used_start or start >= used_end for used_start, used_end in used):
            return start, end
    return None


def build_rewrite_note(unit: dict[str, Any], comments: list[dict[str, Any]], rewrite: str) -> str:
    explicit = str(unit.get("rewrite_note") or "").strip()
    if explicit:
        return explicit
    removed = [
        str(comment.get("target") or "").strip()
        for comment in comments
        if str(comment.get("target") or "").strip()
        and str(comment.get("target") or "").strip().lower() not in rewrite.lower()
    ]
    if removed:
        shown = "、".join(f"“{target}”" for target in removed[:3])
        return (
            f"改写说明：替换了 {shown} 等表达，并调整了句式和搭配，使意思更精确、"
            "语气更正式，在保留原意的同时达到 Band 7.5 水平。"
        )
    return "改写说明：调整了用词和句式，使表达更正式、连贯，在保留原意的同时达到 Band 7.5 水平。"


def render_original(original: str, ranges: list[tuple[int, int, int, str, str]]) -> str:
    parts: list[str] = []
    cursor = 0
    for start, end, cid, target, _text in sorted(ranges, key=lambda item: item[0]):
        parts.append(escape_text(original[cursor:start]))
        parts.append(
            f'<mark class="comment" data-comment="{cid}" data-target="{escape_attr(target)}">'
            f"{escape_text(original[start:end])}<sup class=\"comment-ref\">{cid}</sup></mark>"
        )
        cursor = end
    parts.append(escape_text(original[cursor:]))
    return "".join(parts)


def render_paragraph_block(unit: dict[str, Any], next_id: int) -> tuple[str, int]:
    original = str(unit.get("original") or "").strip()
    if not original:
        return "", next_id
    comments = list(unit.get("comments") or [])
    ranges: list[tuple[int, int, int, str, str]] = []
    cid = next_id
    for comment in comments:
        target = str(comment.get("target") or "").strip()
        text = str(comment.get("text") or "").strip()
        if not target:
            raise SystemExit("Every comment in the review plan needs a non-empty 'target'.")
        if not text:
            raise SystemExit(f"Comment target {target!r} has empty text.")
        span = locate_span(original, target, [(item[0], item[1]) for item in ranges])
        if span is None:
            raise SystemExit(
                f"Could not anchor comment target {target!r} inside the student paragraph: {original[:100]}"
            )
        ranges.append((span[0], span[1], cid, target, text))
        cid += 1

    block = ['<div class="paragraph-block">', f'<p class="original">{render_original(original, ranges)}</p>']
    if ranges:
        block.append('<ol class="comment-list">')
        for _start, _end, rid, target, text in ranges:
            block.append(
                f'<li class="comment-item" data-comment="{rid}">'
                f'<span class="comment-target">{escape_text(target)}</span>'
                f'<span class="comment-text">{escape_text(text)}</span></li>'
            )
        block.append("</ol>")
    rewrite = str(unit.get("rewrite") or "").strip()
    if rewrite:
        note = build_rewrite_note(unit, comments, rewrite)
        block.append('<div class="rewrite">')
        block.append(f'<p class="rewrite-text"><em>{escape_text(rewrite)}</em></p>')
        block.append(f'<p class="rewrite-note">{escape_text(note)}</p>')
        block.append("</div>")
    block.append("</div>")
    return "\n".join(block), cid


def band_sort_key(value: str) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return -1.0


def build_strengths(plan: dict[str, Any]) -> list[str]:
    explicit = plan.get("strengths")
    if isinstance(explicit, list) and explicit:
        return [str(item).strip() for item in explicit if str(item).strip()]
    scores = plan.get("scores") if isinstance(plan.get("scores"), dict) else {}
    numeric = {
        key: band_sort_key(scores.get(key, ""))
        for key, _label in CRITERIA
        if str(scores.get(key, "")).strip()
    }
    strengths: list[str] = []
    if numeric:
        best = max(numeric.values())
        if len(set(numeric.values())) == 1:
            best_key = next(key for key, _label in CRITERIA if numeric.get(key) == best)
            strengths.append(
                f"四项评分均为 {scores.get(best_key)}，基础比较均衡，"
                "说明学生已具备基本的任务意识和语言控制力。"
            )
        else:
            labels = [label for key, label in CRITERIA if numeric.get(key) == best]
            best_key = next(key for key, _label in CRITERIA if numeric.get(key) == best)
            strengths.append(
                f"{'、'.join(labels)}是相对稳定的部分（{scores.get(best_key)}），"
                "说明学生已具备基本的任务意识和语言控制力。"
            )
    strengths.append("文章结构基本完整，读者可以跟上主要观点和论证顺序。")
    return strengths


def build_header(plan: dict[str, Any], input_path: Path | None, target_band: str, today: str) -> str:
    scores = plan.get("scores")
    if not isinstance(scores, dict):
        raise SystemExit("Review plan must contain a 'scores' object.")
    missing = [key for key, _label in CRITERIA if key not in scores]
    if "Overall" not in scores:
        missing.append("Overall")
    if missing:
        raise SystemExit(f"Review plan is missing required scores: {missing}")

    input_name = input_path.name if input_path else "（粘贴文本）"
    rows = []
    for key, label in CRITERIA:
        rows.append(f"<tr><th scope=\"row\">{label}（{key}）</th><td>{escape_text(scores[key])}</td></tr>")
    rows.append(f"<tr class=\"overall\"><th scope=\"row\">总分（Overall）</th><td>{escape_text(scores['Overall'])}</td></tr>")
    prompt = str(plan.get("prompt") or "").strip()
    prompt_html = (
        f'<div class="prompt"><h2>题目</h2><p class="prompt-text">{escape_text(prompt)}</p></div>'
        if prompt
        else ""
    )
    notes = [str(item).strip() for item in plan.get("score_explanation") or [] if str(item).strip()]
    if not notes:
        raise SystemExit("Review plan must contain at least one Chinese 'score_explanation' item.")
    notes_html = "\n".join(f"<li>{escape_text(note)}</li>" for note in notes)
    return f"""<header class="review-header">
<h1>{TASK_TITLE}</h1>
<dl class="meta">
<dt>输入文件</dt><dd>{escape_text(input_name)}</dd>
<dt>批改日期</dt><dd>{escape_text(today)}</dd>
<dt>目标分数</dt><dd>{escape_text(target_band)}</dd>
</dl>
{prompt_html}
<table class="score-table">
<caption>评分（针对学生原稿）</caption>
<thead><tr><th>评分项</th><th>分数</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody>
</table>
<ul class="score-notes">
{notes_html}
</ul>
</header>"""


def build_feedback(plan: dict[str, Any]) -> str:
    improvements = [str(item).strip() for item in plan.get("focus_feedback") or [] if str(item).strip()]
    if not 3 <= len(improvements) <= 5:
        raise SystemExit(
            f"Review plan needs 3-5 Chinese 'focus_feedback' items for the feedback section; got {len(improvements)}."
        )
    strengths = build_strengths(plan)
    return f"""<section class="section" id="feedback">
<h2>简短反馈</h2>
<h3>优点</h3>
<ul class="strengths">
{chr(10).join(f"<li>{escape_text(item)}</li>" for item in strengths)}
</ul>
<h3>优先改进点</h3>
<ol class="improvements">
{chr(10).join(f"<li>{escape_text(item)}</li>" for item in improvements)}
</ol>
</section>"""


def model_paragraphs_from_plan(plan: dict[str, Any]) -> list[str]:
    value = plan.get(MODEL_PLAN_KEY, [])
    if isinstance(value, str):
        return [part.strip() for part in value.split("\n") if part.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


def build_model(plan: dict[str, Any]) -> tuple[str, int]:
    paragraphs = model_paragraphs_from_plan(plan)
    if len(paragraphs) != 4:
        raise SystemExit(f"Model answer must contain exactly 4 paragraphs; got {len(paragraphs)}.")
    words = word_count(" ".join(paragraphs))
    if not MODEL_MIN_WORDS <= words <= MODEL_MAX_WORDS:
        raise SystemExit(
            f"Model answer word count must be {MODEL_MIN_WORDS}-{MODEL_MAX_WORDS}; got {words}."
        )
    if not re.match(r"^overall\b", paragraphs[1], flags=re.I):
        raise SystemExit("Task 1 model answer paragraph 2 must begin with 'Overall'.")
    notes_value = plan.get("model_structure_notes")
    if isinstance(notes_value, list) and len(notes_value) == 4:
        notes = [str(item).strip() for item in notes_value]
    else:
        notes = MODEL_STRUCTURE_NOTES
    body = "\n".join(f'<p class="model-paragraph">{escape_text(paragraph)}</p>' for paragraph in paragraphs)
    return f"""<section class="section" id="{MODEL_SECTION_ID}">
<h2>Band 8.0 范文</h2>
<div class="model-text">
{body}
</div>
<p class="model-wordcount">（范文共 {words} 词）</p>
<div class="model-note">
<h3>范文结构说明</h3>
<ol class="structure-notes">
{chr(10).join(f"<li>{escape_text(note)}</li>" for note in notes)}
</ol>
</div>
</section>""", words


def image_data_uri(path: Path) -> str:
    mime, _encoding = mimetypes.guess_type(str(path))
    if not mime or not mime.startswith("image/"):
        raise SystemExit(f"Not a recognised image file: {path}")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def build_visual(images: list[Path], plan: dict[str, Any]) -> str:
    facts = [str(item).strip() for item in plan.get("visual_facts") or [] if str(item).strip()]
    if not facts:
        raise SystemExit("Task 1 review plan must contain Chinese 'visual_facts' for the 看图要点 section.")
    if not images:
        raise SystemExit("Task 1 HTML needs at least one --image chart file to inline.")
    figures = []
    for index, path in enumerate(images, start=1):
        figures.append(
            '<figure class="visual">\n'
            f'<img src="{image_data_uri(path)}" alt="题目图表 {index}">\n'
            f"<figcaption>题目图表 {index}（先看图，再阅读批注）</figcaption>\n"
            "</figure>"
        )
    points = "\n".join(f"<li>{escape_text(item)}</li>" for item in facts)
    return "\n".join(figures) + (
        '\n<div class="visual-points">\n<h3>看图要点</h3>\n'
        f'<ul class="visual-points-list">\n{points}\n</ul>\n</div>'
    )


def build_html(plan: dict[str, Any], input_path: Path | None, target_band: str, images: list[Path]) -> str:
    units = list(plan.get("review_units") or [])
    if not units:
        raise SystemExit("Review plan must contain at least one review unit.")
    today = datetime.now().strftime("%Y-%m-%d")
    header = build_header(plan, input_path, target_band, today)
    visual = build_visual(images, plan)

    blocks: list[str] = []
    next_id = 1
    rewrite_count = 0
    for unit in units:
        block, next_id = render_paragraph_block(unit, next_id)
        if not block:
            continue
        blocks.append(block)
        if str(unit.get("rewrite") or "").strip():
            rewrite_count += 1
    if not blocks:
        raise SystemExit("No review unit with non-empty 'original' text was found in the plan.")
    if rewrite_count == 0:
        raise SystemExit("Review plan must contain at least one italic rewrite.")
    feedback = build_feedback(plan)
    model, _words = build_model(plan)
    input_name = input_path.name if input_path else "IELTS Task 1"
    footer = (
        "本报告由 ielts-task1-review 生成：批注与讲解为中文，"
        "学生原文、Band 7.5 改写与 Band 8.0 范文保持英文。"
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape_text(TASK_TITLE)} — {escape_text(input_name)}</title>
<style>{STYLE}</style>
</head>
<body>
{header}
<main>
<section class="section" id="reviewed-text">
<h2>带批注的原文</h2>
<p class="section-intro">原文中黄色高亮并带编号的词句是批注锚点，编号与段落后批注列表一一对应；每条批注指出问题并给出改法。</p>
{visual}
{chr(10).join(blocks)}
</section>
{feedback}
{model}
</main>
<footer class="review-footer">
<p>{escape_text(footer)}</p>
</footer>
</body>
</html>
"""


def default_output_path(input_path: Path | None) -> Path:
    if input_path:
        return input_path.with_name(f"{input_path.stem}(reviewed).html")
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    return Path.cwd() / f"IELTS_Task1_Reviewed_{stamp}.html"


def avoid_overwrite(path: Path) -> Path:
    if not path.exists():
        return path
    suffix = path.suffix
    stem = path.stem
    parent = path.parent
    if stem.endswith("(reviewed)"):
        prefix = stem[: -len("(reviewed)")]
        template = lambda n: parent / f"{prefix}(reviewed {n}){suffix}"
    else:
        template = lambda n: parent / f"{stem} {n}{suffix}"
    for n in range(2, 100):
        candidate = template(n)
        if not candidate.exists():
            return candidate
    raise SystemExit(f"Could not find non-overwriting filename for {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_json", type=Path)
    parser.add_argument("--input-docx", type=Path, default=None, help="Original input DOCX; used for the header and default output name.")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--image",
        type=Path,
        action="append",
        default=[],
        help="Chart image to inline as a base64 data URI. Repeat for multiple images.",
    )
    parser.add_argument("--target-band", default="Band 7.5（改写）/ Band 8.0（范文）")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--cleanup-plan",
        action="store_true",
        help="Delete the review JSON after the HTML is successfully created; use for temporary review_plan_*.json files.",
    )
    args = parser.parse_args()

    plan = json.loads(args.review_json.read_text(encoding="utf-8"))
    output = args.output or default_output_path(args.input_docx)
    if not args.overwrite:
        output = avoid_overwrite(output)
    document = build_html(plan, args.input_docx, args.target_band, args.image)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    print(output)
    if args.cleanup_plan:
        args.review_json.unlink()
        print(f"Deleted temporary review plan: {args.review_json}")


if __name__ == "__main__":
    main()
