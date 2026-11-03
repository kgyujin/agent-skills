# 채용공고 맞춤형 지원서류 튜닝

![License](https://img.shields.io/github/license/kgyujin/job-application-tailor-skill)
![Last Commit](https://img.shields.io/github/last-commit/kgyujin/job-application-tailor-skill)
![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-6b46c1?logo=anthropic&logoColor=white)
![Codex](https://img.shields.io/badge/Codex-compatible-10a37f?logo=openai&logoColor=white)
![Skill Format](https://img.shields.io/badge/format-SKILL.md-blue)

이 스킬은 채용공고와 지원서류를 비교해 맞춤형 수정안을 만들고, 여러 공고의 지원 우선순위를 정하며, GitHub 저장소에서 포트폴리오 후보를 정리합니다. Claude Code와 Codex에서 같은 `SKILL.md`를 사용할 수 있습니다.

## 한눈에 보기

| 모드 | 이런 때 사용하세요 | 결과 |
| --- | --- | --- |
| 모드 A: 단일 공고 튜닝 | 공고 하나에 맞춰 지원서류를 조정할 때 | 새 지원서류와 부족한 요건(gap) 보고 |
| 모드 B: 다중 공고 순위 | 여러 공고 중 지원할 순서를 정할 때 | 100점 만점 적합도 순위표 |
| 모드 C: GitHub 프로젝트 정리 | GitHub에서 포트폴리오 후보를 찾을 때 | 사용자 확인을 거친 프로젝트 초안 |

처음 사용할 때는 다음 순서로 진행하세요:

1. Claude Code 또는 Codex에 스킬을 설치합니다.
2. 원하는 모드의 예시처럼 채용공고와 서류 또는 GitHub 정리 요청을 전달합니다.
3. 결과를 확인합니다. 모드 C는 초안에 포함할 저장소를 먼저 확정합니다. 모드 A와 B에서는 원본 보존 여부와 gap을 확인합니다.

## 설치

### npx로 설치

clone 없이 설치하고, 갱신과 삭제도 `npx skills`로 합니다. Node.js가 필요합니다.

```bash
npx skills add kgyujin/job-application-tailor-skill -g -a claude-code -a codex   # 설치
npx skills update -g job-application-tailor                                      # 갱신
npx skills remove -g job-application-tailor                                      # 삭제
```

`-g`는 모든 프로젝트에서 쓰도록 사용자 폴더에 설치하고, `-a`는 설치할 도구를 고릅니다. `-a`를 빼면 설치할 때 물어봅니다. 같은 컴퓨터에서 아래 직접 설치와 함께 쓰지 마세요. 두 방식이 같은 스킬 폴더를 씁니다.

### Claude Code

다음 명령으로 스킬을 설치하세요:

```bash
git clone \
  https://github.com/kgyujin/job-application-tailor-skill.git \
  ~/.claude/skills/job-application-tailor-skill
```

설치 후 Claude Code를 재시작하면 `job-application-tailor` 스킬이 표시됩니다. 대화 중 “이 채용공고에 맞게 이력서 수정해줘”처럼 요청하면 Claude가 이 스킬을 불러옵니다.

### Codex

Codex 앱이나 클라이언트가 네이티브 스킬 폴더를 지원하면 다음 경로에 설치하세요:

```bash
git clone \
  https://github.com/kgyujin/job-application-tailor-skill.git \
  ~/.codex/skills/job-application-tailor-skill
```

이후 “이 채용공고에 맞게 서류 다듬어줘”라고 요청하면 Codex가 `SKILL.md`를 자동으로 찾아 따릅니다.

스킬 폴더 자동 인식을 지원하지 않는 순수 `codex-cli` 환경에서는 같은 경로에 클론한 뒤, 대화에서 파일을 직접 지정하세요:

```text
~/.codex/skills/job-application-tailor-skill/SKILL.md의 절차에 따라
[채용공고]에 맞게 [이력서/자기소개서/포트폴리오]를 수정해줘.
```

또는 프로젝트 루트나 `~/.codex/AGENTS.md`에 다음 참조를 추가할 수 있습니다:

```markdown
## 채용공고 맞춤형 서류 작성
채용공고에 맞춰 이력서/자기소개서/포트폴리오를 수정해야 하면
~/.codex/skills/job-application-tailor-skill/SKILL.md의 절차를 따른다.
```

## 모드 C를 위한 추가 준비

모드 C는 GitHub CLI(`gh`), GitHub용 명령줄 도구로 GitHub 데이터를 읽습니다. 사용 전에 다음을 확인하세요:

- [GitHub CLI(`gh`)](https://cli.github.com) 설치
- `gh auth login`으로 로그인
- `gh auth status`로 인증 상태 확인

비공개 저장소까지 스캔하려면 인증에 `repo` 스코프가 필요합니다. 모드 A와 B는 `gh`를 추가로 설치하지 않아도 됩니다.

## 사용 방법

아래 예시처럼 자연어로 요청하세요. 모드 C로 만든 초안은 검토한 뒤 모드 A의 포트폴리오 조정이나 모드 B의 사용자 프로필 보완에 활용할 수 있습니다.

### 모드 A: 단일 공고 튜닝

공고 하나에 맞춰 이력서·자기소개서·포트폴리오의 내용과 순서를 조정할 때 사용하세요.

입력 예시는 다음과 같습니다:

```text
[채용공고 원문 또는 URL]

내 이력서: ./이력서.md
내 자기소개서: ./자기소개서.md
내 포트폴리오: ./포트폴리오.md

이 공고에 맞게 위 서류들을 수정해줘.
```

진행 순서는 다음과 같습니다:

1. 공고의 필수 자격요건·우대사항·주요 업무·기술 키워드를 요약합니다.
2. 기존 서류와 요구사항을 대조해 매칭 항목과 부족한 항목(gap)을 분류합니다.
3. 요청받은 서류만 작성합니다. 기존 자기소개서가 없어도 확인된 경험으로 신규 작성할 수 있습니다.
4. 문항별 구조, 단어·구절·내용 반복과 최종 분량을 검토합니다. 반복 판단 기준은 [SKILL.md](./SKILL.md)를 따릅니다.
5. 사실 근거와 확인 사항은 제출 본문과 별도인 검토 메모에 남기고, 미확인이 남으면 초안으로 표시합니다.

결과는 원본을 덮어쓰지 않고 새 파일로 저장합니다:

- 이력서: `이력서_회사명_직무명_v01.md`
- 자기소개서: `자기소개서_회사명_직무명_v01.md`
- 포트폴리오: `포트폴리오_조정메모_회사명_직무명_v01.md`

같은 파일이 있으면 다음 버전을 사용합니다. 저장 위치의 문서 규칙을 우선하며, 원본 형식을 유지할 수 있으면 해당 확장자를 사용합니다. 텍스트 수정안은 글꼴·시각 양식 보존을 보장하지 않습니다.

### 모드 B: 다중 공고 순위 매기기

공고 두 개 이상을 비교해 지원 우선순위를 정할 때 사용하세요.

입력 예시는 다음과 같습니다:

```text
[채용공고 1 원문 또는 URL]
[채용공고 2 원문 또는 URL]
[채용공고 3 원문 또는 URL]

내 이력서: ./이력서.md

이 공고들 중 나에게 맞는 순서대로 순위를 매겨줘.
```

기본 채점 기준은 다음과 같습니다:

| 기준 | 기본 가중치 |
| --- | ---: |
| 필수 자격요건 충족률 | 40% |
| 우대사항 충족률 | 20% |
| 직무 범위 적합도 | 15% |
| 경력 연차 부합도 | 10% |
| 근무조건 적합도 | 15% |

충족, 부분 충족, 미충족, 미확인과 해당 없음을 구분합니다. 해당 없음만 제외해 가중치를 재배분하고, 미확인은 점수 범위와 정보 충족률로 표시합니다. 상세 계산은 [채점 기준](./reference/ranking-criteria.md)을 따릅니다.

진행 순서는 다음과 같습니다:

1. 공고별 필수 자격요건·우대사항·근무조건을 정리합니다.
2. 사용자의 경력 연차·기술 스택·도메인 경험을 추출합니다.
3. 확인된 정보에는 점수와 등급을, 정보가 부족하면 잠정 범위를 제시합니다. 평가 근거가 전혀 없으면 순위를 만들지 않습니다.
4. 지원 필수 조건 미충족은 점수와 별도로 표시하고 강력 추천으로 분류하지 않습니다.
5. 사용자가 선택한 공고는 모드 A로 이어서 튜닝합니다.

### 모드 C: GitHub 프로젝트 자동 정리

GitHub 저장소에서 포트폴리오에 활용할 프로젝트를 찾고 초안으로 정리할 때 사용하세요.

입력 예시는 다음과 같습니다:

```text
내 GitHub 저장소 중 포트폴리오에 쓸 만한 프로젝트를 정리해줘.
public 저장소만 봐줘.
```

진행 순서는 다음과 같습니다:

1. `gh` 설치와 인증 상태를 확인합니다. 준비되지 않았다면 안내 후 멈춥니다.
2. 지정한 공개 범위와 조직을 적용하며, 이미 제공한 선택은 재확인하지 않습니다.
3. README, 설정·의존성 파일, 언어 통계와 커밋 수 비율을 조사합니다. 조회 한도와 누락 가능성도 보고합니다.
4. 후보와 근거를 제시하고 새 후보의 포함 여부, 실제 역할·수행 기간과 공개 가능 범위를 확인합니다. 저장소 활동 기간과 커밋 수 비율을 실제 수행 기간·기여도로 단정하지 않습니다.
5. 확정된 저장소만으로 Markdown 초안을 만듭니다. [resume-markdown-editor](https://github.com/kgyujin/resume-markdown-editor) 호환성은 실제 대상 버전의 계약을 확인한 경우에만 검증됐다고 보고합니다.
6. `github_프로젝트_초안_YYYY-MM-DD_v01.md`로 저장하고, 사용자가 요청한 후속 작업을 확인된 근거로 진행합니다.

비공개 저장소의 조회 허용과 지원서 기재 허용은 구분합니다. 공개 가능 범위가 미확인인 정보는 제출용 초안에 넣지 않습니다. README의 프로젝트 성과는 본인 역할을 확인한 뒤 개인 경험에 반영하며, 확인 질문은 별도 검토 메모에 남깁니다.

## 핵심 원칙

- **사실 왜곡 금지**: 기존 서류와 GitHub 자료에서 확인한 사실만 사용합니다. 근거 없는 경력·기술·성과 수치는 만들지 않습니다.
- **원본 보존**: 지원서류와 포트폴리오 원본을 덮어쓰지 않고 새 파일이나 조정 메모로 저장합니다.
- **gap 공개**: 요구사항과 매칭되지 않거나 확인이 필요한 항목을 숨기지 않고 보고합니다.
- **로컬 인증만 사용**: 모드 C는 사용자의 로컬 `gh` 인증 세션으로 GitHub 데이터를 읽습니다. 토큰을 코드나 파일에 저장하지 않습니다.

## 세부 기준과 절차

- [`SKILL.md`](./SKILL.md): 모드 A·B·C의 전체 실행 절차
- [`reference/checklist.md`](./reference/checklist.md): 모드 A 최종 점검 목록
- [`reference/ranking-criteria.md`](./reference/ranking-criteria.md): 모드 B 배점과 경계 사례
- [`reference/github-scan-criteria.md`](./reference/github-scan-criteria.md): 모드 C 저장소 필터링, `gh` 명령, Markdown 필드 매핑

## 저장소 구조

```text
job-application-tailor-skill/
├── SKILL.md                    # 모드 A·B·C 전체 절차
├── reference/
│   ├── checklist.md            # 모드 A 점검 목록
│   ├── ranking-criteria.md     # 모드 B 채점 기준
│   └── github-scan-criteria.md # 모드 C GitHub 스캔 기준
├── README.md
└── LICENSE
```

## 라이선스

[MIT](./LICENSE)
