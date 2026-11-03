<p align="right">
  <a href="README.md">🇺🇸 English</a> | <strong>🇰🇷 한국어</strong>
</p>

# eli5 (Codex Skill)

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Codex%20CLI-000000.svg)
![Format](https://img.shields.io/badge/format-SKILL.md-orange.svg)
![Ported from](https://img.shields.io/badge/ported%20from-Claude%20Code-6b57ff.svg)

> 어떤 주제든 5살짜리에게 설명하듯 — 큰 그림 위주, 글자는 최소한으로.

이 저장소는 [Codex CLI](https://developers.openai.com/codex) 스킬로, Thariq Shihipar가 Claude Code용으로 만든 원본 [`eli5` 스킬](https://github.com/anthropics/claude-plugins-community/tree/main/eli5)을 그대로 이식한 버전입니다. 동작 방식은 완전히 동일하고, `~/.codex/skills`에서 쓸 수 있도록 패키징만 다시 했습니다.

## 무엇을 하나요

ELI5 설명을 요청하면, 이 스킬은 큰 이미지와 최소한의 텍스트로 구성된 독립형 HTML artifact를 만들어 줍니다. 호기심 많은 아이(혹은 아주 피곤한 어른)에게 바로 건네줘도 이해가 될 만한 설명 자료입니다.

## 사용법

```
/eli5 DNS는 어떻게 동작하나요
```

```
/eli5 노을이 질 때 하늘이 왜 빨갛게 변하나요
```

주제는 자유롭게 바꿔서 사용하세요. 질문이 구체적일수록 결과물도 더 좋아집니다.

## 설치

### npx로 설치

clone 없이 설치하고, 갱신과 삭제도 `npx skills`로 합니다. Node.js가 필요합니다.

```bash
npx skills add kgyujin/eli5-codex-skill -g -a claude-code -a codex   # 설치
npx skills update -g eli5                                            # 갱신
npx skills remove -g eli5                                            # 삭제
```

`-g`는 모든 프로젝트에서 쓰도록 사용자 폴더에 설치하고, `-a`는 설치할 도구를 고릅니다. `-a`를 빼면 설치할 때 물어봅니다. 같은 컴퓨터에서 아래 직접 설치와 함께 쓰지 마세요. 두 방식이 같은 스킬 폴더를 씁니다.

### 직접 설치

Codex 스킬 디렉터리에 바로 클론합니다.

```sh
git clone https://github.com/kgyujin/eli5-codex-skill.git ~/.codex/skills/eli5
```

이미 다른 경로에 이 저장소를 클론해 두었다면, 심볼릭 링크만 걸어도 됩니다.

```sh
ln -s /path/to/eli5-codex-skill ~/.codex/skills/eli5
```

Codex CLI를 재시작(또는 리로드)한 뒤 `/eli5 <주제>`로 바로 사용할 수 있습니다.

## 구성

```
eli5-codex-skill/
├── SKILL.md      # Codex가 읽는 스킬 정의(이름, 설명, 프롬프트)
├── README.md     # 영어 버전(기본)
├── README.ko.md  # 지금 보고 있는 한국어 버전
└── LICENSE       # MIT
```

`SKILL.md`는 Codex와 Claude Code가 공통으로 이해하는 프런트매터 형식을 사용하기 때문에, 이 스킬(그리고 대부분의 유사한 스킬)은 두 도구 사이를 거의 손대지 않고 오갈 수 있습니다.

## 출처 및 크레딧

- 원본 스킬: claude-community 마켓플레이스의 [`eli5`](https://github.com/anthropics/claude-plugins-community/tree/main/eli5), 작성자 Thariq Shihipar (MIT License).
- 이 저장소는 원본 스킬의 프롬프트를 Codex CLI 스킬 구조에 맞춰 그대로 옮긴 것이며, 동작상 변경 사항은 없습니다.

## 라이선스

MIT — [LICENSE](./LICENSE) 참고.
