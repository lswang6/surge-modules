# Surge Modules

## WeChat Ads Privacy / 微信去广告（免解密）

小程序广告拦截补充模块，使用 10 条精确域名规则，无需 MITM 或远程脚本。可与下面的 AdvertisingLite Privacy 一起使用。

[查看模块](WeChat-Ads-Privacy.sgmodule) · [Raw 下载](https://raw.githubusercontent.com/lswang6/surge-modules/main/WeChat-Ads-Privacy.sgmodule)

在 Surge「模块 → 从 URL 安装」粘贴：

```text
https://raw.githubusercontent.com/lswang6/surge-modules/main/WeChat-Ads-Privacy.sgmodule
```

- 拦截 `wxsnsdy.wxs.qq.com`、`wxsmsdy.video.qq.com`、`wxsnsdythumb.wxs.qq.com` 三个小程序广告资源域名。
- 拦截 `ads-shopping.shouqianba.com`、`ad.maoyan.com` 两个广告域名。这两项也会影响同域名的独立 App 广告。
- 补充捷停车 `e.jparking.cn`、丰巢 `dsp.fcbox.com`、闪送 `ads.ishansong.com`、小兔充充 `ad.xiaotucc.com`、小电充电 `smarket.dian.so`。规则同样作用于独立 App 对这些主机的请求。
- 不拦截整个 `wxs.qq.com`、`qq.com`、`qpic.cn` 或 `servicewechat.com`；不添加公众号、聊天、支付、登录或银行接口的 MITM。现有代理、DNS 和证书设置不变。

**边界：**这是按域名过滤，无法区分同一域名内的广告与其他内容，也不能保证屏蔽公众号、朋友圈或视频号广告。小程序“看广告领奖励”可能无法使用；如出现内容加载异常，停用本模块对照。模块不清理已缓存广告，不自动同步上游。它不改变其他模块的解密行为；与 AdvertisingLite Privacy 配合时，继续保留 `-mp.weixin.qq.com` 排除。

### 审查结论与参考（2026-09-30）

| 来源 | 做法 | 本次取舍 |
| --- | --- | --- |
| [whatshub 迁移后的模块](https://yfamilys.com/module/wechatad.module) / [GitHub 同名模块](https://github.com/deezertidal/shadowrocket-rules/blob/main/modules/wechatad.module) | 对 `mp.weixin.qq.com/mp/getappmsgad` 调用 [NobyDa Wechat.js](https://github.com/NobyDa/Script/blob/0b8d083d444f4476700cb9d5d059c07b42da85eb/QuantumultX/File/Wechat.js)，清空广告字段 | 需要解密整个公众号主机，与既有排除冲突；未采用。原站返回迁移通知，核对的是新站内容及 GitHub 副本。 |
| [fmz200 微信小程序规则](https://github.com/fmz200/wool_scripts/blob/3ca7487b4e4b86d9af76e50df72c62eacfbb659e/Loon/plugin/WeChatMiniAds.plugin) | 精确广告域名，以及大量小程序接口重写和脚本 | 采用 6 条 DOMAIN 规则，并将丰巢、闪送、小兔充充和小电的 4 条广告主机重写改为精确域名拦截。域名用途判断来自上游规则，并非对服务器全部接口的验证；不加入银行、乘车码、登录、订单等共用业务接口。 |
| [fmz200 公众号模块](https://github.com/fmz200/wool_scripts/blob/3ca7487b4e4b86d9af76e50df72c62eacfbb659e/Surge/module/split/partW/WeChatOfficialAccount.sgmodule) / [QingRex 公众号模块](https://github.com/QingRex/LoonKissSurge/blob/913ec005f544221e6c56a7d0ecec81c4b3b914bb/Surge/微信公众号去广告.sgmodule) | 响应修改或按路径返回空 JSON；后者还拦截整个 `wxs.qq.com` | 同样需要公众号 MITM；未采用整站拦截，也未删除相关文章、搜索等非纯广告功能。 |
| [ddgksf2013 微信规则](https://github.com/ddgksf2013/Rewrite/blob/dc3ea2c1fb2db870676b26da24006083eb1d44d3/AdBlock/WeChat.conf) | 同一个 `getappmsgad` 接口的响应替换 | 作者已标注“已失效”，且不包含公众号信息流、朋友圈广告。未将这些旧规则计作有效覆盖。 |

Surge 的 MITM 按主机启用，脚本只匹配一个广告路径，并不代表只解密该路径。负向名单优先命中时，公众号广告脚本也无法处理对应 HTTPS 响应。见 [Surge MITM 文档](https://manual.nssurge.com/http/mitm.html)。

检查时，当前 Mac 配置把上述三个微信广告域名放行到 DIRECT；收钱吧、猫眼、捷停车和丰巢已被其他规则拦截。本模块的规则会插入主配置规则顶部，让这些广告拦截优先于宽泛的微信直连规则。已有同类精确 REJECT 规则时不必重复安装。

验证：`python3 test_wechat_module.py` 检查精确拦截和免解密边界；另以 Surge CLI 检查含这些规则的测试配置。没有实际登录微信逐个测试广告位、聊天、支付、小游戏奖励或 iOS，规则来源不等于效果保证。

来源为 fmz200/wool_scripts 的上述固定快照，原插件署名可莉及其贡献者。lswang6 于 2026-09-30 整理为十条 Surge 域名规则；本模块按 **GPL-3.0-only** 发布，见 [LICENSE-GPL-3.0](LICENSE-GPL-3.0)。下方 AdvertisingLite Privacy 仍使用其原有 GPL-2.0 许可。

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
