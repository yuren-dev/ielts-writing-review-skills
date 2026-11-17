<div align="center">
  <img src="./assets/ielts-writing-review-skills-hero.png" alt="IELTS Writing Review Skills" width="100%">

  <h1>IELTS Writing Review Skills</h1>

  <p>
    面向 Codex、Claude Code 与 Antigravity CLI 的 IELTS Academic Writing Task 1 / Task 2 本地批改技能。
    输出单文件 HTML 批改报告：批注锚定学生原文、官方评分、教师风格点评、精修改写、Band 8.0 范文，
    批改与讲解全部使用中文。
  </p>

  <p>
    <a href="./README.md"><strong>简体中文</strong></a>
    · <a href="./docs/README.en.md">English</a>
    · <a href="./docs/README.ja.md">日本語</a>
    · <a href="./docs/README.ko.md">한국어</a>
    · <a href="./docs/README.es.md">Español</a>
    · <a href="./docs/README.vi.md">Tiếng Việt</a>
    · <a href="./docs/README.hi.md">हिन्दी</a>
    · <a href="./docs/README.ar.md">العربية</a>
    · <a href="./docs/README.fr.md">Français</a>
    · <a href="./docs/README.bn.md">বাংলা</a>
    · <a href="./docs/README.pt.md">Português</a>
    · <a href="./docs/README.id.md">Bahasa Indonesia</a>
    · <a href="./docs/README.ur.md">اردو</a>
    · <a href="./docs/README.ru.md">Русский</a>
  </p>

  <p>
    <a href="https://github.com/AaronL725/ielts-writing-review-skills/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/AaronL725/ielts-writing-review-skills?style=for-the-badge&label=Stars&color=ffd166"></a>
    <a href="./LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-8ef0b0?style=for-the-badge"></a>
    <img alt="Self-contained HTML output" src="https://img.shields.io/badge/output-HTML-62d2ff?style=for-the-badge">
    <img alt="Chinese marking and explanation" src="https://img.shields.io/badge/comments-中文-brightgreen?style=for-the-badge">
  </p>
</div>

## Fork 说明

本仓库是 [AaronL725/ielts-writing-review-skills](https://github.com/AaronL725/ielts-writing-review-skills) 的 fork（基于上游 commit `4b2428d`），遵循上游 MIT License。上游的教师样本、官方 band descriptors、提取脚本与致谢全部保留。

本 fork 的改动：

1. **输出改为 HTML**：批改产物是单个自包含 `.html` 文件（内联 CSS，无外链；Task 1 图表以 base64 内联），浏览器直接打开可读、可打印。不再默认生成 `(reviewed).docx`。
2. **批改和讲解都用中文**：所有批注、看图要点、评分说明、简短反馈、改写说明、范文结构说明和章节标题都用中文；学生原文、Band 7.5 斜体改写和 Band 8.0 范文保持英文。
3. **保留标注形式**：批注仍锚定学生原文的具体词句，带连续编号上标，并在段落后按编号列出；原文段落后仍附 Band 7.5 斜体改写。
4. 新增 HTML 生成与校验脚本；旧 DOCX 生成/校验脚本保留在 `scripts/` 中作为 legacy，不再被 SKILL.md 引用。

`docs/` 下的多语言 README 来自上游，仍描述上游的 DOCX 行为；本 fork 的用法以根目录中文 README 为准。

## 这个仓库是什么

这个仓库打包了两个 IELTS 写作批改 skills，让 AI agent 不只是给泛泛建议，而是按照接近真实老师的方式完成一整套批改流程：识别题目和学生原文、把中文批注锚定到具体词句、按官方评分维度打分、添加局部精修改写，并生成对应的高质量范文，最后产出一份可直接阅读和打印的 HTML 报告。

**默认目标水平：斜体改写稳定 Band 7.5，结尾范文稳定 Band 8.0。** 如果你不额外指定目标分，两个 skill 都会默认把局部 italic rewrite 校准到稳定 7.5，把最后的 model answer / model essay 校准到稳定 8.0。你也可以在 prompt 里写 `Target band: 7.5`、`Target band: 8.0` 等，让 agent 按你的目标分调整反馈重点。

| Skill | 适合场景 | 默认输出 |
| --- | --- | --- |
| `$ielts-task1-review` | Academic Task 1 图表、表格、地图、流程图、混合图 | 自包含 reviewed HTML：内联图表 + 中文看图要点、原文锚定批注（中文）、评分、反馈、Band 7.5 斜体改写、4 段 Band 8.0 范文 |
| `$ielts-task2-review` | Task 2 观点类、讨论类、问题解决类、利弊类、混合类作文 | 自包含 reviewed HTML：原文锚定批注（中文）、评分、反馈、Band 7.5 斜体改写、4 段 Band 8.0 范文 |

## 输入文件要求

请使用**未批改过的 `.docx`** 作为输入。Reviewed 文件只适合作为效果预览，不要再拿 reviewed 文件重复批改。

| 类型 | Word 文档中应该怎么放 | 不要这样放 |
| --- | --- | --- |
| Task 1 | 题目文字放在最前面；图表/地图/流程图作为 Word 内嵌图片放在题目后；学生答案放在图片后，并用正常段落分开 | 不要把学生答案放在图片前；不要缺少图表；不要把评分、范文或旧批注混进输入文件 |
| Task 2 | 题目完整放在最前面；如果有 outline，可以放在题目后、正式作文前；正式作文放在最后，并用正常段落分开 | 不要把题目放在作文后；不要把 outline 当成正式作文；不要把旧反馈、范文或 reviewed 内容放进输入文件 |

这些位置很重要，因为 skill 会先区分题目、图片、outline 和学生正文，再把 HTML 批注锚定到学生正文段落上。

## 示例文件

仓库的 `examples/` 目录包含一组 Task 1 和 Task 2 示例。未带 `(reviewed)` 的文件是输入示例；带 `(reviewed)` 的 HTML 是当前输出效果预览，旧的 reviewed DOCX 保留作对照。

| 示例 | 文件 |
| --- | --- |
| Task 1 输入 | [C19T4 Writing Task 1.docx](<./examples/C19T4 Writing Task 1.docx>) |
| Task 1 reviewed HTML（当前输出） | [C19T4 Writing Task 1(reviewed).html](<./examples/C19T4 Writing Task 1(reviewed).html>) |
| Task 2 输入 | [C19T4 Writing Task 2.docx](<./examples/C19T4 Writing Task 2.docx>) |
| Task 2 reviewed HTML（当前输出） | [C19T4 Writing Task 2(reviewed).html](<./examples/C19T4 Writing Task 2(reviewed).html>) |
| 旧版 reviewed DOCX（legacy 对照） | `examples/C19T4 Writing Task 1(reviewed).docx`、`examples/C19T4 Writing Task 2(reviewed).docx` |

示例 HTML 使用各 skill 的 `references/review_plan_example.json` 生成；Task 1 预览内联的图表来自 `references/sample_images/`。

## 核心亮点

| 真实批改体验 | IELTS 内置知识 | Agent 友好 |
| --- | --- | --- |
| 批注锚定学生原文，黄色高亮 + 连续编号，不是纯文本括号批注 | 使用官方 IELTS band descriptors 评分 | 可作为 Codex、Claude Code、Antigravity CLI 本地 skill 使用 |
| 批注、评分解释、反馈、改写说明全部中文 | 内置教师风格规则和样本提炼参考 | 包含 DOCX 提取、HTML 生成、HTML 校验脚本 |
| 在原文段落后插入 Band 7.5 斜体改写和中文改写说明 | Task 1 强制先看图，Task 2 强制先看任务回应 | 输出单文件 HTML，自包含、无外链、打印友好 |
| 输出分数页、短反馈和 Band 8.0 范文（含中文结构说明） | 默认斜体改写 Band 7.5，结尾范文 Band 8.0 | 保留原文件，只输出独立 reviewed HTML |

## 批改流程

```mermaid
flowchart LR
    A[学生答案或作文 .docx] --> B[提取题目 / 图片 / 正文]
    B --> C[按教师风格制定批改方案]
    C --> D[生成自包含 HTML]
    D --> E[HTML 校验]
    E --> F[中文分数、反馈与范文]
    D --> G[Reviewed HTML]
    E --> G
```

## 安装

### 通用 agent 安装提示词

```text
Install the IELTS Writing Review Skills from this GitHub repository: https://github.com/yuren-dev/ielts-writing-review-skills and put the two skills into the correct local skills directory.
```

也可以手动安装。先克隆本 fork：

```bash
git clone https://github.com/yuren-dev/ielts-writing-review-skills.git
cd ielts-writing-review-skills
```

### Codex

把两个 skill 安装到 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/ielts-task1-review skills/ielts-task2-review "${CODEX_HOME:-$HOME/.codex}/skills/"
```

### Claude Code

安装为 Claude Code 个人 skills：

```bash
mkdir -p "$HOME/.claude/skills"
cp -R skills/ielts-task1-review skills/ielts-task2-review "$HOME/.claude/skills/"
```

如果想只在某个项目中使用，可以复制到项目级 `.claude/skills`：

```bash
mkdir -p .claude/skills
cp -R skills/ielts-task1-review skills/ielts-task2-review .claude/skills/
```

### Antigravity CLI

把两个 skill 复制到 Antigravity CLI 的 skills 目录：

```bash
mkdir -p "$HOME/.gemini/antigravity-cli/skills"
cp -R skills/ielts-task1-review skills/ielts-task2-review "$HOME/.gemini/antigravity-cli/skills/"
```

安装后启动 Antigravity CLI 并执行 `/skills`，可以看到 `ielts-task1-review` 与 `ielts-task2-review`（本 fork 已按该路径实测可见）。

## Prompt 示例

```text
Use $ielts-task1-review to review my IELTS Academic Writing Task 1 answer: [paste the path of your answer]
```

```text
Use $ielts-task2-review to review my IELTS Writing Task 2 essay: [paste the path of your essay]
```

```text
Use $ielts-task1-review to review my IELTS Academic Writing Task 1 answer. Target band: [your target band]. File: [paste the path of your answer]
```

```text
Use $ielts-task2-review to review my IELTS Writing Task 2 essay. Target band: [your target band]. File: [paste the path of your essay]
```

输出文件与输入同目录：`MyEssay.docx` → `MyEssay(reviewed).html`，直接双击用浏览器打开即可；批注、评分解释和反馈都是中文。

## 每个 Skill 包含什么

Task 1 skill 包含视觉分析流程、Task 1 官方评分标准、教师风格批改规则、样本提炼参考、图表样本、DOCX 提取脚本、HTML 生成脚本（图表 base64 内联）和 HTML 校验脚本。

Task 2 skill 包含题目与作文提取、Task 2 官方评分标准、教师风格批改规则、样本提炼参考、教师样本匹配逻辑、HTML 生成脚本和 HTML 校验脚本。

两个 skill 的 `scripts/` 目录中还保留旧的 DOCX 生成与校验脚本（legacy），方便对照或回退；当前 SKILL.md 已不再使用它们。

## 仓库结构

```text
.
|-- assets/
|   `-- ielts-writing-review-skills-hero.png
|-- docs/
|   |-- README.ar.md
|   |-- README.bn.md
|   |-- README.en.md
|   |-- README.es.md
|   |-- README.fr.md
|   |-- README.hi.md
|   |-- README.id.md
|   |-- README.ja.md
|   |-- README.ko.md
|   |-- README.pt.md
|   |-- README.ru.md
|   |-- README.ur.md
|   `-- README.vi.md
|-- examples/
|   |-- C19T4 Writing Task 1.docx
|   |-- C19T4 Writing Task 1(reviewed).docx
|   |-- C19T4 Writing Task 1(reviewed).html
|   |-- C19T4 Writing Task 2.docx
|   |-- C19T4 Writing Task 2(reviewed).docx
|   `-- C19T4 Writing Task 2(reviewed).html
|-- skills/
|   |-- ielts-task1-review/
|   |   |-- SKILL.md
|   |   |-- agents/
|   |   |-- references/
|   |   `-- scripts/
|   `-- ielts-task2-review/
|       |-- SKILL.md
|       |-- agents/
|       |-- references/
|       `-- scripts/
|-- LICENSE
`-- README.md
```

## 兼容性

| Agent | 状态 | 说明 |
| --- | --- | --- |
| Codex | Ready | 复制到 `$CODEX_HOME/skills`，通常是 `~/.codex/skills` |
| Claude Code | Ready | 复制到 `~/.claude/skills` 或项目 `.claude/skills` |
| Antigravity CLI | Ready | 复制到 `~/.gemini/antigravity-cli/skills`，`/skills` 中可见 |
| 其他本地 agents | Manual | 使用通用安装提示词，并把两个 skill 放到对应 agent 的本地 skills 目录 |

## License 与致谢

- 本仓库基于 [AaronL725/ielts-writing-review-skills](https://github.com/AaronL725/ielts-writing-review-skills) fork 而来，感谢原作者整理教师样本、评分标准与技能框架。
- 上游与本 fork 均采用 [MIT License](./LICENSE)；使用、修改、再分发请保留上游版权与许可声明。
- 官方 IELTS band descriptors 的英文原文仅作评分参考，本 fork 的中文批改与讲解为额外改动。

## ⭐️ 给上游仓库点 Star

如果这个仓库能节省你批改 IELTS Writing 的时间，欢迎给上游 [AaronL725/ielts-writing-review-skills](https://github.com/AaronL725/ielts-writing-review-skills) 点一个 star。
