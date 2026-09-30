"""Run with python3 test_module.py; no network or third-party dependencies."""
from pathlib import Path
import fnmatch
import re

text = Path(__file__).with_name('AdvertisingLite-Privacy.sgmodule').read_text()
assert '#!name=AdvertisingLite Privacy\n' in text
assert re.search(r'^#!desc=.+$', text, re.M)
assert set(re.findall(r'^\[(.+)\]$', text, re.M)) == {'General', 'Rule', 'URL Rewrite', 'Map Local', 'MITM'}
assert not re.search(r'^(ca-p12|ca-passphrase|skip-server-cert-verify|http-api|external-controller-access)\s*=', text, re.M | re.I)
hosts = [h.strip() for h in re.search(r'^hostname = %INSERT% (.+)$', text, re.M)[1].split(',')]
assert len(hosts) == len(set(hosts))
negative = [h for h in hosts if h.startswith('-')]
positive = [h for h in hosts if not h.startswith('-')]
assert len(negative) == 193 and len(positive) == 710
assert hosts == negative + positive
assert not {h[1:] for h in negative} & set(positive)

def decrypts(host):
    for pattern in hosts:
        if fnmatch.fnmatchcase(host.lower(), pattern.lstrip('-').lower()):
            return not pattern.startswith('-')
    return False

for host in ('openapi.boc.cn', 'mp.weixin.qq.com', 'client.mail.163.com', 'geetest.htsc.com', 'mbank5.jsbchina.cn', 'api.futunn.com', 'api1.futunn.com', 'legy.line-apps.com', 'home.mi.com'):
    assert not decrypts(host), host
for host in ('api.caiyunapp.com', 'image.spdbccc.com.cn', 'images.cib.com.cn', 'www.baidu.com'):
    assert decrypts(host), host
blocked = re.findall(r'^DOMAIN,([^,]+),REJECT$', text, re.M)
assert len(blocked) == len(set(blocked)) == 78
assert {'adv.ccb.com', 'pagead2.googlesyndication.com', 'pubads.g.doubleclick.net', 'goblin.hupu.com'} <= set(blocked)
assert all(not decrypts(host) for host in blocked)
assert re.search(r'^\[URL Rewrite\]\n', text, re.M)
assert 'image\\.spdbccc\\.com\\.cn' in text and 'api\\.caiyunapp\\.com' in text
print('OK: metadata, 193 exclusions, 710 retained MITM patterns, 78 domain blocks, and privacy regressions')
