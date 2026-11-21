---
name: english-reading-kit
description: Turn an English article, essay, or book chapter into a polished bilingual study kit — paragraph-level translation, CEFR-annotated vocabulary with memory hooks, exam-aligned paraphrase/grammar/writing material, machine-read audio (whole text, section, paragraph, and word level), a book-style HTML reader that works on phones, a spelling test with an auto-collecting wrong-answer notebook, and a distributable zip package. Use when the user provides English prose (URL, file, or pasted text) and asks for 翻译 / 精读 / 生词标注 / 朗读音频 / 中英对照页面 / 学习包, or wants a text turned into KET/PET/IELTS-style study material.
---

# English Reading Kit

Build a complete study kit from one piece of English prose. The output is a small set of HTML pages plus audio, readable on a phone, printable, and aligned to a language exam when one is named.

This skill encodes hard-won layout and pipeline rules. Read the rules before writing any HTML — most of them exist because the naive version looks fine on a desktop and falls apart when someone actually reads it.

## When to use

- User gives a URL / PDF / text and asks for translation, 精读, 生词注解, 朗读, 对照阅读.
- User wants a "学习包", a mobile-readable page, or audio for an article.
- User names an exam (KET / PET / 高考 / IELTS) and wants the text turned into practice material.
- User asks to extend an existing kit (add listening, add dictation, add a wrong-answer book).

Do **not** use for: pure document translation with no study angle, subtitle files, or copyrighted text the user has no right to reproduce at length — in that case summarize and quote sparingly instead of reproducing whole chapters.

## Non-negotiable rules

1. **Translate paragraph-for-paragraph, 1:1.** Every source paragraph gets exactly one translation paragraph. Assert the counts match before generating anything downstream; per-paragraph audio, the reader pairing, and the study flow all depend on it. If counts mismatch, merge or split until they align.
2. **The reader is a book page, not a card wall.** Continuous prose, no per-paragraph cards, no bordered translation blocks, no permanent play-button gutter. Details in `references/layout.md`.
3. **Translation is a footnote, not a second column.** Smaller, muted, directly under its paragraph, no border, no background.
4. **Audio lives at four granularities**: whole text, section, paragraph, word. Paragraph-level clips are what make a reader feel like a reader; word clips are what make vocabulary study stick.
5. **Vocabulary annotation is level-aware.** Tag every entry A2 / B1 / B2 / C1 plus a 熟词僻义 flag. Never annotate everything at one level; the learner needs to know what to skip.
6. **Every generated page must pass the gates** in `references/verify.md` before you report success: tag balance, audio refs exist, JS parses, 390px render, 1:1 pairing, zip integrity.
7. **Never claim audio "sounds right" if you could not listen.** Say what was generated and that pronunciation of invented proper nouns is machine-approximate.

## Pipeline

### 0. Intake
- Fetch the text (web_fetch for URLs) or read the file.
- Record the source URL and rights status in the page footer.
- Note the target exam and the learner level; if unnamed, infer B1 (PET) as the default and say so.

### 1. Extract and normalize
- Strip navigation, footers, ads, and image alt text.
- Fix PDF/OCR damage: ligatures (`ﬁ fl ﬀ` → `fi fl ff`), dropped spaces, `YouKnow-Who` → `You-Know-Who`. Keep a list of corrections; mention them once in the final message.
- Keep paragraph breaks exactly as in the source — they become the pairing unit.

### 2. Segment
Group paragraphs into 10–15 reading units of 200–400 words each, aligned to narrative or argumentative breaks (scene change, new speaker, new topic). Each unit gets an English title and a Chinese subtitle.

### 3. Translate
- One paragraph in, one paragraph out. Same order, same count.
- Translate for comprehension, not word-for-word: keep English word order only when Chinese allows it.
- Leave proper nouns in a consistent transliteration; keep the English in parentheses on first mention if it helps.
- Store translations as plain paragraphs in the same HTML block; do not merge two source paragraphs into one translation.

### 4. Annotate vocabulary
Per unit, 10–20 entries. Card fields, in this order:

| field | notes |
|---|---|
| headword | the surface form as it appears in the text |
| IPA | British IPA; mark stress |
| part of speech | n. / v. / adj. / phrase |
| level | A2 / B1 / B2 / C1 / 熟词僻义 |
| Chinese gloss | primary sense **in this context** first |
| example | a short collocation or the source sentence |
| memory hook | one line: word formation, sound, image, or word-family — not a dictionary definition |

Rules:
- **熟词僻义 is the highest-value tag.** `firm` = company, `nerve` = cheek, `common` = vulgar, `bun` = hair bun, `stroke` = to stroke. Learners misread these far more often than they fail on unknown words.
- **Phrases get their own cards**: `the last person to…`, `think better of it`, `come in handy`, `get a grip on oneself`.
- Memory hooks must be *specific*: “crane = 鹤 → 伸脖子” beats “think of a crane”.

### 5. Align to the exam
Full detail in `references/exam.md`. Minimum for any exam-aligned kit:
- a **paraphrase table** (source word → the wording an exam would use) — this is the single highest-value artifact;
- **grammar points mined from the text itself**, each with the actual sentence;
- **writing frames** lifted from the text plus one or two model answers;
- **listening tasks** in the exam's item types.

### 6. Generate audio
Full detail in `references/audio.md`. On macOS, `say` + `ffmpeg` produce everything without an API key.

```bash
say -v Daniel -r 168 -o out.aiff -f text.txt
ffmpeg -y -loglevel error -i out.aiff -ac 1 -ar 22050 -b:a 64k out.mp3
```

Produce `audio/full.mp3`, `audio/NN.mp3` per unit, `audio/para/NNN.mp3` per paragraph, `audio/words/NNN.mp3` per headword. Use `scripts/make_audio.py` for the batch, then verify every referenced file exists.

### 7. Build the reader
Follow `references/layout.md`. The short version:

- continuous prose, 690px measure, no cards;
- section header = numeral + English title + muted Chinese subtitle + one small “朗读本节” link;
- paragraph hover shows a ghost play button **outside the text column** (hidden below 700px);
- translation as `.zh` footnote: 0.85rem, muted, no border;
- vocabulary collapsed into `<details>本节生词 · N`;
- whole-text player collapsed into one summary line.

### 8. Add practice
`references/practice.md`:
- **spelling test**: mask 60% of letters (first and last always visible), typed answer, per-letter error feedback;
- **wrong-answer notebook**: wrong answers auto-collected into `localStorage`, one card at a time, “答对一次消一格”, export/import for `file://` contexts.

### 9. Package and verify
- `index.html` entry page + `README.txt` + the pages + `audio/` in one folder.
- `zip -r -X … && unzip -t …`.
- Run the gates in `references/verify.md`.
- Report: what was produced, how to open it on a phone, what is machine-generated, and the one or two honest caveats.

## Layout lessons (why the rules exist)

The first iteration put a 30px play-button gutter on every paragraph, a bordered translation block under each, and a card around each section. It looked tidy in a screenshot and was unpleasant to read: 107 paragraphs became 107 little boxes, and the prose never flowed. The fix was not decoration — it was removing structure:

| don't | do |
|---|---|
| card per section | plain headings, whitespace, thin rules |
| 30px control column | absolutely positioned button in the margin |
| bordered/coloured translation block | muted footnote text, no border |
| always-visible word chips | collapsed `<details>` |
| 4-line audio player at top | one summary line, opens on demand |

When in doubt: fewer containers, less chrome, more text.

## Files

| Resource | Use |
|---|---|
| `references/layout.md` | reader/page CSS skeleton, mobile breakpoints, print, tables, what breaks reading |
| `references/audio.md` | TTS recipes, voices, rates, clip granularity, naming, verification |
| `references/exam.md` | CEFR tagging, paraphrase tables, grammar mining, writing frames, listening item types |
| `references/practice.md` | spelling-test algorithm, wrong-answer notebook data model, export/import |
| `references/verify.md` | acceptance gates: tag balance, audio refs, JS syntax, 390px render, packaging |
| `scripts/make_audio.py` | batch TTS from a JSON item list → mp3 |
| `scripts/check_pages.py` | static checks for generated HTML pages |

## Reporting

End with: file list and sizes, what the learner should do first, how to open it on a phone (local server is the reliable path), and any machine-generated limitation. Do not claim the audio was auditioned.
