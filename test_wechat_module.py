"""Check the no-decryption boundary: python3 test_wechat_module.py."""
from pathlib import Path
import re

text = Path(__file__).with_name('WeChat-Ads-Privacy.sgmodule').read_text()
assert '#!name=WeChat Ads Privacy\n' in text
assert re.search(r'^#!desc=.+$', text, re.M)
assert re.findall(r'^\[([^\]]+)\]$', text, re.M) == ['Rule']
rules = [line for line in text.splitlines() if line.strip() and not line.startswith(('#', '['))]
assert len(rules) == len(set(rules)) == 10
assert all(re.fullmatch(r'DOMAIN,[a-z0-9.-]+,REJECT', line) for line in rules)
blocked = {line.split(',')[1] for line in rules}
assert {'wxsnsdy.wxs.qq.com', 'wxsmsdy.video.qq.com', 'wxsnsdythumb.wxs.qq.com'} <= blocked
for host in ('mp.weixin.qq.com', 'wxs.qq.com', 'res.wx.qq.com', 'weixin.qq.com',
             'wx.qq.com', 'wx.tenpay.com', 'mch.weixin.qq.com', 'servicewechat.com',
             'qpic.cn', 'qlogo.cn', 'video.qq.com', 'saas-ad.cloudpnr.com',
             'api.shouqianba.com', 'wx.maoyan.com', 'webchatapp.fcbox.com',
             'miniprogram.ishansong.com', 'mapi.xiaotucc.com', 'file.dian.so'):
    assert host not in blocked, host
print('OK: ten exact blocks; no MITM, scripts, rewrites, DNS changes or broad suffix rules')
