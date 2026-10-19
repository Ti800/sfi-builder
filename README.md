# sfi-builder

从官方 [SagerNet/sing-box](https://github.com/SagerNet/sing-box)（含 `clients/apple` 子模块）构建 **完整版** sing-box iOS 客户端（SFI）未签名 IPA，供企业证书等自行重签。

- 自动：每 6 小时检查官方最新 release（含预发布），有新版本即构建并发布到 Releases
- 手动：Actions → Build SFI IPA → Run workflow，可指定 tag、通道、Bundle ID

## 重签要点
| Bundle | Bundle ID | 关键权限 |
|---|---|---|
| sing-box.app | `<id>` | Network Extension (packet-tunnel), App Group `group.<id>`, iCloud（可选） |
| Extension.appex | `<id>.extension` | Network Extension (packet-tunnel), App Group |
| WidgetExtension / ShareExtension / ActionExtension / FileProviderExtension / IntentsExtension | `<id>.widget/.share/.action/.fileprovider/.intents` | App Group |

Release 附带 `entitlements-*.zip`（已展开变量），可供重签工具参考。
App Group 必须与 Info.plist 中 `AppGroupIdentifier`（`group.<id>`）一致，否则 VPN 扩展与主 App 无法共享配置；如证书的 Bundle ID 不同，用 Run workflow 填 `bundle_id` 重新编译即可。

## AltStore / Feather 源
```
https://raw.githubusercontent.com/Ti800/sfi-builder/main/source.json
```
自定义 `bundle_id` 构建会生成 `source-<bundle_id>.json`。每次构建后自动更新。
