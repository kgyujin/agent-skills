# Scene JSON format

Portable helpers consume UTF-8 JSON; no network calls or package installation occur. Resolve `pptxgenjs` through normal Node resolution (local `node_modules` or caller-provided `NODE_PATH`). `PYTHON` selects the Python interpreter used for the standard-library CJK ZIP patch. Preview additionally requires ReportLab, Pillow and PyMuPDF. Fonts are referenced in PPTX, not embedded.

Canvas is **1280 × 720 px at 96 dpi** (13.333 × 7.5 inches). Element `fontSize` is px and converts to 0.75 pt. Other canvas sizes are rejected. Coordinates start at the top left. Colors are six hex digits without `#`.

Root: `width`, `height`, `font` (default Pretendard), optional `meta` (`title`, `author`, `subject`), optional `theme` (`background`, `text`, `muted`, `accent`, `line`), and `slides` array. Each slide has `title`, optional `section`, `notes` string, `frame` (false hides all standard framing), and `elements`. The default frame uses a section at y30, title at y79 and page count at y676. Keep body elements below y211 and above y648.

Elements:

- `text`: `x,y,w,h,text,fontSize,bold,color,align` (left/center/right). Plain text with explicit newlines; complex rich text is unsupported. PPTX-only `options` may pass PptxGenJS text options, but companion preview does not interpret them.
- `rect`, `ellipse`: `x,y,w,h,fill,stroke,strokeWidth`.
- `line`: `points:[[x,y],...]`, optional `startArrow,endArrow,stroke,strokeWidth`. Every segment must be horizontal or vertical, including reverse directions. Alternatively use `x,y,w,h` for one orthogonal segment.
- `image`: `x,y,w,h,path`. Resource path is relative to scene JSON. Contain placement preserves aspect ratio and centers the image. Use PNG/JPEG for companion compatibility.
- `table`: `x,y,w,h,fontSize,rows`. Rows are a rectangular array of plain strings. Default style has horizontal rules only, blue bold headers, bold row labels and vertically centered text. Optional `colWidths` is an array of positive pixel widths summing to `w`; `highlightColumn` is a zero-based accent column; `banded` enables alternate pale rows with optional `bandColor`. No spans or rich cells. For hierarchical V9 comparisons use `templates/v9-comparison.json` editable text/shapes instead of a dense cell grid.
- `barChart`: `x,y,w,h,series:[{name,labels:[...],values:[...]}]`, optional `colors:[hex,...]`. Native PowerPoint bar chart; preview supports nonnegative values only and renders an approximate column chart. No axis or legend parity guarantee.

Unknown types, gradients and diagonal line segments are rejected by builders. Use a dedicated authoring tool for unsupported structures rather than silently flattening them. Audit warnings require review and are not aesthetic scores. Bounds checks do not measure glyph clipping, overlap or real-app font substitution.

```sh
node scripts/build_deck.cjs assets/example-deck.json output.pptx
python3 scripts/audit_deck.py assets/example-deck.json output.pptx
python3 scripts/preview_scene.py assets/example-deck.json preview.pdf --font-regular /path/to/regular.ttf --font-bold /path/to/bold.ttf
```

Preview creates a PDF, a sibling `<name>-renders/slide-NN.png` set at 1920×1080 and `contact-sheet.png`. It is a **companion renderer**, not an export of the PPTX. Real PowerPoint/Keynote/LibreOffice output must be checked separately when available.
