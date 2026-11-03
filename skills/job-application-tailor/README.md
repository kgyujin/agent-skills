<div align="center">

# job-application-tailor

[![Claude Code](https://img.shields.io/badge/Claude_Code-skill-D97757)](#설치)
[![Codex](https://img.shields.io/badge/Codex-skill-412991)](#설치)
[![License](https://img.shields.io/github/license/kgyujin/job-application-tailor-skill)](LICENSE)

이 에이전트 스킬은 채용공고에 맞춰 지원서류를 고치고 지원할 공고의 순서를 정합니다.<br>
GitHub 저장소에서 포트폴리오에 쓸 프로젝트를 찾아 초안으로 정리하기도 합니다.

</div>

공고를 볼 때마다 이력서와 자기소개서를 손으로 맞추면 놓치는 요건이 생깁니다. 있지도 않은 경험을 부풀리기도 쉽습니다. 이 스킬은 공고의 요건과 내 서류를 한 줄씩 대조해 맞는 것과 부족한 것을 나눕니다. 확인된 사실만으로 새 서류를 씁니다. 원본은 건드리지 않고 새 파일로 저장합니다.

## 세 가지 모드

| 모드 | 이럴 때 | 결과 |
| --- | --- | --- |
| A. 공고 하나에 맞추기 | 지원할 공고가 정해졌을 때 | 고친 이력서, 자기소개서, 포트폴리오 메모와 부족한 요건(gap) 목록 |
| B. 여러 공고 순위 매기기 | 어디부터 지원할지 고민될 때 | 100점 만점 적합도 순위표 |
| C. GitHub 프로젝트 정리 | 포트폴리오에 넣을 프로젝트를 찾을 때 | 내가 고른 저장소만 담은 프로젝트 초안 |

C로 만든 초안은 A에서 포트폴리오를 조정하거나 B에서 내 정보를 보완할 때 이어서 쓸 수 있습니다.

## 설치

```bash
npx skills add kgyujin/job-application-tailor-skill -g
```

설치할 도구(Claude Code, Codex)를 고르는 화면이 나옵니다. Node.js가 필요합니다. 제 다른 스킬과 함께 고르려면 `npx skills add kgyujin/agent-skills -g`를 쓰세요.

| 하려는 일 | 명령 |
| --- | --- |
| 갱신 | `npx skills update -g job-application-tailor` |
| 삭제 | `npx skills remove -g job-application-tailor` |

모드 C는 [GitHub CLI](https://cli.github.com)(`gh`)로 저장소를 읽습니다. `gh auth login`으로 로그인하고 `gh auth status`로 확인해 두세요. 비공개 저장소까지 보려면 `repo` 권한이 필요합니다. A와 B는 `gh`가 없어도 됩니다.

<details>
<summary>직접 설치(clone)</summary>

```bash
git clone https://github.com/kgyujin/job-application-tailor-skill.git ~/.claude/skills/job-application-tailor
git clone https://github.com/kgyujin/job-application-tailor-skill.git ~/.codex/skills/job-application-tailor
```

쓰는 도구 쪽 한 줄만 실행하면 됩니다. 스킬 폴더를 인식하지 않는 Codex CLI라면 `~/.codex/AGENTS.md`에 다음을 넣습니다.

```markdown
## 채용공고 맞춤형 서류 작성
채용공고에 맞춰 이력서/자기소개서/포트폴리오를 수정해야 하면
~/.codex/skills/job-application-tailor/SKILL.md의 절차를 따른다.
```

</details>

> [!NOTE]
> 한 컴퓨터에서는 npx 설치와 직접 설치 중 하나만 쓰세요. 두 방식이 같은 스킬 폴더를 씁니다.

## 사용법

자연어로 요청하면 됩니다. Claude Code에서는 `/job-application-tailor`, Codex에서는 `$job-application-tailor`로 직접 부를 수도 있습니다.

### A. 공고 하나에 맞추기

```text
[채용공고 원문 또는 URL]

내 이력서: ./이력서.md
내 자기소개서: ./자기소개서.md
내 포트폴리오: ./포트폴리오.md

이 공고에 맞게 위 서류들을 수정해줘.
```

1. 공고의 필수 요건, 우대사항, 주요 업무, 기술 키워드를 요약합니다.
2. 내 서류와 대조해 맞는 항목과 부족한 항목(gap)을 나눕니다.
3. 요청한 서류만 씁니다. 자기소개서가 없으면 확인된 경험으로 새로 씁니다.
4. 문항별 구조, 같은 표현의 반복, 분량을 점검합니다.
5. 근거와 확인할 점은 제출용 본문과 따로 검토 메모에 남깁니다. 확인 안 된 것이 있으면 초안으로 표시합니다.

결과는 `이력서_회사명_직무명_v01.md`처럼 새 파일로 저장합니다. 같은 이름이 있으면 다음 버전 번호를 씁니다. 글꼴이나 시각 양식까지 보존한다고 약속하지는 않습니다.

### B. 여러 공고 순위 매기기

```text
[채용공고 1 원문 또는 URL]
[채용공고 2 원문 또는 URL]

내 이력서: ./이력서.md

이 공고들 중 나에게 맞는 순서대로 순위를 매겨줘.
```

| 기준 | 기본 비중 |
| --- | ---: |
| 필수 요건 충족 | 40% |
| 우대사항 충족 | 20% |
| 직무 범위 적합도 | 15% |
| 근무조건 적합도 | 15% |
| 경력 연차 부합 | 10% |

요건마다 충족, 부분 충족, 미충족, 미확인, 해당 없음으로 나눕니다. 정보가 부족하면 점수 대신 범위로 보여 줍니다. 필수 요건을 못 채운 공고는 점수와 별도로 표시합니다. 자세한 계산은 [채점 기준](reference/ranking-criteria.md)에 있습니다.

### C. GitHub 프로젝트 정리

```text
내 GitHub 저장소 중 포트폴리오에 쓸 만한 프로젝트를 정리해줘. public 저장소만 봐줘.
```

1. `gh` 로그인 상태를 확인합니다. 준비가 안 됐으면 방법을 안내하고 멈춥니다.
2. README, 설정과 의존성 파일, 언어 비율, 커밋 비율을 살펴 후보를 고릅니다.
3. 후보마다 근거를 보여 줍니다. 넣을지, 내 실제 역할과 기간, 공개해도 되는 범위를 묻습니다. 커밋 수만으로 기여도를 단정하지 않습니다.
4. 확정한 저장소만으로 `github_프로젝트_초안_YYYY-MM-DD_v01.md`를 만듭니다.

비공개 저장소는 읽어도 되는지와 지원서에 써도 되는지를 구분합니다. 공개 범위를 확인하지 못한 정보는 제출용 초안에 넣지 않습니다.

## 지키는 원칙

- **사실만 씁니다.** 서류와 GitHub에서 확인한 것만 씁니다. 근거 없는 경력, 기술, 성과 수치를 만들지 않습니다.
- **원본을 지킵니다.** 원본 파일을 덮어쓰지 않고 새 파일이나 메모로 저장합니다.
- **부족한 점을 숨기지 않습니다.** 공고와 맞지 않거나 확인이 필요한 항목을 그대로 알려 줍니다.
- **토큰을 저장하지 않습니다.** 모드 C는 내 컴퓨터의 `gh` 로그인만 씁니다.

## 폴더 구성

```text
job-application-tailor-skill/
├── SKILL.md                     # 모드 A, B, C 전체 절차
├── reference/
│   ├── checklist.md             # 모드 A 최종 점검 목록
│   ├── ranking-criteria.md      # 모드 B 채점 기준과 경계 사례
│   └── github-scan-criteria.md  # 모드 C 저장소 고르기, gh 명령, 초안 항목
└── LICENSE
```
