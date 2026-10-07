# Surge Modules

## Advertising AllInOne Privacy / 合并去广告（推荐替代旧版）

将本仓库 AdvertisingLite Privacy 与 blackmatrix7 AllInOne 的广告过滤整理为一个模块。沿用已有敏感域名排除，不扩大 MITM 范围；去除已识别的通用关键词误拦及功能干预，处理本次确认的重复或响应冲突，不引入 AllInOne 的远程脚本；未宣称完成全部正则表达式的语义等价证明。

[合并模块 Raw](https://raw.githubusercontent.com/lswang6/surge-modules/main/Advertising-AllInOne-Privacy.sgmodule) · [审查、取舍与验证](ALLINONE-REVIEW.md)

```text
https://raw.githubusercontent.com/lswang6/surge-modules/main/Advertising-AllInOne-Privacy.sgmodule
```

用此版本时停用 **AdvertisingLite Privacy、原 AllInOne**，仅启用合并版；原 AdvertisingLite 和 AdvertisingLite MITM (2) 也不要同时启用。**WeChat Ads Privacy 继续独立保留**，Sukka 分流引用不变。不要将“合并”理解为收录所有上游功能：知乎功能脚本、地区跳转和新增解密域名不在本版本范围内。

这是经过审查的固定快照，不会自动合并上游 master。MITM 仍需自行配置并信任 CA；部分共享主机仍需解密，不能保证所有 App 去广告或零误拦。旧 Raw 文件保留以便回退。GPL-2.0-only，见 [LICENSE](LICENSE)。

## Sukka Reject Balanced / 通用去广告（兼容优化）

基于 Sukka Reject Base 的审核快照：2026-09-30 从 134,574 条中移除 9 条有正常业务用途或匹配范围过宽的条目，保留 **134,565 条**广告、追踪等域名规则。免 MITM、无脚本；并未逐个验证全部域名，不保证零误拦。

[审查、排除原因和安装说明](SUKKA-REVIEW.md) · [模块 Raw](https://raw.githubusercontent.com/lswang6/surge-modules/main/Sukka-Reject-Balanced.sgmodule) · [原生 DOMAIN-SET Raw](https://raw.githubusercontent.com/lswang6/surge-modules/main/Sukka-Reject-Balanced.domainset) · [常规 RULE-SET `.list` Raw](https://raw.githubusercontent.com/lswang6/surge-modules/main/Sukka-Reject-Balanced.list)

三种形式任选一种。已有 Sukka `DOMAIN-SET` 的配置，**优先替换原地址并保留策略与顺序**。模块规则会置于主配置规则前面，固定使用 `REJECT`，不受已有广告策略组开关控制。不要叠加旧版；另有 `reject-drop` 等列表时，相同域名可能仍被它们拦截，详见审查说明。

本派生版、原始快照和转换源码按 **AGPL-3.0-only** 发布，见 [LICENSE-AGPL-3.0](LICENSE-AGPL-3.0) 和下方文件级许可范围。更新采用人工审查快照，客户端刷新 Raw 不等于自动合并上游。

## Google Maps CN Offset / Google 地图中国偏移修正

在中国境内用浏览器打开 Google 地图时卫星图与路网错位；网页地址加上 `gl=cn` 即恢复正常。本模块用 **2 条 URL Rewrite（302）** 自动补上该参数，不改动 `data=` 段，已带参数的地址不再跳转。无脚本、无规则集。

[查看模块](Google-Maps-CN-Offset.sgmodule) · [Raw 下载](https://raw.githubusercontent.com/lswang6/surge-modules/main/Google-Maps-CN-Offset.sgmodule)

在 Surge「模块 → 从 URL 安装」粘贴：

```text
https://raw.githubusercontent.com/lswang6/surge-modules/main/Google-Maps-CN-Offset.sgmodule
```

**边界：**HTTPS 地址重写必须解密主机，因此会把 `www.google.com`、`www.google.com.hk` 加入 MITM，需已安装并信任 Surge CA。仅对 Safari/Chrome 等浏览器内的 `/maps` 路径生效；Google Maps App 使用自有加密接口，无法通过此模块修正。偏移是否消失依赖 Google 对 `gl=cn` 的处理，未在 iOS 设备实测。验证：`python3 test_google_maps_module.py`。按 **GPL-2.0-only** 发布，见 [LICENSE](LICENSE)。

## WeChat Ads Privacy / 微信去广告（免解密）

小程序广告拦截补充模块，使用 **13 条精确 DOMAIN 规则**，无需 MITM、脚本、远程 RULE-SET 或 DNS 修改。可与下面的 AdvertisingLite Privacy 一起使用。

[查看模块](WeChat-Ads-Privacy.sgmodule) · [Raw 下载](https://raw.githubusercontent.com/lswang6/surge-modules/main/WeChat-Ads-Privacy.sgmodule) · [来源、许可与取舍](WECHAT-SOURCES.md)

在 Surge「模块 → 从 URL 安装」粘贴：

```text
https://raw.githubusercontent.com/lswang6/surge-modules/main/WeChat-Ads-Privacy.sgmodule
```

- 保留微信广告资源、收钱吧、猫眼、捷停车、丰巢、闪送、小电的 9 条精确规则；不扩大至父域或业务接口。同主机的独立 App 请求也会受影响。
- 2026-09-30 **加 4 删 1**：新增 U净 `ads.zhinengxiyifang.cn`、P云 `ad-api.4pyun.com` / `ad-files.4pyun.com`、朵朵 `ad.duoduo.link`；移除只有 `/advert` 路径依据、整域升格证据不足的 `ad.xiaotucc.com`。
- P云官方明确 `ad-api.4pyun.com` 为广告服务；`ad-files.4pyun.com` 的用途依据上游维护者分类，未取得同等官方确认。朵朵上游包含后缀匹配，本模块仅拦截精确主机。
- `et.ykccn.com` 虽有上游整域拒绝先例，广告专用性证据不足，暂不纳入。**ETCP 没有可靠的新增整域免 MITM 候选**，不纳入 `ife.etcp.cn` / `static.etcp.cn` 等业务或共享主机。

**边界：**按域名过滤无法区分同主机的广告与其他内容，不保证去除全部微信广告、公众号、朋友圈、视频号或 ETCP 广告；激励广告奖励可能不可用。`e.jparking.cn` 保留现有多项目整域拦截先例，但广告专用性未证实，**真实扫码付款及停车离场未测试**。出现异常请停用模块对照。模块不清理已缓存广告，也不改变其他模块的解密行为；与 AdvertisingLite Privacy 配合时继续保留 `-mp.weixin.qq.com` 排除。

维护较活跃的来源不等于每条规则都新验证，也不等于本模块自动导入第三方变化。本仓库手工审查固定快照；原 Raw 地址更新后，用户通过该地址下载本模块快照。

验证：`python3 test_wechat_module.py` 检查规则、metadata 去重及敏感业务保护；`python3 test_module.py` 检查另一模块回归。Surge CLI 仅对仓库外临时规则配置执行语法检查，不加载配置。静态检查不能证明真实广告、登录、支付、奖励或 iOS 效果。

原始来源保留可莉、fmz200 及贡献者归属；新增四条采用 AWAvenue-Ads-Rule 的 GPLv3 发布文件，zirawell/R-Store 只作本次新增项的交叉佐证。固定 SHA、文件变更日期、转换差异与许可记录见 [WECHAT-SOURCES.md](WECHAT-SOURCES.md)。本模块按 **GPL-3.0-only** 发布，见 [LICENSE-GPL-3.0](LICENSE-GPL-3.0)；下方 AdvertisingLite Privacy 的 GPL-2.0 不变。

## AdvertisingLite Privacy

Privacy-focused ad filtering for Surge, derived from blackmatrix7's AdvertisingLite.

隐私优化去广告模块：保留必要的广告过滤，减少 HTTPS 解密范围。模块自带名称和中文说明，可替代原来的 **AdvertisingLite** 和 **AdvertisingLite MITM (2)**，无需再安装这两个旧模块。

### Install / 安装

在 Surge「模块 → 从 URL 安装」粘贴以下地址，安装后启用：

```text
https://raw.githubusercontent.com/lswang6/surge-modules/main/AdvertisingLite-Privacy.sgmodule
```

[查看模块](AdvertisingLite-Privacy.sgmodule) · [Raw 下载](https://raw.githubusercontent.com/lswang6/surge-modules/main/AdvertisingLite-Privacy.sgmodule)

### Included / 处理范围

- 保留上游 URL Rewrite、Map Local 和必要的 HTTP 处理设置。
- 710 条正向 MITM 匹配，用于需要按 HTTPS 路径过滤的广告与图片资源。
- 193 条前置负向排除：92 条敏感业务、23 条无用或错误条目，以及 78 条改为域名级拦截的条目。
- 内置 78 条 `DOMAIN,...,REJECT`，这些广告无需 MITM，也不依赖主配置中的特定策略组。模块启用期间，这些规则会直接拦截对应域名。
- 保留专用广告和静态图片/CDN 的过滤；不按银行、支付等品牌整体删除。对业务 API、账户、通信、就诊等共用主机采取保守排除。

模块不包含代理节点、账户、API 密钥、DNS 配置、CA 私钥或脚本。MITM 需使用你自己配置并信任的证书；模块不会关闭服务器证书验证。`router.com` 等 Surge 内置模块由用户独立管理，不包含在本模块中。

### Limitations / 边界

广告和登录、交易等业务共用 HTTPS 主机时，按路径过滤需要先解密该主机。为保护敏感业务，这部分广告可能恢复。保留了金融服务的专用广告/图片域名，不代表所有金融服务完全不经 MITM。

请关闭或移除原来的 AdvertisingLite、AdvertisingLite MITM (2)，避免重复规则。也不建议与 AllInOne 或其他会覆盖 MITM 名单的模块同时启用。负向匹配必须在相关正向匹配之前；如有其他模块，请检查合并后的生效配置。

更新本模块时沿用同一个 raw 地址。此仓库维护的是经审查的规则快照，不会自动跟随上游变化。Map Local 的空响应仍引用上游公开的 `blank` 资源，需要能够下载这些资源。

### Validation / 验证

`python3 test_module.py` 运行基础隐私、顺序和广告拦截检查；安装后的生效验证还需使用 Surge。

2026-09-30 在 Surge Mac 6.10.0 上验证：敏感主机使用原站证书，保留的广告路径仍返回空响应。未逐个验证全部 App、登录和广告位；iOS 使用相同模块语法，但未进行设备实测。

### Attribution / 来源与许可

规则来源：[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)，AdvertisingLite 的 2025-07-12 本地安装快照。原作者：blackmatrix7。

2026-09-30，lswang6 修改 MITM 范围，加入排除条目并将原配置已拦截的 78 个广告域名并入模块。上游模块 SHA-256：`728bc7c8077b0346efe92287f2f96e42875c86722a2a3238604d8582b4c4c5fd`。

本派生模块按上游 **GNU GPL version 2** 发布，完整条款见 [LICENSE](LICENSE)。上游项目与 Surge 官方不为本次修改背书。

Surge 官方文档：[模块](https://manual.nssurge.com/profile/module.html) · [MITM 与负向匹配](https://manual.nssurge.com/http/mitm.html)。

## 文件级许可范围

本仓库包含独立来源的作品，根目录 `LICENSE` 不覆盖所有文件：

| 文件 | 许可 |
| --- | --- |
| `AdvertisingLite-Privacy.sgmodule` | GPL-2.0，见 `LICENSE` |
| `Google-Maps-CN-Offset.sgmodule`、`test_google_maps_module.py` | GPL-2.0-only，见 `LICENSE` |
| `Advertising-AllInOne-Privacy.sgmodule`、`sources/allinone.sgmodule`、`advertising-allinone-review.json`、`build_advertising_allinone.py`、`test_advertising_allinone.py`、`ALLINONE-REVIEW.md` | GPL-2.0-only，见 `LICENSE` |
| `WeChat-Ads-Privacy.sgmodule` | GPL-3.0-only，见 `LICENSE-GPL-3.0` |
| `Sukka-Reject-Balanced.domainset`、`Sukka-Reject-Balanced.list`、`Sukka-Reject-Balanced.sgmodule`、`sources/sukka-reject.conf`、`sukka-review.json`、`build_sukka.py`、`test_sukka.py`、`SUKKA-REVIEW.md` | AGPL-3.0-only，见 `LICENSE-AGPL-3.0` |

Sukka 原始规则 © Sukka 与贡献者；本次修改由 lswang6 于 2026-09-30 完成。各模块的来源说明、署名与许可分别保留。
