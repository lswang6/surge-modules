#!/usr/bin/env python3
"""Rebuild the reviewed module from the unchanged baseline and pinned raw snapshot.
SPDX-License-Identifier: GPL-2.0-only
Upstream: blackmatrix7; modified by lswang6 on 2026-09-30.
Run: python3 build_advertising_allinone.py (includes boundary regression checks).
"""
import argparse
import fnmatch
import hashlib
import json
from collections import Counter
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
BASE_SHA = '3ea67a6551efe9a364984d213a47106df911985f72345f31f6a93b489c7ef53f'
SOURCE_SHA = '66a8282facc2c339363bdf924b0a65eeaf11b57acf4b5839538044303a2d388d'
PIN = 'a75313d36b049b8aca5b26beffafb1b0ec8c564d'
# Explicit source-line decisions, not keyword-based mass deletion.
DROP_GROUPS = {
    'Oray STARTUP 由收窄且有边界的基线901覆盖；删除无边界重复项，避免绕过新边界': [902],
    '广告专用性不足，保守移除；不表示已确认业务故障': [115,224,450],
    '版本、升级或补丁检查，非广告': [175,190,214,230,325,422,508,581,608,744,826,840,860,868,873,877,929,991,1014,1079,1103,1129,1209,1241,1246],
    '通知、消息或已读状态，非广告': [232,234,323,386,419,473,656,662,672,843,899,1016,1017,1086,1136,1140,1219,1260],
    '账户、登录、退出、用户资料、鉴权或安全状态，非广告': [463,484,607,647,671,750,843,957,982,1104,1325],
    '商品、订单、会员权益或账户列表，非广告': [465,559,592,605,610,646,648,657,658,745,746,747,762,763,792,1251,1252],
    '搜索、内容列表、用户任务或正常业务入口，非广告': [122,194,195,242,288,303,304,308,331,333,391,402,414,439,455,513,550,560,571,588,589,591,593,596,597,600,603,614,615,616,623,625,626,627,628,636,641,645,653,673,677,678,702,709,736,757,759,767,773,810,811,815,820,854,856,878,911,928,931,951,955,999,1024,1025,1049,1076,1080,1084,1085,1091,1116,1131,1157,1190,1214,1218,1221,1249,1272,1289,1322,1323,1332,1333],
    '整个服务或业务根路径，不能仅阻断广告；具体广告子路径另有保留': [114,141,395,905,1107],
}
# Keep advertising alternatives; remove unrelated alternatives in the same pattern.
NARROW = {
    132: (r'^https?://(mobile|shop)\.laichon\.com/api/(exposureAdvStatistics|getWebAdvList)(?:[/?]|$)', '删除 goodsList 商品列表分支'),
    168: (r'^https?://api\-cfg\.wtzw\.com/v1/adv(?:[/?]|$)', '删除 reward/operation 非明确广告分支'),
    220: (r'^https?://api\.wfdata\.club/v2/yesfeng/infoCenterAd(?:[/?]|$)', '删除 yesList 内容列表分支'),
    326: (r'^https?://foodie-api\.yiruikecorp\.com/v\d/banner/overview', '删除 notice 通知分支，保留既有 banner'),
    349: (r'^https?://helper\.2bulu\.com/(saveSplashFrequencyStatistics|getSplash)(?:[/?]|$)', '仅保留既有开屏及其统计，删除任务、内容和通用入口分支'),
    372: (r'^https?://interface(\d)?\.music\.163\.com/eapi/ad(?:[/?]|$)', '仅保留 ad 路径，删除 abtest/sp/hot/store/search 业务分支并加边界'),
    379: (r'^https?://iphone\.ac\.qq\.com/.*/Support/bootScreen', '删除 getSystemConf 通用配置分支'),
    393: (r'^https?://list-app-m\.i4\.cn/(adclickcb|getopfstadinfo)\.xhtml', '删除 getHotSearchList 搜索分支'),
    398: (r'^https?://m\.client\.10010\.com/mobileService/(activity|customer)/(get_client_adv|get_startadv)', '删除 accountListData 账户分支'),
    475: (r'^https?://r\.inews\.qq\.com/(adsBlacklist|getBannerAds|getFullScreenPic)(?:[/?]|$)', '删除远程配置、热搜、定位上报分支，保留广告和开屏'),
    476: (r'^https?://r\.inews\.qq\.com/getSplash(?:[/?]|$)', '删除远程配置、热搜和定位上报；getBannerAds 由基线475保留，仅保留 getSplash 避免重复'),
    481: (r'^https?://res\.xiaojukeji\.com/resapi/activity/get(Ruled|Preload)', '删除 PasMultiNotices 通知分支'),
    624: (r'^https://cn-app\.narwaltech\.com/operate/appPosition/listSplash', '删除设备提示和一般活动列表，保留开屏'),
    870: (r'^https?://capi\.lkcoffee\.com/resource/m/sys/app/adposNew', '删除 homePage/contactor/modules 正常首页模块'),
    901: (r'^https?://client-api-v2\.oray\.com/materials/SLCC_IOS_STARTUP(?:[/?]|$)', '仅保留开屏并加边界；删除 DEVICE 业务分支，PROMOTION 由基线903保留原响应'),
    903: (r'^https?://client-api-v2\.oray\.com/materials/SUNLOGIN_CLIENT_IOS_PROMOTION(?:[/?]|$)', 'PROMOTION 加路径边界，保留原 blank_dict.json 动作；避免基线901不同响应覆盖'),
    977: (r'^https?://games\.mobileapi\.hupu\.com/.+?/interfaceAdMonitor/(hotkey|init|hupuBbsPm)\.', '删除 search/status/hupuBbsPm 非广告服务分支'),
    1009: (r'^https?://home\.mi\.com/cgi-op/api/v\d/recommendation/(banner|openingBanner)', '删除 myTab 业务入口'),
    1061: (r'^https?://lens\.leoao\.com/lens/.+(queryAppBanners|Advert|popup)', '删除 getUserScheme 用户方案分支'),
    1208: (r'^https?://sdk\.alibaba\.com\.ailbaba\.me/[^/?]+/v\d/advert\?position=[^2]+', '删除 version/top_notice，保留既有广告分支并限制路径不跨 query'),
    1223: (r'^https?://spclient\.wg\.spotify\.com/(?:ad-logic|ads)(?:[/?]|$)', '仅保留确定广告路径且加边界；排除 canvases/cards/enabled-tracks/crashlytics/banners 及任意后缀匹配'),
    1270: (r'^https?://wmapi\.meituan\.com/api/v\d/(openscreen\?ad|startpicture)', '删除包含正常业务响应的 loadInfo 分支'),
    1294: (r'^https?://www\.xiaohongshu\.com/api/sns/v\d/ads/resource', '删除 hey_gallery 正常业务分支'),
}
# Only three uncovered, specific-host advertising endpoints pass the review.
ADD = {
    187: (r'^https://mxsa\.mxbc\.net/api/v1/adinfo/adplace/query(?:[/?]|$)', '蜜雪广告位查询；已有 limitedAds 不覆盖此路径'),
    197: (r'^https://res\.kfc\.com\.cn/CRM/kfcad/custom_v2/wxapp(?:[/?]|$)', '肯德基广告资源；已有 apphome5/apphome6/advertisement 不覆盖'),
    340: (r'^https?://api\.douban\.com/b[^/?]*/common_ads\?', '豆瓣 common_ads；限制 b 路径段，不让 .* 越过路径或查询边界'),
}


def records(lines):
    section = ''
    for number, line in enumerate(lines, 1):
        if line.startswith('['):
            section = line[1:-1]
        elif line and not line.startswith('#'):
            yield number, section, line


def pattern(line):
    return line.split('"')[1] if line.startswith('"') else None


def build(output_dir=ROOT):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    baseline = (ROOT / 'AdvertisingLite-Privacy.sgmodule').read_bytes()
    source = (ROOT / 'sources/allinone.sgmodule').read_bytes()
    assert hashlib.sha256(baseline).hexdigest() == BASE_SHA, 'Baseline changed: re-review required'
    assert hashlib.sha256(source).hexdigest() == SOURCE_SHA, 'Pinned snapshot mismatch'
    base, upstream = baseline.decode().splitlines(), source.decode().splitlines()
    drops = {n: reason for reason, numbers in DROP_GROUPS.items() for n in numbers}
    assert not (drops.keys() & NARROW.keys())
    metadata = {
        1: '#!name=Advertising AllInOne Privacy',
        2: '#!desc=以 AdvertisingLite Privacy 为基线，仅补充 3 条现有 MITM 范围内的明确广告路径；清理已识别的升级、通知、账户与业务拦截。保留 78 条 DOMAIN、193 条负 MITM 与 710 条正 MITM 原顺序，不新增解密主机，不含脚本、IP 规则或非广告重定向。HTTPS 过滤需 MITM；负匹配保护的敏感主机广告可能保留。保留既有广告图片启发式，不保证零误拦截。替代原 Privacy 模块使用。',
        3: '#!author=blackmatrix7; modified by lswang6',
        7: '#!version=2026.09.30.2',
        10: '# Derived from AdvertisingLite Privacy and pinned blackmatrix7 AllInOne.',
        11: '# Modified by lswang6: reviewed advertising-only delta; unchanged MITM scope.',
        12: '# SPDX-License-Identifier: GPL-2.0-only; see LICENSE.',
    }
    out, audit = [], []
    sections = {n: sec for n, sec, _ in records(base)}
    for n, line in enumerate(base, 1):
        if line == '[Map Local]':
            out.append('# Reviewed AllInOne additions (no additional MITM hosts).')
            for source_line, (p, reason) in ADD.items():
                rule = f'"{p}" - reject'
                out.append(rule)
                audit.append(dict(source='allinone', source_line=source_line, section='URL Rewrite', decision='add', reason=reason,
                                  original=upstream[source_line-1], output_line=len(out), output=rule, output_pattern=p))
            out.append('')
        original = line
        decision, reason = 'keep', '保留基线；无经确认必须删改的业务分支，不推测批量删广告'
        if n in drops:
            decision, reason, line = 'remove', drops[n], None
        elif n in NARROW:
            p, reason = NARROW[n]
            line = '"' + p + '"' + line.split('"', 2)[2]
            decision = 'narrow'
        elif n in metadata:
            line, decision, reason = metadata[n], 'metadata', '更新名称、来源、授权标识及实际边界说明'
        if line is not None:
            out.append(line)
        if n in sections or n in metadata:
            audit.append(dict(source='baseline', source_line=n, section=sections.get(n, 'metadata'), decision=decision,
                              reason=reason, original=original, output_line=len(out) if line is not None else None,
                              output=line, output_pattern=pattern(line) if line else None))
    # Only anchor unanchored URL patterns; escape the three reviewed literal hosts.
    for row in audit:
        p = row['output_pattern']
        if p and p.startswith(('http:', 'https:', 'https?:')):
            fixed = '^' + p
            escaped_hosts = []
            for host in ('api-global.soulapp.me', 'dynamicad.kfc.com.cn', 'dili.sqcosmos.com'):
                normalized_url = p.replace(r'\/', '/')
                prefix = re.match(r'^https?://', normalized_url)
                if prefix and normalized_url[len(prefix[0]):].startswith(host + '/'):
                    fixed = '^' + p.replace(host, host.replace('.', r'\.'), 1)
                    escaped_hosts.append(host)
            rule = '"' + fixed + '"' + row['output'].split('"', 2)[2]
            row.update(decision='anchor', reason='补充 URL 起始锚点，防止查询中嵌入目标 URL 被误匹配；保留原 action',
                       output=rule, output_pattern=fixed, escaped_literal_hosts=escaped_hosts)
            if escaped_hosts:
                row['reason'] += '；转义指定 literal host 点号'
            out[row['output_line'] - 1] = rule
    text = '\n'.join(out) + '\n'
    output_records = list(records(out))
    domain = [l for _, s, l in output_records if s == 'Rule']
    assert domain == [l for _, s, l in records(base) if s == 'Rule'] and len(domain) == 78
    assert text.split('[MITM]\n')[1] == baseline.decode().split('[MITM]\n')[1]
    host_line = next(l for _, s, l in output_records if s == 'MITM')
    hosts = [h.strip() for h in host_line.split('%INSERT%', 1)[1].split(',')]
    negative = [h[1:] for h in hosts if h.startswith('-')]
    positive = [h for h in hosts if not h.startswith('-')]
    assert (len(negative), len(positive)) == (193, 710)
    compiled = [re.compile(pattern(l)) for _, s, l in output_records if s in ('URL Rewrite', 'Map Local')]
    assert not any(s == 'Script' or l.startswith(('URL-REGEX,', 'IP-CIDR')) for _, s, l in output_records)
    assert all(l.endswith(' - reject') for _, s, l in output_records if s == 'URL Rewrite')
    for p, _ in ADD.values():
        host = p.split('://', 1)[1].split('/', 1)[0].replace('\\.', '.')
        assert any(fnmatch.fnmatchcase(host, h) for h in positive)
        assert not any(fnmatch.fnmatchcase(host, h) for h in negative)
    # Basic full-output regression: these business URLs must not match ANY retained path rule.
    allowed = [
        'https://spclient.wg.spotify.com/' + p for p in ('adsfoo', 'ad-logicfoo', 'canvases/v1', 'cards/v1', 'enabled-tracks/v1', 'v1/canvases', 'v1/cards', 'v1/enabled-tracks')
    ] + [
        'https://api.gotokeep.com/anno/v1/upgrade/check', 'https://api.ulife.group/auth/account/getUpgradeStrategy',
        'https://api.ulife.group/auth/account/entrance', 'https://api.zhuishushenqi.com/notification/shelfMessage',
        'https://r.inews.qq.com/getNewsRemoteConfig', 'https://r.inews.qq.com/getQQNewsRemoteConfig',
        'https://r.inews.qq.com/searchHotCatList', 'https://r.inews.qq.com/upLoadLoc',
        'https://mobile.laichon.com/api/v1/goods/goodsList', 'https://m.client.10010.com/mobileService/customer/accountListData',
        'https://api.sodalife.xyz/v1/goods', 'https://sdk.alibaba.com.ailbaba.me/xgapp.php/v2/version',
        'https://sdk.alibaba.com.ailbaba.me/xgapp.php/v2/top_notice?x=1',
        'https://sns.amap.com/ws/msgbox/pull?x=1', 'https://rp.hpplay.cn/logouts',
        'https://example.org/ad/a', 'https://example.org/advertisement',
    ]
    allowed += ['https://' + h + '/' + p for h in ('api.ulife.group', 'spclient.wg.spotify.com', 'api.douban.com')
                for p in ('signin', 'signout', 'login', 'logout', 'notification', 'upgrade')]
    anchor_ads = ['http://ad.myfriday.cn/d/json/1.1', 'https://api-global.soulapp.me/app/open/get',
                  'https://dynamicad.kfc.com.cn/api/app5/homepage/ai/popup', 'http://dili.sqcosmos.com/jiekou/endpage/ad']
    allowed += ['https://www.xiaoxiongmeishu.com/api/home/v1/config/appInit',
                'https://www.xiaoxiongmeishu.com/api/s/v1/popup/createCouponPopup',
                'https://api.xiaoyi.com/v5/app/config?userid=1', 'https://open.qyer.com/qyer/config/get',
                'https://client-api-v2.oray.com/materials/SLCC_IOS_DEVICE',
                'https://client-api-v2.oray.com/materials/SLCC_IOS_STARTUPSuffix',
                'https://client-api-v2.oray.com/materials/SUNLOGIN_CLIENT_IOS_PROMOTIONSuffix']
    allowed += ['https://api.douban.com/?next=' + url for url in anchor_ads]
    allowed += [url.replace(host, host.replace('.', 'X')) for url, host in zip(anchor_ads[1:],
                ('api-global.soulapp.me', 'dynamicad.kfc.com.cn', 'dili.sqcosmos.com'))]
    assert all(not p.pattern.startswith(('http:', 'https:', 'https?:')) for p in compiled)
    for url in anchor_ads:
        assert any(p.search(url) for p in compiled), url
    for url in allowed:
        assert not any(p.search(url) for p in compiled), url
    blocked = ['https://mxsa.mxbc.net/api/v1/adinfo/adplace/query', 'https://res.kfc.com.cn/CRM/kfcad/custom_v2/wxapp?x=1',
               'https://api.douban.com/b2/common_ads?x=1', 'https://r.inews.qq.com/getSplash?x=1',
               'https://spclient.wg.spotify.com/ads', 'https://spclient.wg.spotify.com/ads/v1',
               'https://spclient.wg.spotify.com/ad-logic?x=1']
    for url in blocked:
        assert any(p.search(url) for p in compiled), url
    for n, (p, _) in ADD.items():
        for url in ('https://example.org/ad/', 'https://example.org/?u=' + blocked[list(ADD).index(n)], blocked[list(ADD).index(n)].split('?')[0] + 'Suffix?x=1'):
            assert not re.search(p, url), (n, url)
    for endpoint in ('SLCC_IOS_STARTUP', 'SUNLOGIN_CLIENT_IOS_PROMOTION'):
        url = 'https://client-api-v2.oray.com/materials/' + endpoint
        assert sum(bool(p.search(url)) for p in compiled) == 1, url
    for endpoint in ('getBannerAds', 'getSplash'):
        url = 'https://r.inews.qq.com/' + endpoint
        assert sum(bool(p.search(url)) for p in compiled) == 1, url
    # Per-upstream-rule disposition; identical pattern does NOT imply identical action.
    normalized = {}
    for row in audit:
        if row['source'] == 'baseline' and row['output_pattern']:
            normalized.setdefault(row['output_pattern'].replace('\\/', '/'), []).append(row['output_line'])
    covered = {133:104,134:104,484:894,729:476,747:1208,773:1223,774:1223}
    reviewed_originals = {pattern(base[n-1]).replace('\\/', '/'): (reason, None) for n, reason in drops.items()}
    reviewed_originals.update({pattern(base[n-1]).replace('\\/', '/'): (reason, replacement) for n, (replacement, reason) in NARROW.items()})
    upstream_audit = []
    for n, section, line in records(upstream):
        p = pattern(line)
        reason, decision = '未同时证明具体主机、明确广告路径及未被现有规则语义覆盖；保守不引入', 'exclude'
        refs = []
        if n in ADD:
            decision, reason = 'add_narrowed', ADD[n][1]
        elif n == 370:
            reason = 'openUpgrade 为升级接口，明确非广告，排除'
        elif n == 767:
            reason = '任意后缀 .+ad_slot 可跨路径或查询；未证明具体广告端点，不制造新增规则'
        elif n in covered:
            decision, reason = 'covered', '已被保留或收窄后的基线广告规则覆盖；不更改其动作'
            refs = [r['output_line'] for r in audit if r['source']=='baseline' and r['source_line']==covered[n]]
        elif section == 'Script':
            reason = '不引入上游 24 条脚本'
        elif section == 'Rule':
            reason = '不引入上游 DOMAIN/IP/URL-REGEX；非广告功能排除，广告 URL-REGEX 不额外扩展范围'
        elif section == 'MITM':
            reason = '不导入上游 MITM；严格保留基线正负匹配'
        elif section == 'General':
            reason = '使用基线 General，不扩展 HTTP 引擎主机'
        elif not line.endswith(' - reject'):
            reason = '非广告重定向，不引入'
        elif p and not p.startswith(('^http', 'http')):
            reason = '通用或未锚定具体主机匹配，不引入'
        elif p and p.replace('\\/', '/') in reviewed_originals:
            reason = '基线同源规则已审查删改：' + reviewed_originals[p.replace('\\/', '/')][0]
        elif p and p.replace('\\/', '/') in normalized:
            decision, reason = 'same_pattern', '与保留基线 pattern 相同；保留基线动作，未将 reject 等同于 Map Local'
            refs = normalized[p.replace('\\/', '/')]
        if n in ADD:
            refs = [r['output_line'] for r in audit if r['source']=='allinone' and r['source_line']==n]
        upstream_audit.append(dict(source_line=n, section=section, original=line, pattern=p, decision=decision, reason=reason, output_lines=refs))
    counts = dict(Counter(r['decision'] for r in audit if r['section'] in ('URL Rewrite', 'Map Local')))
    counts.update(literal_host_escaped=sum(bool(r.get('escaped_literal_hosts')) for r in audit), domain=78, mitm_negative=193, mitm_positive=710, added_mitm=0,
                  output_url_rewrite=sum(s=='URL Rewrite' for _,s,_ in output_records),
                  output_map_local=sum(s=='Map Local' for _,s,_ in output_records),
                  upstream_scripts_excluded=sum(s=='Script' for _,s,_ in records(upstream)),
                  upstream_domain_excluded=8, upstream_ip_excluded=3, upstream_urlregex_excluded=12,
                  upstream_redirect_excluded=sum(s=='URL Rewrite' and not l.endswith(' - reject') for _,s,l in records(upstream)),
                  baseline_path_rules=sum(s in ('URL Rewrite','Map Local') for _,s,_ in records(base)),
                  output_path_rules=len(compiled), net_path_rules=len(compiled)-sum(s in ('URL Rewrite','Map Local') for _,s,_ in records(base)))
    manifest = dict(schema=1, license='GPL-2.0-only', upstream_author='blackmatrix7', modified_by='lswang6',
                    inputs={'baseline': {'file':'AdvertisingLite-Privacy.sgmodule','sha256':BASE_SHA},
                            'allinone': {'file':'sources/allinone.sgmodule','sha256':SOURCE_SHA,'pin':PIN,
                                         'metadata_date':'2025-08-26','latest_file_commit_date':'2025-12-21'}},
                    output={'file':'Advertising-AllInOne-Privacy.sgmodule','sha256':hashlib.sha256(text.encode()).hexdigest()},
                    counts=counts, validation={'allowed_urls':allowed,'blocked_urls':blocked + anchor_ads,'result':'passed',
                    'limitations':'静态 pattern/边界检查；未进行 Surge 实机或业务功能验收。保留基线未确认非广告的图片等启发式。'},
                    baseline_and_additions=audit, upstream_dispositions=upstream_audit,
                    shortlist=[r for r in upstream_audit if r['source_line'] in (133,134,187,197,340,370,484,729,747,767,773,774)])
    (output_dir / 'Advertising-AllInOne-Privacy.sgmodule').write_text(text)
    (output_dir / 'advertising-allinone-review.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(counts, ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT)
    build(parser.parse_args().output_dir)
