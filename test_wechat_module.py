"""Check the no-decryption boundary: python3 test_wechat_module.py."""
from pathlib import Path
import re

text = Path(__file__).with_name('WeChat-Ads-Privacy.sgmodule').read_text()
metadata = re.findall(r'^#!([^=\n]+)=(.+)$', text, re.M)
assert len(metadata) == len(dict(metadata)) == 4
assert set(dict(metadata)) == {'name', 'desc', 'author', 'homepage'}
assert dict(metadata)['name'] == 'WeChat Ads Privacy'
assert dict(metadata)['homepage'] == 'https://github.com/lswang6/surge-modules'
assert '13 条精确域名规则' in dict(metadata)['desc']
assert '# SPDX-License-Identifier: GPL-3.0-only' in text
lines = [line.strip() for line in text.splitlines() if line.strip()]
assert [line for line in lines if line.startswith('[')] == ['[Rule]']
rules = [line for line in lines if not line.startswith(('#', '['))]
assert len(rules) == len(set(rules)) == 13
assert all(re.fullmatch(r'DOMAIN,[a-z0-9.-]+,REJECT', line) for line in rules)
blocked = {line.split(',')[1] for line in rules}
assert blocked == {
    'wxsnsdy.wxs.qq.com', 'wxsmsdy.video.qq.com', 'wxsnsdythumb.wxs.qq.com',
    'ads-shopping.shouqianba.com', 'ad.maoyan.com', 'e.jparking.cn',
    'dsp.fcbox.com', 'ads.ishansong.com', 'smarket.dian.so',
    'ads.zhinengxiyifang.cn', 'ad-api.4pyun.com',
    'ad-files.4pyun.com', 'ad.duoduo.link',
}
for host in ('mp.weixin.qq.com', 'wxs.qq.com', 'res.wx.qq.com', 'weixin.qq.com',
             'wx.qq.com', 'wx.tenpay.com', 'mch.weixin.qq.com', 'servicewechat.com',
             'qpic.cn', 'qlogo.cn', 'video.qq.com', 'saas-ad.cloudpnr.com',
             'api.shouqianba.com', 'wx.maoyan.com', 'webchatapp.fcbox.com',
             'miniprogram.ishansong.com', 'mapi.xiaotucc.com', 'file.dian.so',
             'ad.xiaotucc.com', 'psbg.jparking.cn', 'csg.jparking.cn',
             'cw.jparking.cn', 'etgw.jparking.cn', 'sytgate.jslife.com.cn',
             'api-c-prod.etcp.cn', 'ife.etcp.cn', 'static.etcp.cn',
             'et.ykccn.com', 'gw3.ykccn.com', 'web-stable-cdn.ykccn.com',
             'papi.4pyun.com', 'api.4pyun.com', 'auth.4pyun.com',
             'app.4pyun.com', 'qr.4pyun.com',
             'zhinengxiyifang.cn', '4pyun.com', 'jparking.cn', 'etcp.cn',
             'ykccn.com', 'duoduo.link', 'sub.ad.duoduo.link',
             'api-marketing.zhinengxiyifang.cn', 'adsoss.zhinengxiyifang.cn'):
    assert host not in blocked, host
print('OK: 13 exact blocks, unique metadata, protected business hosts; no MITM, scripts, rewrites, remote rule sets, DNS changes or broad rules')
