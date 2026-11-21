#!/usr/bin/env python3
"""Static checks for generated reading-kit pages.

Checks per file:
  1. HTML tag balance
  2. every audio/[^\"]+ reference exists on disk
  3. every same-page #anchor has a matching id
  4. each inline <script> parses (via `node --check`, skipped when node is absent)

Usage:
  python3 check_pages.py *.html
  python3 check_pages.py --root . harry-potter-ch1-reader.html
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser

VOID = {"br", "img", "meta", "link", "hr", "input", "source", "audio", "track", "embed", "area", "base", "col", "param", "wbr"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"stray </{tag}> at {self.getpos()}")
            return
        if self.stack[-1][0] == tag:
            self.stack.pop()
            return
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                self.errors.append(
                    f"</{tag}> at {self.getpos()} closes while "
                    f"{[t for t, _ in self.stack[i + 1:]]} still open")
                del self.stack[i:]
                break
        else:
            self.errors.append(f"stray </{tag}> at {self.getpos()}")


def check_js(scripts, label):
    if not shutil.which("node"):
        return [f"{label}: node not found, JS check skipped"]
    problems = []
    for i, js in enumerate(scripts, 1):
        if not js.strip():
            continue
        fd, path = tempfile.mkstemp(suffix=".js")
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write(js)
        r = subprocess.run(["node", "--check", path], capture_output=True, text=True)
        os.unlink(path)
        if r.returncode != 0:
            problems.append(f"{label}: script #{i} syntax error\n{r.stderr.strip()}")
    return problems


def check(path, root):
    src = open(path, encoding="utf-8").read()
    problems = []

    p = Balance()
    p.feed(src)
    problems += [f"{path}: {e}" for e in p.errors]
    if p.stack:
        problems.append(f"{path}: unclosed at EOF {[t for t, _ in p.stack][:6]}")

    refs = set(re.findall(r'(?:src|data-a|data-src|href)="(audio/[^"#?]+)"', src))
    # paths assembled at runtime ("audio/words/'+i+'") are not static and cannot be checked here
    refs = {r for r in refs if not any(c in r for c in "'+`$")}
    for r in sorted(refs):
        if not os.path.exists(os.path.join(root, r)):
            problems.append(f"{path}: missing file {r}")

    ids = set(re.findall(r'id="([^"]+)"', src))
    for anchor in set(re.findall(r'href="#([^"]+)"', src)):
        if not anchor:
            continue
        if anchor not in ids and not anchor.startswith("!"):
            problems.append(f"{path}: anchor #{anchor} has no target")

    scripts = re.findall(r"<script[^>]*>(.*?)</script>", src, re.S)
    problems += check_js(scripts, path)

    return problems, len(refs), len(scripts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--root", default=".", help="directory that audio paths are relative to")
    args = ap.parse_args()

    bad = 0
    for f in args.files:
        if not os.path.exists(f):
            print(f"!! {f}: not found")
            bad += 1
            continue
        problems, nrefs, nscripts = check(f, args.root)
        if problems:
            bad += 1
            print(f"✗ {f}  ({len(problems)} problem(s), {nrefs} audio refs, {nscripts} scripts)")
            for x in problems[:20]:
                print("   -", x)
        else:
            print(f"✓ {f}  {nrefs} audio refs, {nscripts} scripts")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
