#!/usr/bin/env python3
"""mdlinks: offline Markdown link checker (relative files and #anchors). Stdlib only."""
import os, re, sys, argparse

LINK = re.compile(r'(?<!\!)\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)|!\[[^\]]*\]\(\s*<?([^)\s>]+)>?[^)]*\)')
HEAD = re.compile(r'^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$')
FENCE = re.compile(r'^\s*(```|~~~)')

def slug(text):
    text = re.sub(r'`|\*|_|\[|\]|\([^)]*\)', lambda m: '' if m.group(0) in '`*_[]' else '', text)
    text = text.strip().lower()
    text = re.sub(r'[^\w\- ]', '', text)
    return text.replace(' ', '-')

def scan(path):
    """Return (anchors, links[(line, target)])."""
    anchors, links, seen, fence = set(), [], {}, False
    with open(path, encoding='utf-8', errors='replace') as f:
        for n, line in enumerate(f, 1):
            if FENCE.match(line):
                fence = not fence
                continue
            if fence:
                continue
            m = HEAD.match(line)
            if m:
                s = slug(m.group(2))
                k = seen.get(s, 0)
                seen[s] = k + 1
                anchors.add(s if k == 0 else f'{s}-{k}')
            for a in re.findall(r'<a\s+[^>]*(?:name|id)="([^"]+)"', line):
                anchors.add(a)
            clean = re.sub(r'`[^`]*`', '', line)
            for m in LINK.finditer(clean):
                links.append((n, m.group(1) or m.group(2)))
    return anchors, links

def check(files):
    cache, problems = {}, []
    def info(p):
        if p not in cache:
            cache[p] = scan(p)
        return cache[p]
    for f in files:
        _, links = info(f)
        for n, t in links:
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', t) or t.startswith('//'):
                continue
            target, _, frag = t.partition('#')
            if target:
                p = os.path.normpath(os.path.join(os.path.dirname(f), target.split('?')[0]))
                if not os.path.exists(p):
                    problems.append((f, n, t, 'file not found'))
                    continue
            else:
                p = f
            if frag and p.lower().endswith(('.md', '.markdown')) and os.path.isfile(p):
                if frag.lower() not in info(p)[0]:
                    problems.append((f, n, t, 'anchor not found'))
    return problems

def collect(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for r, ds, fs in os.walk(p):
                ds[:] = [d for d in ds if not d.startswith('.') and d != 'node_modules']
                out += [os.path.join(r, x) for x in sorted(fs) if x.lower().endswith(('.md', '.markdown'))]
        else:
            out.append(p)
    return out

def main(argv=None):
    ap = argparse.ArgumentParser(description='Check relative links and anchors in Markdown files.')
    ap.add_argument('paths', nargs='*', default=['.'])
    a = ap.parse_args(argv)
    probs = check(collect(a.paths))
    for f, n, t, why in probs:
        print(f'{f}:{n}: {t}: {why}')
    print(f'{len(probs)} broken link(s)')
    return 1 if probs else 0

if __name__ == '__main__':
    sys.exit(main())
