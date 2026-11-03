#!/usr/bin/env python3
"""작성자: Git 이력 참조. 작성목적: 장면/PPTX의 구조 및 자산 검사.
작성일: 2026-10-22. 시각적 품질이나 실제 앱 렌더를 보증하지 않는다.
"""
import argparse
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET


def audit(scene_file, pptx_file):
    scene_path=Path(scene_file);scene=json.loads(scene_path.read_text());errors=[];warnings=[]
    if (scene.get('width'),scene.get('height'))!=(1280,720):errors.append('Canvas must be 1280 x 720')
    native_text=0;tables=0;charts=0
    for index,slide in enumerate(scene.get('slides',[]),1):
        if not slide.get('notes'):warnings.append(f'Slide {index}: empty speaker notes')
        image_area=0
        for e in slide.get('elements',[]):
            label=f'Slide {index} {e.get("type")}'
            if e.get('gradient'):warnings.append(f'{label}: gradient unsupported')
            if e['type']=='line':
                points=e.get('points',[[e.get('x',0),e.get('y',0)],[e.get('x',0)+e.get('w',0),e.get('y',0)+e.get('h',0)]])
                if any(x<0 or y<0 or x>1280 or y>720 for x,y in points):errors.append(f'{label}: outside canvas')
            else:
                if any(key not in e for key in ('x','y','w','h')):errors.append(f'{label}: missing geometry');continue
                if e['x']<0 or e['y']<0 or e['w']<=0 or e['h']<=0 or e['x']+e['w']>1280 or e['y']+e['h']>720:errors.append(f'{label}: outside canvas or invalid size')
            if e['type'] in ('text','table') and e.get('fontSize',26)<18:warnings.append(f'{label}: font below 18 px')
            if e['type']=='text':native_text+=1
            if e['type']=='table':tables+=1
            if e['type']=='barChart':charts+=1
            if e['type']=='image':
                resource=scene_path.parent/e['path']
                if not resource.is_file():errors.append(f'{label}: missing resource {e["path"]}')
                else:
                    try:
                        from PIL import Image
                        with Image.open(resource) as image:
                            iw,ih=image.size
                            if min(iw/e['w'],ih/e['h'])<1.5:warnings.append(f'{label}: image density below 1.5x')
                    except ImportError:warnings.append('Pillow unavailable: image density unverified')
                image_area+=e['w']*e['h']
        if image_area>1280*720*.85:warnings.append(f'Slide {index}: images cover over 85% canvas; verify editability')
    ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
    with zipfile.ZipFile(pptx_file) as archive:
        names=archive.namelist(); roots={}
        for name in names:
            if name.endswith('.xml'):
                try:roots[name]=ET.fromstring(archive.read(name))
                except ET.ParseError as exc:errors.append(f'Invalid XML {name}: {exc}')
        slides=[r for n,r in roots.items() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
        if len(slides)!=len(scene['slides']):errors.append('Slide count mismatch')
        presentation=roots.get('ppt/presentation.xml');size=presentation.find('p:sldSz',ns) if presentation is not None else None
        if size is None or abs(int(size.get('cx'))/int(size.get('cy'))-16/9)>.001:errors.append('PPTX canvas ratio mismatch')
        actual_text=sum(len(r.findall('.//a:t',ns)) for r in slides)
        if actual_text<native_text:errors.append('Native text count below scene text count')
        if sum(len(r.findall('.//a:tbl',ns)) for r in slides)<tables:errors.append('Missing native tables')
        if len([n for n in names if n.startswith('ppt/charts/chart') and n.endswith('.xml')])<charts:errors.append('Missing native charts')
        font=scene.get('font','Pretendard')
        for name,root in roots.items():
            if name.startswith('ppt/theme/'):
                ea=root.findall('.//a:majorFont/a:ea',ns)+root.findall('.//a:minorFont/a:ea',ns)
                if len(ea)<2 or any(e.get('typeface')!=font for e in ea):errors.append(f'{name}: East Asian font mismatch')
        notes=[n for n in names if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml')]
        if len(notes)<sum(bool(s.get('notes')) for s in scene['slides']):errors.append('Missing notes parts')
    warnings.append(f'Font {scene.get("font","Pretendard")} is referenced, not embedded; target-machine availability and real PPTX rendering remain unverified')
    print(json.dumps({'errors':errors,'warnings':warnings,'slides':len(scene['slides']),'nativeTextRuns':actual_text},ensure_ascii=False,indent=2))
    return bool(errors)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('scene');parser.add_argument('pptx');args=parser.parse_args();raise SystemExit(audit(args.scene,args.pptx))
