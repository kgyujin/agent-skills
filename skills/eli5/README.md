<p align="right">
  <strong>English</strong> | <a href="README.ko.md">한국어</a>
</p>

<div align="center">

# eli5

[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-D97757)](#install)
[![Codex](https://img.shields.io/badge/Codex-skill-412991)](#install)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

An agent skill that explains any topic like you're five.<br>
Big pictures, almost no words.

</div>

Ask something like "how does DNS work?" and you get a single self-contained HTML explainer built from big visuals and very few words. The goal is something you could hand to a curious kid, or a very tired adult, and have it click right away.

This is a port of the [`eli5` skill](https://github.com/anthropics/claude-plugins-community/tree/main/eli5) that Thariq Shihipar wrote for Claude Code. It behaves exactly the same and is packaged so it works in both Claude Code and Codex skill folders.

## Usage

```text
/eli5 how does DNS work
```

```text
/eli5 why does the sky turn red at sunset
```

In Codex you can also call it with `$eli5`. The more concrete the question, the better the picture explainer.

## Install

```bash
npx skills add kgyujin/eli5-codex-skill -g
```

You'll be asked which tools to install it for (Claude Code, Codex). Requires Node.js. To pick from all of my skills at once, use `npx skills add kgyujin/agent-skills -g`.

| Task | Command |
| --- | --- |
| Update | `npx skills update -g eli5` |
| Remove | `npx skills remove -g eli5` |

<details>
<summary>Manual install (clone)</summary>

```bash
git clone https://github.com/kgyujin/eli5-codex-skill.git ~/.claude/skills/eli5
git clone https://github.com/kgyujin/eli5-codex-skill.git ~/.codex/skills/eli5
```

Run only the line for the tool you use. If you already cloned it elsewhere, a symlink works too: `ln -s /path/to/eli5-codex-skill ~/.codex/skills/eli5`. Then start a new session and try `/eli5 <topic>`.

</details>

> [!NOTE]
> Use either the npx install or the manual install on one machine, not both. They share the same skill folder.

## Layout

```text
eli5-codex-skill/
├── SKILL.md      # skill definition (name, description, prompt), shared by Claude Code and Codex
├── README.md     # this file
├── README.ko.md  # Korean version
└── LICENSE       # MIT
```

## Credits

- Original: [`eli5`](https://github.com/anthropics/claude-plugins-community/tree/main/eli5) in the claude-community marketplace by Thariq Shihipar, MIT License.
- This repo copies the original prompt into the skill folder layout without behavior changes.
