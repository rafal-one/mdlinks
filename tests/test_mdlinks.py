import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import mdlinks

def mk(d, name, text):
    p = os.path.join(d, name)
    with open(p, 'w') as f: f.write(text)
    return p

def test_slug():
    assert mdlinks.slug('Hello, World `x`!') == 'hello-world-x'

def test_ok_and_broken():
    with tempfile.TemporaryDirectory() as d:
        mk(d, 'b.md', '# Title\n## Sub Part\n')
        a = mk(d, 'a.md', '[x](b.md) [y](b.md#sub-part) [z](#me)\n# Me\n[w](https://e.com)\n')
        assert mdlinks.check([a]) == []
        c = mk(d, 'c.md', '[x](nope.md) [y](b.md#zzz) `[q](bad.md)`\n```\n[f](bad.md)\n```\n')
        r = mdlinks.check([c])
        assert [x[3] for x in r] == ['file not found', 'anchor not found']

def test_duplicate_headings():
    with tempfile.TemporaryDirectory() as d:
        a = mk(d, 'a.md', '# A\n# A\n[x](#a-1)\n')
        assert mdlinks.check([a]) == []

if __name__ == '__main__':
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); print('ok', k)
