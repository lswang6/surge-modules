# 微信模块来源与取舍

审查日：2026-09-30。由旧 10 条**加 4 删 1，得到 13 条**；全部为 `DOMAIN,<完整主机名>,REJECT`。只处理精确主机，无 MITM、脚本、远程 RULE-SET、DNS 修改。上游规则是来源证据，不是广告专用性或真实业务安全保证。

## 采纳与排除

| 决定 | 精确主机 | 来源与转换／风险边界 |
| --- | --- | --- |
| 保留 3 条 | `wxsnsdy.wxs.qq.com`、`wxsmsdy.video.qq.com`、`wxsnsdythumb.wxs.qq.com` | [F] 的 DOMAIN REJECT；第二条拼写为 `wxsmsdy`，不能用近似主机作佐证。广告资源或奖励流程可能受影响。 |
| 保留 2 条 | `ads-shopping.shouqianba.com`、`ad.maoyan.com` | [F] 的 DOMAIN REJECT，不扩大至收银、订单、登录主机。 |
| 保留 1 条 | `e.jparking.cn` | 保留 [F] 的既有规则；[停车插件][JP]和 Sukka 仅作整域拦截旁证，不复制其列表或新增规则，也不将 [F] 的许可扩用于这些项目。多个项目收录不等于独立实测，广告专用性未证实，实际缴费未测试。 |
| 保留 2 条 | `dsp.fcbox.com`、`ads.ishansong.com` | 旧模块由 [F] 的 `/adSearch/`、`/advert` 路径转整域；[A] L378/L112 及 [Z] L20/L15 另有整域证据。拒绝连接与上游空 JSON 响应不同，取件／配送业务未实测。 |
| 保留 1 条 | `smarket.dian.so` | [Z] L26 明确 `host, smarket.dian.so, reject`，补足旧 [F] 主机前缀 URL 重写之外的整域依据。充电业务未实测。 |
| 新增 1 条 | `ads.zhinengxiyifang.cn` | 直接数据来源 [A] L122：`\|\|ads.zhinengxiyifang.cn^`；[U] L14 的 `/api/v1.1/ads/` 路径佐证 U净广告用途，不能仅凭该路径推出整域安全。转为精确 DOMAIN，不含子域。 |
| 新增 1 条 | `ad-api.4pyun.com` | 直接数据来源 [A] L20；[Z] L11 有 host reject。[P云官方网关说明][P]明确这是广告服务；[广告 SDK 文档][SDK]说明停车／交易场景，仅引用事实，不复制代码。 |
| 新增 1 条 | `ad-files.4pyun.com` | 直接数据来源 [A] L22；[Z] L12 有 host reject。广告用途依据维护者分类，官方资料只直接确认 ad-api，不能把该确认延伸至此主机；业务回归未做。 |
| 新增 1 条 | `ad.duoduo.link` | 直接数据来源 [A] L36；[D] 具名朵朵校友圈模块与 [Z] L28 交叉佐证。上游分别为 DOMAIN-SUFFIX / host-suffix，**本模块保守收窄为精确 DOMAIN**，不拦子域。按更广微信广告范围纳入，不称扫码消费必需项。 |
| 移除 1 条 | `ad.xiaotucc.com` | [F] 只有 `/advert` 路径依据，整域升格证据不足；恢复本模块对此主机的不拦截，不采用需要 MITM 的路径替代。 |
| 暂不新增 | `et.ykccn.com` | [Y] 与 [Z] 有整域 REJECT，但没有充分广告用途／专用性依据；同模块 `gw3.ykccn.com` 的广告路径不能证明此主机用途。 |
| 排除停车共享主机 | `psbg.jparking.cn`、`csg.jparking.cn`、`cw.jparking.cn`、`etgw.jparking.cn`、`sytgate.jslife.com.cn` | `psbg` 有[附近停车场查询源码][BUSINESS]；其他主机广告专用性不明或仅限定路径证据，不提升为整域拒绝。 |
| 排除 ETCP 主机 | `api-c-prod.etcp.cn`、`ife.etcp.cn`、`static.etcp.cn` | `ife.etcp.cn` / `static.etcp.cn` 在 [ETCP 规则][E]中只有广告路径依据；`api-c-prod.etcp.cn` 则是[公开源码中的停车查询主机][ETCP-BUSINESS]，不属于该广告路径证据。这些证据不能证明上述主机承载同主机支付，也不足以将其整域拦截。没有可靠的新增整域免 MITM 候选，亦不纳入用途、许可与依赖未确认的 `logs-bigdata.yeehaw.com.cn`。 |
| 保护 P云业务 | `papi.4pyun.com`、`api.4pyun.com`、`auth.4pyun.com`、`app.4pyun.com`、`qr.4pyun.com` | [P]分别列为支付网关、开放停车网关、授权、支付中转、优惠二维码；全部列入不拦断言，父域 `4pyun.com` 也不拦。 |
| 排除其他业务／共享主机 | `gw3.ykccn.com`、`web-stable-cdn.ykccn.com`、`zhinengxiyifang.cn`、`api-marketing.zhinengxiyifang.cn`、`adsoss.zhinengxiyifang.cn` | [Y]/[U] 的路径、重写或共享 CDN 证据不直接变成整域拦截；保留现有微信聊天、支付、登录及其他敏感主机保护测试。 |

## 固定来源、文件变更日期与许可

下列日期均按 Asia/Taipei 当地日期记录，为具体文件的最后变更日期，不是仓库 pushed_at，也不是每条规则的验证日期；固定链接包含内容快照 SHA。新增四条统一取自 AWA 的 **GPLv3 发布文件**，不用其 MIT build 分支或其他许可文件替代来源记录。

| 标识／文件 | 文件变更日期与性质 | 归属／许可 |
| --- | --- | --- |
| [F：WeChatMiniAds.plugin][F] | 2025-06-30，历史重建提交；文件头日期更早。不称近期微信专项维护 | 可莉、原贡献者及 fmz200；[根 GPLv3][FL]。README 另有传播限制声明，其与根许可、转载授权关系仍不确定；保留历史归属，不宣称授权链已完全核清。 |
| [A：AWAvenue-Ads-Rule.txt][A] | 2026-09-21，发布内容实际新增两条其他广告域名；源规则亦于当日变更。不是本模块四条均当天新增／重验 | AWAvenue-Ads-Rule Contributor；[该发布快照 GPLv3][AL]。`\|\|host^` 收窄为精确 DOMAIN；不复制带其他许可的 Replenish。 |
| [Z：wechatAdBlock.list][Z] | 2026-09-28，`add bahecloud` 实际规则更新；不代表旧条目全部重验 | zirawell/R-Store；[已核对的 GPLv3 许可快照][ZL]。用于交叉佐证及 smarket 保留依据，不订阅整表。 |
| [U：UJing.sgmodule][U] | 2025-10-18，`update split rules` | 署名奶思，fmz200 托管；[GPLv3][UL]。仅引用路径用途，不移植脚本、响应修改或 MITM。 |
| [Y：ykc.sgmodule][Y] | 2026-05-09，`opt sth` | zirawell/R-Store，[GPLv3][ZL]；作为排除决策证据。 |
| [D：duoduo.sgmodule][D] | 2025-12-04 committer；author 为 2025-07-15。`opt format` 是格式整理，不算广告语义重验 | zirawell/R-Store，GPLv3；项目许可核对见 [ZL]，仅交叉佐证。 |

本模块由 lswang6 于 2026-09-30 整理／修改，继续使用 **GPL-3.0-only**，完整文本见 [LICENSE-GPL-3.0](LICENSE-GPL-3.0)。Sukka 的 [reject 源][S]在 2026-09-28 有实际规则变更，但使用 [AGPLv3][SL]，本次只做交叉参考，未复制其列表。AdGuard 与 anti-AD 的维护和误杀修复记录只说明可供复核，未作为本轮新增数据来源；自动构建、镜像收录和多个转载都不能替代逐条验证。

## 推荐复核项目

| 项目与固定源文件 | 最近相关源码变更（Asia/Taipei） | 建议用途 |
| --- | --- | --- |
| [AWAvenue：rule/domain.txt][AWA-SOURCE] | 2026-09-21 | 首要广告域名对照；本轮新增数据仍取上表 GPLv3 发布文件，按实际文件记录许可。 |
| [zirawell：微信汇总][Z] | 2026-09-28 | 核对微信小程序整域规则及具名模块用途，避免将路径规则直接升格。 |
| [AdGuard：mobile adservers][ADGUARD] | 2026-09-25 | 核对广告用途与例外；带路径、应用或页面条件的规则不直接转为全局 DOMAIN。 |
| [anti-AD：白名单][ANTIAD] | 2026-09-20 | 优先复核误杀修复与业务例外，不直接导入聚合列表。 |
| [Sukka：reject 源][S] | 2026-09-28 | 辅助交叉参考；AGPLv3，本次不复制其列表。 |

源码更新不是全规则实测，文件日期也不代表本模块每条规则在该日重新验证；上述推荐不表示自动导入第三方变化。

## 更新与真实效果边界

维护较活跃的来源不等于每条规则都新验证，也不等于本模块自动导入第三方变化。只在准备更新时人工审查源 diff、删除／例外、用途和许可；原 Raw 地址不变，更新后用户下载的是本模块审查后的快照。

两项 Python 检查验证静态集合、metadata 去重及敏感主机边界；Surge CLI 仅检查仓库外临时规则配置语法，不加载或安装。**没有真实扫码付款、停车离场、登录、充电、取件、广告奖励或 iOS 实机验收**。按域名拒绝无法区分同主机的业务和广告；不保证全部微信广告或 ETCP 去广告，未发现误杀报告也不等于没有误杀。出现异常时停用模块对照并撤回相关条目。

[F]: https://github.com/fmz200/wool_scripts/blob/3ca7487b4e4b86d9af76e50df72c62eacfbb659e/Loon/plugin/WeChatMiniAds.plugin
[FL]: https://github.com/fmz200/wool_scripts/blob/3ca7487b4e4b86d9af76e50df72c62eacfbb659e/LICENSE
[A]: https://github.com/TG-Twilight/AWAvenue-Ads-Rule/blob/2cac354cb5c8d59af0332168396ba8fa935d0aa0/AWAvenue-Ads-Rule.txt
[AL]: https://github.com/TG-Twilight/AWAvenue-Ads-Rule/blob/2cac354cb5c8d59af0332168396ba8fa935d0aa0/LICENSE
[Z]: https://github.com/zirawell/R-Store/blob/e254e48e7a5aaf9e2b45e28f6126d3aa8291d868/Rule/QuanX/Adblock/All/filter/wechatAdBlock.list
[ZL]: https://github.com/zirawell/R-Store/blob/6c1089cf3a552aca8db15583de4f2199391cf43d/LICENSE
[U]: https://github.com/fmz200/wool_scripts/blob/6f218c9cb5122be78c71f32139643350bc5a1d40/Surge/module/split/partU/UJing.sgmodule
[UL]: https://github.com/fmz200/wool_scripts/blob/6f218c9cb5122be78c71f32139643350bc5a1d40/LICENSE
[Y]: https://github.com/zirawell/R-Store/blob/6c1089cf3a552aca8db15583de4f2199391cf43d/Rule/Surge/Adblock/Applet/Wechat/Y/%E4%BA%91%E5%BF%AB%E5%85%85/ykc.sgmodule
[D]: https://github.com/zirawell/R-Store/blob/d23e571290ae86ccf7cc6f29dd30770cb5afe299/Rule/Surge/Adblock/Applet/Wechat/D/%E6%9C%B5%E6%9C%B5%E6%A0%A1%E5%8F%8B%E5%9C%88/duoduo.sgmodule
[JP]: https://github.com/androidcn/userscripts/blob/2de7769fede7b3f9ee60e9435560beb6a2356211/jparking_AD.plugin#L12-L17
[BUSINESS]: https://github.com/xuetongoll/park-spider/blob/84e35594484891e7b6ada11a1c04b08f1d06102f/tools/spider_park/spider_park.py#L36-L42
[E]: https://github.com/zirawell/Ad-Cleaner/blob/1adec999a867f2c0cfc72ab90027efec5fbc3dde/Adblock/Applet/Wechat/E/ETCP/rewrite/etcp.conf#L1-L5
[P]: https://doc.4pyun.com/openapi/
[SDK]: https://doc.4pyun.com/openapi/api/adverting-jsapi.html
[S]: https://github.com/SukkaW/Surge/blob/79b7fa2db24a09694d85d116f940239b78101bf8/Source/domainset/reject.conf
[SL]: https://github.com/SukkaW/Surge/blob/79b7fa2db24a09694d85d116f940239b78101bf8/LICENSE
[ETCP-BUSINESS]: https://github.com/xuetongoll/park-spider/blob/84e35594484891e7b6ada11a1c04b08f1d06102f/tools/spider_park/spider_park.py#L158-L169
[AWA-SOURCE]: https://github.com/TG-Twilight/AWAvenue-Ads-Rule/blob/18afc16ca15b8130a45e61471e73ad9c2c9ca3cb/rule/domain.txt
[ADGUARD]: https://github.com/AdguardTeam/AdGuardFilters/blob/4c79c829c1f5c93a7e1435d3f2c5994bbf0151e1/MobileFilter/sections/adservers.txt
[ANTIAD]: https://github.com/privacy-protection-tools/anti-AD/blob/c1bc8d906e7ec416c9a9e6dbe4d2656e01c6db5c/scripts/lib/white_domain_list.php
