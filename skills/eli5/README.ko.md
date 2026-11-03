<p align="right">
  <a href="README.md">English</a> | <strong>한국어</strong>
</p>

<div align="center">

# eli5

[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-D97757)](#설치)
[![Codex](https://img.shields.io/badge/Codex-skill-412991)](#설치)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

어떤 주제든 다섯 살 아이에게 말하듯 설명해 주는 에이전트 스킬입니다.<br>
큰 그림 위주로, 글자는 최소한으로.

</div>

"DNS가 어떻게 동작해?"처럼 물으면 큰 그림과 짧은 글로 된 HTML 설명 자료 한 장을 만들어 줍니다. 호기심 많은 아이나 아주 피곤한 어른에게 바로 건네도 이해되는 수준이 목표입니다.

이 스킬은 Thariq Shihipar가 Claude Code용으로 만든 [`eli5` 스킬](https://github.com/anthropics/claude-plugins-community/tree/main/eli5)을 옮긴 것입니다. 동작은 원본과 같습니다. Claude Code와 Codex 양쪽 스킬 폴더에서 쓸 수 있게 묶었습니다.

## 사용법

```text
/eli5 DNS는 어떻게 동작하나요
```

```text
/eli5 노을이 질 때 하늘이 왜 빨갛게 변하나요
```

Codex에서는 `$eli5`로도 부릅니다. 질문이 구체적일수록 그림 설명도 좋아집니다.

## 설치

```bash
npx skills add kgyujin/eli5-codex-skill -g
```

설치할 도구(Claude Code, Codex)를 고르는 화면이 나옵니다. Node.js가 필요합니다. 제 다른 스킬과 함께 고르려면 `npx skills add kgyujin/agent-skills -g`를 쓰세요.

| 하려는 일 | 명령 |
| --- | --- |
| 갱신 | `npx skills update -g eli5` |
| 삭제 | `npx skills remove -g eli5` |

<details>
<summary>직접 설치(clone)</summary>

```bash
git clone https://github.com/kgyujin/eli5-codex-skill.git ~/.claude/skills/eli5
git clone https://github.com/kgyujin/eli5-codex-skill.git ~/.codex/skills/eli5
```

쓰는 도구 쪽 한 줄만 실행하면 됩니다. 이미 다른 곳에 받아 두었다면 `ln -s /path/to/eli5-codex-skill ~/.codex/skills/eli5`처럼 링크만 걸어도 됩니다. 설치한 뒤에는 새 대화에서 `/eli5 <주제>`로 부릅니다.

</details>

> [!NOTE]
> 한 컴퓨터에서는 npx 설치와 직접 설치 중 하나만 쓰세요. 두 방식이 같은 스킬 폴더를 씁니다.

## 폴더 구성

```text
eli5-codex-skill/
├── SKILL.md      # 스킬 정의(이름, 설명, 프롬프트). Claude Code와 Codex 공용
├── README.md     # 영어 안내
├── README.ko.md  # 한국어 안내(지금 문서)
└── LICENSE       # MIT
```

## 출처

- 원본: claude-community 마켓플레이스의 [`eli5`](https://github.com/anthropics/claude-plugins-community/tree/main/eli5), 작성자 Thariq Shihipar, MIT 라이선스
- 이 저장소는 원본 프롬프트를 스킬 폴더 구조에 맞춰 그대로 옮겼고 동작은 바꾸지 않았습니다.
