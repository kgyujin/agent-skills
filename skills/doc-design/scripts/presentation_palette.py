"""Curated presentation palette selection and non-destructive token resolution.

New documents: explicit choice > stored choice > topic match > neutral.
Existing literal colors are preserved. Only @role tokens are resolved for PPTX.
"""
from pathlib import Path
import copy
import json
import re

CATALOG = Path(__file__).resolve().parents[1] / 'assets' / 'presentation-palettes.json'

def catalog():
    return json.loads(CATALOG.read_text(encoding='utf-8'))

def choose_palette(topic='', explicit=None, stored=None):
    presets = catalog()
    selected = explicit if explicit and explicit != 'auto' else stored
    if selected and selected != 'auto':
        return selected, 'explicit' if explicit and explicit != 'auto' else 'saved'
    topic = str(topic).casefold()
    ranked = []
    for name, preset in presets.items():
        hits = 0
        for keyword in preset['keywords']:
            word = keyword.casefold()
            found = bool(re.search(r'(?<![a-z0-9])' + re.escape(word) + r'(?![a-z0-9])', topic)) if word.isascii() else word in topic
            hits += int(found)
        ranked.append((hits, name))
    best = max(ranked, key=lambda item: item[0])
    return (best[1], 'topic') if best[0] else ('neutral', 'fallback')

def _mix(a, b, ratio):
    """a에 b를 ratio만큼 섞는다(0이면 a, 1이면 b)."""
    return ''.join(f'{round(int(a[i:i+2],16)*(1-ratio) + int(b[i:i+2],16)*ratio):02X}' for i in (0,2,4))

def _luminance(color):
    values=[int(color[i:i+2],16)/255 for i in (0,2,4)]
    values=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in values]
    return sum(x*w for x,w in zip(values,[.2126,.7152,.0722]))

def contrast(a, b):
    low, high = sorted([_luminance(a), _luminance(b)])
    return (high+.05)/(low+.05)

def _readable(color, background, target, toward):
    """color를 toward 쪽으로 조금씩 섞어 background 대비 target 이상이 되게 한다."""
    for step in range(0, 21):
        candidate = _mix(color, toward, step / 20)
        if contrast(candidate, background) >= target:
            return candidate
    return toward

def complete_roles(colors):
    """레이아웃이 쓰는 확장 역할(어두운 면·두 번째 강조 등)이 없으면 기본 역할에서 만든다."""
    c=dict(colors)
    c.setdefault('bg','FFFFFF')
    c.setdefault('faint',_mix(c['muted'],c['bg'],.35))
    c.setdefault('dark',_mix(c['ink'],c['accent'],.18))
    c.setdefault('onDark','FFFFFF')
    c.setdefault('darkMuted',_mix(c['dark'],'FFFFFF',.68))
    c.setdefault('darkLine',_mix(c['dark'],'FFFFFF',.14))
    c.setdefault('darkAccent',_readable(_mix(c['accent'],'FFFFFF',.5),c['dark'],4.6,'FFFFFF'))
    c.setdefault('hot',c['secondary'])
    c.setdefault('hotSoft',_mix('FFFFFF',c['hot'],.14))
    c.setdefault('hotInk',_readable(_mix(c['hot'],'000000',.22),c['hotSoft'],4.6,'000000'))
    c.setdefault('accentInk',_readable(_mix(c['accent'],'000000',.25),c['accentSoft'],4.6,'000000'))
    c.setdefault('neutral',_mix(c['muted'],'FFFFFF',.35))
    c.setdefault('onHot',max([c['dark'],'FFFFFF'],key=lambda x:contrast(x,c['hot'])))
    # 어두운 면 위의 두 번째 강조. 대비가 낮으면 밝게 섞는다.
    c.setdefault('darkHot',_readable(c['hot'],c['dark'],4,'FFFFFF'))
    return c

def colors_for(name):
    presets = catalog()
    if name in presets:
        return complete_roles(presets[name]['colors'])
    # Existing HTML palette names remain valid when reused by PPTX preferences.
    css = (CATALOG.parent / 'css' / 'palettes.css').read_text(encoding='utf-8')
    block = re.search(r'html\[data-palette="' + re.escape(name) + r'"\]\s*\{([^}]+)\}', css)
    if not block:
        raise ValueError('Unknown palette: ' + str(name))
    tokens = dict(re.findall(r'--([a-z-]+):\s*#([a-fA-F0-9]{6})', block.group(1)))
    return complete_roles({role:tokens[token] for role,token in {'ink':'ink','muted':'muted','paper':'surface-2','line':'line','accent':'accent','secondary':'ink-2','accentSoft':'accent-soft','white':'surface','onAccent':'on-accent'}.items()})

COLOR_FIELDS = {'color','fill','lineColor','headerFill','headerColor','borderColor','headerLineColor','labelColor','axisColor','gridColor','background'}

def apply_scene_palette(scene, topic=None, explicit=None, stored=None):
    result = copy.deepcopy(scene)
    # A palette embedded in an existing scene is an authored choice.
    chosen, reason = choose_palette(topic or scene.get('topic') or scene.get('title',''), explicit or scene.get('palette'), stored)
    colors = colors_for(chosen)
    def resolve(value):
        if isinstance(value, str) and value.startswith('@'):
            role, separator, strength = value[1:].partition('/')
            if role not in colors:
                raise ValueError('Unknown color role: ' + role)
            color = colors[role]
            if separator:
                if not strength.isdigit() or not 0 <= int(strength) <= 100:
                    raise ValueError('Color tint must be 0..100: ' + value)
                ratio = int(strength) / 100
                color = ''.join(f'{round(int(color[i:i+2],16)*ratio + 255*(1-ratio)):02X}' for i in (0,2,4))
            return color
        return value
    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key in COLOR_FIELDS:
                    node[key] = resolve(value)
                elif key == 'colors' and isinstance(value, list):
                    node[key] = [resolve(v) for v in value]
                else:
                    walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    if 'background' in result:
        result['background'] = resolve(result['background'])
    walk(result.get('slides', []))
    result['palette'] = chosen
    return result, chosen, reason
