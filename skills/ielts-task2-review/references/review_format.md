# Reviewed HTML Format

每次 Task 2 批改输出**一个自包含 HTML 文件**（不是 DOCX）。浏览器直接打开可读、可打印；不引用任何外部 CSS、JS、字体或图片。本文档规定 HTML 的结构、class 名与中英文分工。

## 输出文件命名

- DOCX 输入：输出到输入文件同目录，`MyEssay.docx` → `MyEssay(reviewed).html`。
- 粘贴文本输入：用 `--output` 指定路径；未指定时输出到当前目录 `IELTS_Task2_Reviewed_YYYYMMDD_HHMM.html`。
- 永不覆盖原始输入；默认遇到同名输出时自动改用 `(reviewed 2).html` 等，只有显式 `--overwrite` 才覆盖。
- 输入仍是**未批改过的 `.docx`**：先运行 `scripts/extract_task2_input.py`，提取流程与旧 DOCX 流程相同。

## 五段结构

输出必须按以下顺序包含五段。评分针对**学生原稿**，不是改写稿。

1. **页头**：`header.review-header`
   - `<h1>` 中文标题（如“雅思写作 Task 2 批改报告”）。
   - `<dl class="meta">` 列出输入文件名、批改日期、目标分（默认 Band 7.5 改写 / Band 8.0 范文）。
   - `div.prompt`：`<h2>题目</h2>` + `p.prompt-text`（题目保持英文原文）。
   - `table.score-table`：四项分数 + 总分（Overall），行标签中文并括注英文评分项名称。
   - `ul.score-notes`：中文评分说明（来自 `score_explanation`）。
2. **带批注的原文**：`section#reviewed-text`
   - 按顺序复现学生原文段落，每段一个 `div.paragraph-block > p.original`。
   - 凡有批注的词句用 `<mark class="comment" data-comment="N" data-target="原文词句">原文词句<sup class="comment-ref">N</sup></mark>` 包裹；编号从 1 连续递增。
   - 批注列在该段下方：`ol.comment-list > li.comment-item[data-comment="N"]`，内含 `span.comment-target`（原文词句）和 `span.comment-text`（中文批注）。
3. **斜体改写**：每个 `paragraph-block` 内，原文段与批注之后放 `div.rewrite`
   - `p.rewrite-text > em`：英文 Band 7.5 改写，斜体。
   - `p.rewrite-note`：一句中文说明，讲清改了什么、为什么这样改。
4. **简短反馈**：`section#feedback`
   - `<h2>简短反馈</h2>`。
   - `<h3>优点</h3>` + `ul.strengths`（至少 1 条中文）。
   - `<h3>优先改进点</h3>` + `ol.improvements`（3–5 条中文，先写阻止稳定 Band 7.5 的问题，再写迈向 8.0 的方向）。
5. **范文**：`section#model-essay`
   - `<h2>Band 8.0 范文</h2>`，四个 `p.model-paragraph`（英文，250–300 词，四段：引言 / 主体一 / 主体二 / In conclusion 结论）。
   - `p.model-wordcount` 中文词数行。
   - `div.model-note`：`<h3>范文结构说明</h3>` + `ol.structure-notes`（4 条中文，说明每段作用）。

## CSS class 约定

| 选择器 | 作用 |
| --- | --- |
| `header.review-header` | 页头（标题、元信息、题目、分数表、评分说明） |
| `dl.meta` | 输入文件 / 日期 / 目标分 |
| `table.score-table` | 四项分数 + 总分表；整体行加 `.overall` |
| `ul.score-notes` | 中文评分说明 |
| `section#reviewed-text` | 带批注的正文 |
| `div.paragraph-block` | 一个原文段落 + 该段批注 + 该段改写 |
| `p.original` | 学生原文（英文） |
| `mark.comment` | 批注锚点高亮；`data-comment` 为编号，`data-target` 为原文词句 |
| `sup.comment-ref` | 锚点编号上标 |
| `ol.comment-list` / `li.comment-item` | 段落后批注列表；`li` 的 `data-comment` 与锚点一一对应 |
| `span.comment-target` | 批注所针对的原文词句 |
| `span.comment-text` | 中文批注（问题 + 改法） |
| `div.rewrite` / `p.rewrite-text` / `p.rewrite-note` | 斜体改写块（英文斜体 + 中文说明） |
| `section#feedback` / `ul.strengths` / `ol.improvements` | 简短反馈 |
| `section#model-essay` / `p.model-paragraph` / `p.model-wordcount` / `div.model-note` / `ol.structure-notes` | Band 8.0 范文与结构说明 |

## 最小示例片段

```html
<div class="paragraph-block">
  <p class="original">Some people think practical skills are <mark class="comment" data-comment="1" data-target="very important">very important<sup class="comment-ref">1</sup></mark> for students.</p>
  <ol class="comment-list">
    <li class="comment-item" data-comment="1"><span class="comment-target">very important</span><span class="comment-text">“非常重要”过于笼统，建议改成更精确的程度表达，如 a key role。</span></li>
  </ol>
  <div class="rewrite">
    <p class="rewrite-text"><em>Some people argue that practical skills play a key role in students’ education.</em></p>
    <p class="rewrite-note">改写说明：把笼统的 very important 换成更精确的 a key role，语气更学术，原意不变。</p>
  </div>
</div>
```

## 批注写法

- 每条批注必须锚定学生原文的**具体词句**（`target` 必须在 `p.original` 中逐字出现；找不到就让生成脚本报错，不要退化成整段或题目）。
- 编号唯一且从 1 连续递增；每个 `data-comment` 都有对应批注，每条批注都有对应锚点。
- 批注用中文，写清**问题 + 怎么改**，例如“口语化，建议换成 …”“与前句重复，建议用 whereas 引出对比”。
- 禁止脱离原文的泛泛建议（如“注意语法”“多积累词汇”），禁止把批注锚到题目、outline、评分区或范文上。
- 中文批注中可保留被引用的英文原词、术语或改写示例；但这些英文只作为引用或术语出现，整条批注仍须是中文。

## 中英文分工

- **中文**：所有批注、评分说明、简短反馈、改写说明、范文结构说明、章节标题、页头标签、目标分说明。
- **英文**：学生原文、Band 7.5 斜体改写、Band 8.0 范文。
- 官方 band descriptor 可引用简短英文原文，但必须紧跟中文解释。
- 评分项名称采用“中文（English criterion）”形式，英文只作为术语。

## 自包含与打印

- `<html lang="zh-CN">`、`<meta charset="utf-8">`，全文 UTF-8。
- 样式全部写在 `<head>` 的内联 `<style>` 中；不出现外链 CSS/JS/字体/图片，不出现 `http(s)://` 形式的 `src`/`href`。
- 不使用 `<script>`；不引用外部图标或 CDN。
- 白底黑字，批注高亮在打印时仍可辨认；`@media print` 中保留 `mark.comment` 底色，并让反馈与范文另起一页。

## 校验

```bash
python3 scripts/validate_review_html.py "MyEssay(reviewed).html" --plan review_plan.json --input-docx MyEssay.docx
```

校验器会检查：HTML 可解析、五段结构齐全、UTF-8、自包含、批注编号连续且与锚点一一对应、每条批注与反馈含中文、改写段数/批注条数/范文词数与 plan 一致。

## 清理

成功生成并通过校验后，删除临时 `review_plan_*.json`、临时提取文本等副产物；不要删除学生原稿、最终 `(reviewed).html` 或仓库内的参考文件。
