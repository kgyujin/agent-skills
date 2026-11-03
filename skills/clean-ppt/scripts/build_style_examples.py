#!/usr/bin/env python3
"""Build authored style specimens from one fictional proposal, without measured claims.
Each family changes composition, not just colors. Rendering remains a separate step.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INK = '202C3B'
MUTED = '536172'
WHITE = 'FFFFFF'
STYLES = [
    ('editorial', '에디토리얼', '2459A6', 'F0F4F9', '큰 제목과 비대칭 열', '기획 의도와 변화 설명'),
    ('warm', '웜 리포트', '79533C', 'F5F1EA', '따뜻한 바탕과 수직 순서', '교육, 팀 회고, 서비스 제안'),
    ('technical', '테크니컬', '17666C', 'EFF6F6', '왼쪽 탐색 영역과 단계 도식', '기술 구조와 처리 경로'),
    ('executive', '디시전', '304E85', 'EFF2F8', '요약 영역과 비교 매트릭스', '의사결정과 검토 회의'),
    ('studio', '스튜디오', '8D4739', 'F7F2EF', '큰 번호와 편집형 정보 블록', '제품 소개와 포트폴리오'),
]


def text(x, y, w, h, content, size=26, bold=False, color=INK):
    return dict(type='text', x=x, y=y, w=w, h=h, text=content, fontSize=size, bold=bold, color=color)


def rect(x, y, w, h, fill):
    return dict(type='rect', x=x, y=y, w=w, h=h, fill=fill, stroke=fill, strokeWidth=0)


def line(x, y, xx, yy, color='C7D0DA', arrow=False):
    return dict(type='line', points=[[x, y], [xx, yy]], stroke=color, strokeWidth=2,
                **({'endArrow': 'triangle'} if arrow else {}))


def frame(title, subtitle, elements, style, index, background=WHITE, sidebar=False):
    key, name, accent, pale, _, _ = style
    header_x = 272 if sidebar else 64
    common = [rect(0, 0, 1280, 720, background)]
    if sidebar:
        common += [rect(0, 0, 216, 720, pale), text(32, 44, 154, 30, 'SEARCH LAB', 18, True, accent)]
        for number, label in enumerate(['제안 개요', '범위 비교', '처리 흐름'], 1):
            y = 205 + (number-1)*96
            common += [text(32, y, 152, 32, f'0{number}', 22, True, accent), text(32, y+37, 160, 38, label, 23, number==index)]
        common += [text(32, 592, 160, 44, '설계 예제', 20, False, MUTED)]
    else:
        common += [text(64, 30, 800, 28, f'CLEAN PPT   /   {name}', 16, True, accent)]
    common += [text(header_x, 80, 1216-header_x, 66, title, 44, True), text(header_x, 162, 1216-header_x, 56, subtitle, 23, False, MUTED)]
    footer = [line(header_x, 662, 1216, 662), text(header_x, 681, 900, 21, '사내 문서 검색 제안  /  가상 기획 예제 · 실측 결과 아님', 13, False, MUTED), text(1140, 680, 76, 24, f'0{index} / 03', 15, False, MUTED)]
    return dict(title=title, section=name, frame=False,
                notes=f'{title}. {subtitle} 제안 단계이므로 성과 수치로 설명하지 않습니다.', elements=common+elements+footer)


def editorial(s):
    a,p=s[2:4]
    return [
      frame('사내 문서 검색 제안', '반복 질문을 관련 안내문과 연결하는 작은 시험', [
        text(64,258,646,180,'질문에서\n근거 있는 초안까지',62,True),
        text(64,477,590,88,'문서를 찾고, 출처를 확인한 뒤\n담당자가 답변을 검토합니다.',27),
        rect(776,244,440,354,p),text(808,271,370,38,'시험 계획',28,True,a),
        text(808,336,370,54,'30개 문서 · 계획',32,True),text(808,399,370,54,'3명 참여 · 계획',32,True),text(808,462,370,54,'2주 검토 · 계획',32,True),
        text(808,540,370,32,'공개 안내문부터 시작',22,False,MUTED)],s,1),
      frame('문서 탐색 방식의 변화', '확인 기준은 유지하고, 자료를 찾는 순서를 바꿉니다.', [
        text(64,256,300,90,'문서 탐색의\n변화',40,True,a),text(64,381,290,116,'제안은 정보 탐색을\n돕는 범위입니다.\n판단은 사람이 합니다.',25),
        rect(422,242,350,60,'F1F3F5'),text(446,256,305,38,'현재 방식 · 가정',26,True),rect(796,242,420,60,a),text(820,256,370,38,'제안 방식',26,True,WHITE),
        *sum(([text(446,y,300,70,l,25),text(820,y,370,70,r,25,True),line(422,y+88,1216,y+88)] for y,l,r in [(330,'문서 위치를 직접 확인','질문과 관련된 문서 조회'),(442,'답변과 문서를 따로 확인','초안에 출처 함께 표시'),(554,'담당자가 답변 판단','담당자의 최종 검토 유지')]),[])],s,2),
      frame('질문부터 최종 확인까지', '기계가 찾고 작성한 내용은 담당자가 확인합니다.', [
        *sum(([text(x,257,245,56,f'0{i+1}',40,True,a),line(x,326,x+245,326,a),text(x,357,245,42,h,30,True),text(x,420,245,95,d,25)] for i,(x,h,d) in enumerate([(64,'질문 입력','필요한 내용을\n자연어로 전달'),(366,'문서 조회','관련된 공개\n안내문 검색'),(668,'초안 작성','출처를 함께\n제시하는 답변'),(970,'사람 검토','내용과 근거를\n최종 확인')])),[]),
        line(315,282,348,282,a,True),line(617,282,650,282,a,True),line(919,282,952,282,a,True),rect(64,565,1152,62,p),text(88,580,1104,40,'초기 제외 범위  |  권한 문서와 자동 의사결정',24,True,a)],s,3)]


def warm(s):
    a,p=s[2:4]
    return [
      frame('사내 문서 검색 제안', '팀이 자주 묻는 질문에서 시작합니다.', [
        rect(64,244,684,359,WHITE),text(96,273,615,48,'반복 질문의 다음 단계',36,True),
        text(96,356,610,118,'문서 탐색과 답변 초안을\n하나의 흐름으로 연결합니다.',35,True,a),
        text(96,518,600,58,'출처 확인과 최종 판단은 담당자가 맡습니다.',25),
        text(808,259,390,40,'작은 시험의 범위',28,True,a),
        *sum(([line(808,y-14,1216,y-14,'CFC4B6'),text(808,y,390,50,h,31,True),text(808,y+56,390,38,d,22,False,MUTED)] for y,h,d in [(329,'30개 안내문','공개 사내 문서 정리'),(465,'3명 · 2주','사용 질문과 미응답 기록')]),[])],s,1,p),
      frame('도움을 줄 업무와 남길 판단', '자동화 범위를 넓히기 전에 책임을 구분합니다.', [
        text(64,251,510,43,'도움을 줄 업무',31,True,a),text(674,251,520,43,'담당자가 할 일',31,True),
        *sum(([rect(64,y,530,94,WHITE),text(88,y+26,480,48,l,27),rect(674,y,542,94,'E8DDD1'),text(698,y+26,494,48,r,27)] for y,l,r in [(320,'질문과 관련된 안내문 찾기','문서가 최신인지 확인하기'),(436,'출처와 답변 초안 함께 제시','내용과 근거가 맞는지 검토하기')]),[]),
        text(64,579,1152,42,'권한 문서와 자동 의사결정은 초기 시험에서 제외합니다.',25,True,a)],s,2,p),
      frame('시험과 후속 검토', '측정값을 미리 정하지 않고, 관찰할 질문을 정합니다.', [
        line(98,278,98,432,'B6A493'),line(64,500,1216,500,'B6A493'),
        *sum(([rect(76,y,44,44,a),text(86,y+7,30,30,str(i+1),22,True,WHITE),text(160,y,250,42,h,29,True,a),text(380,y,814,43,m,28,True),text(380,y+53,814,42,d,24,False,MUTED)] for i,(y,h,m,d) in enumerate([(251,'첫째 주','공개 안내문 30개 정리 · 계획','최신본과 공개 범위를 확인합니다.'),(388,'둘째 주','직원 3명과 질문 시험 · 계획','답변과 출처를 함께 살펴봅니다.'),(525,'시험 이후','답하지 못한 질문 보완','정확성, 응답시간과 비용은 별도 확인합니다.') ])),[])],s,3,p)]


def technical(s):
    a,p=s[2:4]
    return [
      frame('사내 문서 검색 제안','공개 안내문을 근거로 답변 초안을 구성합니다.',[
        text(272,248,890,115,'검색과 생성 사이에\n확인 가능한 근거',46,True),
        *sum(([rect(x,410,280,152,p),text(x+24,434,232,48,h,29,True,a),text(x+24,491,232,45,d,23)] for x,h,d in [(272,'공개 문서','권한 문서는 제외'),(604,'출처 표시','초안과 근거 연결'),(936,'사람 검토','최종 내용 확인')]),[]),
        text(272,602,944,34,'계획: 문서 30개 · 직원 3명 · 2주 시험',23,False,MUTED)],s,1,sidebar=True),
      frame('검토 대상과 제외 범위','사용자에게 보여 줄 근거와 책임을 구분합니다.',[
        rect(272,244,944,58,a),text(296,259,270,36,'구분',24,True,WHITE),text(622,259,570,36,'초기 설계',24,True,WHITE),
        *sum(([text(296,y,270,41,h,26,True),text(622,y,570,60,d,26),line(272,y+64,1216,y+64)] for y,h,d in [(322,'검색 대상','공개 사내 안내문'),(400,'제외 범위','권한이 필요한 문서'),(478,'답변 형태','참고한 문서가 연결된 초안'),(556,'사람의 역할','출처와 내용 확인 후 사용')]),[])],s,2,sidebar=True),
      frame('처리 흐름과 확인 지점','도구의 결과를 바로 확정 답변으로 취급하지 않습니다.',[
        *sum(([rect(x,264,208,152,p if i<3 else a),text(x+20,283,168,42,f'0{i+1}',29,True,a if i<3 else WHITE),text(x+20,343,168,42,h,26,True,INK if i<3 else WHITE),text(x,449,208,98,d,24)] for i,(x,h,d) in enumerate([(272,'질문 입력','질문과 필요한\n맥락 전달'),(517,'문서 검색','관련 안내문과\n출처 조회'),(762,'초안 작성','문서에 근거한\n답변 작성'),(1007,'담당자 확인','내용과 출처를\n검토한 뒤 사용')])),[]),
        line(488,340,505,340,a,True),line(733,340,750,340,a,True),line(978,340,995,340,a,True),
        rect(272,567,944,60,p),text(292,581,904,40,'확인 지점  |  검색 결과와 초안을 최종 답변으로 바로 확정하지 않습니다.',23,True,a)],s,3,sidebar=True)]


def executive(s):
    a,p=s[2:4]
    return [
      frame('사내 문서 검색 제안','도입 판단을 위한 제한된 시험',[
        rect(64,238,1152,149,a),text(96,265,1088,61,'공개 문서부터 작게 검토',44,True,WHITE),text(96,335,1080,36,'문서 검색과 출처가 있는 답변 초안을 연결합니다.',26,False,WHITE),
        *sum(([text(x,428,330,38,h,23,True,a),text(x,480,330,57,b,42,True),text(x,558,330,47,d,24,False,MUTED)] for x,h,b,d in [(64,'준비 자료 · 계획','문서 30개','최신본과 공개 범위 확인'),(476,'참여 범위 · 계획','직원 3명','실제 질문으로 시험'),(888,'시험 기간 · 계획','2주','미응답과 사용 부담 기록')]),[])],s,1),
      frame('도입 판단 기준','모든 항목은 미측정입니다. 시험에서 확인할 질문을 정의합니다.',[
        rect(64,240,1152,56,a),text(88,253,265,37,'검토 항목',24,True,WHITE),text(470,253,720,37,'확인할 질문',24,True,WHITE),
        *sum(([rect(64,y-15,1152,83,p if i%2==0 else WHITE),text(88,y,265,42,h,26,True),text(470,y,720,48,d,25)] for i,(y,h,d) in enumerate([(326,'정확성','질문에 맞는 문서를 찾는가'),(409,'출처','초안의 근거를 확인할 수 있는가'),(492,'응답시간','업무 중 기다릴 수 있는 수준인가'),(575,'비용','지속 운영에 필요한 비용은 얼마인가')])),[])],s,2),
      frame('시험 후 결정 순서','확인되지 않은 성능을 전제로 적용 범위를 넓히지 않습니다.',[
        *sum(([rect(x,247,350,64,p),text(x+22,262,306,39,h,27,True,a),text(x,353,350,84,d,28,True),text(x,472,350,100,b,25,False,MUTED)] for x,h,d,b in [(64,'01  기록 확인','질문과 답변을\n함께 살펴보기','답하지 못한 질문과\n출처 확인 문제 정리'),(465,'02  조건 검토','정확성·시간·비용\n확인하기','운영 부담과\n개선 필요 사항 확인'),(866,'03  범위 결정','시험 결과로\n확대 여부 판단','권한 문서 포함 여부는\n별도 검토')]),[]),line(424,279,451,279,a,True),line(825,279,852,279,a,True),text(64,596,1152,39,'결정의 근거  |  예상 수치보다 실제 시험 기록을 먼저 확인',24,True,a)],s,3)]


def studio(s):
    a,p=s[2:4]
    return [
      frame('사내 문서 검색 제안','반복되는 질문을 문서와 연결하는 방법',[
        text(64,255,1152,90,'찾기 쉽게, 확인할 수 있게',64,True),
        line(64,384,1216,384,a),
        text(64,429,480,118,'검색 결과와 답변 초안을\n같은 흐름에서 확인합니다.',29),
        *sum(([text(x,427,160,49,n,34,True,a),text(x,499,160,45,h,26,True)] for x,n,h in [(640,'01','공개 안내문'),(858,'02','연결된 출처'),(1076,'03','사람 검토')]),[]),
        text(64,595,1152,36,'제안의 중심  /  문서 탐색을 돕고, 최종 판단은 담당자에게',23,False,MUTED)],s,1),
      frame('같은 질문, 다른 탐색 방식','판단 책임은 유지하고 탐색 방법을 바꿉니다.',[
        text(64,241,245,72,'현재 · 가정',35,True,MUTED),text(64,383,245,72,'제안 방식',35,True,a),
        text(378,243,812,50,'문서 위치를 찾고 내용을 따로 확인',33,True),text(378,310,812,46,'답변에 필요한 안내문을 직접 찾습니다.',25,False,MUTED),line(64,362,1216,362),
        text(378,385,812,50,'관련 문서와 답변 초안을 함께 확인',33,True,a),text(378,452,812,46,'출처를 따라가며 답변의 근거를 살펴봅니다.',25,False,MUTED),
        rect(64,554,1152,70,p),text(88,574,1104,42,'유지할 기준  |  담당자가 출처와 내용을 최종 확인',25,True,a)],s,2),
      frame('시험 계획 한눈에 보기','제안한 범위를 구체적인 행동으로 옮깁니다.',[
        text(64,246,184,103,'01',75,True,a),text(266,257,310,45,'안내문 정리',32,True),text(640,257,560,85,'계획: 공개 문서 30개의\n최신본과 범위를 확인합니다.',27),line(64,369,1216,369),
        text(64,399,184,103,'02',75,True,a),text(266,410,310,45,'작은 시험',32,True),text(640,410,560,85,'계획: 직원 3명과 2주간\n질문과 미응답을 기록합니다.',27),line(64,523,1216,523),
        text(64,560,1152,55,'다음 판단  →  정확성, 응답시간, 비용 확인 후 적용 범위 검토',26,True,a)],s,3)]


def build():
    catalog=[]
    for style,factory in zip(STYLES,[editorial,warm,technical,executive,studio]):
        key,name,accent,pale,structure,purpose=style
        folder=ROOT/'examples/styles'/key;folder.mkdir(parents=True,exist_ok=True)
        slides=factory(style)
        if key in ('editorial','studio'):
            for element in slides[0]['elements']:
                if element.get('type')=='text' and element.get('y')==80:
                    element['fontSize']=28; element['color']=accent
        if key=='warm':
            slides[0]['elements'].insert(1,rect(0,0,18,720,accent))
        scene=dict(width=1280,height=720,font='Pretendard',theme=dict(background=WHITE,text=INK,muted=MUTED,accent=accent,line='C7D0DA'),meta=dict(title=f'{name} 스타일 예제',author='Clean PPT',subject='가상 기획 제안'),slides=slides)
        (folder/'scene.json').write_text(json.dumps(scene,ensure_ascii=False,indent=2)+'\n')
        (folder/'notes.md').write_text('# 발표 메모\n\n'+'\n\n'.join(f'## {i}. {s["title"]}\n\n{s["notes"]}' for i,s in enumerate(scene['slides'],1))+'\n')
        catalog.append(dict(id=key,name=name,structure=structure,purpose=purpose,scene=f'examples/styles/{key}/scene.json',preview=f'examples/styles/{key}/preview.png'))
    (ROOT/'assets/style-catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':build()
