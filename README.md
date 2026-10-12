# mdlinks

Install: `pip install mdlinks-cli` (command: `mdlinks`)

Offline Markdown link checker: verifies relative file links and `#anchor` links (GitHub-style slugs). Ignores code spans/fences and external URLs. Zero dependencies.

```
python3 mdlinks.py [paths...]     # default: current dir; exit 1 if broken links
```
Output: `docs/a.md:12: ../b.md#intro: anchor not found`

Tests: `python3 tests/test_mdlinks.py`

## Donate
If it saved you time: PayPal 4433@vp.pl

Donate: https://paypal.me/RafalBaranowski
