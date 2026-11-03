#!/usr/bin/env python3
"""작성자: Git 이력 참조. 작성목적: 장면의 보조 PDF, PNG와 전체 축소판 생성.
작성일: 2026-10-22. PPTX 내보내기가 아니며 PowerPoint 줄바꿈 검증을 대체하지 않는다.
"""
import argparse
import json
import warnings
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import pymupdf as fitz
from PIL import Image, ImageOps, ImageDraw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scene'); parser.add_argument('output')
    parser.add_argument('--font-regular', required=True); parser.add_argument('--font-bold', required=True)
    args = parser.parse_args()
    scene_path = Path(args.scene).resolve(); scene = json.loads(scene_path.read_text())
    if (scene['width'], scene['height']) != (1280, 720):
        raise ValueError('Only 1280 x 720 scenes supported')
    pdfmetrics.registerFont(TTFont('SceneRegular', args.font_regular))
    pdfmetrics.registerFont(TTFont('SceneBold', args.font_bold))
    output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=(1280, 720))
    theme = {'background':'FFFFFF','text':'192A40','muted':'526174','accent':'2459A6','line':'CDD6E1', **scene.get('theme',{})}
    def color(value): return '#' + value.lstrip('#')
    def draw_text(e):
        size=e.get('fontSize',26); font='SceneBold' if e.get('bold') else 'SceneRegular'
        pdf.setFont(font,size); pdf.setFillColor(color(e.get('color',theme['text'])))
        lines=[]
        for paragraph in str(e.get('text','')).split('\n'):
            current=''
            for char in paragraph:
                if current and pdfmetrics.stringWidth(current+char,font,size)>e['w']:
                    lines.append(current);current=''
                current+=char
            lines.append(current)
        if lines and size + (len(lines)-1)*size*1.2 > e['h']:
            warnings.warn(f"Text exceeds scene box height: {str(e.get('text',''))[:48]}")
        for index,line in enumerate(lines):
            x=e['x']; y=720-e['y']-size-index*size*1.2
            if e.get('align')=='right': pdf.drawRightString(x+e['w'],y,line)
            elif e.get('align')=='center': pdf.drawCentredString(x+e['w']/2,y,line)
            else: pdf.drawString(x,y,line)
    for number, slide in enumerate(scene['slides'],1):
        pdf.setFillColor(color(theme['background']));pdf.rect(0,0,1280,720,fill=1,stroke=0)
        if slide.get('frame',True):
            draw_text(dict(text=slide.get('section',''),x=56,y=30,w=1168,h=24,fontSize=13,color=theme['muted']))
            draw_text(dict(text=slide.get('title',''),x=56,y=79,w=1168,h=64,fontSize=44,bold=True))
            draw_text(dict(text=f"{number} / {len(scene['slides'])}",x=1120,y=676,w=104,h=20,fontSize=13,color=theme['muted'],align='right'))
        for e in slide.get('elements',[]):
            kind=e['type']; x=e.get('x',0); y=720-e.get('y',0)-e.get('h',0); w=e.get('w',0); h=e.get('h',0)
            if e.get('gradient'): raise ValueError('Gradients unsupported')
            if kind=='text':draw_text(e)
            elif kind in ('rect','ellipse'):
                pdf.setFillColor(color(e.get('fill',theme['background'])));pdf.setStrokeColor(color(e.get('stroke',theme['line'])));pdf.setLineWidth(e.get('strokeWidth',1))
                if kind=='rect':pdf.rect(x,y,w,h,fill=1,stroke=1)
                else:pdf.ellipse(x,y,x+w,y+h,fill=1,stroke=1)
            elif kind=='line':
                points=e.get('points') or [[x,e.get('y',0)],[x+w,e.get('y',0)+h]]
                pdf.setStrokeColor(color(e.get('stroke',theme['accent'])));pdf.setFillColor(color(e.get('stroke',theme['accent'])));pdf.setLineWidth(e.get('strokeWidth',2))
                for start,end in zip(points,points[1:]):
                    if start[0]!=end[0] and start[1]!=end[1]:raise ValueError('Only orthogonal lines supported')
                    pdf.line(start[0],720-start[1],end[0],720-end[1])
                for enabled,tip,previous in [(e.get('endArrow'),points[-1],points[-2]),(e.get('startArrow'),points[0],points[1])]:
                    if enabled:
                        dx=tip[0]-previous[0];dy=tip[1]-previous[1];length=(dx*dx+dy*dy)**.5
                        if not length:raise ValueError('Arrow endpoint segment must have length')
                        ux=dx/length;uy=dy/length;p=pdf.beginPath();p.moveTo(tip[0],720-tip[1]);p.lineTo(tip[0]-ux*12-uy*5,720-(tip[1]-uy*12+ux*5));p.lineTo(tip[0]-ux*12+uy*5,720-(tip[1]-uy*12-ux*5));p.close();pdf.drawPath(p,fill=1,stroke=0)
            elif kind=='image':
                resource=scene_path.parent/e['path']; image=Image.open(resource);iw,ih=image.size; scale=min(w/iw,h/ih)
                pdf.drawImage(ImageReader(image),x+(w-iw*scale)/2,y+(h-ih*scale)/2,iw*scale,ih*scale,mask='auto')
            elif kind=='table':
                rows=e['rows'];rh=h/len(rows);widths=e.get('colWidths',[w/len(rows[0])]*len(rows[0]))
                if len(widths)!=len(rows[0]) or any(cw<=0 for cw in widths) or abs(sum(widths)-w)>.01:
                    raise ValueError('Table colWidths must be positive and sum to w')
                for ri,row in enumerate(rows):
                    top=e['y']+ri*rh
                    if ri>0 and e.get('banded') and ri%2==1:
                        pdf.setFillColor(color(e.get('bandColor','EEF3F9')));pdf.rect(x,720-top-rh,w,rh,fill=1,stroke=0)
                    offset=0
                    for ci,cell in enumerate(row):
                        cw=widths[ci];size=e.get('fontSize',24)
                        draw_text(dict(text=str(cell),x=x+offset+18,y=top+(rh-size)/2-2,w=cw-36,h=rh-16,fontSize=size,bold=ri==0 or ci==0,color=theme['accent'] if ri==0 or ci==e.get('highlightColumn') else theme['text']))
                        offset+=cw
                    pdf.setStrokeColor(color(theme['line']));pdf.setLineWidth(1.3 if ri==0 else .7)
                    pdf.line(x,720-top-rh,x+w,720-top-rh)
            elif kind=='barChart':
                series=e['series'];labels=series[0]['labels'];maximum=max(max(s['values']) for s in series)
                if maximum<=0 or any(v<0 for s in series for v in s['values']):raise ValueError('Preview bar chart supports nonnegative values with positive maximum only')
                step=w/len(labels);bw=step*.7/len(series)
                for si,s in enumerate(series):
                    pdf.setFillColor(color(e.get('colors',[theme['accent']])[si%len(e.get('colors',[theme['accent']]))]))
                    for vi,v in enumerate(s['values']):pdf.rect(x+vi*step+si*bw,y+30,bw-4,(h-60)*v/maximum,fill=1,stroke=0)
                for vi,label in enumerate(labels):draw_text(dict(text=label,x=x+vi*step,y=e['y']+h-28,w=step,h=28,fontSize=18))
            else:raise ValueError(f'Unsupported element type: {kind}')
        pdf.showPage()
    pdf.save()
    render_dir=output.parent/(output.stem+'-renders');render_dir.mkdir(exist_ok=True)
    thumbs=[]
    with fitz.open(output) as document:
        for index,page in enumerate(document,1):
            pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)); filename=render_dir/f'slide-{index:02}.png';pix.save(str(filename))
            thumb=Image.open(filename).convert('RGB');thumb.thumbnail((640,360));thumbs.append(thumb.copy())
    contact=Image.new('RGB',(1280,380*((len(thumbs)+1)//2)),'#E5E9EF')
    draw=ImageDraw.Draw(contact)
    for index,thumb in enumerate(thumbs):contact.paste(thumb,((index%2)*640,(index//2)*380));draw.text(((index%2)*640+8,(index//2)*380+362),str(index+1),fill='black')
    contact.save(render_dir/'contact-sheet.png')
    print(f'Companion PDF: {output}; renders: {render_dir}. This is not a PPTX export.')

if __name__=='__main__':main()
