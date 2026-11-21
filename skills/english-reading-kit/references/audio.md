# Audio: producing a full reading kit with macOS `say`

No API key needed. `say` renders text to AIFF; `ffmpeg` converts to mp3. A 4,500-word chapter takes roughly 5 minutes to synthesise on an M-series Mac.

## Command shape

```bash
say -v Daniel -r 168 -o /tmp/t.aiff -f /tmp/t.txt
ffmpeg -y -loglevel error -i /tmp/t.aiff -ac 1 -ar 22050 -b:a 64k /tmp/t.mp3
```

- `-f file` avoids shell-quoting problems with apostrophes and quotes. Always write the text to a UTF-8 file first.
- `-r` is words per minute. `168` yields ≈185 effective wpm because of punctuation pauses — close to a PET listening pace.
- 64 kbps mono 22.05 kHz is ≈0.5 MB/min and fine for speech.

## Voices

| Voice | Locale | Use |
|---|---|---|
| `Daniel` | en-GB (male) | default for British exams (KET/PET/IELTS) |
| `Flo`, `Kate`, `Serena` | en-GB (female) | accent variety on a second pass |
| `Samantha`, `Alex` | en-US | comparison listening |

macOS `say -v '?'` lists what is installed. `say -x` (phoneme dump) is **not** available on the current build; do not rely on it to check pronunciation.

## Four clip granularities

| Level | Path | Purpose |
|---|---|---|
| whole text | `audio/full.mp3` | commute / bedtime listening, scrubbing |
| section | `audio/01.mp3 … NN.mp3` | one sitting = one clip |
| paragraph | `audio/para/001.mp3 …` | tap a paragraph, hear that paragraph |
| word | `audio/words/001.mp3 …` | vocabulary study, spelling test, dictation |

Section and full clips can be assembled from paragraph clips with the ffmpeg concat demuxer, which also guarantees the durations add up:

```bash
# list.txt
file '/abs/path/001.aiff'
file '/abs/path/002.aiff'
ffmpeg -y -f concat -safe 0 -i list.txt -ac 1 -ar 22050 -b:a 64k full.mp3
```

## Text preparation before synthesis

```python
t = re.sub(r'<[^>]+>', ' ', html_block)   # strip markup
t = html.unescape(t)
t = t.replace('\u2014', ', ')             # em dash → pause, not "dash"
t = t.replace('\u2013', ', ')
t = t.replace('\u201c','"').replace('\u201d','"')
t = t.replace('\u2018',"'").replace('\u2019',"'")
t = re.sub(r'\s+', ' ', t).strip()
```

- Keep `Mr.` / `Mrs.` / `Dr.` — `say` reads them as Mister / Missus / Doctor.
- Single words: append a period so the pitch falls (`"firm."`), and add 100 ms of silence so no device clips the onset:
  `ffmpeg -af "adelay=120|120"`.
- Do **not** respell invented names speculatively. Instead publish a small pronunciation table (IPA) next to the audio and state that proper nouns are machine-read.

## Naming and lookup

Use zero-padded, order-based names: `para/007.mp3`, `words/123.mp3`. The page stores the path in the element (`data-a`, `data-src`), so renaming later is a sed away.

A common bug: files written as `audio/1.mp3` while the page references `audio/01.mp3`. Assert both directions before shipping:

```python
refs = set(re.findall(r'(?:src|data-a|data-src)="(audio/[^"]+)"', html))
missing = [r for r in refs if not os.path.exists(r)]
```

## Durations

Read them back with ffprobe and inject into the UI labels:

```python
d = float(subprocess.run(
    ['ffprobe','-v','error','-show_entries','format=duration',
     '-of','default=nw=1:nk=1', mp3], capture_output=True, text=True).stdout)
label = f"{int(d)//60}:{int(d)%60:02d}"
```

Never hand-write durations.

## Playback in the page

- `<audio preload="metadata">` so the duration shows without downloading everything.
- Speed control is free: `audio.playbackRate = 0.75 | 1 | 1.25`. Do not render extra slow files.
- Always swallow the autoplay rejection: `var p = a.play(); if (p && p.catch) p.catch(function(){});`
- Pause every other player before starting a new one; on mobile only one audio element should be live.
- Sequential section playback: play clip *n*, on `ended` wait ~260 ms, then *n+1*; scroll the active paragraph into view with `block:'center'`.

## Quality claims

You cannot hear the output. Say: “generated with macOS `say` (Daniel, en-GB)”, give counts and total duration, and add a one-line caveat that invented proper nouns may be approximated. Never say the audio was checked by ear.
