#!/usr/bin/env python3
"""Inspect scene geometry, solid-background contrast and optional measured text fit.

Author: Git history. Created: 2026-10-22.
This checks the companion renderer's character wrapping, not PowerPoint's layout.
No aesthetic score is assigned. Text overlap without font metrics is only a warning.
"""
import argparse
import json
import math
from pathlib import Path


def intersects(a, b, tolerance=2):
    return min(a[0]+a[2], b[0]+b[2])-max(a[0], b[0]) > tolerance and min(a[1]+a[3], b[1]+b[3])-max(a[1], b[1]) > tolerance


def contains(a, b):
    return a[0] <= b[0] and a[1] <= b[1] and a[0]+a[2] >= b[0]+b[2] and a[1]+a[3] >= b[1]+b[3]


def box(element):
    return tuple(element[key] for key in ('x', 'y', 'w', 'h'))


def contrast(first, second):
    def luminance(hex_color):
        rgb = bytes.fromhex(hex_color.lstrip('#'))
        if len(rgb) != 3:
            raise ValueError('Colors must have six hex digits')
        linear = [v/255/12.92 if v/255 <= .04045 else ((v/255+.055)/1.055)**2.4 for v in rgb]
        return sum(v*w for v, w in zip(linear, (.2126, .7152, .0722)))
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light+.05)/(dark+.05)


def font_measure(regular, bold=None):
    """Load explicit font files; never silently substitute a different font."""
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('LayoutRegular', str(regular)))
    if bold:
        pdfmetrics.registerFont(TTFont('LayoutBold', str(bold)))
    def measure(text, size, is_bold):
        if is_bold and not bold:
            raise ValueError('Bold font required to measure bold text')
        return pdfmetrics.stringWidth(text, 'LayoutBold' if is_bold else 'LayoutRegular', size)
    return measure


def text_lines(element, measure):
    size = element.get('fontSize', 26)
    lines = []
    for paragraph in str(element.get('text', '')).split('\n'):
        current = ''
        for char in paragraph:
            if current and measure(current+char, size, element.get('bold', False)) > element['w']:
                lines.append(current)
                current = ''
            current += char
        lines.append(current)
    return lines


def audit(scene, measure=None, consistency=False):
    errors, warnings = [], []
    width, height = scene.get('width', 1280), scene.get('height', 720)
    theme = {'background': 'FFFFFF', 'text': '192A40', 'muted': '526174', **scene.get('theme', {})}
    if (width, height) != (1280, 720):
        errors.append('Canvas must be 1280 x 720')
    if measure is None:
        warnings.append('Font metrics unavailable: wrapping and text height unverified; overlaps use container boxes.')
    for number, slide in enumerate(scene.get('slides', []), 1):
        elements = []
        if slide.get('frame', True):
            for text, y, size, h, bold in [(slide.get('section', ''), 30, 13, 24, False), (slide.get('title', ''), 79, 44, 64, True)]:
                elements.append(dict(type='text', text=text, x=56, y=y, w=1168, h=h, fontSize=size, bold=bold))
            elements.append(dict(type='text', text=f'{number} / {len(scene["slides"])}', x=1120, y=676, w=104, h=20, fontSize=13, align='right', color=theme['muted']))
        elements += slide.get('elements', [])
        backgrounds, texts, body_sizes = [], [], set()
        for index, element in enumerate(elements):
            label = f'Slide {number} element {index+1}'
            kind = element.get('type')
            if kind == 'line':
                points = element.get('points') or [[element.get('x', 0), element.get('y', 0)], [element.get('x', 0)+element.get('w', 0), element.get('y', 0)+element.get('h', 0)]]
                if any(not 0 <= x <= width or not 0 <= y <= height for x, y in points):
                    errors.append(f'{label}: line outside canvas')
                continue
            try:
                bounds = box(element)
                if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in bounds) or bounds[2] <= 0 or bounds[3] <= 0:
                    raise ValueError()
            except (KeyError, ValueError):
                errors.append(f'{label}: invalid geometry')
                continue
            if not contains((0, 0, width, height), bounds):
                errors.append(f'{label}: outside canvas')
            if kind in ('rect', 'ellipse', 'image', 'table', 'barChart'):
                backgrounds.append((kind, bounds, element.get('fill', theme['background'])))
                continue
            if kind != 'text' or not str(element.get('text', '')).strip():
                continue
            size = element.get('fontSize', 26)
            if not isinstance(size, (int, float)) or not math.isfinite(size) or size <= 0:
                errors.append(f'{label}: invalid font size')
                continue
            if element.get('options'):
                warnings.append(f'{label}: PPTX-only text options are not measured')
            occupied = [bounds]
            if measure:
                try:
                    lines = text_lines(element, measure)
                    required = size + (len(lines)-1)*size*1.2
                    if required > element['h']+2:
                        errors.append(f'{label}: text height {required:.1f} exceeds {element["h"]:.1f}')
                    occupied = []
                    for row, line in enumerate(lines):
                        line_width = measure(line, size, element.get('bold', False))
                        if line_width > element['w']+1:
                            errors.append(f'{label}: glyph exceeds text width')
                        offset = {'left': 0, 'right': element['w']-line_width, 'center': (element['w']-line_width)/2}.get(element.get('align', 'left'), 0)
                        if line.strip():
                            occupied.append((element['x']+offset, element['y']+row*size*1.2, line_width, size))
                except ValueError as exc:
                    warnings.append(f'{label}: fit unverified: {exc}')
            for region in occupied:
                background = theme['background']
                for shape, shape_bounds, fill in reversed(backgrounds):
                    if intersects(region, shape_bounds, 0):
                        background = fill if shape == 'rect' and contains(shape_bounds, region) else None
                        break
                if background is None:
                    warnings.append(f'{label}: contrast unverified over mixed or non-solid background')
                    break
                try:
                    ratio = contrast(element.get('color', theme['text']), background)
                    # WCAG large text: 24 px regular or approximately 18.67 px bold.
                    threshold = 3 if size >= 24 or (element.get('bold') and size >= 18.67) else 4.5
                    if ratio < threshold:
                        warnings.append(f'{label}: low contrast {ratio:.2f}:1 (reference {threshold}:1)')
                        break
                except ValueError as exc:
                    errors.append(f'{label}: {exc}')
                    break
            for previous_label, previous_regions in texts:
                if any(intersects(a, b) for a in occupied for b in previous_regions):
                    warnings.append(f'{label}: text overlaps {previous_label}; inspect rendered page')
            texts.append((label, occupied))
            if 180 <= element['y'] <= 640 and 18 <= size <= 40:
                body_sizes.add(size)
        if consistency and len(body_sizes) > 4:
            warnings.append(f'Slide {number}: {len(body_sizes)} body text sizes; review hierarchy')
    return {'errors': errors, 'warnings': warnings, 'slides': len(scene.get('slides', [])), 'textFitMeasured': measure is not None, 'scope': 'Scene/companion layout only; real PPTX rendering and visual review remain required.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenes', nargs='+')
    parser.add_argument('--font-regular', type=Path)
    parser.add_argument('--font-bold', type=Path)
    parser.add_argument('--check-consistency', action='store_true')
    args = parser.parse_args()
    if args.font_bold and not args.font_regular:
        parser.error('--font-bold requires --font-regular')
    try:
        measure = font_measure(args.font_regular, args.font_bold) if args.font_regular else None
    except (ImportError, OSError, ValueError) as exc:
        parser.error(str(exc))
    reports = {}
    for filename in args.scenes:
        try:
            reports[filename] = audit(json.loads(Path(filename).read_text()), measure, args.check_consistency)
        except (OSError, ValueError, TypeError) as exc:
            reports[filename] = {'errors': [str(exc)], 'warnings': []}
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    return int(any(report['errors'] for report in reports.values()))


if __name__ == '__main__':
    raise SystemExit(main())
