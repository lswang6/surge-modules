# Advertising AllInOne Privacy 审查与合并

<!-- SPDX-License-Identifier: GPL-2.0-only -->

审查日期：2026-09-30。作者 blackmatrix7；合并及修改 lswang6。此版本将 AdvertisingLite Privacy 的过滤与 AllInOne 中经审查的补充整理为一个模块；不是原 AllInOne 的完整功能合集。

## 来源与更新情况

- 基础文件：[AdvertisingLite-Privacy.sgmodule](AdvertisingLite-Privacy.sgmodule)，沿用本仓库已有隐私排除；原基础文件不改动，可回退。
- AllInOne：[固定提交原文](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/a75313d36b049b8aca5b26beffafb1b0ec8c564d/rewrite/Surge/AllInOne/AllInOne.sgmodule)，原字节保存在 [sources/allinone.sgmodule](sources/allinone.sgmodule)。SHA-256：`66a8282facc2c339363bdf924b0a65eeaf11b57acf4b5839538044303a2d388d`。
- 截至审查日，下载的 master 与该快照字节一致。该文件最近提交为 `a75313d36b049b8aca5b26beffafb1b0ec8c564d`，提交时间 **2025-12-21T16:23:05Z**；模块内部仍写 **2025-08-26 02:12:35**，两者不能混作同一更新时间。这不证明所有规则失效，也不代表已验证适配当前 App。
- 上游完整 GPL version 2 与本仓库 [LICENSE](LICENSE) 字节一致，SHA-256 为 `8177f97513213526df2cf6184d8ff986c675afb514d4e68a404010521b880643`。本次派生文件采用 GPL-2.0-only；独立的微信 GPL-3.0-only 模块及 Sukka AGPL-3.0-only 文件不并入此作品，其许可保持不变。

## 为什么不能直接拼接

原 AllInOne 含 8 条 DOMAIN、3 条 IP 规则、12 条 URL-REGEX、807 条 URL Rewrite（745 拒绝、62 跳转）、24 条脚本和 831 项 MITM。它的范围明显超出去广告。

| 问题 | 可复核实例 | 本次处理原则 |
| --- | --- | --- |
| 无主机限制的关键词拦截 | `(?i)\badvertisement`、`(?i)\badvertising`、通用 `/ad/` | 不把任意网站含相应字符串的正常页面当作广告 |
| 拦截普通功能 | 知乎通知计数/消息、`api.ulife.group/auth/account/entrance`、商品列表、App 升级检查 | 不从 AllInOne 引入这些功能干预；基础文件中已识别的同类规则也清理 |
| 正常内容与广告混在一个表达式 | Spotify `canvases`、`cards`、`enabled-tracks` 与广告接口并列；腾讯新闻远程配置与广告并列 | 广告分支单独保留，功能分支排除；接口语义未经运行验证的条目保守不加入 |
| 与去广告无关的跳转 | Bili 国际版地区/登录参数修改，以及软件下载站跳转 | 62 条跳转不引入，不猜测修复其历史目的 |
| 解密范围扩大 | 包含 `mp.weixin.qq.com`、`api*.futunn.com`、`home.mi.com`、`client.mail.163.com` 等 | 不并入 831 项名单，保留基础模块已有 193 项前置排除、710 项正向匹配及顺序 |
| 脚本功能不只是广告 | 知乎推荐/评论/用户信息/黑名单功能与开屏脚本混合 | 不引入这 24 条脚本；这不表示所有脚本有恶意或无效 |
| 大量重复 | 规范化转义斜线后，807 条重写中的 578 条与基础 Rewrite/Map Local 有相同匹配表达式 | 匹配表达式相同不代表响应动作相同，优先保留已有空响应，不把 Map Local 简单改成拒绝 |

Surge 按顺序匹配 MITM 主机，负向排除应位于正向匹配之前。HTTPS 路径过滤需要主机经 MITM 解密；不在解密范围的路径规则不能承诺生效。依据：[MITM 文档](https://manual.nssurge.com/http/mitm.html)、[URL Rewrite](https://manual.nssurge.com/http/url-rewrite.html)、[Map Local](https://manual.nssurge.com/http/map-local.html)。

## 远程脚本复核

独立子代理审查了 24 个声明和两份脚本，并用 Node vm 模拟 Surge globals 做最小复现，不发 App 请求：

- [startup.js 固定源](https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/a75313d36b049b8aca5b26beffafb1b0ec8c564d/script/startup/startup.js)：BiliBili 分支修改 `body`，最终却根据 `response` 返回，修改结果丢失；Fa米家分支缺 `break`，特定响应结构会被下一分支覆盖。
- AllInOne 的“京东”声明实际匹配 `hd.mina.mi.com`，脚本对应“小爱音箱”；美团 `/loadInfo?` 将最后字母设为可选，并非匹配查询问号，还会匹配不应命中的路径前缀。
- [知乎脚本固定源](https://gist.githubusercontent.com/blackmatrix7/f5f780d0f56b319b6ad9848fd080bb18/raw/e2f0646ba9b3bb72b025395b7d2d255c3b241286/zheye.min.js)：存在模块声明与内部路由不一致，部分声明会空转；同时含黑名单、关键词、用户字段展示和可选外部服务调用，不能等同纯广告过滤。未独立确认该 Gist 的授权，不复制或改发它。

脚本 SHA-256 分别为 `431801d369b495d34b7a1c1d6cc43abdb1d159dd0d82491ee756c0ae834b625c`、`41863c4c0ce5eefbdda9a5a96d7605bde70a89a9cc24ee0875f3d751aed2f757`。因此合并版不带入这 24 条脚本，而不是仅改名后声称已经修复所有脚本。上游 README 有额外转载/删除文字，与根 GPL 文本存在张力；这里保留来源及完整 GPL，不将其改写为对下游新增的许可限制，也不宣称解决所有第三方授权问题。

## 合并结果

- 保留 **78 条精确 DOMAIN 拒绝规则**，MITM **193 项负向排除＋710 项正向匹配**，顺序和内容与原 Privacy 完全一致；新增解密主机 **0**。
- 基础模块 1229 条路径规则中，移除 **163 条**可能干预普通业务的规则，收窄 **23 条**混合匹配；从 AllInOne 实际补入 **3 条**未覆盖的广告路径：蜜雪广告位、肯德基广告资源、豆瓣 common_ads。
- 成品包含 **436 条 URL Rewrite＋633 条 Map Local**。未机械搬入原 AllInOne 的 62 条跳转、24 条脚本、8 条域名、3 条 IP 及12条 URL-REGEX。
- 额外复核已对 **28 条**继承规则补起始锚点，避免在查询参数中的嵌入网址触发；放行小熊美术初始化／优惠券入口、小蚁用户配置、穷游通用配置，以及 Oray 设备资料路径。Oray 启动广告选用基线首条的空文本，推广素材选用原空 JSON，移除冲突重复项，腾讯新闻广告重复分支作收窄。
- “移除”包含为兼容性作出的保守取舍，**不表示每一条都已在真实 App 复现误拦**。保留部分历史广告图片/开屏启发式，也不表示每条已证实广告专用。没有为凑数量新增规则。

每一条基础规则及上游规则的保留、删改、未纳入原因见 [逐项审计 JSON](advertising-allinone-review.json)。用 `python3 build_advertising_allinone.py` 可从两个固定 SHA-256 输入重建；原始快照、生成源码、测试和完整 GPL 一起发布。旧文件继续作为固定输入，不静默覆盖旧 Raw 地址。

## 验证

- 独立子代理测试覆盖 86 个业务 URL 负例、8 个广告正例、敏感域名排除、78 条域名拦截、规范化后重复、凭据标记及 SHA-256；两次重建要求逐字节一致。
- 主 agent 在 **Surge Mac 6.10.0** 上将模块的 `%INSERT%` / `%APPEND%` 展开成仓库外临时配置，并补 `FINAL,DIRECT`，运行 `surge-cli --check`：通过。未加载该临时配置或切换现有模块。
- 合并版 **1069 个表达式**使用 macOS Foundation ICU 编译：全部通过。Python 回归与 ICU 编译不能证明真实 App 响应、证书信任或广告效果。
- 可复跑：`python3 test_advertising_allinone.py`。已有三个模块的测试也在发布前运行；独立许可范围及旧产物不改。

最终模块 SHA-256：`7d06eff69750d1dfced5dfc84c0b7548a4e0b0aa9cc4d64c07b7b781ec4aef87`。规范化字符串去重和已发现的分支冲突已验证；未宣称完成全部正则的语义等价证明。

## 安装与回退

[合并版 Raw](https://raw.githubusercontent.com/lswang6/surge-modules/main/Advertising-AllInOne-Privacy.sgmodule)

在 Surge 从 URL 安装合并版后，停用 AdvertisingLite Privacy 和原 AllInOne；旧 AdvertisingLite / AdvertisingLite MITM (2) 也应保持停用。启用合并版即可。微信免 MITM 模块继续单独启用，Sukka 引用无需改变。不要让新旧三份广告模块同时生效。

本次发布不自动修改设备配置或模块开关。Surge 模块启用状态不会跨设备同步，Mac 与 iPhone 需分别处理（[官方模块说明](https://manual.nssurge.com/profile/module.html)）。如需回退，停用合并版并重新启用旧 AdvertisingLite Privacy；保留微信模块。

## 边界

这是手工审查快照，不是自动合并上游服务。下载 Raw 只取得本仓库最后发布版本。保留规则不等于逐项实测有效，未做真实 App 广告展示、登录、支付、消息推送及 iPhone 设备验收。MITM 仍需要用户自己的 CA；现有正向匹配中包含共享主机，所以“不扩大 MITM”不等于“完全不解密业务”。其他主配置和模块的规则也可能独立影响相同请求。

Map Local 保留的空响应资源仍引用上游公开资源，网络不可达时需检查外部资源更新。文件中不包含用户证书、节点或凭据。
