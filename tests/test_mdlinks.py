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

import pytest

def test_images_and_titles(tmp_path):
    (tmp_path/'i.png').write_bytes(b'x')
    a = mk(str(tmp_path), 'a.md', '![alt](i.png) ![b](gone.png "t") [t](i.png "title")\n')
    r = mdlinks.check([a])
    assert [x[2] for x in r] == ['gone.png']

def test_angle_brackets_and_query(tmp_path):
    mk(str(tmp_path), 'b.md', '# B\n')
    a = mk(str(tmp_path), 'a.md', '[x](<b.md>) [y](b.md?raw=1) [z](b.md#b)\n')
    assert mdlinks.check([a]) == []

def test_external_schemes_ignored(tmp_path):
    a = mk(str(tmp_path), 'a.md', '[m](mailto:a@b.c) [h](http://x/y) [p](//cdn/x) [f](ftp://z)\n')
    assert mdlinks.check([a]) == []

def test_html_anchor_and_case(tmp_path):
    a = mk(str(tmp_path), 'a.md', '<a name="top"></a>\n# Big Title\n[x](#top) [y](#BIG-title)\n')
    assert mdlinks.check([a]) == []

def test_slug_punctuation():
    assert mdlinks.slug('What is this? (really)') == 'what-is-this'
    assert mdlinks.slug('**Bold** and _it_') == 'bold-and-it'

def test_tilde_fence_ignored(tmp_path):
    a = mk(str(tmp_path), 'a.md', '~~~\n[x](bad.md)\n~~~\n')
    assert mdlinks.check([a]) == []

def test_non_md_fragment_not_checked(tmp_path):
    mk(str(tmp_path), 'c.txt', 'hi')
    a = mk(str(tmp_path), 'a.md', '[x](c.txt#L5)\n')
    assert mdlinks.check([a]) == []

def test_subdir_relative(tmp_path):
    (tmp_path/'sub').mkdir()
    mk(str(tmp_path), 'top.md', '# Top\n')
    a = mk(str(tmp_path/'sub'), 'a.md', '[x](../top.md#top) [y](../nope.md)\n')
    assert [x[3] for x in mdlinks.check([a])] == ['file not found']

def test_collect_skips_hidden_and_node_modules(tmp_path):
    for d in ('.git', 'node_modules', 'docs'):
        (tmp_path/d).mkdir()
        mk(str(tmp_path/d), 'x.md', '# x\n')
    got = mdlinks.collect([str(tmp_path)])
    assert [os.path.basename(os.path.dirname(g)) for g in got] == ['docs']

def test_main_exit_codes(tmp_path, capsys):
    good = mk(str(tmp_path), 'g.md', '# G\n[x](#g)\n')
    bad = mk(str(tmp_path), 'b.md', '[x](nope.md)\n')
    assert mdlinks.main([good]) == 0
    assert mdlinks.main([bad]) == 1
    out = capsys.readouterr().out
    assert 'b.md:1: nope.md: file not found' in out and '1 broken link(s)' in out

def test_missing_input_file(tmp_path):
    assert mdlinks.main([str(tmp_path/'absent.md')]) == 2

def test_binary_garbage_tolerated(tmp_path):
    p = tmp_path/'g.md'; p.write_bytes(b'\xff\xfe[x](nope.md)\n')
    assert mdlinks.main([str(p)]) == 1

if __name__ == '__main__':
    for k, v in list(globals().items()):
        if k.startswith('test_'): v(); print('ok', k)
