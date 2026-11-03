# 도구별 설치와 호출

배포 저장소 이름은 `skill-router-skill`, 내부 스킬 이름은 `skill-router`로 유지한다. 저장소를 만들거나 이름을 변경한 사실을 이 안내만으로 주장하지 않는다.

권장 배포 구조:

```text
skill-router-skill/
└── skills/
    └── skill-router/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── references/hosts.md
```

`SKILL.md`의 frontmatter는 두 도구가 공유하는 `name`과 `description`을 사용한다. Codex 전용 자동 호출 설정은 `agents/openai.yaml`에 두고, Claude Code에서는 기본 자동 호출 동작을 사용한다. 이 파일은 모델 변경이나 외부 API 연결을 요구하지 않는다.

| 항목 | Codex | Claude Code |
| --- | --- | --- |
| 개인 설치 | `$CODEX_HOME/skills/skill-router`, 미설정 시 `~/.codex/skills/skill-router` | `~/.claude/skills/skill-router` |
| 직접 요청 표기 | `$skill-router` | `/skill-router` |
| 자동 호출 | `agents/openai.yaml`의 `policy.allow_implicit_invocation: true` | `disable-model-invocation: true`를 설정하지 않은 기본 상태 |
| 전역 안내 위치 | `$CODEX_HOME/AGENTS.md`, 미설정 시 `~/.codex/AGENTS.md` | `~/.claude/CLAUDE.md` |

설치 시 `skill-router` 폴더 전체를 각 도구의 개인 스킬 폴더에 복사한다. 대상이 있으면 기존 내용과 차이를 확인하고 백업한 뒤 갱신한다. Claude Code만 사용하는 환경에서는 Claude 경로에만 설치하면 된다.

같은 컴퓨터에서 두 도구가 같은 파일을 사용하려면 Claude Code의 스킬 폴더를 기존 원본 폴더로 연결하는 심볼릭 링크를 사용할 수 있다. 원본 폴더를 이동·삭제하면 연결이 깨지므로 배포 저장소 이름 변경과 설치 경로 변경을 구분한다. 복사본을 사용할 때는 두 설치본을 함께 갱신한다.

전역 안내는 관련 실무 요청에서 `skill-router`를 적용하고 필요한 전문 스킬을 조합하라는 짧은 지침이면 충분하다. 기존 전역 규칙을 통째로 교체하지 않는다. 자동 호출 허용이나 전역 안내가 모든 요청의 호출을 보장하지는 않는다.

설치 검증은 공통 frontmatter, 상대 참조 파일, 자동 호출 설정, 설치 경로를 확인한다. 실제 검증은 각 도구의 대화에서 직접 호출과 스킬명을 지정하지 않은 요청을 따로 실행해 적용 여부와 결과를 확인한다. 파일 형식 통과를 실제 호출 성공으로 보고하지 않는다.

근거: Codex의 로컬 `skill-creator` 지침과 `references/openai_yaml.md`, [Claude Code 스킬 공식 문서](https://code.claude.com/docs/en/skills), [Claude Code 전역 지침 공식 문서](https://code.claude.com/docs/en/memory).
