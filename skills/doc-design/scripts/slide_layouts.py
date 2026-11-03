"""발표 레이아웃 라이브러리: layout 이름과 내용만 적은 슬라이드를 네이티브 개체 목록으로 펼친다.

작성자: Git 이력 참조
작성목적: 좌표를 손으로 쓰지 않고도 정돈되고 밀도 있는 발표 장면을 만든다.
작성일: 2026-10-10
주요 입력: scene JSON. slide에 "layout"이 있으면 펼치고, 없으면 기존 elements를 그대로 쓴다.
주요 출력: elements만 가진 scene. 색은 @역할 토큰으로 남겨 presentation_palette가 테마별로 칠한다.
디자인 언어(무대와 여백):
  - 장마다 증거 하나가 주인공이다. 주인공은 옅은 면(무대) 위에 놓고, 해석은 오른쪽 여백 열에 둔다.
  - 진한 색 면은 장마다 한 곳(핵심 수치 타일·선택된 단계)에만 쓴다. 비교 기준은 회색, 우리 값은 강조색.
  - 칩·원형 번호 배지·띠 같은 장식 대신 면의 농도와 크기로 위계를 만든다.
주의사항:
  - 캔버스는 1280×720 px 기준이다.
  - 글자 폭은 근사치로 계산한다. 긴 문장은 줄바꿈(\\n)을 직접 넣고 렌더 이미지로 확인한다.
  - slide.elements에 적은 개체는 레이아웃 위에 덧붙는다.
변경사항 내역:
- 2026-10-10 | 최초 작성 | 참고 발표 구도를 일반화한 레이아웃
- 2026-10-10 | 재설계 | 무대·여백 열 구성, 장식 제거, 18종으로 정리, 화면 설명은 확대 조각 방식
"""
from __future__ import annotations

import copy
import math
import re
import struct
from pathlib import Path

W, H = 1280, 720
L, R = 72, 1208
CW = R - L
GAP = 32           # 무대와 여백 열 사이
MARGIN_W = 300     # 오른쪽 여백 열 폭
TOP = 196
BOTTOM = 636
TITLE = 34
BODY = 17


# ---------------------------------------------------------------- 기본 개체
def text_width(text: str, size: float, bold: bool = False) -> float:
    """Pretendard 기준 근사 폭(px)."""
    width = 0.0
    for char in str(text):
        if char == ' ':
            width += .27
        elif ord(char) > 0x2E80:
            width += .94
        elif char in 'MW%@mw':
            width += .82
        elif char in 'il.,:;|\'!':
            width += .3
        else:
            width += .58
    return width * size * (1.04 if bold else 1)


def line_count(text, size: float, width: float, bold: bool = False) -> int:
    return sum(max(1, math.ceil(text_width(part, size, bold) / max(width, 1) - .02)) for part in str(text).split('\n'))


def T(x, y, w, h, text, size=BODY, color='@ink', bold=False, align='left', anchor='top', **extra):
    element = {'type': 'text', 'x': round(x, 1), 'y': round(y, 1), 'w': round(max(w, 1), 1), 'h': round(max(h, 1), 1),
               'fontSize': size, 'color': color, 'bold': bold, 'align': align, 'anchor': anchor}
    if isinstance(text, list):
        element['paragraphs'] = text
    else:
        element['text'] = str(text)
    if size >= 30 and 'letterSpacing' not in extra:
        element['letterSpacing'] = round(-size * .018, 2)
    element.update(extra)
    return element


def B(x, y, w, h, fill, line=None, radius=0, **extra):
    element = {'type': 'rect', 'x': round(x, 1), 'y': round(y, 1), 'w': round(max(w, 1), 1), 'h': round(max(h, 1), 1), 'fill': fill}
    if line:
        element['lineColor'] = line
    if radius:
        element['radius'] = radius
    element.update(extra)
    return element


def LN(x, y, w, h=0, color='@line', width=1, **extra):
    element = {'type': 'line', 'x': round(x, 1), 'y': round(y, 1), 'w': round(w, 1), 'h': round(h, 1), 'color': color, 'width': width}
    element.update(extra)
    return element


def stage(x, y, w, h, fill='@paper', name='무대'):
    return B(x, y, w, h, fill, radius=14, name=name)


def runs(text, base='@ink', strong=None, size=None, bold=False):
    """'일반 **강조** 일반' 표기를 run 목록으로 바꾼다. 줄바꿈은 문단을 나눈다."""
    paragraphs = []
    for line in str(text).split('\n'):
        paragraph = []
        for part in re.split(r'(\*\*.+?\*\*)', line):
            if not part:
                continue
            strong_part = part.startswith('**') and part.endswith('**')
            run = {'text': part[2:-2] if strong_part else part, 'bold': True if strong_part else bold,
                   'color': (strong or base) if strong_part else base}
            if size:
                run['fontSize'] = size
            paragraph.append(run)
        paragraphs.append(paragraph or [{'text': ' ', 'color': base}])
    return paragraphs


def plain(text) -> str:
    return re.sub(r'\*\*(.+?)\*\*', r'\1', str(text))


def value_unit(x, y, value, unit, size, color='@ink', unit_color=None, h=None, width=None, align='left'):
    """큰 숫자와 작은 단위를 한 텍스트 상자의 두 run으로 놓는다."""
    unit_size = max(14, round(size * .3))
    paragraph = [{'text': str(value), 'fontSize': size, 'bold': True, 'color': color, 'letterSpacing': round(-size * .03, 2)}]
    if unit:
        paragraph.append({'text': ' ' + str(unit), 'fontSize': unit_size, 'bold': True, 'color': unit_color or color})
    w = width or text_width(str(value), size, True) + text_width(' ' + str(unit or ''), unit_size, True) + 24
    return T(x, y, min(w, W - x), h or size * 1.2, [paragraph], size, color, align=align, anchor='bottom')


def image_size(path: Path) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if data.startswith(b'\x89PNG'):
        return struct.unpack('>II', data[16:24])
    if data.startswith(b'\xff\xd8'):
        index = 2
        while index < len(data) - 9:
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack('>HH', data[index + 5:index + 9])
                return width, height
            index += 2 + struct.unpack('>H', data[index + 2:index + 4])[0]
    return None


# ---------------------------------------------------------------- 공통 틀
class Ctx:
    def __init__(self, scene, slide, index, total, base_dir):
        self.scene, self.slide, self.index, self.total = scene, slide, index, total
        self.base = Path(base_dir or '.')
        self.top = TOP
        self.bottom = BOTTOM


def frame(s: dict, ctx: Ctx) -> list:
    """구역 표시(작은 강조색 사각형 + 이름), 명사형 제목, 선택적 리드 한 줄, 하단 주석과 쪽 번호."""
    out = []
    if s.get('kicker') or s.get('tag'):
        out.append(B(L, 47, 8, 8, '@accent', radius=2))
        label = []
        if s.get('kicker'):
            label.append({'text': s['kicker'], 'bold': True, 'color': '@accentInk'})
        if s.get('tag'):
            label.append({'text': ('    ' if label else '') + s['tag'], 'color': '@muted'})
        out.append(T(L + 18, 41, CW - 18, 20, [label], 13, '@muted', anchor='middle', name='구역'))
    title = s.get('title', '')
    lines = line_count(title, TITLE, CW, True)
    out.append(T(L, 72, CW, lines * 44, title, TITLE, '@ink', True, lineSpacing=1.05, name='제목'))
    y = 72 + lines * 44
    if s.get('lead'):
        lead_lines = line_count(plain(s['lead']), 18, CW)
        out.append(T(L, y + 8, CW, lead_lines * 27, runs(s['lead'], '@muted', '@ink'), 18, '@muted', name='리드'))
        y += 8 + lead_lines * 27
    ctx.top = max(TOP, y + 36)
    ctx.bottom = BOTTOM
    if s.get('note'):
        out.append(T(L, 660, CW - 140, 20, s['note'], 12, '@muted', anchor='middle', name='주석'))
    if ctx.scene.get('pageNumbers', True) and not s.get('hidePage'):
        label_text = s.get('pageLabel') or f'{ctx.index:02d}'
        out.append(T(R - 120, 660, 120, 20, label_text, 12, '@muted', True, align='right', anchor='middle', name='쪽 번호'))
    return out


def margin(items, x, y, w, bottom):
    """오른쪽 여백 열: 강조색 짧은 선 + 값 또는 제목 + 설명. items: [{value,unit,label}] 또는 [{title,text}]."""
    out = []
    for item in items:
        if y > bottom - 40:
            break
        out.append(LN(x, y, 24, 0, '@accent', 2))
        y += 14
        if 'value' in item:
            out.append(value_unit(x, y, item['value'], item.get('unit', ''), 32, item.get('color', '@ink'), width=w, h=40))
            y += 44
            text = item.get('label', '')
        else:
            lines = line_count(item.get('title', ''), 17, w, True)
            out.append(T(x, y, w, lines * 24, item.get('title', ''), 17, '@ink', True, lineSpacing=1.2))
            y += lines * 24 + 4
            text = item.get('text', '')
        if text:
            lines = line_count(text, 14, w)
            out.append(T(x, y, w, lines * 21, text, 14, '@muted', lineSpacing=1.25))
            y += lines * 21
        y += 26
    return out, y


def label_above(x, y, w, text, color='@muted'):
    """y에서 끝나는 작은 머리글."""
    return T(x, y - 20, w, 20, text, 13, color, True, anchor='bottom')


# ---------------------------------------------------------------- 표지·구역·마무리
def cover(s, ctx):
    style = s.get('style', 'split')
    title = s.get('title', '')
    if style == 'dark':
        ctx.slide['background'] = '@dark'
        ink, sub, accent, rule = '@onDark', '@darkMuted', '@darkAccent', '@darkLine'
    else:
        ctx.slide['background'] = '@bg'
        ink, sub, accent, rule = '@ink', '@muted', '@accentInk', '@line'
    split = style == 'split'
    width = 640 if split else 1000
    out = []
    if split:
        out.append(B(800, 0, W - 800, H, '@accent', name='표지 색면'))
    if s.get('eyebrow'):
        out.append(T(L, 72, width, 22, s['eyebrow'], 14, accent, True))
    lines = line_count(title, 48, width, True)
    y = 320 - lines * 30
    out.append(T(L, y, width, lines * 60, title, 48, ink, True, lineSpacing=1.08, name='제목'))
    y += lines * 60 + 20
    if s.get('subtitle'):
        out.append(T(L, y, width, 64, s['subtitle'], 20, sub, lineSpacing=1.3))
    out.append(LN(L, 590, width if split else CW, 0, rule))
    if s.get('team'):
        out.append(T(L, 606, width - 160, 24, s['team'], 16, ink, True))
    if s.get('date'):
        out.append(T(L + (width if split else CW) - 220, 606, 220, 24, s['date'], 16, sub, align='right'))
    motif = s.get('motif')
    if split and s.get('image'):
        out.append({'type': 'image', 'x': 840, 'y': 140, 'w': 330, 'h': 440, 'path': s['image'], 'name': '표지 이미지'})
    elif motif and motif.get('values'):
        values, top = motif['values'], max(motif['values'])
        if split:
            area_x, area_w, base, max_h = 848, W - 848 - 48, 560, 300
        else:
            area_x, area_w, base, max_h = 760, R - 760, 520, 120
        step = area_w / len(values)
        for index, value in enumerate(values):
            height = max(3, value / top * max_h)
            hot = index == motif.get('highlight', -1)
            if split:
                out.append(B(area_x + index * step + step * .18, base - height, step * .64, height, '@white' if hot else '@white', opacity=1 if hot else .32))
            else:
                out.append(B(area_x + index * step + step * .18, base - height, step * .64, height, accent if hot else rule))
        if motif.get('label'):
            out.append(T(area_x, base + 12, area_w, 18, motif['label'], 12, '@onAccent' if split else sub, align='right'))
    return out


def section(s, ctx):
    ctx.slide['background'] = '@accentSoft'
    out = []
    if s.get('number') is not None:
        out.append(T(L - 4, 150, 400, 150, str(s['number']), 140, '@accent', True, letterSpacing=-6, name='구역 번호'))
    title = s.get('title', '')
    out.append(T(L, 330, 600, 120, title, 46, '@ink', True, lineSpacing=1.08, name='제목'))
    if s.get('subtitle'):
        out.append(T(L, 330 + line_count(title, 46, 600, True) * 56 + 14, 560, 70, s['subtitle'], 19, '@muted', lineSpacing=1.35))
    items = s.get('items', [])
    if items:
        card_h = 40 + len(items) * 64
        y0 = (H - card_h) / 2
        out.append(B(740, y0, R - 740, card_h, '@white', radius=14))
        for index, item in enumerate(items):
            y = y0 + 20 + index * 64
            if index:
                out.append(LN(772, y, R - 740 - 64, 0))
            out.append(T(772, y, 40, 64, str(index + 1), 18, '@accentInk', True, anchor='middle'))
            out.append(T(812, y, R - 812 - 32, 64, item, 19, '@ink', anchor='middle'))
    return out


def closing(s, ctx):
    ctx.slide['background'] = '@accent'
    out = [T(L, 270, CW, 80, s.get('title', ''), 56, '@onAccent', True, name='제목')]
    if s.get('subtitle'):
        out.append(T(L, 360, 900, 40, s['subtitle'], 20, '@onAccent'))
    if s.get('contact'):
        out.append(T(L, 606, CW, 24, s['contact'], 15, '@onAccent'))
    return out


# ---------------------------------------------------------------- 목록·표
def agenda(s, ctx):
    """차례: 2열 타일. 번호가 크게, 쪽은 오른쪽 위."""
    out = frame(s, ctx)
    rows = s.get('rows', [])
    cols = 2 if len(rows) > 3 else 1
    per_col = math.ceil(len(rows) / cols)
    gap = 20
    tw = (CW - gap * (cols - 1)) / cols
    th = min(104, (ctx.bottom - ctx.top - gap * (per_col - 1)) / per_col)
    for index, row in enumerate(rows):
        col, rank = divmod(index, per_col)
        x, y = L + col * (tw + gap), ctx.top + rank * (th + gap)
        out.append(B(x, y, tw, th, '@paper', radius=12))
        out.append(T(x + 24, y, 60, th, str(index + 1), 30, '@accent', True, anchor='middle'))
        paragraphs = [[{'text': row.get('title', ''), 'bold': True, 'fontSize': 20, 'color': '@ink'}]]
        if row.get('text'):
            paragraphs.append([{'text': row['text'], 'fontSize': 14, 'color': '@muted'}])
        out.append(T(x + 84, y, tw - 84 - 110, th, paragraphs, 14, '@ink', anchor='middle', lineSpacing=1.3))
        if row.get('page'):
            out.append(T(x + tw - 130, y, 106, th, str(row['page']), 15, '@accentInk', True, align='right', anchor='middle'))
    return out


def table_layout(s, ctx, rows=None, top=None):
    out = [] if rows is not None else frame(s, ctx)
    rows = rows or s['rows']
    top = ctx.top if top is None else top
    side = s.get('side')
    width = CW - (MARGIN_W + GAP if side else 0)
    available = ctx.bottom - top - (44 if s.get('callout') else 0)
    height = min(available, 44 + 54 * (len(rows) - 1))
    styles = [{'row': 0, 'bold': True, 'fontSize': 13, 'color': '@muted'}]
    for col in s.get('strongColumns', []):
        styles.append({'col': col, 'bold': True})
    for row in s.get('highlightRows', []):
        styles.append({'row': row, 'fill': '@accentSoft', 'bold': True, 'color': '@accentInk'})
    for col in s.get('strongColumns', []):
        styles.append({'row': 0, 'col': col, 'color': '@muted', 'fontSize': 13})
    out.append({'type': 'table', 'x': L, 'y': top, 'w': width, 'h': height, 'rows': rows,
                'columnWidths': s.get('columnWidths', [1] * len(rows[0])), 'rowHeights': [.8] + [1] * (len(rows) - 1),
                'columnAligns': s.get('columnAligns', ['left'] * len(rows[0])), 'fontSize': s.get('fontSize', 16),
                'headerFill': '@paper', 'headerColor': '@muted', 'fill': '@bg', 'color': '@ink',
                'borderColor': '@line', 'cellPadding': 12, 'cellStyles': styles, 'name': '표'})
    if s.get('callout'):
        out.append(T(L, top + height + 14, width, 26, runs(s['callout'], '@muted', '@accentInk'), 15, '@muted', anchor='middle'))
    if side:
        parts, _ = margin(side.get('stats', []), R - MARGIN_W, top + 4, MARGIN_W, ctx.bottom)
        out += parts
    return out


def _number(value) -> float:
    try:
        return float(str(value).replace(',', ''))
    except ValueError:
        return 0.0


def tiers(s, ctx):
    """구간별 값. 값 타일의 농도로 순위를 보이고, 오른쪽에 환산 값을 둔다."""
    out = frame(s, ctx)
    rows = s['rows']
    labels = s.get('headers', ['', '', ''])
    x1, tile_w = L + 400, 230
    x2 = x1 + tile_w + 60
    notes = s.get('notes', [])
    y = ctx.top + 24
    out.append(label_above(L, y - 6, 380, labels[0] + ('   ' + s['headerSub'] if s.get('headerSub') else '')))
    out.append(label_above(x1, y - 6, tile_w, labels[1]))
    out.append(label_above(x2, y - 6, R - x2, labels[2]))
    gap = 10
    row_h = min(92, (ctx.bottom - y - (124 if notes else 0)) / len(rows))
    fills = s.get('fills') or ['@accentInk', '@accent', '@accentSoft', '@paper']
    ranked = sorted(range(len(rows)), key=lambda i: -_number(rows[i].get('value', 0)))
    for index, row in enumerate(rows):
        ry = y + index * row_h
        fill = row.get('fill') or fills[min(ranked.index(index), len(fills) - 1)]
        if _number(row.get('value', 0)) == 0:
            fill = '@paper'
        strong = fill in ('@accentInk', '@accent', '@dark', '@hot')
        out.append(T(L, ry, 380, row_h - gap, row.get('label', ''), 21, '@hotInk' if row.get('warn') else '@ink', True, anchor='middle'))
        out.append(B(x1, ry, tile_w, row_h - gap, fill, radius=10))
        out.append(value_unit(x1 + 22, ry, row.get('value', ''), row.get('unit', ''), 40, '@onAccent' if strong else ('@accentInk' if fill == '@accentSoft' else '@muted'), h=row_h - gap - 10))
        detail = [[{'text': row.get('detailLabel', '') + ('   ' if row.get('detailLabel') else ''), 'fontSize': 14, 'color': '@muted'},
                   {'text': str(row.get('detail', '')), 'fontSize': 26, 'bold': True, 'color': '@ink', 'letterSpacing': -.5}]]
        out.append(T(x2, ry, R - x2, row_h - gap, detail, 14, '@muted', anchor='middle'))
        if index < len(rows) - 1:
            out.append(LN(x2, ry + row_h - gap / 2, R - x2))
    if notes:
        ny = y + len(rows) * row_h + 14
        width = (CW - 20 * (len(notes) - 1)) / len(notes)
        for index, note in enumerate(notes):
            nx = L + index * (width + 20)
            out.append(B(nx, ny, width, ctx.bottom - ny, '@paper', radius=12))
            out.append(T(nx + 22, ny + 16, width - 44, 20, note.get('title', ''), 13, '@accentInk', True))
            out.append(T(nx + 22, ny + 42, width - 44, ctx.bottom - ny - 50, runs(note.get('text', ''), '@ink', '@ink'), 15, '@ink', lineSpacing=1.3))
    return out


def compare(s, ctx):
    """대비: 왼쪽 회색 카드(이전·문제)와 오른쪽 강조 카드(이후·해결)를 행 단위로 맞춘다."""
    out = frame(s, ctx)
    y = ctx.top
    if s.get('intro'):
        lines = line_count(plain(s['intro']), 17, CW)
        out.append(T(L, y - 10, CW, lines * 26, runs(s['intro'], '@muted', '@ink'), 17, '@muted', lineSpacing=1.3))
        y += lines * 26 + 10
    labels = s.get('headers', ['', '', ''])
    rows = s['rows']
    aside = s.get('aside')
    label_w = 170
    xb = L + label_w
    card_w = (R - xb - 48) / 2
    xa = xb + card_w + 48
    head = 40
    row_h = min(78, (ctx.bottom - y - head - (64 if aside else 0)) / len(rows))
    height = head + row_h * len(rows) + 8
    out.append(B(xb, y, card_w, height, '@paper', radius=14))
    out.append(B(xa, y, card_w, height, '@accentSoft', radius=14))
    out.append(T(L, y + 12, label_w, 22, labels[0], 13, '@muted', True))
    out.append(T(xb + 22, y + 12, card_w - 44, 22, labels[1], 13, '@muted', True))
    out.append(T(xa + 22, y + 12, card_w - 44, 22, labels[2] if len(labels) > 2 else '', 13, '@accentInk', True))
    for index, row in enumerate(rows):
        ry = y + head + index * row_h
        if index:
            out.append(LN(L, ry, label_w - 16))
            out.append(LN(xb + 22, ry, card_w - 44))
            out.append(LN(xa + 22, ry, card_w - 44, 0, '@white'))
        out.append(T(L, ry, label_w - 16, row_h, row.get('label', ''), 18, '@ink', True, anchor='middle'))
        out.append(T(xb + 22, ry, card_w - 44, row_h, row.get('before', ''), 15, '@muted', anchor='middle', lineSpacing=1.25))
        out.append(T(xb + card_w, ry, 48, row_h, '→', 18, '@accent', True, align='center', anchor='middle'))
        out.append(T(xa + 22, ry, card_w - 44, row_h, row.get('after', ''), 16, '@ink', True, anchor='middle', lineSpacing=1.25))
    if aside:
        ay = y + height + 18
        paragraph = [{'text': aside.get('label', '') + '      ', 'bold': True, 'color': '@accentInk'}]
        for item in aside.get('items', []):
            paragraph += [{'text': item.get('name', '') + '  ', 'bold': True, 'color': '@ink'}, {'text': item.get('text', '') + '      ', 'color': '@muted'}]
        out.append(T(L, ay, CW, 36, [paragraph], 14, '@muted', anchor='middle'))
    return out


# ---------------------------------------------------------------- 수치·차트
def bars(items, x, y, w, row=76):
    """가로 막대 비교. 막대 위에 이름, 끝에 값. (개체 목록, 끝 y)."""
    out = []
    top = max(item['value'] for item in items) or 1
    track = w - 150
    for item in items:
        highlight = item.get('highlight', False)
        out.append(T(x, y, w, 22, item['label'], 15, '@ink' if highlight else '@muted', highlight))
        width = max(4, item['value'] / top * track)
        out.append(B(x, y + 30, width, 22, item.get('color') or ('@accent' if highlight else '@neutral'), radius=4))
        out.append(T(x + width + 14, y + 24, 150, 34, item.get('display', str(item['value'])), 24, '@accentInk' if highlight else '@ink', True, anchor='middle', letterSpacing=-.5))
        y += row
    return out, y


def hero_number(s, ctx):
    """핵심 수치 타일(진한 강조색) + 오른쪽 비교 막대."""
    out = frame(s, ctx)
    top, bottom = ctx.top, ctx.bottom
    tile_w = 470
    out.append(B(L, top, tile_w, bottom - top, '@accent', radius=16, name='핵심 수치'))
    out.append(T(L + 36, top + 30, tile_w - 72, 24, s.get('label', ''), 17, '@onAccent', True))
    out.append(value_unit(L + 30, top + 70, s.get('value', ''), s.get('unit', ''), 132, '@onAccent', h=170, width=tile_w - 50))
    if s.get('sub'):
        out.append(T(L + 36, bottom - 90, tile_w - 72, 60, s['sub'], 15, '@onAccent', lineSpacing=1.35))
    if s.get('bars'):
        bx = L + tile_w + 64
        out.append(stage(bx - 32, top, R - bx + 32, bottom - top))
        if s.get('barTitle'):
            out.append(T(bx, top + 24, R - bx - 32, 20, s['barTitle'], 13, '@muted', True))
        parts, y = bars(s['bars'], bx, top + 64, R - bx - 32)
        out += parts
        if s.get('barNote'):
            out.append(T(bx, bottom - 64, R - bx - 32, 44, s['barNote'], 13, '@muted', lineSpacing=1.3))
    return out


def chart(s, ctx):
    """옅은 무대 위의 네이티브 차트 + 오른쪽 해석 열."""
    out = frame(s, ctx)
    spec = copy.deepcopy(s['chart'])
    has_margin = bool(s.get('stats') or s.get('takeaway'))
    stage_w = CW - (MARGIN_W + GAP if has_margin else 0)
    out.append(stage(L, ctx.top, stage_w, ctx.bottom - ctx.top))
    inner_top = ctx.top + 22
    if s.get('chartTitle'):
        out.append(T(L + 28, inner_top, stage_w - 56, 20, s['chartTitle'], 13, '@muted', True))
        inner_top += 28
    spec.update({'type': 'chart', 'x': L + 16, 'y': inner_top, 'w': stage_w - 32, 'h': ctx.bottom - inner_top - 14, 'name': '차트'})
    for key, value in {'fontSize': 13, 'axisColor': '@muted', 'lineColor': '@line', 'gridColor': '@line', 'gapWidth': 70}.items():
        spec.setdefault(key, value)
    spec.setdefault('legend', len(spec.get('series', [])) > 1)
    out.append(spec)
    if has_margin:
        items = list(s.get('stats', []))
        if s.get('takeaway'):
            items.append({'title': s['takeaway'], 'text': s.get('takeawayText', '')})
        parts, _ = margin(items, R - MARGIN_W, ctx.top + 8, MARGIN_W, ctx.bottom)
        out += parts
    return out


def proportion(s, ctx):
    out = frame(s, ctx)
    groups = s['groups']
    stage_w = CW - MARGIN_W - GAP
    out.append(stage(L, ctx.top, stage_w, ctx.bottom - ctx.top))
    inner = stage_w - 64
    y = ctx.top + 30
    step = (ctx.bottom - ctx.top - 40) / len(groups)
    for group in groups:
        highlight = group.get('highlight', False)
        out.append(T(L + 32, y, inner, 22, group.get('label', ''), 16, '@ink' if highlight else '@muted', True))
        total = sum(part['value'] for part in group['parts']) or 1
        bx = L + 32
        bh = min(84, step - 74)
        for index, part in enumerate(group['parts']):
            pw = inner * part['value'] / total
            first = index == 0
            fill = ('@accent' if highlight else '@neutral') if first else '@white'
            color = '@onAccent' if first and highlight else ('@ink' if first else '@muted')
            out.append(B(bx, y + 32, max(2, pw - 4), bh, fill, radius=8, paragraphs=[
                [{'text': part.get('display', f'{part["value"]}%'), 'fontSize': 30, 'bold': True, 'color': color, 'letterSpacing': -.8}],
                [{'text': part.get('label', ''), 'fontSize': 13, 'color': color}]], fontSize=13, padding=16, anchor='middle', lineSpacing=1.1))
            bx += pw
        y += step
    parts, y2 = margin(s.get('stats', []), R - MARGIN_W, ctx.top + 8, MARGIN_W, ctx.bottom)
    out += parts
    if s.get('text'):
        out.append(T(R - MARGIN_W, y2 - 6, MARGIN_W, 60, s['text'], 13, '@muted', lineSpacing=1.35))
    return out


def summary(s, ctx):
    """핵심 성과 요약: 진한 강조색 타일의 이전 → 이후 + 옅은 보조 지표 카드."""
    out = frame(s, ctx)
    main = s['main']
    top, bottom = ctx.top, ctx.bottom
    tw = 760
    out.append(B(L, top, tw, bottom - top, '@accent', radius=16, name='핵심 성과'))
    title = [[{'text': main.get('label', ''), 'bold': True, 'color': '@onAccent'}]]
    if main.get('tag'):
        title[0].append({'text': '    ' + main['tag'], 'color': '@onAccent'})
    out.append(T(L + 36, top + 28, tw - 72, 22, title, 15, '@onAccent', anchor='middle'))
    before, after = main['before'], main['after']
    vy = top + 72
    out.append(T(L + 36, vy, 320, 20, before.get('label', ''), 14, '@onAccent'))
    out.append(T(L + 396, vy, 340, 20, after.get('label', ''), 14, '@onAccent', True))
    out.append(B(L + 36, vy + 30, 320, 96, '@white', radius=10, opacity=.14))
    out.append(value_unit(L + 52, vy + 30, before['value'], before.get('unit', ''), 64, '@onAccent', h=92))
    out.append(T(L + 356, vy + 30, 40, 96, '→', 26, '@onAccent', True, align='center', anchor='middle'))
    out.append(B(L + 396, vy + 30, 328, 96, '@white', radius=10))
    out.append(value_unit(L + 412, vy + 30, after['value'], after.get('unit', ''), 64, '@accentInk', h=92))
    dy = vy + 146
    if main.get('delta'):
        out.append(T(L + 36, dy, tw - 72, 32, [[{'text': main['delta'], 'bold': True, 'color': '@onAccent', 'fontSize': 22},
                                                {'text': '   ' + main.get('deltaSub', ''), 'color': '@onAccent', 'fontSize': 17}]], 17, '@onAccent', anchor='middle'))
    bullets = main.get('bullets', [])
    if bullets:
        by = dy + 50
        out.append(LN(L + 36, by, tw - 72, 0, '@white', .75))
        out.append(T(L + 36, by + 14, tw - 72, bottom - by - 24, ['·  ' + item for item in bullets], 14, '@onAccent', lineSpacing=1.5))
    side = s.get('side', [])
    sx = L + tw + 20
    sh = (bottom - top - 20 * (len(side) - 1)) / max(len(side), 1)
    for index, card in enumerate(side):
        y = top + index * (sh + 20)
        out.append(B(sx, y, R - sx, sh, '@paper', radius=16))
        out.append(T(sx + 26, y + 22, R - sx - 52, 20, card.get('label', ''), 13, '@accentInk', True))
        out.append(value_unit(sx + 24, y + 44, card.get('value', ''), card.get('unit', ''), 50, '@ink', h=66))
        if card.get('text'):
            out.append(T(sx + 26, y + 116, R - sx - 52, 44, card['text'], 14, '@ink', lineSpacing=1.25))
        if card.get('foot'):
            out.append(T(sx + 26, y + sh - 34, R - sx - 52, 20, card['foot'], 12, '@muted'))
    return out


# ---------------------------------------------------------------- 흐름·단계
def flow(s, ctx):
    """옅은 무대 위의 단계 타일과 화살표 + 오른쪽 판단 기준 열."""
    out = frame(s, ctx)
    side = s.get('side')
    stage_w = CW - (MARGIN_W + GAP if side else 0)
    out.append(stage(L, ctx.top, stage_w, ctx.bottom - ctx.top))
    rows = s['rows']
    y = ctx.top + 24
    row_h = (ctx.bottom - ctx.top - 24) / len(rows)
    tones = {'accent': ('@accent', None, '@onAccent', '@onAccent'), 'hot': ('@hotSoft', '@hot', '@hotInk', '@ink'),
             'soft': ('@accentSoft', None, '@accentInk', '@ink')}
    for row in rows:
        if row.get('label'):
            out.append(T(L + 28, y, 500, 20, row['label'], 13, '@muted', True))
        steps_ = row['steps']
        gap = 34
        inner = stage_w - 56
        sw = (inner - gap * (len(steps_) - 1)) / len(steps_)
        sy = y + 30
        sh = min(100, row_h - 56)
        for index, step in enumerate(steps_):
            sx = L + 28 + index * (sw + gap)
            fill, line, title_color, text_color = tones.get(step.get('tone'), ('@white', None, '@ink', '@muted'))
            paragraphs = [[{'text': step.get('title', ''), 'bold': True, 'fontSize': 18, 'color': title_color}]]
            if step.get('text'):
                paragraphs.append([{'text': step['text'], 'fontSize': 13, 'color': text_color}])
            out.append(B(sx, sy, sw, sh, fill, line, radius=10, paragraphs=paragraphs, fontSize=13, padding=16, anchor='middle', lineSpacing=1.25, lineWidth=1.5))
            if index < len(steps_) - 1:
                out.append(LN(sx + sw + 6, sy + sh / 2, gap - 12, 0, '@muted', 1.2, arrow='end'))
        y += row_h
    if side:
        x = R - MARGIN_W
        out.append(T(x, ctx.top, MARGIN_W, 20, side.get('title', ''), 13, '@accentInk', True))
        parts, _ = margin(side.get('items', []), x, ctx.top + 36, MARGIN_W, ctx.bottom)
        out += parts
    return out


def steps(s, ctx):
    """단계·연혁: 위쪽 구간 막대(강조 구간만 진하게) + 열별 제목·설명·결과."""
    out = frame(s, ctx)
    y = ctx.top
    stat = s.get('stat')
    if stat:
        out.append(B(L, y, 360, 120, '@accent', radius=14))
        out.append(value_unit(L + 24, y + 6, stat['value'], stat.get('unit', ''), 76, '@onAccent', h=104))
        out.append(T(L + 390, y, 470, 120, stat.get('text', ''), 17, '@ink', anchor='middle', lineSpacing=1.4))
        if s.get('badge'):
            badge = s['badge']
            out.append(B(R - 300, y, 300, 120, '@hotSoft', radius=14))
            out.append(T(R - 280, y + 16, 260, 100, [[{'text': badge.get('label', ''), 'bold': True, 'color': '@hotInk'}],
                                                    [{'text': badge.get('text', ''), 'color': '@ink'}]], 13, '@ink', lineSpacing=1.35))
        y += 160
    items = s['steps']
    gap = 8
    sw = (CW - gap * (len(items) - 1)) / len(items)
    highlight = s.get('highlight', len(items) - 1)
    labelled = any('label' in item for item in items)
    for index, item in enumerate(items):
        sx = L + index * (sw + gap)
        hot = index == highlight
        out.append(B(sx, y, sw, 44, '@accent' if hot else '@paper', radius=8,
                     text=str(item.get('label', index + 1)), fontSize=20 if labelled else 15,
                     color='@onAccent' if hot else ('@ink' if labelled else '@muted'), bold=True, padding=16))
        ty = y + 64
        pad = 4
        out.append(T(sx + pad, ty, sw - 2 * pad - 12, 28, item.get('title', ''), 19, '@accentInk' if hot else '@ink', True))
        lines = line_count(item.get('text', ''), 14, sw - 20)
        out.append(T(sx + pad, ty + 32, sw - 2 * pad - 12, lines * 21, item.get('text', ''), 14, '@muted', lineSpacing=1.3))
        if item.get('result'):
            out.append(T(sx + pad, ty + 32 + max(2, lines) * 21 + 14, sw - 2 * pad - 12, 22, '→  ' + item['result'], 14, '@accentInk' if hot else '@ink', True))
    return out


def actions(s, ctx):
    """한계(회색 무대)와 다음 조치(옅은 강조 무대)를 같은 행에 맞춘다."""
    out = frame(s, ctx)
    labels = s.get('headers', ['현재 한계', '다음 조치'])
    rows = s['rows']
    half = (CW - 48) / 2
    xa = L + half + 48
    head = 44
    row_h = min(86, (ctx.bottom - ctx.top - head - 10) / len(rows))
    height = head + row_h * len(rows) + 10
    out.append(B(L, ctx.top, half, height, '@paper', radius=14))
    out.append(B(xa, ctx.top, half, height, '@accentSoft', radius=14))
    out.append(T(L + 24, ctx.top + 14, half - 48, 22, labels[0], 13, '@muted', True))
    out.append(T(xa + 24, ctx.top + 14, half - 48, 22, labels[1], 13, '@accentInk', True))
    for index, row in enumerate(rows):
        ry = ctx.top + head + index * row_h
        if index:
            out.append(LN(L + 24, ry, half - 48))
            out.append(LN(xa + 24, ry, half - 48, 0, '@white'))
        out.append(T(L + 24, ry, 30, row_h, str(index + 1), 15, '@muted', True, anchor='middle'))
        out.append(T(L + 58, ry, half - 82, row_h, row.get('issue', ''), 17, '@hotInk' if row.get('warn') else '@ink', True, anchor='middle', lineSpacing=1.2))
        out.append(T(L + half, ry, 48, row_h, '→', 18, '@accent', True, align='center', anchor='middle'))
        out.append(T(xa + 24, ry, half - 48, row_h, row.get('action', ''), 16, '@ink', anchor='middle', lineSpacing=1.25))
    return out


def columns(s, ctx):
    """설명 카드 2~4개. 강조 카드는 진한 강조색."""
    out = frame(s, ctx)
    cols = s['columns']
    gap = 20
    cw = (CW - gap * (len(cols) - 1)) / len(cols)
    highlight = s.get('highlight', -1)
    top = ctx.top
    tallest = max(line_count(col.get('text', ''), 16, cw - 56) for col in cols)
    height = min(ctx.bottom - top, 150 + tallest * 25 + (70 if any(col.get('example') for col in cols) else 0))
    for index, col in enumerate(cols):
        cx = L + index * (cw + gap)
        hot = index == highlight
        ink, sub, label = ('@onAccent', '@onAccent', '@onAccent') if hot else ('@ink', '@muted', '@accentInk')
        out.append(B(cx, top, cw, height, '@accent' if hot else '@paper', radius=16))
        out.append(T(cx + 28, top + 28, cw - 56, 20, col.get('kicker', ''), 13, label, True))
        out.append(T(cx + 28, top + 56, cw - 56, 40, col.get('title', ''), 26, ink, True))
        lines = line_count(col.get('text', ''), 16, cw - 56)
        out.append(T(cx + 28, top + 108, cw - 56, lines * 25, col.get('text', ''), 16, ink, lineSpacing=1.35))
        if col.get('example'):
            out.append(LN(cx + 28, top + height - 64, cw - 56, 0, '@white' if hot else '@line'))
            out.append(T(cx + 28, top + height - 56, cw - 56, 40, col['example'], 14, sub, True, anchor='middle'))
    return out


# ---------------------------------------------------------------- 화면·사람·부록
def screen(s, ctx):
    """화면 전체를 무대에 놓고, 설명할 영역은 옅은 강조 면으로 덮은 뒤 오른쪽에 확대 조각으로 보여 준다."""
    out = frame(s, ctx)
    top, bottom = ctx.top, ctx.bottom
    regions = s.get('regions', [])
    stage_w = CW - (MARGIN_W + GAP if regions else 0)
    out.append(stage(L, top, stage_w, bottom - top))
    pad = 22
    iw, ih = stage_w - 2 * pad, bottom - top - 2 * pad - (26 if s.get('caption') else 0)
    path = s.get('image')
    ix, iy = L + pad, top + pad
    size = None
    if path:
        full = ctx.base / path if not Path(path).is_absolute() else Path(path)
        size = image_size(full)
        if size:
            ratio = size[1] / size[0]
            if iw * ratio > ih:
                new_w = ih / ratio
                ix += (iw - new_w) / 2
                iw = new_w
            else:
                ih = iw * ratio
        out.append({'type': 'image', 'x': round(ix, 1), 'y': round(iy, 1), 'w': round(iw, 1), 'h': round(ih, 1), 'path': path, 'name': '화면'})
    else:
        out.append(B(ix, iy, iw, ih, '@white', radius=6, text='화면 이미지 자리', fontSize=16, color='@muted', align='center'))
    for region in regions:
        out.append(B(ix + region['x'] * iw, iy + region['y'] * ih, region.get('w', .1) * iw, region.get('h', .1) * ih,
                     '@accent', radius=4, opacity=.16))
    if s.get('caption'):
        out.append(T(L + pad, bottom - 34, stage_w - 2 * pad, 20, s['caption'], 13, '@muted'))
    if regions:
        x = R - MARGIN_W
        y = top
        box_h = min(120, (bottom - top) / len(regions) - 74)
        image_w, image_h = size if size else (16, 9)
        for region in regions:
            # 영역 안에서 상자 비율에 맞는 부분만 잘라 낸다. 너무 길쭉하면 위쪽(또는 왼쪽)부터 보여 준다.
            rx, ry = region['x'] * image_w, region['y'] * image_h
            rw, rh = region.get('w', .1) * image_w, region.get('h', .1) * image_h
            target = min(max(rw / rh, 150 / box_h), MARGIN_W / box_h)
            if rw / rh < target:
                rh = rw / target
            else:
                rw = rh * target
            rw, rh = min(rw, image_w), min(rh, image_h)
            rx, ry = min(max(0, rx), image_w - rw), min(max(0, ry), image_h - rh)
            if path:
                out.append({'type': 'image', 'x': round(x, 1), 'y': round(y, 1), 'w': round(box_h * target, 1), 'h': round(box_h, 1), 'path': path,
                            'crop': {'l': round(rx / image_w, 4), 't': round(ry / image_h, 4),
                                     'r': round(max(0, 1 - (rx + rw) / image_w), 4), 'b': round(max(0, 1 - (ry + rh) / image_h), 4)},
                            'name': '확대: ' + region.get('title', '')})
                out.append(B(x, y, box_h * target, box_h, 'none', '@line', radius=6))
            y += box_h + 10
            out.append(T(x, y, MARGIN_W, 22, region.get('title', ''), 16, '@ink', True))
            lines = line_count(region.get('text', ''), 13, MARGIN_W)
            out.append(T(x, y + 24, MARGIN_W, lines * 19, region.get('text', ''), 13, '@muted', lineSpacing=1.25))
            y += 24 + lines * 19 + 18
    return out


def team(s, ctx):
    out = frame(s, ctx)
    members = s['members']
    gap = 20
    mw = (CW - gap * (len(members) - 1)) / len(members)
    height = ctx.bottom - ctx.top
    for index, member in enumerate(members):
        mx = L + index * (mw + gap)
        out.append(B(mx, ctx.top, mw, height, '@paper', radius=16))
        ph = min(mw - 48, height - 150)
        if member.get('photo'):
            out.append({'type': 'image', 'x': round(mx + 24, 1), 'y': ctx.top + 24, 'w': round(mw - 48, 1), 'h': round(ph, 1), 'path': member['photo'], 'name': member.get('name', '사진')})
        else:
            out.append(B(mx + 24, ctx.top + 24, mw - 48, ph, '@accentSoft', radius=10, text=member.get('name', '?')[:1], fontSize=52, color='@accent', bold=True, align='center'))
        out.append(T(mx + 24, ctx.top + ph + 44, mw - 48, 30, member.get('name', ''), 21, '@ink', True))
        out.append(T(mx + 24, ctx.top + ph + 78, mw - 48, 44, member.get('role', ''), 14, '@accentInk', True, lineSpacing=1.25))
    return out


def answer(s, ctx):
    """질의응답 부록: 옅은 강조 면의 답 + 근거 표."""
    out = frame(s, ctx)
    y = ctx.top
    text = s.get('answer', '')
    lines = line_count(plain(text), 18, CW - 140)
    ah = lines * 28 + 40
    out.append(B(L, y, CW, ah, '@accentSoft', radius=14))
    out.append(T(L + 28, y, 60, ah, s.get('answerLabel', '답'), 18, '@accentInk', True, anchor='middle'))
    out.append(T(L + 96, y, CW - 124, ah, runs(text, '@ink', '@accentInk'), 18, '@ink', anchor='middle', lineSpacing=1.35))
    body = s.get('body', {})
    if body.get('rows'):
        out += table_layout(body, ctx, rows=body['rows'], top=y + ah + 24)
    return out


LAYOUTS = {
    'cover': cover, 'section': section, 'closing': closing, 'agenda': agenda,
    'hero-number': hero_number, 'chart': chart, 'table': table_layout, 'tiers': tiers,
    'compare': compare, 'proportion': proportion, 'summary': summary,
    'flow': flow, 'steps': steps, 'actions': actions, 'columns': columns,
    'screen': screen, 'team': team, 'answer': answer,
}

LAYOUT_NOTES = {
    'cover': '표지. style=split(기본, 오른쪽 강조색 면), light, dark. 선택: 막대 모티프, 이미지',
    'section': '구역 구분. 옅은 강조색 바탕, 큰 번호, 흰 카드의 소항목',
    'closing': '마무리. 강조색 전면',
    'agenda': '차례·부록 목록. 번호가 큰 2열 타일',
    'hero-number': '진한 강조색 핵심 수치 타일 + 무대 위 비교 막대',
    'chart': '무대 위 네이티브 차트 + 오른쪽 해석 열',
    'table': '네이티브 표(옅은 머리 행, 강조 행) + 선택적 오른쪽 수치 열',
    'tiers': '구간별 값. 순위에 따라 농도가 다른 값 타일 + 환산 값 + 보조 카드',
    'compare': '대비. 회색 카드(이전·문제)와 강조 카드(이후·해결)를 행으로 맞춤',
    'proportion': '무대 위 비율 막대(이전/이후) + 오른쪽 변화 수치',
    'summary': '핵심 성과. 강조색 타일의 이전 → 이후 + 보조 지표 카드',
    'flow': '무대 위 단계 타일·화살표(1~3줄) + 오른쪽 판단 기준',
    'steps': '단계·연혁. 구간 막대(강조 구간만 진하게), 선택적 상단 수치 타일',
    'actions': '한계(회색)와 다음 조치(강조) 두 무대를 행으로 맞춤',
    'columns': '설명 카드 2~4개, 강조 카드는 진한 강조색',
    'screen': '화면 전체 + 설명 영역을 옅게 덮고 오른쪽에 확대 조각과 설명',
    'team': '팀원 카드(사진 없으면 이니셜)',
    'answer': '질의응답 부록. 옅은 강조 면의 답 + 근거 표',
}

SENTENCE_ENDING = re.compile(r'(?:[다요죠까]|었나|았나|했나|하나요|는가|인가|인지|을까|ㄹ까|한가|는지|[.?!])\s*$')


def sentence_titles(scene: dict) -> list[tuple[int, str]]:
    """명사형이 아닌(문장형) 제목을 찾는다. 리드 한 줄과 본문은 검사하지 않는다."""
    found = []
    for index, slide in enumerate(scene.get('slides', []), 1):
        title = str(slide.get('title', '')).strip()
        # 마무리 인사(감사합니다)는 제목 규칙의 예외다.
        if title and slide.get('layout') != 'closing' and SENTENCE_ENDING.search(title):
            found.append((index, title))
    return found


def expand_scene(scene: dict, base_dir=None) -> dict:
    """layout 슬라이드를 elements로 펼친 새 scene을 돌려준다. 입력은 바꾸지 않는다."""
    result = copy.deepcopy(scene)
    slides = result.get('slides', [])
    if not any(isinstance(slide, dict) and 'layout' in slide for slide in slides):
        return result
    if result.get('width', W) != W or result.get('height', H) != H:
        raise ValueError('layout 슬라이드는 1280×720 scene에서만 쓸 수 있습니다.')
    result.setdefault('background', '@bg')
    total = sum(1 for slide in slides if not slide.get('appendix'))
    for index, slide in enumerate(slides, 1):
        layout = slide.get('layout')
        if not layout:
            continue
        if layout not in LAYOUTS:
            raise ValueError(f'Slide {index}: 알 수 없는 layout {layout!r}. 사용 가능: {", ".join(LAYOUTS)}')
        if slide.get('appendix') and not slide.get('pageLabel'):
            slide['pageLabel'] = slide.get('kicker', '부록')
        ctx = Ctx(result, slide, index, total, base_dir)
        try:
            elements = LAYOUTS[layout](slide, ctx)
        except KeyError as error:
            raise ValueError(f'Slide {index} ({layout}): 필수 항목 {error} 이(가) 없습니다.') from None
        slide['elements'] = elements + slide.get('elements', [])
    return result
