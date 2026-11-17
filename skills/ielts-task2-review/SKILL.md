---
name: ielts-task2-review
description: Use this skill to review IELTS Writing Task 2 essays in a specific teacher's style. Trigger when the user asks for IELTS Task 2 correction, Band 7.5 or 8.0 improvement, teacher-style essay marking, comments on a Task 2 essay, a self-contained reviewed HTML report, Chinese marking and explanation, or a full Task 2 model essay based on a student's draft. Supports both pasted prompt+essay text and simple .docx input containing the task prompt and student essay.
---

# IELTS Task 2 Review

## Core Rule

Imitate the teacher's marking style before giving generic IELTS advice, and meet these three hard requirements for every review:

1. **输出 HTML，不输出 DOCX。** 批改产物是单个自包含 HTML 文件（内联 CSS，无外链），浏览器直接打开可读、可打印。不要再生成 `(reviewed).docx`。
2. **保留标注形式。** 批注必须锚定学生原文的具体词句，带连续编号上标，并在该段下方按编号列出；段落后保留 Band 7.5 斜体改写。不能退化成整段泛评或纯文本括号批注。
3. **批改和讲解都用中文。** 所有批注、评分说明、简短反馈、改写说明、范文结构说明、章节标题都用中文写；学生原文、斜体改写、范文保持英文。

Use the full teacher samples and the official descriptors as the two authorities:

1. Read `references/teacher_style.md` before reviewing.
2. Read `references/ielts_task2_band_descriptors.md` before scoring.
3. Use `references/teacher_samples_index.md` to find relevant sample files, then read specific full samples from `references/teacher_samples/` when needed.
4. Use `references/review_format.md` for the HTML output structure, class names, and Chinese/English split.

## Workflow

1. Identify the Task 2 prompt and the student's essay.
   - Normal input is an unreviewed `.docx` (the extraction flow is unchanged) or pasted prompt+essay text.
   - For a `.docx`, first run `scripts/extract_task2_input.py` to separate the prompt, optional outline, and student essay.
   - Preserve `student_essay_paragraph_indices` from the extraction result and include it in the review plan.
   - Treat short outline bullets after the prompt as planning notes, not as the scored essay.
   - Existing comments, italic rewrites, feedback, or model essays are not expected in normal use. If detected, treat them as accidental leftover material only; do not score, rewrite, or copy them as part of the student's essay.
   - For pasted text, separate prompt and essay from headings, blank lines, or explicit labels.
2. Check task fit before polishing language.
   - If the essay content, position, or logic is significantly off-topic, mark this first in comments.
   - Later italic rewrites and the final model essay must redirect the mistaken idea back to the task.
3. Select relevant teacher samples before writing comments.
   - Use `scripts/find_teacher_sample.py` with the input filename or prompt.
   - The script normalizes spaces/underscores, so `C17T3 Writing Task 2.docx` maps to `C17T3_Writing_Task_2.json`.
   - If the exact file sample is not relevant, use `references/teacher_samples_index.md` and the prompt wording to choose a closer sample.
4. Split the essay into review units.
   - Use sentence-level units when problems are local.
   - Use paragraph-level units when logic, task response, or coherence needs bigger repair.
5. Add teacher-style comments in Chinese.
   - Keep comments short, practical, and anchored to specific words or phrases.
   - Every comment must state the problem and the fix, e.g. `“非常重要”过于笼统，建议换成 a key role` or `与前句重复，建议用 whereas 引出对比`.
   - A non-empty comment target must match text inside the selected student essay paragraph; do not fall back to prompt, outline, or the whole wrong paragraph.
   - Do not write generic advice detached from the original text.
6. Add italic rewrites after the relevant original unit.
   - Rewrites stay in English, concise, formal, and natural at a stable Band 7.5 standard.
   - Keep rewrites close to the student's intended meaning; avoid making local fixes sound like an over-polished Band 9 sample.
7. Score the student's original essay strictly using official Task 2 descriptors.
   - Score Task Response, Coherence & Cohesion, Lexical Resource, Grammatical Range & Accuracy, and estimated overall band.
   - Criterion scores and the estimated overall score may use whole or half bands, such as `6`, `6.5`, or `7`; do not force criterion scores to integers.
   - Write `score_explanation` in Chinese, with evidence from the essay.
8. Give concise Chinese feedback oriented to Band 7.5 / 8.0.
   - The plan needs 3-5 Chinese `focus_feedback` items: first the blockers preventing stable Band 7.5, then the most useful moves toward 8.0.
   - Keep this section short, like the teacher samples.
9. Write a 250-300 word model essay at a stable Band 8.0 standard.
   - Use exactly four paragraphs:
     1. Introduction: paraphrase the prompt and state the essay's position.
     2. Body paragraph 1.
     3. Body paragraph 2.
     4. Conclusion: begin with `In conclusion`.
   - Keep the model essay in English.
   - Align it with the official criteria.
   - Preserve the student's main position when it is on-topic and defensible; correct flawed or off-topic logic.
   - It must be strong enough for Band 8.0: a clear and well-developed position, relevant and well-extended support, well-managed cohesion, flexible topic vocabulary, and mostly error-free grammar.
   - Keep it realistic and teacher-like, not an over-polished Band 9 essay.
10. Build the review plan, then generate the reviewed HTML.
    - Reuse the existing review plan JSON shape (see below); do not change the plan format.
    - Write `comments.text`, `score_explanation` and `focus_feedback` in Chinese; keep `prompt`, `review_units.original`, `rewrite` and `model_essay` in English.
    - For input `MyEssay.docx`, output `MyEssay(reviewed).html` in the same folder unless the user specifies another path.
    - Anchor comments only inside extracted student essay paragraphs, never inside prompt or outline paragraphs. The generator stops with an error if a target is not found.
    - Keep the original prompt and student essay in the report; do not repeat the prompt inside the essay body.
    - The HTML must be self-contained: inline `<style>`, no external CSS/JS/fonts/images, UTF-8, `lang="zh-CN"`.
    - Do not use `<script>`, CDN links, or visible legacy headings such as `Reviewed Essay`, `Score`, or `Model Essay`; use the Chinese section headings defined in `references/review_format.md`.
    - For pasted text, pass `--output /path/IELTS_Task2_Reviewed_YYYYMMDD_HHMM.html`.
    - Never overwrite the original essay unless explicitly requested. The generator avoids overwriting by default; use `--overwrite` only deliberately.
11. Validate the HTML with the bundled validator. Do not deliver an unvalidated report.
    - The validator checks the five-part structure, comment numbering/anchoring, Chinese comments and feedback, self-containment, and counts against the plan.
12. Reply in Chinese with the scores, a short feedback summary, and the model essay.
    - Also give the absolute path of the generated HTML file.
13. Clean up temporary byproducts after a successful review.
    - Delete temporary review plan files such as `review_plan_c17t3.json` (or use `--cleanup-plan`).
    - Prefer creating review plans in `/tmp`.
    - Do not delete source essays, final reviewed `.html` files, or bundled reference files.

## Bundled Resources

- `references/teacher_style.md`: teacher imitation rules distilled from the 11 samples.
- `references/teacher_samples_index.md`: prompt and count index for all samples.
- `references/teacher_samples/*.json` and `*.md`: full extracted teacher-reviewed samples.
- `references/ielts_task2_band_descriptors.md`: complete Task 2 descriptors extracted from the local PDF.
- `references/review_format.md`: HTML report structure, CSS class names, comment rules, and the Chinese/English split.
- `scripts/extract_task2_input.py`: extract prompt, optional outline, and student essay from a Task 2 DOCX; it also protects against accidental leftover reviewed content.
- `scripts/find_teacher_sample.py`: find matching bundled teacher samples using normalized filename and prompt overlap.
- `scripts/create_review_html.py`: render a self-contained reviewed HTML from the JSON review plan; comments are anchored to the student's original phrases, numbered continuously, and rendered with Chinese explanations.
- `scripts/validate_review_html.py`: verify the five-part HTML structure, comment numbering/anchoring, Chinese comments and feedback, self-containment, model essay length and four-paragraph structure, and counts against the plan.
- `scripts/extract_teacher_samples.py`: regenerate sample references from the 11 source DOCX files.
- `scripts/extract_task2_band_descriptors.py`: regenerate descriptors from the PDF.

Legacy: `scripts/create_review_docx.py` and `scripts/validate_review_docx.py` are kept for backwards compatibility but are no longer used by this skill.

## JSON Review Plan For HTML Creation

`scripts/create_review_html.py` reuses the same review plan format as the legacy DOCX script. First produce a JSON file with this shape (Chinese values shown for the fields that must be Chinese):

```json
{
  "prompt": "Task prompt",
  "student_essay_paragraph_indices": [12, 14, 16, 18],
  "review_units": [
    {
      "original": "Student sentence or paragraph.",
      "comments": [{"target": "specific phrase", "text": "中文批注：问题 + 改法"}],
      "rewrite": "English Band 7.5 rewrite."
    }
  ],
  "scores": {
    "Task Response": "6.5",
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
  "model_essay": [
    "Paragraph 1: introduction with paraphrase and position.",
    "Paragraph 2: body paragraph 1.",
    "Paragraph 3: body paragraph 2.",
    "Paragraph 4: In conclusion, ..."
  ]
}
```

`focus_feedback` must contain 3-5 items. Optional fields used by the HTML renderer: `rewrite_note` on a review unit (Chinese one-sentence rewrite explanation), `strengths` (Chinese strengths list), and `model_structure_notes` (four Chinese notes). When omitted, the renderer generates a reasonable Chinese note.

Then run:

```bash
python3 scripts/create_review_html.py review_plan.json --input-docx MyEssay.docx --cleanup-plan
python3 scripts/validate_review_html.py "MyEssay(reviewed).html" --plan review_plan.json --input-docx MyEssay.docx
```

If the review plan is a permanent example/reference file, omit `--cleanup-plan`.

## Quality Bar

- The reviewed report is a single self-contained HTML file, not a DOCX.
- All comments, feedback, scoring explanations, rewrite notes, structure notes, and section headings are in Chinese; student original, italic rewrites, and model essay stay in English.
- Comments must be anchored to specific text inside the student essay paragraphs and numbered continuously; every `data-comment` matches a comment item and vice versa.
- Italic rewrites must appear after the original unit and be written at a stable Band 7.5 standard.
- The score must evaluate the original essay, not the revised essay.
- The model essay must be exactly 4 paragraphs, 250-300 words, and should stand securely at Band 8.0 according to the official Task 2 descriptors.
- The style should look closer to the teacher's samples than to a generic IELTS tutor.
- The generated HTML must pass `scripts/validate_review_html.py`.
- Temporary files from the review process should be removed after successful validation.
