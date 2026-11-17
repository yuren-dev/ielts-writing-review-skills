---
name: ielts-task1-review
description: Use this skill to review IELTS Academic Writing Task 1 answers in a specific teacher's style. Trigger when the user asks for IELTS Task 1 correction, chart/table/map/process description review, Band 7.5 or 8.0 improvement, teacher-style marking, comments on a Task 1 answer, a self-contained reviewed HTML report, Chinese marking and explanation, or a full Task 1 model answer based on a student's draft and visual prompt. Supports .docx input containing an embedded chart image and pasted text with an attached image or image path.
---

# IELTS Task 1 Review

## Core Rule

Analyze the visual prompt before correcting the student's writing. For Task 1, accurate chart/table/map/process understanding is part of Task Achievement, so do not polish language before identifying the main features. Every review must also meet these three hard requirements:

1. **输出 HTML，不输出 DOCX。** 批改产物是单个自包含 HTML 文件：内联 CSS，图表以 base64 data URI 内嵌，浏览器直接打开可读、可打印。不要再生成 `(reviewed).docx`。
2. **保留标注形式。** 批注必须锚定学生原文的具体词句，带连续编号上标，并在该段下方按编号列出；段落后保留 Band 7.5 斜体改写。不能退化成整段泛评或纯文本括号批注。
3. **批改和讲解都用中文。** 所有批注、看图要点、评分说明、简短反馈、改写说明、范文结构说明、章节标题都用中文写；学生原文、斜体改写、范文保持英文。

Use these references in order:

1. Read `references/visual_analysis_protocol.md` to inspect the visual.
2. Read `references/teacher_style.md` for Task 1 teacher-style marking.
3. Read `references/ielts_task1_band_descriptors.md` before scoring.
4. Use `references/teacher_samples_index.md` to find relevant samples, then read full samples from `references/teacher_samples/` when useful.
5. Use `references/review_format.md` for the HTML structure, class names, and Chinese/English split.

## Workflow

1. Identify the prompt, embedded image, and student answer.
   - Normal input is an unreviewed `.docx` (the extraction flow is unchanged) or pasted text with an image path.
   - For `.docx`, extract embedded images with `scripts/extract_docx_images.py` to a scratch directory such as `/tmp/ielts_task1_images_<unique>`.
   - Inspect the extracted image directly before reviewing. This is mandatory: never score or rewrite a Task 1 answer from the text alone.
   - For `.docx`, also run `scripts/extract_task1_input.py` so the review plan can distinguish prompt text from student answer paragraphs.
   - For pasted text, require an image attachment or image path.
2. Build an internal visual facts note, written in Chinese.
   - Identify visual type, units, categories, time periods, axes, legends, stages, and key values.
   - Identify overview-level features before local details.
   - These facts become the Chinese 看图要点 shown below the inlined chart; keep them concise and accurate.
3. Check the student's Task Achievement.
   - Mark inaccurate chart type, wrong units, missing overview, wrong key feature selection, inaccurate values, or irrelevant details in comments.
4. Select the closest teacher samples by visual type before writing comments.
   - First classify the new task as bar chart, line graph, table, pie chart, map, process, or mixed visual.
   - Use `references/teacher_samples_index.md` to find similar sample files, then inspect one or two matching full samples.
   - Prefer same visual type and same main challenge, such as trend comparison, proportions, maps, process sequencing, or mixed table/chart reporting.
5. Split the answer into review units.
   - Use sentence-level units for grammar, articles, plural forms, data phrasing, collocation, and formal wording.
   - Use paragraph-level units for overview errors, poor grouping, data misreading, map/process sequencing, or missing comparisons.
6. Add teacher-style comments in Chinese.
   - Keep comments short, practical, and anchored to specific words or phrases.
   - Every comment must state the problem and the fix, e.g. `图表类型不准确：应写 bar chart` or `barely 偏口语，建议用 just under`.
   - Prioritize Task Achievement problems before style polishing.
   - Do not write generic advice detached from the original text.
7. Add italic rewrites after relevant units.
   - Rewrites stay in English, concise, formal, data-accurate, and at a stable Band 7.5 standard.
   - Keep rewrites learnable and close to the student's intended meaning; do not turn local fixes into over-complex Band 9 wording.
8. Score the student's original answer strictly using official Task 1 descriptors.
   - Score Task Achievement, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy, and estimated overall band.
   - Criterion scores and the estimated overall score may use whole or half bands, such as `6`, `6.5`, or `7`; do not force criterion scores to integers.
   - Write `score_explanation` in Chinese, with evidence from the answer.
9. Give concise Chinese feedback oriented to Band 7.5 / 8.0.
   - The plan needs 3-5 Chinese `focus_feedback` items: first the blockers preventing stable Band 7.5, then the most useful moves toward 8.0.
10. Write a 150-200 word model answer at a stable Band 8.0 standard.
    - Use exactly four paragraphs:
      1. Introduction: paraphrase the task prompt.
      2. Overview: begin with `Overall` and summarize the main features.
      3. Body paragraph 1: report the first logical group of details.
      4. Body paragraph 2: report the second logical group of details.
    - Keep the model answer in English.
    - Align it with the visual and official criteria; correct any inaccurate visual interpretation.
    - It must be strong enough for Band 8.0: skilful key feature selection, clear overview, logical grouping, precise data language, natural comparisons, well-managed cohesion, and mostly error-free grammar.
    - Keep it realistic and teacher-like, not an over-complex Band 9 answer.
11. Build the review plan, then generate the reviewed HTML with the inlined chart.
    - Reuse the existing review plan JSON shape (see below); do not change the plan format.
    - Write `comments.text`, `visual_facts`, `score_explanation` and `focus_feedback` in Chinese; keep `prompt`, `review_units.original`, `rewrite` and `model_answer` in English.
    - For input `MyAnswer.docx`, output `MyAnswer(reviewed).html` in the same folder unless the user specifies another path.
    - Pass every extracted chart image with `--image`; the generator converts it to a base64 data URI. Multiple `--image` flags are allowed.
    - The figure and Chinese 看图要点 go before the annotated answer paragraphs. The rule "inspect the visual first" is unchanged.
    - Anchor comments only inside extracted student answer paragraphs, never inside prompt text or image captions. The generator stops with an error if a target is not found.
    - Keep the original prompt and visual in the report; do not repeat the task prompt inside the answer body.
    - The HTML must be self-contained: inline `<style>`, no external CSS/JS/fonts/images, UTF-8, `lang="zh-CN"`.
    - Do not use `<script>`, CDN links, or visible legacy headings such as `Reviewed Answer`, `Score`, or `Model Answer`; use the Chinese section headings defined in `references/review_format.md`.
    - For pasted text, pass `--output /path/IELTS_Task1_Reviewed_YYYYMMDD_HHMM.html`.
    - Never overwrite the original answer unless explicitly requested. The generator avoids overwriting by default; use `--overwrite` only deliberately.
12. Validate the HTML with the bundled validator. Do not deliver an unvalidated report.
    - The validator checks the five-part structure, inlined chart and Chinese visual notes, comment numbering/anchoring, Chinese comments and feedback, self-containment, and counts against the plan.
13. Reply in Chinese with the scores, a short feedback summary, and the model answer.
    - Also give the absolute path of the generated HTML file.
14. Clean up temporary byproducts after a successful review.
    - Delete temporary files such as `review_plan_*.json`, extracted scratch images, and unpacked DOCX folders.
    - Do not delete source answers, final reviewed `.html` files, or bundled reference files.

## Bundled Resources

- `references/visual_analysis_protocol.md`: checklist for charts, tables, maps, processes, and mixed visuals.
- `references/teacher_style.md`: Task 1 teacher-style rules distilled from samples.
- `references/teacher_samples_index.md`: sample index with image files and counts.
- `references/teacher_samples/*.json` and `*.md`: full extracted teacher-reviewed samples.
- `references/sample_images/*`: extracted visual prompts from the 12 sample DOCX files.
- `references/ielts_task1_band_descriptors.md`: complete Task 1 descriptors extracted from the local PDF.
- `references/review_format.md`: HTML report structure, CSS class names, comment rules, and the Chinese/English split.
- `scripts/extract_docx_images.py`: extract visual prompts from new input DOCX files to a unique scratch directory by default.
- `scripts/extract_task1_input.py`: extract prompt, student answer, and student answer paragraph indices from a Task 1 DOCX.
- `scripts/create_task1_review_html.py`: render a self-contained reviewed HTML from the JSON review plan; chart images are inlined as base64, comments are anchored to the student's original phrases and numbered continuously, and explanations are in Chinese.
- `scripts/validate_task1_review_html.py`: verify the five-part HTML structure, inlined chart and Chinese visual notes, comment numbering/anchoring, Chinese comments and feedback, self-containment, model answer length and four-paragraph structure, and counts against the plan.
- `scripts/extract_task1_teacher_samples.py`: regenerate teacher sample references.
- `scripts/extract_task1_band_descriptors.py`: regenerate descriptors from the PDF.

Legacy: `scripts/create_task1_review_docx.py`, `scripts/validate_task1_review_docx.py`, and `scripts/create_and_validate_task1_review.py` are kept for backwards compatibility but are no longer used by this skill.

## JSON Review Plan For HTML Creation

`scripts/create_task1_review_html.py` reuses the same review plan format as the legacy DOCX script. First produce a JSON file with this shape (Chinese values shown for the fields that must be Chinese):

```json
{
  "prompt": "Task prompt or visual prompt summary",
  "student_answer_paragraph_indices": [4, 6, 8, 10],
  "visual_facts": ["中文看图要点：图表类型、单位、时间范围、主要特征。"],
  "review_units": [
    {
      "original": "Student sentence or paragraph.",
      "comments": [{"target": "specific phrase", "text": "中文批注：问题 + 改法"}],
      "rewrite": "English Band 7.5 rewrite."
    }
  ],
  "scores": {
    "Task Achievement": "6.5",
    "Coherence & Cohesion": "7",
    "Lexical Resource": "6.5",
    "Grammatical Range & Accuracy": "6.5",
    "Overall": "6.5"
  },
  "score_explanation": ["中文评分说明，带原文证据。"],
  "focus_feedback": [
    "中文优先改进点 1（阻止稳定 Band 7.5 的问题）。",
    "中文优先改进点 2。",
    "中文优先改进点 3（迈向 8.0 的方向）。"
  ],
  "model_answer": [
    "Paragraph 1: introduction/paraphrase.",
    "Paragraph 2: Overall ...",
    "Paragraph 3: first detail group.",
    "Paragraph 4: second detail group."
  ]
}
```

`focus_feedback` must contain 3-5 items and `visual_facts` must be non-empty. Optional fields used by the HTML renderer: `rewrite_note` on a review unit (Chinese one-sentence rewrite explanation), `strengths` (Chinese strengths list), and `model_structure_notes` (four Chinese notes). When omitted, the renderer generates a reasonable Chinese note.

Then run:

```bash
python3 scripts/extract_docx_images.py "MyAnswer.docx" --out /tmp/ielts_task1_images_run
python3 scripts/create_task1_review_html.py review_plan.json --input-docx MyAnswer.docx --image /tmp/ielts_task1_images_run/MyAnswer_image1.png --cleanup-plan
python3 scripts/validate_task1_review_html.py "MyAnswer(reviewed).html" --plan review_plan.json --input-docx MyAnswer.docx
```

If the review plan is a permanent example/reference file, omit `--cleanup-plan`. For pasted text, pass the attached image path directly to `--image` and set `--output`.

## Quality Bar

- The visual must be inspected before scoring or rewriting, and the chart must be inlined in the HTML with Chinese 看图要点 below it.
- Similar teacher samples should be selected by visual type before writing the final comments and model answer.
- The reviewed report is a single self-contained HTML file, not a DOCX.
- All comments, visual notes, feedback, scoring explanations, rewrite notes, structure notes, and section headings are in Chinese; student original, italic rewrites, and model answer stay in English.
- Comments must stay within the extracted student answer paragraphs; prompt text and image captions are not valid anchor targets.
- Comments must be anchored to specific text and numbered continuously; every `data-comment` matches a comment item and vice versa.
- Important Task Achievement issues must be commented first.
- Italic rewrites must be data-accurate and written at a stable Band 7.5 standard.
- The score must evaluate the original answer.
- The model answer must be exactly 4 paragraphs, 150-200 words, and should stand securely at Band 8.0 according to the official Task 1 descriptors.
- The style should look closer to the teacher's Task 1 samples than to a generic IELTS tutor.
- The generated HTML must pass `scripts/validate_task1_review_html.py`.
