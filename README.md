# Surge Modules

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
