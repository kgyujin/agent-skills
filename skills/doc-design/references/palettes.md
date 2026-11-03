# 발표용 컬러 테마

색은 **바탕 · 회색 면(paper) · 옅은 강조 면(accentSoft) · 강조색(accent)** 네 단계의 농도로 쓴다. 장마다 진한 강조 면은 한 곳, 옅은 면은 주인공 증거의 무대로 쓴다. 강조색은 채도를 한 단계 낮춘 색으로 골라 넓은 면에 칠해도 촌스럽지 않게 했다. 두 번째 강조(hot)는 경고·주의 한두 곳에만 쓴다. 어두운 면(dark)은 `cover style=dark` 같은 선택 사항이다.

| 테마 | 주제 키워드 예 | 바탕 | 강조 | 옅은 강조 | 두 번째 강조 | 어두운 면 |
|---|---|---|---|---|---|---|
| midnight | AIOps, MLOps, 서빙, 예측 | #FFFFFF | #2F5BC9 | #EFF3FB | #D3612F | #141A26 |
| olive | 제주, 농업, 식품, 로컬 | #FAF9F4 | #52702A | #EDEFE5 | #B9652B | #1F231A |
| ocean | 해양, 수산, 헬스케어, 웰니스 | #FFFFFF | #0E716D | #EDF4F4 | #D35D47 | #10302F |
| cobalt | 핀테크, 결제, 플랫폼, 스타트업 | #FFFFFF | #3A4FD4 | #F0F2FC | #C9901F | #12163A |
| evergreen | ESG, 탄소중립, 탄소, 산림 | #FFFFFF | #1D6B48 | #EEF4F1 | #B5852A | #12291E |
| violet | 디자인, 브랜드, 마케팅, 콘텐츠 | #FFFFFF | #5944B0 | #F3F1F9 | #C47F2C | #211A36 |
| ruby | 리스크, 장애, 보안, 위기 | #FFFFFF | #AE2A40 | #F9EFF1 | #375787 | #241A1D |
| sunset | 문화, 커머스, 리테일, 라이프스타일 | #FBF8F3 | #B0512C | #F5EBE4 | #2E6E72 | #2A211C |
| scientific | 독성, 분자, 화학, 의료 | #FFFFFF | #B63E4C | #F8E9EC | #D9822B | #3B2C33 |
| technology | 소프트웨어, 개발, 클라우드, 서버 | #FFFFFF | #315CBD | #EAF0FC | #E8692E | #23314D |
| business | 경영, 운영, 금융, 매출 | #FFFFFF | #225CA8 | #E9F0FA | #A75420 | #243447 |
| nature | 환경, 생태, 탄소, 에너지 | #FFFFFF | #2D6E52 | #E7F1E9 | #D99A1E | #253E33 |
| education | 교육, 학습, 문화, 인문 | #FFFFFF | #744885 | #F0E8F3 | #E0873A | #3C2F44 |
| neutral | 주제 미지정 | #FFFFFF | #3F6174 | #EAF0F3 | #94553E | #2A3539 |

색 값·키워드의 정본은 `assets/presentation-palettes.json`이다. 값이 없는 역할(어두운 면 등)은 `presentation_palette.complete_roles()`가 기본 역할에서 만든다. 대비 테스트는 본문/보조 글자, 강조색 위 흰 글자, 어두운 면 위 글자, 옅은 칸 위 진한 글자 조합을 검사한다.

## 자동 선택

**사용자 명시 > 저장된 팔레트 > 주제 키워드 > neutral.** 기존 문서의 RGB 색은 자동 교체하지 않는다. scene에 적힌 `palette`는 제작자의 기존 선택으로 존중한다. 키워드 동점이면 목록 순서(새 테마 우선)로 정한다. 로그에 선택 결과가 찍히므로 주제와 맞는지 확인한다. 같은 내용을 다른 테마로 보여 줄 때는 `--palette`만 바꾼다.

```bash
python3 SKILL_DIR/scripts/pdfdesign.py pptx ./deck.json ./out/deck.pptx --topic "태양광 발전량 예측"   # midnight
python3 SKILL_DIR/scripts/pdfdesign.py pptx ./deck.json ./out/deck-olive.pptx --palette olive
python3 SKILL_DIR/scripts/pdfdesign.py init report ./out/report.html --style clean --palette midnight
```

HTML 문서도 같은 이름의 색조를 쓸 수 있다(`palettes.css`). `clean` 스타일과 함께 쓰면 발표와 같은 색 체계가 된다.

## 색 역할

PPTX JSON의 색 필드에는 역할을 쓴다. 레이아웃은 모두 역할로 칠한다.

| 역할 | 쓰임 |
|---|---|
| `@ink`, `@muted`, `@faint` | 제목·본문, 보조 글자, 글자가 아닌 약한 표시(화살표 등) |
| `@bg`, `@white`, `@paper`, `@line` | 슬라이드 바탕, 흰 칸, 옅은 칸, 구분선 |
| `@accent`, `@accentInk`, `@accentSoft`, `@onAccent` | 주 강조(우리 서비스·선택값), 흰 바탕 위 강조 글자, 옅은 강조 칸, 강조색 위 글자 |
| `@secondary`, `@neutral` | 비교 그룹, 기준선·이전 값 막대 |
| `@hot`, `@hotInk`, `@hotSoft`, `@onHot` | 두 번째 강조(결론·경고·번호 배지), 흰 바탕 위 글자, 옅은 칸, hot 위 글자 |
| `@dark`, `@onDark`, `@darkMuted`, `@darkLine`, `@darkAccent`, `@darkHot` | 어두운 면(표지·핵심 카드)과 그 위의 글자·선·강조 |
| `@accent/20` | 강조색 20%와 흰색 80%를 섞은 색. 단계형 차트에 쓴다 |

- 데이터 그룹 색(`accent` = 우리 것, `neutral` = 기준)은 문서 전체에서 같은 뜻을 유지한다.
- 진한 강조 면(`accent` 채움)은 한 화면에 한 곳. 옅은 면(`paper`, `accentSoft`)으로 묶음을 만든다.
- `hot`은 한 화면에서 한두 곳에만 쓴다. 표·차트의 그룹 색으로 쓰지 않는다.
- 색만으로 구분하지 말고 범례 이름이나 값 라벨을 함께 쓴다.
- 표지는 제목·부제·발표 정보와 필요할 때 주제 이미지로 구성한다. 팔레트 시안표·핵심 지표·결론·목차를 표지에 넣지 않는다.
