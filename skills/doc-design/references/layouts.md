# 발표 레이아웃 라이브러리

`scene.json`의 슬라이드에 `"layout"`을 적으면 `pdfdesign.py pptx`가 좌표·색·글자 크기를 계산해 네이티브 PowerPoint 개체로 펼친다. 좌표를 손으로 쓰는 `elements` 슬라이드와 섞어 쓸 수 있고, `elements`에 적은 개체는 레이아웃 위에 덧붙는다. 전체 예시는 [layout-gallery.json](../examples/layout-gallery.json), 렌더 결과는 `docs/layouts-*.png`와 `docs/themes-pptx.png`에 있다.

```bash
python3 SKILL_DIR/scripts/pdfdesign.py layouts                       # 레이아웃·테마 목록
python3 SKILL_DIR/scripts/pdfdesign.py pptx deck.json out/deck.pptx --palette olive
```

캔버스는 1280×720 px다. 색은 `@역할` 토큰으로 칠해지므로 `--palette`만 바꾸면 전체 테마가 바뀐다.

## 디자인 언어: 무대와 여백

- **장마다 주인공 하나.** 차트·흐름·화면 같은 핵심 증거는 옅은 회색 둥근 면(무대) 위에 놓고, 해석은 오른쪽 300px 여백 열에 짧은 강조선 + 값/제목 + 설명으로 둔다.
- **진한 색 면은 장마다 한 곳.** 핵심 수치 타일(`hero-number`, `summary`), 선택된 단계, 강조 카드만 강조색으로 채운다. 나머지는 옅은 강조색(`accentSoft`)과 회색 면(`paper`)의 농도 차이로 묶는다.
- **비교 기준은 회색, 우리 값은 강조색.** 막대·비율·표 강조 행이 같은 규칙을 따른다. 두 번째 강조(`hot`)는 경고·주의 한두 곳에만.
- **장식 대신 크기.** 칩, 원형 번호 배지, 진행 막대, 하단 띠, 삼각형 같은 장식은 쓰지 않는다. 숫자 크기, 굵기, 면 농도로 위계를 만든다.
- **공통 틀.** 왼쪽 위 작은 강조색 사각형 + 구역 이름, 34px 명사형 제목, 선택적 리드 한 줄, 아래 주석과 두 자리 쪽 번호. 본문 시작선과 좌우 여백(72px)은 모든 장에서 같다.

## 공통 필드 (표지·구역·마무리 제외)

| 필드 | 뜻 |
|---|---|
| `kicker` | 구역 이름(예: "검증된 성과") |
| `tag` | 구역 이름 옆 보조 표기(예: "기획서 ② AI 솔루션") |
| `title` | **명사형 제목.** 문장형이면 생성이 멈춘다 |
| `lead` | 제목 아래 한 줄. 결론 문장은 여기에 쓴다. `**굵게**` 표기 가능 |
| `note` | 왼쪽 아래 작은 주석(예시 데이터 표시, 계산 조건) |
| `appendix` | `true`면 쪽 번호 대신 kicker(예: "부록 2")를 표시하고 본문 쪽 수에서 뺀다 |
| `hidePage`, `pageLabel` | 쪽 번호 숨김, 쪽 표시 직접 지정 |

## 레이아웃별 필드

| layout | 언제 | 필드 |
|---|---|---|
| `cover` | 표지 | `style`(`split` 기본: 오른쪽 강조색 면 · `light` · `dark`), `eyebrow`, `title`, `subtitle`, `team`, `date`, `motif{values, highlight, label}`(작은 막대 모티프), `image`(split의 오른쪽 면) |
| `section` | 구역 구분 | `number`, `title`, `subtitle`, `items[]` |
| `closing` | 마무리 | `title`, `subtitle`, `contact` |
| `agenda` | 차례·부록 목록 | `rows[{title,text,page}]` (4개 이상이면 2열 타일) |
| `hero-number` | 핵심 수치 하나 | `label`, `value`, `unit`, `sub`, `bars[{label,value,display,highlight}]`, `barTitle`, `barNote` |
| `chart` | 데이터 그래프 + 해석 | `chart`(네이티브 차트 필드), `chartTitle`, `chartWidth`, `stats[{value,unit,label}]`, `takeaway`, `takeawayText` |
| `table` | 정확한 값 비교 | `rows`(첫 행 머리글), `columnWidths`, `columnAligns`, `highlightRows[]`, `strongColumns[]`, `callout`, `side{stats[]}` |
| `tiers` | 구간·등급별 값 | `headers[3]`, `headerSub`, `rows[{label,value,unit,detailLabel,detail,warn,fill}]`, `fills[]`, `notes[{title,text}]` |
| `compare` | 이전/이후, 문제/해결 | `intro`, `headers[3]`, `rows[{label,before,after}]`, `aside{label,items[{name,text}]}` |
| `proportion` | 비율 이전/이후 | `groups[{label,highlight,parts[{value,display,label}]}]`, `stats[]`, `text` |
| `summary` | 사업 가치·성과 요약 | `main{label,tag,before{label,value,unit},after{...},delta,deltaSub,bullets[]}`, `side[{label,value,unit,text,foot}]` |
| `flow` | 처리 흐름 | `rows[{label,steps[{title,text,tone}]}]`(tone: `accent`·`soft`·`hot`), `side{title,items[{title,text}]}` |
| `steps` | 단계·연혁·실행 기록 | `steps[{label?,title,text,result}]`, `highlight`, `stat{value,unit,text}`, `badge{label,text}` |
| `actions` | 한계 → 다음 조치 | `headers[2]`, `rows[{issue,action,warn}]` |
| `columns` | 2~4열 설명 | `columns[{kicker,title,text,example}]`, `highlight` |
| `screen` | 화면 캡처 설명 | `image`, `regions[{x,y,w,h,title,text}]`(이미지 대비 0~1), `caption` |
| `team` | 팀원 | `members[{name,role,photo}]` (사진이 없으면 이니셜) |
| `answer` | 질의응답 부록 | `answer`(답 문단), `body`(`rows` 근거 표와 `table` 필드) |

`screen`은 번호 상자·원형 배지를 쓰지 않는다. 설명할 영역을 화면 위에 옅은 강조색으로 덮고, 오른쪽 열에 그 영역을 잘라 낸 확대 조각과 설명을 둔다. 영역이 길쭉하면 위쪽(또는 왼쪽)부터 잘라 보이므로 보여 줄 부분만 영역으로 잡는다.

## 고르는 기준

- 증거 형태에 맞게 바꾼다: 정확한 값 → `table`·`tiers`, 핵심 수치 하나 → `hero-number`, 분포·추세 → `chart`, 비율 변화 → `proportion`, 대비 → `compare`, 과정 → `flow`·`steps`, 화면 → `screen`, 결론 → `summary`·`actions`.
- 같은 레이아웃은 같은 비교가 이어질 때만 연속으로 쓴다. 진한 강조 면이 있는 장(`hero-number`, `summary`, 강조 카드)이 세 장 이상 이어지지 않게 한다.
- 데이터를 고쳐야 하는 그래프는 `chart`(네이티브 차트)를 쓴다. `hero-number` 막대와 `proportion` 비율 막대는 도형이라 값을 바꾸면 다시 생성해야 한다.

## 테마

`--palette`로 고른다. 지정이 없으면 주제 키워드로 고른다(명시 > 저장 선호 > 주제 > neutral). 값과 역할은 [palettes.md](palettes.md)에 있다.
