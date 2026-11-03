#!/usr/bin/env node
/** 작성자: Git 이력 참조
 * 작성목적: 제한된 장면 JSON을 편집 가능한 PPTX로 생성한다. 단위는 px, 96 dpi이다.
 * 작성일: 2026-10-22
 * 변경사항 내역: 최초 작성. 의존성은 일반 Node 모듈 탐색으로 해결한다.
 */
const fs = require('fs');
const path = require('path');
const {spawnSync} = require('child_process');
const PptxGenJS = require('pptxgenjs');
async function main() {
  const [input, output] = process.argv.slice(2);
  if (!input || !output) throw Error('Usage: node build_deck.cjs scene.json output.pptx');
  const scene = JSON.parse(fs.readFileSync(input, 'utf8'));
  if (scene.width !== 1280 || scene.height !== 720 || !Array.isArray(scene.slides)) throw Error('Require width=1280, height=720, slides array');
  const pptx = new PptxGenJS(); pptx.layout = 'LAYOUT_WIDE';
  const font = scene.font || 'Pretendard';
  const theme = {background:'FFFFFF',text:'192A40',muted:'526174',accent:'2459A6',line:'CDD6E1',...(scene.theme||{})};
  pptx.author = scene.meta?.author || ''; pptx.subject = scene.meta?.subject || ''; pptx.title = scene.meta?.title || '';
  pptx.theme = {headFontFace:font,bodyFontFace:font,lang:'ko-KR'};
  const px = n => n/96;
  for (const [index, page] of scene.slides.entries()) {
    const slide = pptx.addSlide(); slide.background = {color:theme.background};
    const text = (e) => slide.addText(String(e.text ?? ''), {x:px(e.x),y:px(e.y),w:px(e.w),h:px(e.h),isTextBox:true,fontFace:font,fontSize:(e.fontSize||26)*.75,color:e.color||theme.text,bold:!!e.bold,margin:0,breakLine:false,align:e.align||'left',valign:'top',...e.options});
    if (page.frame !== false) {
      if (page.section) text({text:page.section,x:56,y:30,w:1168,h:24,fontSize:13,color:theme.muted});
      if (page.title) text({text:page.title,x:56,y:79,w:1168,h:64,fontSize:44,bold:true});
      text({text:`${index+1} / ${scene.slides.length}`,x:1120,y:676,w:104,h:20,fontSize:13,color:theme.muted,align:'right'});
    }
    for (const e of page.elements || []) {
      if (e.gradient) throw Error('Gradients unsupported; use solid fill');
      const box = {x:px(e.x),y:px(e.y),w:px(e.w),h:px(e.h)};
      if (e.type === 'text') text(e);
      else if (['rect','ellipse'].includes(e.type)) slide.addShape(pptx.ShapeType[e.type], {...box,fill:{color:e.fill||theme.background},line:{color:e.stroke||theme.line,width:(e.strokeWidth??1)*.75}});
      else if (e.type === 'line') {
        const points = e.points || [[e.x,e.y],[e.x+e.w,e.y+e.h]];
        for (let j=1;j<points.length;j++) {
          const [x1,y1]=points[j-1], [x2,y2]=points[j];
          if(x1!==x2 && y1!==y2) throw Error('Only orthogonal lines supported');
          slide.addShape(pptx.ShapeType.line,{x:px(Math.min(x1,x2)),y:px(Math.min(y1,y2)),w:px(Math.abs(x2-x1)),h:px(Math.abs(y2-y1)),flipH:x2<x1,flipV:y2<y1,line:{color:e.stroke||theme.accent,width:(e.strokeWidth||2)*.75,beginArrowType:e.startArrow&&j===1?'triangle':undefined,endArrowType:e.endArrow&&j===points.length-1?'triangle':undefined}});
        }
      } else if (e.type === 'image') {
        const resource = path.resolve(path.dirname(input),e.path); if(!fs.existsSync(resource)) throw Error(`Missing image: ${e.path}`);
        const measured=spawnSync(process.env.PYTHON || 'python3',[path.join(__dirname,'fix_cjk_theme.py'),'--image-size',resource],{encoding:'utf8'});
        if(measured.status!==0) throw Error(`Cannot size image: ${measured.stderr}`);
        const [iw,ih]=JSON.parse(measured.stdout); const scale=Math.min(box.w/iw,box.h/ih);
        slide.addImage({path:resource,x:box.x+(box.w-iw*scale)/2,y:box.y+(box.h-ih*scale)/2,w:iw*scale,h:ih*scale});
      } else if (e.type === 'table') {
        const widths=e.colWidths || e.rows[0].map(()=>e.w/e.rows[0].length);
        if(widths.length!==e.rows[0].length || widths.some(w=>w<=0) || Math.abs(widths.reduce((a,b)=>a+b,0)-e.w)>.01) throw Error('Table colWidths must be positive and sum to w');
        const none={type:'none',pt:0,color:theme.background};
        const rows=e.rows.map((row,ri)=>row.map((cell,ci)=>({text:String(cell),options:{
          bold:ri===0 || ci===0, color:ri===0 || ci===e.highlightColumn?theme.accent:theme.text,
          fill:{color:ri>0 && e.banded && ri%2===1?(e.bandColor||'EEF3F9'):theme.background},
          border:[none,none,{type:'solid',pt:ri===0?1:.5,color:theme.line},none]
        }})));
        slide.addTable(rows,{...box,fontFace:font,fontSize:(e.fontSize||24)*.75,color:theme.text,
          colW:widths.map(px),margin:[12,14,12,14],valign:'mid',rowH:e.h/e.rows.length/96,autoPage:false});
      } else if(e.type === 'barChart') {
        slide.addChart(pptx.ChartType.bar,e.series,{...box,barDir:'col',catAxisLabelFontFace:font,valAxisLabelFontFace:font,catAxisLabelFontSize:14,valAxisLabelFontSize:14,showLegend:e.series.length>1,showTitle:false,chartColors:e.colors||[theme.accent],showValue:true,showCatName:false,showBorder:false,showCatName:false});
      } else throw Error(`Unsupported element type: ${e.type}`);
    }
    slide.addNotes(page.notes || '');
  }
  await pptx.writeFile({fileName:output});
  const fix = spawnSync(process.env.PYTHON || 'python3',[path.join(__dirname,'fix_cjk_theme.py'),output,font],{encoding:'utf8'});
  if(fix.status !== 0) throw Error(`CJK theme patch failed: ${fix.stderr || fix.error}`);
  console.log(`Wrote ${output} (${scene.slides.length} slides)`);
}
main().catch(error=>{console.error(error.message);process.exitCode=1;});
