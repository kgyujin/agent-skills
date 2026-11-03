<p align="right">
  <strong>🇺🇸 English</strong> | <a href="README.ko.md">🇰🇷 한국어</a>
</p>

# eli5 (Codex Skill)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Codex%20CLI-000000.svg)
![Format](https://img.shields.io/badge/format-SKILL.md-orange.svg)
![Ported from](https://img.shields.io/badge/ported%20from-Claude%20Code-6b57ff.svg)

> Explain literally anything like you're five years old — big pictures, almost no words.

This is a [Codex CLI](https://developers.openai.com/codex) skill, ported from the original [`eli5` skill](https://github.com/anthropics/claude-plugins-community/tree/main/eli5) built for Claude Code by Thariq Shihipar. It works exactly the same way, just packaged for `~/.codex/skills`.

## What it does

When you ask for an ELI5 explanation, the skill produces a self-contained HTML artifact that leans on big visuals and very few words — the kind of explainer you could hand to a curious kid (or a very tired adult) and have it click immediately.

## Usage

```
/eli5 how does DNS work
```

```
/eli5 why does the sky turn red at sunset
```

Swap in any topic — the more concrete the question, the better the picture-explainer turns out.

## Installation

### Install with npx

Install without cloning, then update or remove it with `npx skills`. Requires Node.js.

```bash
npx skills add kgyujin/eli5-codex-skill -g -a claude-code -a codex   # install
npx skills update -g eli5                                            # update
npx skills remove -g eli5                                            # remove
```

`-g` installs into your user folder so every project can use it, and `-a` picks the tools. Leave `-a` out to choose interactively. Don't mix this with the manual install below on the same machine, since both use the same skill folder.

### Manual install

Clone directly into your Codex skills directory:

```sh
git clone https://github.com/kgyujin/eli5-codex-skill.git ~/.codex/skills/eli5
```

Or, if you already have this repo cloned somewhere else, just symlink it in:

```sh
ln -s /path/to/eli5-codex-skill ~/.codex/skills/eli5
```

Restart or reload Codex CLI, then try `/eli5 <topic>`.

## How it's structured

```
eli5-codex-skill/
├── SKILL.md      # the skill definition Codex reads (name, description, prompt)
├── README.md     # you're reading it
├── README.ko.md  # Korean version of this file
└── LICENSE       # MIT
```

`SKILL.md` uses the same frontmatter format Codex and Claude Code both understand, so this skill (and most skills like it) is portable between the two tools with little to no change.

## Credits

- Original skill: [`eli5`](https://github.com/anthropics/claude-plugins-community/tree/main/eli5) in the claude-community marketplace, by Thariq Shihipar (MIT License).
- This repo is a straight port of that skill's prompt into the Codex CLI skill layout — no behavior changes.

## License

MIT — see [LICENSE](./LICENSE).
