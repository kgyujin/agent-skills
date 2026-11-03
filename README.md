<div align="center">

# agent-skills

[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-D97757)](#설치)
[![Codex](https://img.shields.io/badge/Codex-skill-412991)](#설치)
[![스킬 동기화](https://github.com/kgyujin/agent-skills/actions/workflows/sync.yml/badge.svg)](https://github.com/kgyujin/agent-skills/actions/workflows/sync.yml)

Claude Code와 Codex에서 쓰는 제 스킬을 한곳에 모은 저장소입니다.<br>
명령 한 줄로 목록을 띄워 필요한 것만 골라 설치합니다.

</div>

## 설치

```bash
npx skills add kgyujin/agent-skills -g
```

스킬 목록이 나오면 스페이스로 원하는 것을 체크하고 Enter를 누릅니다. 이어서 설치할 도구(Claude Code, Codex)를 고르면 끝입니다. Node.js가 필요합니다.

목록을 거치지 않고 바로 설치할 수도 있습니다.

```bash
npx skills add kgyujin/agent-skills -g --skill doc-design --skill parallax -a claude-code -a codex   # 고른 것만
npx skills add kgyujin/agent-skills -g --skill '*' -a claude-code -a codex                          # 전부
```

## 갱신과 삭제

| 하려는 일 | 명령 |
| --- | --- |
| 설치한 스킬 전부 갱신 | `npx skills update -g` |
| 목록에서 골라 삭제 | `npx skills remove -g` |
| 이름으로 삭제 | `npx skills remove -g doc-design` |
| 이 저장소에서 설치한 스킬 전부 삭제 | `npx skills remove -g kgyujin/agent-skills` |
| 설치한 스킬 보기 | `npx skills ls -g` |

`-g`는 모든 프로젝트에서 쓰도록 사용자 폴더에 설치한다는 뜻입니다. 빼면 지금 있는 프로젝트 폴더에만 설치합니다.

## 스킬 목록

| 스킬 | 하는 일 | 원본 저장소 |
| --- | --- | --- |
| `aws-style-diagram` | AWS 공식 아이콘 스타일로 시스템 구성도, 배포 구성도, CI/CD 그림을 그립니다 | [aws-style-diagram-skill](https://github.com/kgyujin/aws-style-diagram-skill) |
| `doc-design` | PowerPoint에서 고칠 수 있는 발표 PPTX와 PDF, 보고서와 원페이저 PDF를 디자인합니다 | [doc-design-skill](https://github.com/kgyujin/doc-design-skill) |
| `eli5` | 어떤 주제든 다섯 살 아이에게 말하듯 큰 그림으로 설명합니다 | [eli5-codex-skill](https://github.com/kgyujin/eli5-codex-skill) |
| `job-application-tailor` | 채용공고에 맞춰 지원서류를 고치고 지원할 공고의 순서를 정합니다 | [job-application-tailor-skill](https://github.com/kgyujin/job-application-tailor-skill) |
| `parallax` | Claude와 Codex가 같은 대상을 따로 검토한 뒤 결과를 맞대어 보는 교차검증입니다 | [parallax-skill](https://github.com/kgyujin/parallax-skill) |
| `skill-router` | 스킬 이름을 말하지 않아도 요청에 맞는 스킬을 골라 쓰게 합니다 | [skill-router-skill](https://github.com/kgyujin/skill-router-skill) |

스킬별 사용법과 예시는 각 원본 저장소 README에 있습니다.

> [!NOTE]
> 한 컴퓨터에서 같은 스킬을 이 저장소와 원본 저장소 양쪽에서 설치하지 마세요. 둘 다 같은 스킬 폴더를 쓰기 때문에 서로 덮어씁니다.

## 이 저장소가 갱신되는 방식

스킬은 각 원본 저장소에서 고칩니다. 이 저장소는 그 내용을 복사해 둡니다.

1. [`sources.tsv`](sources.tsv)에 스킬 이름, 원본 저장소, 저장소 안 경로를 적습니다.
2. [`scripts/sync.sh`](scripts/sync.sh)가 원본 저장소를 받아 `skills/<이름>/`으로 복사합니다. 설치에 필요 없는 `install.sh`, `tests`, `evals`는 빼고 복사합니다.
3. GitHub Actions의 [스킬 동기화](.github/workflows/sync.yml)가 매일 03:00(한국 시간)에 2를 실행하고 바뀐 것이 있으면 커밋합니다. 급할 때는 Actions 탭에서 바로 실행합니다.

> [!IMPORTANT]
> `skills/` 아래 파일을 이 저장소에서 직접 고치면 다음 동기화 때 원본 내용으로 덮어써집니다. 고칠 것은 원본 저장소에서 고칩니다.

새 스킬을 더할 때는 `sources.tsv`에 한 줄을 넣고 `scripts/sync.sh`를 실행한 뒤 커밋합니다.
