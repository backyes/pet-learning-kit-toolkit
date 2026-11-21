# Verification gates

Run all of these before reporting success. Each one has caught a real defect at least once.

## Gate 1 — structure

```python
from html.parser import HTMLParser
VOID={'br','img','meta','link','hr','input','source','audio'}
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.st=[]; s.er=[]
    def handle_starttag(s,t,a):
        if t not in VOID: s.st.append(t)
    def handle_endtag(s,t):
        if t in VOID: return
        if s.st and s.st[-1]==t: s.st.pop()
        else: s.er.append(t)
```

`len(err) == 0` and `stack == []`. Missing an `<audio>` from `VOID` produces phantom errors; keep that set accurate.

## Gate 2 — every audio reference resolves

```python
refs = set(re.findall(r'(?:src|data-a|data-src)="(audio/[^"]+)"', html))
missing = [r for r in refs if not os.path.exists(r)]
```

Also check the reverse: files present but unreferenced usually means a naming bug (`01.mp3` vs `1.mp3`).

## Gate 3 — inline JavaScript parses

Extract each `<script>` body, write it to a temp file, run `node --check`. Multi-script pages must be checked one by one — a page with a working first script and a broken second one still renders.

```bash
node --check /tmp/check.js && echo OK
```

## Gate 4 — counts

- paragraphs == translations (per section, not just in total);
- word cards == word clips;
- `<b>` highlight count sane;
- `grep -c` the section count and compare with the plan.

## Gate 5 — renders at 390px

Headless Chrome with `--window-size` does **not** emulate a phone viewport reliably; it may lay out at desktop width and crop. The dependable trick is an iframe:

```html
<body style="margin:0;background:#ddd;padding:12px">
<iframe src="page.html" style="width:390px;height:1500px;border:0"></iframe>
</body>
```

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=old --no-sandbox --disable-gpu --disable-breakpad \
  --disable-crash-reporter --no-first-run --user-data-dir=/tmp/cs \
  --hide-scrollbars --window-size=430,1530 \
  --screenshot=/tmp/shot.png "file://$PWD/wrapper.html"
```

Notes:
- always pass a fresh `--user-data-dir`; without it Chrome fails with “Failed to create headless user data directory”;
- `--headless=new` crashes in sandboxed environments on this platform; `--headless=old` works;
- a `#fragment` in the URL does not scroll the screenshot — to inspect a lower section, build a temporary page containing only that section;
- crop with PIL (`Image.crop`) to inspect a region instead of staring at a 9000px tall image.

## Gate 6 — interaction smoke test

You usually cannot click in headless mode. Compensate:
- re-read the event handlers for the **queue mutation** class of bug (see `practice.md`);
- test pure functions (masking, error diffing) in `node` with hard-coded words;
- seed demo data behind a `?demo=1` query param so the empty-state page can be screenshotted with content.

## Gate 7 — print and narrow widths

- 600px: tables keep their hint and scroll only when >4 columns;
- print preview: player, toolbar, chips, back-to-top hidden.

## Gate 8 — packaging

```bash
zip -q -r -X ../pack.zip folder && unzip -t ../pack.zip | tail -2
```

`-X` strips extra attributes (cleaner across platforms). Verify the file count inside the archive and that `index.html` opens the other pages by relative path.

## Reporting template

```
✓ 4 pages, 369 audio files, zip verified
⚠ audio is machine-generated (say/Daniel); proper nouns may be approximated
→ open index.html, or serve with `python3 -m http.server 8765` for phones
```

State what you did **not** verify. “Rendered at 390px” is verifiable; “sounds natural” is not.
