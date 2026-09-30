# SPDX-License-Identifier: GPL-2.0-only
# Modified by lswang6 on 2026-09-30.
"""Offline stdlib regressions; python3 test_advertising_allinone.py.

Python re and fnmatch are approximate probes, NOT Surge/ICU execution.
Unsupported regexes are reported explicitly, never counted as validated.
"""
from pathlib import Path
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'AdvertisingLite-Privacy.sgmodule'
MODULE = ROOT / 'Advertising-AllInOne-Privacy.sgmodule'
UPSTREAM = ROOT / 'sources/allinone.sgmodule'
REPORT = ROOT / 'advertising-allinone-review.json'
BUILDER = ROOT / 'build_advertising_allinone.py'


def sections(text):
    result = {}
    current = None
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            current = line[1:-1]
            assert current not in result, ('duplicate section', current)
            result[current] = []
        else:
            assert current is not None, (number, line)
            result[current].append((number, line))
    return result


def hosts(text):
    lines = re.findall(r'^hostname\s*=\s*%INSERT%\s*(.+)$', text, re.M)
    assert len(lines) == 1, 'exactly one INSERT hostname list required'
    return [item.strip() for item in lines[0].split(',')]


def decrypts(host, patterns):
    for pattern in patterns:
        if fnmatch.fnmatchcase(host.lower(), pattern.lstrip('-').lower()):
            return not pattern.startswith('-')
    return False


def url_rules(parts):
    rows = []
    for section in ('URL Rewrite', 'Map Local', 'Rule'):
        for number, line in parts.get(section, []):
            if section == 'Rule':
                if not line.startswith('URL-REGEX,'):
                    continue
                pattern = line[len('URL-REGEX,'):].rsplit(',', 1)[0]
            else:
                match = re.fullmatch(r'"(.+)"\s+(.+)', line)
                assert match, (number, 'unparsed URL rule', line)
                pattern = match[1]
            rows.append((section, number, pattern, line))
    return rows


BUSINESS = (
    'https://example.org/advertising-guide',
    'https://www.xiaoxiongmeishu.com/api/home/v1/config/appInit',
    'https://api.xiaoyi.com/v5/app/config?userid=123',
    'https://open.qyer.com/qyer/config/get',
    'https://client-api-v2.oray.com/materials/SLCC_IOS_DEVICE',
    'https://api.douban.com/?next=http://ad.myfriday.cn/d/json/1.1',
    'https://api-globalXsoulappXme/app/open/get',
    'https://dynamicadXkfcXcomXcn/api/app5/homepage/ai/popup',
    'http://diliXsqcosmosXcom/jiekou/endpage/ad',
    'https://example.org/advertisement',
    'https://example.org/ad/orders',
    'https://example.org/splash_screen',
    'https://example.org/brand/search/v1.json',
    'https://example.org/businessupgrades',
    'https://api.gotokeep.com/anno/v1/upgrade/check',
    'https://capis.didapinche.com/publish/api/upgrade',
    'https://api.ulife.group/auth/account/entrance',
    'https://api.ulife.group/auth/account/getUpgradeStrategy',
    'https://spclient.wg.spotify.com/canvases/v1/canvases',
    'https://spclient.wg.spotify.com/track/v1/enabled-tracks',
    'https://spclient.wg.spotify.com/track/v1/enabledtracks',
    'https://api.zhihu.com/notifications/v3/count',
    'https://api.zhihu.com/message-push/event',
    'https://api.zhihu.com/settings/new/notification',
    'https://mobile.laichon.com/api/v1/goods/goodsList',
    'https://shop.laichon.com/api/v1/goods/goodsList',
    'https://api.sodalife.xyz/v1/goods',
    'https://api.bwton.com/bff/app/h5/v1/station/goods',
    'https://api.bwton.com/bff/app/index/goods',
    'https://api.zhuishushenqi.com/notification/shelfMessage',
    'https://api.zhuishushenqi.com/user/bookshelf-updated',
    'https://app.ceair.com/customize/security/update',
    'https://capi.douyucdn.cn/api/ios_app/check_update',
    'https://mapi.mafengwo.cn/system/update/check_update',
    'https://hxqapi.hiyun.tv/api/notification/plans',
    'https://appdmkj.5idream.net/v2/login/message/tip',
    'https://blog.nilbt.com/static/api/update',
    'https://ucmp.sf-express.com/proxy/esgcempcore/memberGoods/pointMallService/goodsList',
    'https://vidz.3hxq.cn/api/app/announcements/home',
    'https://info.mina.xiaoaisound.com/account/login',
    'https://hdgateway.zto.com/orders/list',
    'https://www.jd.com/',
    'https://www.google.cn/search?q=business',
)
ADS = (
    'https://info.mina.xiaoaisound.com/advertise/list',
    'https://aag.enmonster.com/apa/advert/demand/home/poster',
    'https://hdgateway.zto.com/getAdInfo',
    'https://ad.xiaotucc.com/advert',
    'https://mxsa.mxbc.net/api/v1/adinfo/adplace/query',
    'https://res.kfc.com.cn/CRM/kfcad/custom_v2/wxapp?x=1',
    'https://api.douban.com/b2/common_ads?x=1',
    'https://spclient.wg.spotify.com/ads/v1',
)


class Regression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = MODULE.read_text()
        cls.base = BASE.read_text()
        cls.parts = sections(cls.text)
        cls.rules = url_rules(cls.parts)
        cls.patterns = hosts(cls.text)
        cls.compiled = []
        cls.unsupported = []
        for section, number, pattern, line in cls.rules:
            try:
                cls.compiled.append((number, re.compile(pattern)))
            except re.error as error:
                cls.unsupported.append((number, pattern, str(error)))
        for entry in cls.unsupported:
            print('PYTHON_REGEX_UNSUPPORTED:', entry, file=sys.stderr)

    def test_scope_and_exclusions(self):
        self.assertEqual(self.patterns, hosts(self.base))
        negatives = [p for p in self.patterns if p.startswith('-')]
        positives = [p for p in self.patterns if not p.startswith('-')]
        self.assertEqual((len(negatives), len(positives)), (193, 710))
        self.assertEqual(self.patterns, negatives + positives)
        self.assertEqual(len(self.patterns), len(set(self.patterns)))
        for host in ('openapi.boc.cn', 'mp.weixin.qq.com', 'client.mail.163.com',
                     'geetest.htsc.com', 'api.futunn.com', 'api1.futunn.com',
                     'home.mi.com', 'fuwu.nhsa.gov.cn', 'sso.ifanr.com'):
            self.assertFalse(decrypts(host, self.patterns), host)
        for host in ('api.caiyunapp.com', 'image.spdbccc.com.cn', 'www.baidu.com'):
            self.assertTrue(decrypts(host, self.patterns), host)
        domain = r'^DOMAIN,([^,]+),REJECT$'
        blocked = re.findall(domain, self.text, re.M)
        self.assertEqual(len(blocked), 78)
        self.assertEqual(len(set(blocked)), 78)
        self.assertEqual(set(blocked), set(re.findall(domain, self.base, re.M)))
        for host in blocked:
            self.assertFalse(decrypts(host, self.patterns), host)

    def test_metadata_and_safety(self):
        for key in ('name', 'desc', 'author', 'repo', 'version'):
            self.assertRegex(self.text, rf'(?m)^#!{key}=\S.+$')
        self.assertIn('AllInOne', self.text.splitlines()[0])
        self.assertEqual(set(self.parts), {'General', 'Rule', 'URL Rewrite', 'Map Local', 'MITM'})
        self.assertNotRegex(self.text, r'(?im)^\s*(?:ca-p12|ca-passphrase|skip-server-cert-verify|http-api|external-controller-access)\s*=')
        self.assertNotRegex(self.text, r'(?i)script-path\s*=|type\s*=\s*http-(request|response)|-----BEGIN .*PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{20,}')
        self.assertNotRegex(self.text, r'(?i)(?:password|passwd|access[_-]?token|api[_-]?key)\s*[=:]\s*["\']?[A-Za-z0-9_+/=-]{12,}')
        self.assertEqual([v for _, v in self.parts['General']],
                         [v for _, v in sections(self.base)['General']])
        for _, line in self.parts['URL Rewrite']:
            self.assertRegex(line, r'\s-\sreject(?:-\w+)?$')
        for _, line in self.parts['Rule']:
            self.assertRegex(line, r'^DOMAIN,[^,]+,REJECT$')

    def test_business_urls(self):
        # Deliberately evaluate every rule, even for an excluded MITM host.
        for original in BUSINESS:
            for url in (original, original.replace('https:', 'http:', 1)):
                with self.subTest(url=url):
                    hits = [n for n, regex in self.compiled if regex.search(url)]
                    self.assertEqual(hits, [], f'{url}: matching module lines {hits}')

    def test_ads(self):
        for url in ADS:
            with self.subTest(url=url):
                self.assertTrue(decrypts(urlsplit(url).hostname, self.patterns))
                self.assertTrue(any(regex.search(url) for _, regex in self.compiled), url)

        # These retained host paths may be HTTP-only or excluded from MITM.
        # Check regex behavior without claiming HTTPS decryption succeeds.
        for url in (
            'http://ad.myfriday.cn/d/json/1.1',
            'https://api-global.soulapp.me/app/open/get',
            'https://dynamicad.kfc.com.cn/api/app5/homepage/ai/popup',
            'http://dili.sqcosmos.com/jiekou/endpage/ad',
            'https://client-api-v2.oray.com/materials/SLCC_IOS_STARTUP',
        ):
            with self.subTest(url=url):
                self.assertTrue(any(regex.search(url) for _, regex in self.compiled), url)

        promotion = 'https://client-api-v2.oray.com/materials/SUNLOGIN_CLIENT_IOS_PROMOTION'
        matches = [n for n, regex in self.compiled if regex.search(promotion)]
        self.assertEqual(len(matches), 1, matches)
        self.assertIn('data="https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/blank/blank_dict.json"',
                      self.text.splitlines()[matches[0] - 1])
        self.assertEqual(sum(bool(regex.search('https://r.inews.qq.com/getBannerAds'))
                             for _, regex in self.compiled), 1)

    def test_duplicates(self):
        # Conservative equivalence: escaped slash has no regex semantic effect.
        seen = {}
        for section, number, pattern, _ in self.rules:
            self.assertTrue(pattern.startswith('^'), f'unanchored rule at {number}: {pattern}')
            key = re.sub(r'\\([^A-Za-z0-9.^$*+?{}\[\]\\|()])', r'\1', pattern)
            self.assertNotIn(key, seen, f'cross-section duplicate {seen.get(key)} and {number}')
            seen[key] = (section, number)

    def test_sources_report_and_reproducibility(self):
        report = json.loads(REPORT.read_text())
        for key, path, expected in (
            ('baseline', BASE, '3ea67a6551efe9a364984d213a47106df911985f72345f31f6a93b489c7ef53f'),
            ('allinone', UPSTREAM, '66a8282facc2c339363bdf924b0a65eeaf11b57acf4b5839538044303a2d388d'),
        ):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
            self.assertEqual(report['inputs'][key]['sha256'], expected)
        self.assertEqual(report['inputs']['allinone']['file'], UPSTREAM.relative_to(ROOT).as_posix())
        self.assertEqual(report['output']['sha256'], hashlib.sha256(MODULE.read_bytes()).hexdigest())
        self.assertEqual(report['output']['file'], MODULE.name)
        counts = report['counts']
        for key, expected in (('domain', 78), ('mitm_negative', 193), ('mitm_positive', 710),
                              ('added_mitm', 0), ('upstream_scripts_excluded', 24)):
            self.assertEqual(counts[key], expected)
        self.assertEqual(counts['output_url_rewrite'], len(self.parts['URL Rewrite']))
        self.assertEqual(counts['output_map_local'], len(self.parts['Map Local']))
        lines = self.text.splitlines()
        source_lines = {'baseline': self.base.splitlines(), 'allinone': UPSTREAM.read_text().splitlines()}
        additions = []
        for row in report['baseline_and_additions']:
            self.assertEqual(source_lines[row['source']][row['source_line'] - 1], row['original'])
            if row['output_line'] is not None:
                self.assertEqual(lines[row['output_line'] - 1], row['output'])
            if row['decision'] == 'add':
                additions.append(row)
        self.assertEqual(len(additions), counts['add'])
        for row in additions:
            # New expressions must name a single literal, already allowed host.
            p = row['output_pattern'].replace(r'\/', '/')
            hostpart = re.match(r'^\^https\??://([^/]+)/', p)
            self.assertIsNotNone(hostpart, p)
            host = hostpart[1].replace(r'\.', '.')
            self.assertRegex(host, r'^[a-z0-9.-]+$')
            self.assertTrue(decrypts(host, self.patterns), host)
            self.assertRegex(p.split('/', 3)[3], r'(?i)ad')
            for url in BUSINESS:
                self.assertIsNone(re.search(p, url), (row['source_line'], url))
        self.assertEqual(len([r for r in report['upstream_dispositions'] if r['section'] == 'Script']), 24)
        # CLI writes only into disposable directories; never overwrites worker output.
        with tempfile.TemporaryDirectory(prefix='allinone-regression-') as directory:
            for run in ('first', 'second'):
                target = Path(directory) / run
                result = subprocess.run([sys.executable, str(BUILDER), '--output-dir', str(target)],
                                        capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for path in (MODULE, REPORT):
                    self.assertEqual((target / path.name).read_bytes(), path.read_bytes(), path.name)

    def test_added_path_boundaries(self):
        for url in ADS[4:7]:
            split = urlsplit(url)
            stem = f'{split.scheme}://{split.netloc}{split.path}'
            for business in (stem + 'Suffix?x=1', 'https://example.org/?next=' + url):
                self.assertEqual([n for n, regex in self.compiled if regex.search(business)], [], business)

    def test_python_coverage(self):
        # No green full-coverage claim when ICU-only patterns were skipped.
        self.assertFalse(self.unsupported, 'Python coverage incomplete; see explicit diagnostics; native ICU check required')


if __name__ == '__main__':
    unittest.main(verbosity=2)
