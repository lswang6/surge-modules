"""Run with python3 test_google_maps_module.py; no network or third-party dependencies."""
from pathlib import Path
import re

text = Path(__file__).with_name('Google-Maps-CN-Offset.sgmodule').read_text()
assert '#!name=Google Maps CN Offset\n' in text
assert set(re.findall(r'^\[(.+)\]$', text, re.M)) == {'URL Rewrite', 'MITM'}
assert not re.search(r'^(ca-p12|ca-passphrase|skip-server-cert-verify)\s*=', text, re.M | re.I)
assert re.search(r'^hostname = %APPEND% www\.google\.com, www\.google\.com\.hk$', text, re.M)

rules = [l.rsplit(' ', 2) for l in text.splitlines() if l and not l.startswith(('#', '[', 'hostname'))]
assert len(rules) == 2 and all(r[2] == '302' for r in rules)

def rewrite(url):
    for pattern, repl, _ in rules:
        if re.match(pattern, url):
            return re.sub(pattern, repl.replace('$', '\\'), url)
    return url

sample = ('https://www.google.com/maps/place/Pullman+Resort+Xishuangbanna/@22.0273267,100.7624247,5260m/'
          'data=!3m1!1e3!4m9!3m8!1s0x312aa4fcf7c5f46d:0x8d704c59a66632dc!5m2!4m1!1i2!8m2!3d22.021833!4d100.763405'
          '!16s%2Fg%2F11mw8jxwxm!5m2!1e1!1e4?entry=ttu&g_ep=EgoyMDI2MTAwNS4wIKXMDSoASAFQAw%3D%3D')
assert rewrite(sample) == sample + '&gl=cn'
assert rewrite('https://www.google.com/maps') == 'https://www.google.com/maps?gl=cn'
assert rewrite('https://www.google.com/maps/@22,100,10z') == 'https://www.google.com/maps/@22,100,10z?gl=cn'
assert rewrite('https://www.google.com.hk/maps?hl=zh') == 'https://www.google.com.hk/maps?hl=zh&gl=cn'
for done in (sample + '&gl=cn', 'https://www.google.com/maps?gl=cn&hl=en', 'https://www.google.com/maps?hl=en&gl=cn&x=1'):
    assert rewrite(done) == done, done  # idempotent: no redirect loop
for other in ('https://www.google.com/search?q=maps', 'https://www.google.com/mapsx', 'https://maps.google.com/'):
    assert rewrite(other) == other, other
print('OK: metadata, 2 rewrites, append/idempotent/non-maps cases')
