#!/usr/bin/env python3
"""Batch text-to-speech for an English reading kit (macOS `say` + ffmpeg).

Inputs
  --json items.json   [{"id":"001","text":"..."} ...]  or  {"001":"..."}
  --text chapter.txt  plain text; items are separated by blank lines

Output
  <out-dir>/<prefix><id>.mp3, one per item, zero-padded ids preserved.

Examples
  python3 make_audio.py --text chapter.txt --out-dir audio/para --prefix "" --pad 0
  python3 make_audio.py --json words.json --out-dir audio/words --rate 150 --pad 120
  python3 make_audio.py --json paras.json --out-dir audio/para --concat audio/full.mp3
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


def load_items(args):
    if args.json:
        data = json.load(open(args.json, encoding="utf-8"))
        if isinstance(data, dict):
            return [(str(k), v) for k, v in data.items()]
        return [(str(d.get("id", i + 1)), d["text"]) for i, d in enumerate(data)]
    if args.text:
        raw = open(args.text, encoding="utf-8").read()
        chunks = [c.strip() for c in re.split(r"\n\s*\n", raw) if c.strip()]
        width = max(3, len(str(len(chunks))))
        return [(str(i + 1).zfill(width), c) for i, c in enumerate(chunks)]
    sys.exit("need --json or --text")


def synth(text, out_aiff, voice, rate):
    fd, tf = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    try:
        with open(tf, "w", encoding="utf-8") as f:
            f.write(text)
        subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", out_aiff, "-f", tf], check=True)
    finally:
        os.unlink(tf)


def to_mp3(aiff, mp3, bitrate, pad_ms):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", aiff]
    if pad_ms:
        cmd += ["-af", f"adelay={pad_ms}|{pad_ms}"]
    cmd += ["-ac", "1", "-ar", "22050", "-b:a", bitrate, mp3]
    subprocess.run(cmd, check=True)


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True).stdout.strip()
    return float(out) if out else 0.0


def mmss(seconds):
    s = int(round(seconds))
    return f"{s // 60}:{s % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--text")
    ap.add_argument("--out-dir", default="audio")
    ap.add_argument("--prefix", default="")
    ap.add_argument("--voice", default="Daniel")
    ap.add_argument("--rate", type=int, default=168)
    ap.add_argument("--bitrate", default="64k")
    ap.add_argument("--pad", type=int, default=0, help="leading silence in ms (short clips)")
    ap.add_argument("--concat", help="also build one continuous mp3 from the clips")
    args = ap.parse_args()

    if not shutil.which("say") or not shutil.which("ffmpeg"):
        sys.exit("macOS `say` and `ffmpeg` are required")

    items = load_items(args)
    os.makedirs(args.out_dir, exist_ok=True)
    tmpdir = tempfile.mkdtemp(prefix="tts-")
    made, total = [], 0.0

    try:
        for i, (item_id, text) in enumerate(items, 1):
            aiff = os.path.join(tmpdir, f"{item_id}.aiff")
            mp3 = os.path.join(args.out_dir, f"{args.prefix}{item_id}.mp3")
            synth(text, aiff, args.voice, args.rate)
            to_mp3(aiff, mp3, args.bitrate, args.pad)
            d = duration(mp3)
            total += d
            made.append(mp3)
            print(f"[{i}/{len(items)}] {os.path.basename(mp3)}  {mmss(d)}  {os.path.getsize(mp3)//1024} KB",
                  flush=True)

        if args.concat:
            lst = os.path.join(tmpdir, "list.txt")
            with open(lst, "w", encoding="utf-8") as f:
                for m in made:
                    f.write("file '%s'\n" % os.path.abspath(m))
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                 "-i", lst, "-ac", "1", "-ar", "22050", "-b:a", args.bitrate, args.concat],
                check=True)
            print(f"concat → {args.concat}  {mmss(duration(args.concat))}")

        print(f"done: {len(made)} clips, total {mmss(total)}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
