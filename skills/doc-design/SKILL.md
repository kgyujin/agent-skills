---
name: doc-design
description: 발표 자료(PPTX와 PDF)와 보고서·원페이저(PDF)를 디자인한다. 발표는 PowerPoint에서 바로 고칠 수 있는 PPTX를 정본으로 만들고 같은 파일에서 PDF를 낸다. 18종 레이아웃과 14종 테마로 장마다 증거 하나가 먼저 읽히게 구성하고, 슬라이드 제목은 명사형으로 쓴다. 보고서와 원페이저는 HTML 템플릿에서 PDF로 출력한다. 참고 PDF가 있으면 전 페이지의 서체, 정렬, 여백, 밀도를 분석해 원리만 가져온다. "발표자료 만들어줘", "PPT 예쁘게", "PPTX로 편집하게", "기존 PPT 다듬어줘", "보고서 PDF", "원페이저", "디자인 시안", "스타일만 바꿔줘" 같은 요청에 쓴다. PDF의 글자 추출, 병합, 분할만 하는 요청에는 쓰지 않는다.
---

# doc-design

발표 자료와 문서를 읽기 쉽게 디자인하고 사용자가 직접 고칠 수 있는 원본을 함께 넘긴다. 디자인만 요청받으면 글의 주장, 순서, 문장, 수치를 바꾸지 않는다. 내용이 넘치면 글자를 줄이기 전에 배치를 바꾸거나 장을 나눈다.

`SKILL_DIR`는 이 파일이 있는 폴더다. 명령은 `python3 SKILL_DIR/scripts/pdfdesign.py <명령>`으로 실행한다(스크립트 이름은 예전 이름을 그대로 쓴다).

## 무엇을 만드나

| 요청 | 산출물 | 제작 경로 |
|---|---|---|
| 발표 자료 새로 만들기, 기존 PPT 다시 디자인 | PPTX(정본) + 같은 파일에서 낸 PDF | 장면 JSON → `pptx` 명령 |
| 보고서, 원페이저, 인쇄용 문서 | PDF + HTML 원본 | HTML 템플릿 → `render` 명령 |
| 수식과 그림이 많은 학회식 발표 | PDF + HTML 원본 | `talk` 템플릿 |

편집이 필요한 발표는 PPTX 경로가 기본이다. 기존 HTML을 PPTX로 자동 변환하지는 않는다.

## 원칙

1. **장마다 주인공 하나.** 차트, 흐름, 화면 같은 핵심 증거를 옅은 면 위에 크게 두고 해석은 옆 열에 짧게 쓴다. 진한 강조 면은 장마다 한 곳에만 쓴다.
2. **제목은 명사형.** "~다", "~요", "~나"로 끝나는 제목을 쓰지 않고 결론 문장은 제목 아래 `lead` 한 줄에 둔다. 디자인만 요청받아도 문장형 제목은 명사형으로 바꾸고 원래 문장은 lead로 옮긴다.
3. **표지는 표지 역할만.** 제목, 부제, 발표자, 날짜, 주제 이미지만 둔다. KPI, 결론, 목차, 설명 문단을 기본으로 넣지 않는다.
4. **편집할 수 있게.** 글자, 표, 단순 도식, 지원 차트는 네이티브 개체로 만든다. 슬라이드 전체를 이미지로 넣은 PPTX는 편집용 원본이 아니다.
5. **장식 대신 크기와 농도.** 칩, 원형 번호, 진행 막대, 하단 띠를 붙이지 않는다. 숫자 크기, 굵기, 면 농도로 위계를 만든다.
6. **없는 것을 만들지 않는다.** 사용자가 준 수치만 쓴다. 계획, 실측, 예시를 구분한다. 요청하지 않은 '출처' 라벨이나 참고자료 페이지를 넣지 않는다.
7. **렌더로 판단한다.** 자동 검사 통과는 디자인 품질의 증거가 아니다. 전체 축소판과 모든 장을 실제 크기로 본다.

## 먼저 읽을 지침

- 발표: [발표 제작 절차](references/presentation.md), [레이아웃](references/layouts.md), [발표 검수](references/presentation-review.md)
- 참고 자료가 있을 때: [전체 시각 설계](references/visual-storytelling.md)
- PowerPoint 편집과 PDF 출력: [편집용 발표](references/editable-presentations.md)
- 문서(HTML): [디자인 규칙](references/design-rules.md), [컴포넌트](references/components.md)
- 색: [테마와 팔레트](references/palettes.md), 반복 점검: [반복 검토](references/anti-ai-design.md)

## 작업 순서

1. **범위 확인.** 디자인만 바꾸는지 새로 만드는지, 발표 시간, 청중, 화면 비율, 산출물을 확인한다. 대화나 자료에 이미 있으면 다시 묻지 않는다. 없으면 16:9와 편집용 PPTX를 기본으로 하고 그 가정을 짧게 알린다. 기존 파일은 덮어쓰지 않고 새 버전으로 저장한다.
2. **근거 읽기.** 내용의 근거(평가 기준, 코드, 원본 표)를 먼저 읽는다. 참고 PDF가 있으면 전 페이지를 렌더해 보고 `페이지 | 초점 | 주/보조 영역 | 자산 | 밀도` 표로 정리한다. 도형이나 색만 베끼지 않는다.
3. **스토리보드.** 장마다 `제목 | 청중이 가져갈 핵심 | 화면에 남길 근거 | 레이아웃 | 발표 메모`를 한 줄로 쓴다. 5분 기술 발표는 7~10장에서 시작하되 고정 규칙으로 쓰지 않는다. 자세한 설명은 발표 메모로 옮기고 핵심 조건과 수치는 화면에 남긴다.
4. **테마 고르기.** 사용자 지정 > 저장한 선호 > 주제 자동 선택(`--topic`) > neutral 순이다. 기존 문서의 색을 유지하라는 요청이 있으면 그대로 둔다.
5. **어려운 장부터 제작.** 표지보다 가장 복잡한 비교, 흐름, 실행 화면 두 장을 실제 내용으로 먼저 만든다. [레이아웃 갤러리](examples/layout-gallery.json)에서 장마다 `layout`을 고르고 레이아웃에 없는 구도만 `elements` 좌표로 쓴다([시각 예제](examples/visual-analysis.json)).
6. **시안이 필요하면 구조로 비교.** 디자인 개선 요청이나 "몇 가지 시안"에는 같은 표지, 대표 본문, 마무리 세 장으로 A/B를 만든다. 색만 바꾼 안은 다른 시안으로 치지 않는다. 사용자가 고르겠다고 한 경우에만 기다린다.
7. **출력과 검수.** 오류를 고치고 경고를 확인한다. 전체 축소판에서는 반복과 밀도를 본다. 개별 장에서는 글자 크기, 정렬, 차트 내부 글자, 선 방향을 본다. [발표 검수](references/presentation-review.md)의 네 관점(발표자, 청중, 디자이너, 근거 검토자)으로 다시 읽고 고친 최신 파일을 다시 렌더한다.
8. **전달.** PPTX와 PDF, 장수, 고른 테마, 확인한 앱과 확인하지 못한 앱, 이미지로 남은 요소의 편집 한계를 짧게 알린다. 발표자용이면 메모도 넣는다.

## 명령

```bash
python3 SKILL_DIR/scripts/pdfdesign.py layouts                                   # 레이아웃과 테마 목록
python3 SKILL_DIR/scripts/pdfdesign.py pptx deck.json ./out/deck.pptx --topic "물류 운영 분석"
python3 SKILL_DIR/scripts/pdfdesign.py render-pptx ./out/deck.pptx ./out/deck.pdf --app '/Applications/Keynote.app' --preview
python3 SKILL_DIR/scripts/pdfdesign.py init report ./out/report.html --style swiss --topic "과학 데이터 분석"
python3 SKILL_DIR/scripts/pdfdesign.py render ./out/report.html --preview
python3 SKILL_DIR/scripts/pdfdesign.py check ./out/report.html --strict
python3 SKILL_DIR/scripts/pdfdesign.py options                                   # 모든 옵션
```

| 축 | 옵션 | 값 |
|---|---|---|
| 발표 테마 | `--palette` | midnight, olive, ocean, cobalt, evergreen, violet, ruby, sunset, scientific, technology, business, nature, education, neutral |
| 문서 스타일 | `--style` | swiss, editorial, bold, minimal, tech, academic, soft, classic, split, clean |
| 문서 색조 | `--palette` | indigo, navy, terracotta, forest, plum, mono, graphite, crimson, teal, sand |
| 주제로 고르기 | `--topic` | 주제를 설명하는 문장 |
| 폰트, 밀도, 모서리, 포인트색 | `--font`, `--density`, `--radius`, `--accent` | `options`로 확인 |

기본 폰트는 Pretendard다. 명조체는 요청할 때만 고운바탕을 쓴다. HTML 템플릿은 `report`(A4 보고서), `onepager`(A4 한 장), `deck`(짧은 발표), `talk`(수식과 그림이 있는 발표) 네 가지다. 생성되는 `pdf-design.css`는 직접 고치지 않고 문서 전용 스타일은 HTML의 `<style>`에 쓴다.

## 실행 환경

- PPTX 생성: Python 3 표준 라이브러리만 쓴다.
- PPTX → PDF: PowerPoint의 '내보내기 → PDF' 또는 macOS Keynote(`render-pptx`). 앱이 없으면 PDF 출력을 마쳤다고 하지 않는다.
- HTML → PDF: Chrome, Chromium, Edge 중 하나. 미리보기 PNG에는 Poppler가 필요하다. Chrome을 직접 부르지 말고 CLI를 쓴다.
- 실제 데이터 차트를 이미지 생성 모델로 그리지 않는다. 가상 예제에는 예시 데이터라고 표시한다.
