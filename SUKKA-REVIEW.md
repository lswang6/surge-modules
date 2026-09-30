# Sukka Reject Balanced：审查与使用说明

<!-- SPDX-License-Identifier: AGPL-3.0-only -->

本文件记录 2026-09-30 对 `https://ruleset.skk.moe/List/domainset/reject.conf` 的兼容性调整。本派生版由 lswang6 维护，不代表 Sukka 或 Surge 官方建议。

## 原文件已经可以用于 Surge

它是 **DOMAIN-SET 域名集**，不是完整配置，也不是可以直接用 `RULE-SET` 引用的文件。文件扩展名不决定语法。

| 内容 | Surge 含义 | 转换后的 `.list` 行 |
| --- | --- | --- |
| `example.com` | 仅精确主机 | `DOMAIN,example.com` |
| `.example.com` | 域名自身及所有子域 | `DOMAIN-SUFFIX,example.com` |

原生域名集适合这种大型纯域名列表。常规 `.list` 只是等价格式，不能通过统一添加 `DOMAIN-SUFFIX` 或仅修改文件扩展名实现。`.list` 内不写策略，策略写在引用它的 `RULE-SET` 行上。

官方语法：[域名规则](https://manual.nssurge.com/rules/domain.html)、[规则集](https://manual.nssurge.com/rules/ruleset.html)、[模块](https://manual.nssurge.com/profile/module.html)。

## 本次快照与范围

- 上游标注更新时间：`2026-09-30T11:11:16.839Z`（台北时间 2026-09-30 19:11:16）。这是文件生成时间，不等于每个域名都在当天验证。
- 原始快照：134,574 条，133,418 条后缀匹配、1,156 条精确匹配；没有重复行或被其他后缀规则完全覆盖的冗余项。
- 原始 SHA-256：`f699906c1c1e0db1614cb4ba29d515002dd5de12cf764f4675a1744533265928`。
- 原始字节保存在 [sources/sukka-reject.conf](sources/sukka-reject.conf)，供复核和重建。
- [发布快照 `393edcad`](https://github.com/SukkaLab/ruleset.skk.moe/blob/393edcad7e2f021383a82242a9614fd4a7aeb917/List/domainset/reject.conf) 与该 SHA-256 完全一致；该发布提交链接到 [构建源码 `38ac44a1`](https://github.com/SukkaW/Surge/tree/38ac44a1ae08ae3038c523beaec0d7390af4dc6b)。快照时间与源码提交时间分开记录。
- 上游本来就覆盖广告、追踪、隐私保护和挖矿拦截。本次不会把所有分析、统计域名视为错误而删除。
- 这是一份有针对性检查的兼容性快照，**没有逐个验证十余万域名**，也不能承诺零误拦或全部广告消失。

上游构建程序会筛选浏览器过滤语法，并非将所有带路径、上下文条件的规则一律升格成整域封锁。源码中一些转换策略可能涉及取舍，但不能仅凭这些策略断言当前产物的某条规则必然误拦。下面的改动以当前快照中的实际条目和服务用途为依据。

## 本次移除 9 条，保留 134,565 条

原始 1,156 条精确匹配全部保留，后缀匹配由 133,418 条减至 133,409 条；没有扩大任何规则。精确删除记录与来源见 [sukka-review.json](sukka-review.json)。

| 删除的原始行 | 原因与证据 |
| --- | --- |
| `.taio.app` | [Taio](https://taio.app/) 是文本编辑器的官网，链接文档与动作目录；整域封锁会覆盖这些正常内容。 |
| `.mob.com` | 覆盖 [SMSSDK 短信验证码校验 API](https://www.mob.com/about/news/360) `webapi.sms.mob.com` 和厂商开发服务；该 API 文档较旧，未实测登录。 |
| `.jpush.cn` | 覆盖 [极光官方推送与设备管理 API](https://docs.jiguang.cn/jpush/server/push/server_overview)，包括 `api.jpush.cn`、`device.jpush.cn`。 |
| `.jiguang.cn` | 覆盖极光官方文档 `docs.jiguang.cn` 和正常开发服务。 |
| `.getui.com` | 覆盖 [个推 REST API](https://docs.getui.com/getui/server/rest_v2/standard/) `restapi.getui.com` 及文档。 |
| `.plus.com` | [Plusnet](https://www.plus.net/help/broadband/about-your-plusnet-webspace/) 将此后缀用于不同客户的网站托管，不宜按整个共享后缀封锁；服务迁移中，未测试具体客户网站。 |
| `.log.aliyuncs.com` | [阿里云 SLS](https://help.aliyun.com/en/sls/developer-reference/get-started-with-log-service-sdk-for-go) 的多租户服务 API 也处理项目管理和日志查询，不只是统计上传。 |
| `.api.statsigcdn.com` | [Statsig 配置下载](https://docs.statsig.com/client/javascript-mono/UsingSpecsDataAdapter) 使用此主机，不只是事件上报；独立事件收集域名继续按上游规则处理。 |
| `.data` | [IANA](https://www.iana.org/domains/root/db/data.html) 确认是已委派顶级域；此规则会覆盖整个命名空间。本版移除属于范围选择，未复现具体用户故障。 |

这些是服务用途与匹配范围的依据，**不是九个已实测故障**。对 Mob、极光、个推、SLS 等混合用途范围的排除，也可能恢复它们承载的部分分析或营销流量；这是保留正常功能的取舍。

没有按厂商品牌整组删除域名：`.jpush.io`、`.getui.cn`、`.getui.net` 等本轮未取得充分的当前官方端点依据，保持上游状态。因此不能宣称恢复了全部推送。普通广告、追踪和独立事件上报域名仍保留。

停车方面保留精确 `e.jparking.cn`，没有扩大为 `jparking.cn` 后缀；`psbg.jparking.cn`、ETCP 与 P云的前述业务主机没有被这份快照命中，不能算作本次删除项。真实停车扫码与支付流程未测试。

## 安装：三种形式任选一种

推荐在现有配置中直接替换原来的 `DOMAIN-SET` 地址，保留已有策略组和规则顺序。对已有 `AdBlockLite` 策略组的配置：

```ini
DOMAIN-SET,https://raw.githubusercontent.com/lswang6/surge-modules/main/Sukka-Reject-Balanced.domainset,AdBlockLite,extended-matching
```

其他配置可使用内置 `REJECT`，但不要复制一个不存在的策略组名称：

```ini
DOMAIN-SET,https://raw.githubusercontent.com/lswang6/surge-modules/main/Sukka-Reject-Balanced.domainset,REJECT,extended-matching
```

若需要常规 `.list`，改用下面这一行，**不要同时安装两份**：

```ini
RULE-SET,https://raw.githubusercontent.com/lswang6/surge-modules/main/Sukka-Reject-Balanced.list,REJECT,extended-matching
```

若希望通过模块开关管理，可在 Surge「模块 → 从 URL 安装」使用：

```text
https://raw.githubusercontent.com/lswang6/surge-modules/main/Sukka-Reject-Balanced.sgmodule
```

模块只有一条引用本仓库域名集的 `REJECT` 规则，不含 MITM、脚本、DNS 设置或 `DIRECT` 白名单。Surge 将模块规则插在主配置规则前面，所以它可能先于主配置里的放行规则命中，也不受原 `AdBlockLite` 策略组开关控制。需要保留主配置例外和策略选择时，优先用前面的地址替换方式。

## 删除条目不等于全局放行

本次没有添加强制 `DIRECT` 规则。被删除的域名继续交给用户原有的后续规则处理，不改变它应当直连还是代理。

如果旧版域名集仍然启用，它仍可能命中已删除的条目；不要只叠加新版。当前配置还同时引用另外两份上游规则，2026-09-30 核对结果：

| 其他规则 | 本次发现的重叠项 |
| --- | --- |
| `List/non_ip/reject-drop.conf` | `jpush.cn`、`jpush.io`、`getui.com`、`getui.net` 的后缀匹配 |
| `List/non_ip/reject.conf` | `data` 的后缀匹配会继续覆盖本次移除的 `.data`；另有 `pgi.com`，但本次未将它列为删除项 |

本次只派生用户提供的域名集，**未改动这两份独立规则或当前 Surge 配置**。若需要这些服务恢复可用，还应在对应拦截来源中排除相关条目；其他模块、DNS 去广告也可能继续拦截。用 `surge-cli rule explain https://域名/` 查看实际命中来源，不要靠强制直连绕过正常路由。

## 更新与验证

本仓库维护审核后的快照；客户端刷新 Raw 地址只会取得本仓库已经发布的版本，不会自动合并 Sukka 的每日变化。原始快照、审查记录与转换脚本一同公开，后续更新必须重新核对差异和排除范围。

重建：`python3 build_sukka.py`。离线检查：`python3 test_sukka.py`。脚本对原始快照校验 SHA-256，缺失排除项或非法输入直接报错，不静默生成不完整列表。

本次验证覆盖精确/后缀语义、排除效果、可重建性和模块内容。Surge CLI 仅检查仓库外临时配置的语法，未切换或加载当前配置；不等于真实广告、推送、扫码、支付或 iOS 设备验收。

## 来源与许可

原始规则 **Surge © Sukka**，由 Sukka 与贡献者维护。本次筛选、格式转换与包装由 lswang6 于 2026-09-30 完成；保留上游署名、来源链接和识别条目。修改后的输出不沿用原文件的内容哈希。

[上游 README 的 License 声明](https://github.com/SukkaW/Surge/blob/38ac44a1ae08ae3038c523beaec0d7390af4dc6b/README.md#license) 与 [完整 AGPL v3 许可](https://github.com/SukkaW/Surge/blob/38ac44a1ae08ae3038c523beaec0d7390af4dc6b/LICENSE) 为本次依据。本派生规则及转换代码按 **AGPL-3.0-only** 发布，完整条款见 [LICENSE-AGPL-3.0](LICENSE-AGPL-3.0)。原始快照、排除记录、转换代码同时提供；详细文件范围见 [README](README.md#文件级许可范围)。其他独立模块维持各自许可。
