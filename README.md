# agent-skills

Claude Code와 Codex에서 쓰는 제 스킬을 한곳에 모은 저장소입니다. 명령 한 줄로 목록을 띄워 필요한 스킬만 골라 설치하고, 갱신과 삭제도 같은 도구로 합니다.

## 설치

```bash
npx skills add kgyujin/agent-skills -g
```

실행하면 스킬 목록이 나옵니다. 스페이스로 원하는 스킬을 체크하고 Enter를 누르면, 이어서 설치할 도구(Claude Code, Codex 등)를 고릅니다. Node.js가 필요합니다.

목록 없이 바로 설치하려면 이렇게 씁니다.

```bash
npx skills add kgyujin/agent-skills -g --skill pdf-design --skill clean-ppt -a claude-code -a codex   # 고른 것만
npx skills add kgyujin/agent-skills -g --skill '*' -a claude-code -a codex                            # 전부
```

## 갱신과 삭제

```bash
npx skills update -g                        # 설치한 스킬 전부 갱신
npx skills remove -g                        # 목록에서 골라 삭제
npx skills remove -g pdf-design             # 이름으로 삭제
npx skills remove -g kgyujin/agent-skills   # 이 저장소에서 설치한 스킬 전부 삭제
npx skills ls -g                            # 설치한 스킬 보기
```

`-g`는 모든 프로젝트에서 쓰도록 사용자 폴더에 설치한다는 뜻입니다. 빼면 지금 있는 프로젝트 폴더에만 설치합니다.

## 스킬 목록

| 스킬 | 하는 일 | 원본 저장소 |
| --- | --- | --- |
| `aws-style-diagram` | AWS 공식 아이콘 스타일로 시스템 구성도, 배포 구성도, CI/CD 그림을 그립니다 | [aws-style-diagram-skill](https://github.com/kgyujin/aws-style-diagram-skill) |
| `clean-ppt` | 자료를 바탕으로 깔끔한 한국어 발표용 PPTX를 만들거나 기존 PPT를 다시 디자인합니다 | [clean-ppt-skill](https://github.com/kgyujin/clean-ppt-skill) |
| `eli5` | 어떤 주제든 다섯 살 아이도 알아듣게 그림처럼 풀어 설명합니다 | [eli5-codex-skill](https://github.com/kgyujin/eli5-codex-skill) |
| `job-application-tailor` | 채용공고에 맞춰 이력서, 자기소개서, 포트폴리오를 고치고 지원 순서를 비교합니다 | [job-application-tailor-skill](https://github.com/kgyujin/job-application-tailor-skill) |
| `parallax` | Claude와 Codex가 같은 대상을 따로 검토한 뒤 결과를 맞대어 보는 교차검증입니다 | [parallax-skill](https://github.com/kgyujin/parallax-skill) |
| `pdf-design` | 보고서, 원페이저, 발표 자료를 디자인해 PDF와 편집용 PPTX로 냅니다 | [pdf-design-skill](https://github.com/kgyujin/pdf-design-skill) |
| `skill-router` | 요청에 맞는 설치된 스킬을 골라 쓰고 여러 스킬을 조합합니다 | [skill-router-skill](https://github.com/kgyujin/skill-router-skill) |

스킬별 사용법과 예시는 각 원본 저장소 README에 있습니다.

> [!NOTE]
> 한 컴퓨터에서 같은 스킬을 이 저장소와 원본 저장소 양쪽에서 설치하지 마세요. 둘 다 같은 스킬 폴더를 쓰기 때문에 서로 덮어씁니다.

## 이 저장소가 갱신되는 방식

스킬은 각 원본 저장소에서 고치고, 이 저장소는 그 내용을 복사해 둡니다.

- [`sources.tsv`](sources.tsv)에 스킬 이름, 원본 저장소, 저장소 안 경로를 적습니다.
- [`scripts/sync.sh`](scripts/sync.sh)가 원본 저장소를 받아 `skills/<이름>/`으로 복사합니다. 개별 저장소용 `install.sh`, `tests`, `evals`는 빼고 복사합니다.
- GitHub Actions의 [스킬 동기화](.github/workflows/sync.yml)가 매일 03:00(한국 시간)에 위 스크립트를 돌리고, 바뀐 것이 있으면 커밋합니다. 급할 때는 Actions 탭에서 직접 실행합니다.

> [!IMPORTANT]
> `skills/` 아래 파일을 이 저장소에서 직접 고치면 다음 동기화 때 원본 내용으로 덮어써집니다. 고칠 것은 원본 저장소에서 고칩니다.

새 스킬을 더할 때는 `sources.tsv`에 한 줄을 넣고 `scripts/sync.sh`를 실행한 뒤 커밋합니다.
