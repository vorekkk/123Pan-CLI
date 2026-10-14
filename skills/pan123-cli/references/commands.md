## 0.1.0 使用说明

先按[安装与使用](configuration.md)安装，使用显式 `--env-file` 或进程环境提供凭据。支持 `CLIENT_ID` / `CLIENT_SECRET` 兼容别名；只在本机代理使用 Fake-IP DNS 时明确传入 `--allow-fake-ip`。所有子命令 help 可离线查看。

实现采用 77 个端点/协议命令定义覆盖 72 个独立 HTTP 路由，另包含高层传输和本地认证命令。底层 API 的受保护 session / URL 文件避免在 stdout 暴露预上传标识与能力地址。

本文保留原始设计解释和文档差异；具体可用选项、拼写及默认值以运行时 `--help` 为准。API 资料覆盖、模拟测试、真实账户通过是三个独立状态，详见[覆盖清单](api-mapping.md)。

# 123Pan CLI 完整命令参考

编写日期：2026-10-14（Asia/Shanghai）。状态：CLI 0.1.0 已实现；完整命令参数以运行时 --help 为准。

本参考与[技术栈与开发文档](parser-help.md)配套，按全部 API 来源逐项设计命令。输入与返回表来自独立保存的历史官方快照；CLI 参数形式、状态文件和交互规则是本工程的设计。快照目录原名为 260910，实际采集时间为 2026-09-11 08:58:08（北京时间）。真实 API 验收只覆盖[真实联调记录](api-mapping.md)列出的文件管理链路，其余业务域尚未执行真实验证。

87 篇来源中，74 篇声明 API；同一 method/path 重复引用合并后为 72 个独立 OpenAPI 接口。另有 OAuth 浏览器授权页面、返回 URL 的预签名 PUT / CDN GET，以及使用现有接口编排的业务流程。流程指南、规则、FAQ 和空导航页保留来源映射，不虚构为额外接口。

## 官方直连约定

本参考的所有 OpenAPI 命令直接访问 `https://open-api.123pan.com`。developer 模式在本机取得和缓存官方 accessToken，使用官方 Bearer / Platform；OAuth 使用官方授权和 token 接口。上传及下载只使用官方接口返回的传输地址。

全部命令的调用链路不接入自部署网关，不生成或发送 stoken，也不使用 Appwrite JWT；本工程没有网关地址或网关鉴权配置。具体 token / URL 路由和测试规范见技术文档。

## 命令导航

```text
pan123
├── auth ensure | status | clear
├── oauth authorize-url | exchange | refresh
├── user info
├── file
│   ├── list [--api-version v2|v1]
│   ├── info | infos | mkdir | rename | rename-batch
│   ├── trash | copy | copy-batch | copy-progress
│   ├── recover | recover-to | move | safebox-unlock
│   ├── upload | download | download-url
│   └── upload-api
│       ├── v1 create | url | put | parts | complete | result
│       └── v2 create | slice | complete | domains | single | sha1-reuse
├── share create | list | update
│   └── payment create | list | update
├── offline create | progress
├── directlink url | enable | disable | cache-refresh | traffic-logs | offline-logs
│   └── blacklist list | update | switch
├── image
│   ├── upload | mkdir | list | info | move | delete
│   ├── source-copy | source-copy-progress | source-copy-failures
│   ├── offline-create | offline-progress
│   └── upload-api create | get-url | put-slice | complete | async-result
└── transcode
    ├── source-list | folder-list | folder-info | upload | from-cloud
    ├── resolutions | list | run | records | result | delete
    └── download-url | segment-url | all-download-urls
```

`list`、`upload`、`download` 作为根入口别名，分别与 `file list`、`file upload`、`file download` 等价。通用 `--help`、`--version`、`--json`、`--verbose`、`--auth-mode`、`--config`、`--env-file`、超时与输出通道规范见技术文档。

正文中的 `[...]`、`ID`、`PATH`、`NAME` 为设计调用形式，不是可以原样执行的 shell 命令。数值型和字符串型 ID 不互换，标量旗标与描述相同字段的 --request-file 互斥；同一调用只能有一个 stdin 输入消费者。正常创建不默认要求 --yes，有破坏性或可能消耗权益的命令逐项标明确认规则。

## 下载地址命令补充

`pan123 file download-url --file-id ID [--json]` 精确映射 `GET https://open-api.123pan.com/api/v1/file/download_info?fileId=ID`，输入 `fileId:number` 必填，输出 `data.downloadUrl:string`。它返回用户主动请求的完整能力 URL，不下载文件、不承诺链接有效时长或文件已校验。错误 5113 / 5066、Bearer 与 Platform 以及日志脱敏规则与 file download 的地址获取步骤一致。后续 file download 高层流程仍先查详情、下载字节并校验。

以下按业务域提供每条命令的完整字段、类型、必填性、HTTP 参数位置、返回值及限制。

## 命令规格 A：鉴权、文件、分享、离线下载及账号

本节是独立 `123Pan-CLI` 的命令与来源契约参考。CLI 0.1.0 已覆盖全部声明端点。以下 HTTP 字段来自 2026-09-11 获取的官方快照；真实验证仅包含[联调记录](api-mapping.md)列出的文件链路。授权与配额限制由官方返回决定。运行参数以 `pan123 <命令> --help` 为准。

全局 `--auth-mode developer|oauth`（环境变量 `PAN123_AUTH_MODE`，默认 developer）决定 token 来源。开发者身份使用 `PAN123_CLIENT_ID` / `PAN123_CLIENT_SECRET`；第三方 OAuth 身份使用独立 `PAN123_OAUTH_CLIENT_ID` / `PAN123_OAUTH_CLIENT_SECRET` / `PAN123_OAUTH_REDIRECT_URI`，不把两类凭据互换。

所有标记 `域名` 的 OpenAPI URL 统一为 `https://open-api.123pan.com`。除开发者 token 获取、OAuth 授权页/交换、预签名 PUT 和返回的下载链接外，OpenAPI 使用 `Authorization: Bearer <当前身份 token>` 与 `Platform: open_platform`。JSON POST/PUT 使用 `application/json`；multipart 交由编码器产生 boundary。通用 API 成功取决于 `code=0`，业务错误保留 `code/message/x-traceID`；OAuth 裸响应与预签名 PUT 是明确例外。

全局 `--json` 控制输出格式；`--request-file PATH` 接收完整 JSON Body，`-` 表示 stdin，与同名标量/集合参数互斥。表中未传入的可选字段省略，不能默默发送 null/0/false。`--session-file` 是 CLI 生成并保护的上传状态文件，不把 token、签名 URL 或 preuploadID 写入普通日志；内容需绑定当前 auth-mode、账号身份、源文件 MD5/大小、源 API、可信 HTTPS 服务器；本次设计不引入 profile。状态输出为本地权限 0600 的文件（Windows 使用当前用户访问控制）；文件内不存 token/client_secret，只保存必要的上传任务 capability 元数据。`create --session-out PATH` 和 `domains --domains-out PATH` 可指定输出，省略时分别生成 `<state-dir>/uploads/<随机ID>.json` 和 `<state-dir>/upload-domains/<随机ID>.json`，stdout 仅返回脱敏完成状态及所生成路径，后续 `--session-file`/`--domains-file` 使用该路径。保存 session 不代表已支持跨进程断点续传。写入状态与 `--json` 脱敏规则在主文档统一定义。同一条命令最多一个 stdin 消费者：`--request-file -`、`--code-stdin`、`--client-secret-stdin`、`--refresh-token-stdin` 等不得组合，参数冲突在任何请求前拒绝；其余敏感值从各自环境变量读取。所有 `--wait` 是 CLI 有界等待，只调用已有的进度接口或明确允许重复查询的完成接口，不发明新 API。
### A.1 `auth ensure / auth status / auth clear`

**设计调用：**

```shell
pan123 auth ensure [--client-id ID] [--client-secret-stdin]
pan123 auth status
pan123 auth clear
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/access_token`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --client-id / PAN123_CLIENT_ID | `clientID` | string；必填；允许非敏感 ID 参数 |
| --client-secret-stdin / PAN123_CLIENT_SECRET | `clientSecret` | string；必填；不接受密钥值 argv |
| 缓存凭据，不暴露值 | `accessToken / expiredAt` | 响应；token 保密，按 expiredAt 判断失效 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| clientID | string | 必填 |  |
| clientSecret | string | 必填 |  |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| accessToken | string | 必填 | 访问凭证 |
| expiredAt | string | 必填 | access_token过期时间 |

**行为与边界：** ensure 在 developer 模式先读取有效缓存，必要时调用获取凭据接口；在 oauth 模式只校验相应缓存，缺失或失效时引导执行 oauth exchange/refresh，不以开发者凭据代换或自动重放刷新；status 只输出身份模式、过期时间、缓存是否可用，不打印 token；clear 只清除本地缓存，不调用并不存在的远程注销接口。JSON 请求需 Platform: open_platform，无 Bearer。token 有效期按 expiredAt 的带时区时间处理；共享缓存加锁及原子写入，避免同 client_id 多次颁发导致超过 3 个同时使用 token。auth 的 --json 仅输出脱敏元数据；原始响应中的 accessToken 永不输出到日志。

**依据：** [接入指南/开发者接入/获取access_token.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E5%BC%80%E5%8F%91%E8%80%85%E6%8E%A5%E5%85%A5/%E8%8E%B7%E5%8F%96access_token.md)。

### A.2 `oauth authorize-url`

**设计调用：**

```shell
pan123 oauth authorize-url --client-id APP_ID --redirect-uri URI [--state STATE]
```

**HTTP 契约：** `本机生成 URL；用户浏览器访问 GET https://yun.123pan.com/auth?client_id=...&redirect_uri=...&scope=...&state=...`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --client-id / PAN123_OAUTH_CLIENT_ID | `client_id` | string；必填 |
| --redirect-uri / PAN123_OAUTH_REDIRECT_URI | `redirect_uri` | string；必填；已注册回调地址 |
| CLI 固定 scope | `scope` | string；必填；user:base,file:all:read,file:all:write |
| --state 或本机生成随机值 | `state` | string；必填；本机保存并在回调时核对 |

**源契约：授权 query 字段**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| __CLIENT_ID__ | string | 是 | client_id（app_id） |
| __REDIRECT_URL__ | string | 是 | 回调地址 |
| __SCOPE__ | string | 是 | 固定为：user:base,file:all:read,file:all:write |
| __STATE__ | string | 是 | 自定义参数 |

**本地输出：** 授权 URL 及已生成 state 的受保护本地状态；此页不声明响应 JSON。

**行为与边界：** 本命令只构造并输出授权 URL，不把它当作获取 token 的 API。授权正式域名为 https://yun.123pan.com。使用 urllib 进行 query 编码，不能简单字符串拼接。OAuth 凭据是获平台审核的第三方应用 appId/secretId，不能承诺普通开发者 client_id/client_secret 自动具备同等授权资格。

**依据：** [接入指南/第三方挂载应用接入/授权地址.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E7%AC%AC%E4%B8%89%E6%96%B9%E6%8C%82%E8%BD%BD%E5%BA%94%E7%94%A8%E6%8E%A5%E5%85%A5/%E6%8E%88%E6%9D%83%E5%9C%B0%E5%9D%80.md)。

### A.3 `oauth exchange / oauth refresh`

**设计调用：**

```shell
pan123 oauth exchange --client-id APP_ID --redirect-uri URI --code-stdin --state STATE
pan123 oauth refresh [--refresh-token-stdin]
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/oauth2/access_token`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --client-id / PAN123_OAUTH_CLIENT_ID / 当前 OAuth 应用身份 | `client_id` | string；必填；appId |
| --client-secret-stdin / PAN123_OAUTH_CLIENT_SECRET | `client_secret` | string；必填；应用 secretId，敏感 |
| exchange 固定 authorization_code；refresh 固定 refresh_token | `grant_type` | string；必填 |
| --code-stdin / 受保护回调输入 | `code` | string；exchange 必填；敏感 |
| --refresh-token-stdin 或受保护缓存 | `refresh_token` | string；refresh 必填；单次有效，敏感 |
| --redirect-uri / PAN123_OAUTH_REDIRECT_URI | `redirect_uri` | string；exchange 必填；refresh 不发送 |
| --state / 已验证回调输入 | 本地 state 校验 | exchange 本地必需；与授权时保存值比对；不发送 token endpoint |

**源契约：QueryString 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| client_id | string | 是 | 应用标识，创建应用时分配的 appId |
| client_secret | string | 是 | 应用密钥，创建应用时分配的 secretId |
| grant_type | string | 是 | 身份类型 authorization_code 或 refresh_token |
| code | string | 否 | 授权码 |
| refresh_token | string | 否 | 刷新 token，单次请求有效 |
| redirect_uri | string | 否 | authorization_code时必携带，应用注册的回调地址 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| token_type | string | 是 | Bearer |
| access_token | string | 是 | 用来获取用户信息的 access_token。 刷新后，旧 access_token 立即失效 |
| refresh_token | string | 是 | 单次有效，用来刷新 access_token，90 天有效期。刷新后，返回新的 refresh_token，请保存以便下一次刷新使用。 |
| expires_in | number | 是 | access_token的过期时间，单位秒。 |
| scope | string | 是 | 权限 |

**行为与边界：** exchange 在发送 token 请求前必须将 --state 或已验证回调输入与 authorize-url 保存的随机 state 比对，缺失/不一致拒绝交换；该 state 是本地校验字段，不能发送到源文档未声明的 token 参数中。精确契约为 POST + QueryString；不能擅自改为 GET 或 JSON Body。此接口响应是裸对象 token_type/access_token/refresh_token/expires_in/scope，不使用通用 code/message/data 包装。刷新会让旧 access_token 立即失效，refresh_token 单次有效、90 天有效；刷新成功必须在同一缓存锁内原子替换新 token pair，超时且结果未知时不得自动重放单次 refresh token。含 client_secret/code/refresh_token 的完整 query URL、HTTP 调试日志及代理日志必须脱敏。exchange/refresh 默认只输出 token 元数据并写受保护缓存，不在 stdout 打印 token。

**依据：** [接入指南/第三方挂载应用接入/授权code获取access_token.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E7%AC%AC%E4%B8%89%E6%96%B9%E6%8C%82%E8%BD%BD%E5%BA%94%E7%94%A8%E6%8E%A5%E5%85%A5/%E6%8E%88%E6%9D%83code%E8%8E%B7%E5%8F%96access_token.md)。

### A.4 `file list（推荐 V2）`

**设计调用：**

```shell
pan123 file list --parent-id 0 [--limit 100] [--last-file-id ID] [--search TEXT] [--all] [--include-trashed] [--json]
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v2/file/list`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --parent-id | `parentFileId` | number；必填；根目录 0 |
| --limit | `limit` | number；必填；最大 100；CLI 可提供默认 100 |
| --search | `searchData` | string；选填；忽略目录，执行全局搜索 |
| --last-file-id | `lastFileId` | number；选填；后续页 cursor |

**源契约：QueryString 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| parentFileId | number | 必填 | 文件夹ID，根目录传 0 |
| limit | number | 必填 | 每页文件数量，最大不超过100 |
| searchData | string | 选填 | 搜索关键字将无视文件夹ID参数。将会进行全局查找 |
| lastFileId | number | 选填 | 翻页查询时需要填写 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |  |
| --- | --- | --- | --- | --- |
| lastFileId | number | 必填 | -1代表最后一页（无需再翻页查询）其他代表下一页开始的文件id，携带到请求参数中 |  |
| fileList | array | 必填 | 文件列表 |  |
|  | fileId | number | 必填 | 文件Id |
|  | filename | string | 必填 | 文件名 |
|  | type | number | 必填 | 0-文件 1-文件夹 |
|  | size | number | 必填 | 文件大小 |
|  | etag | string | 必填 | md5 |
|  | status | number | 必填 | 文件审核状态。 大于 100 为审核驳回文件 |
|  | parentFileId | number | 必填 | 目录ID |
|  | category | number | 必填 | 文件分类：0-未知 1-音频 2-视频 3-图片 |
|  | trashed | int | 必填 | 文件是否在回收站标识：0 否 1是 |

**行为与边界：** 返回 lastFileId=-1 才是最后一页；--all 由 CLI 按返回 cursor 逐页请求，设置重复 cursor 防护，不依据过滤后为空停止。接口包含回收站文件，默认本地过滤 trashed=1，--include-trashed 保留；此参数是本地呈现策略，不作为不存在的 API query 发送。--search 明确提示全局搜索。字段 fileId/parentFileId 与详情 API 的大写 ID 不同。

**依据：** [API列表/文件管理/文件列表/获取文件列表（推荐）.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8/%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89.md)。

### A.5 `file list --api-version v1（兼容）`

**设计调用：**

```shell
pan123 file list --api-version v1 --parent-id 0 --page 1 --limit 100 --order-by file_id --order-direction asc [--trashed true] [--search TEXT]
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v1/file/list`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --parent-id | `parentFileId` | number；必填 |
| --page | `page` | number；必填 |
| --limit | `limit` | number；必填；最大 100 |
| --order-by | `orderBy` | string；必填；例 file_id/size/file_name |
| --order-direction | `orderDirection` | string；必填；asc/desc |
| --trashed | `trashed` | bool；选填 |
| --search | `searchData` | string；选填 |

**源契约：QueryString 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| parentFileId | number | 必填 | 文件夹ID，根目录传 0 |
| page | number | 必填 | 页码数 |
| limit | number | 必填 | 每页文件数量，最大不超过100 |
| orderBy | string | 必填 | 排序字段,例如:file_id、size、file_name |
| orderDirection | string | 必填 | 排序方向:asc、desc |
| trashed | bool | 选填 | 是否查看回收站的文件 |
| searchData | string | 选填 | 搜索关键字 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileList | array | 必填 |  |
| fileList[*].fileID | number | 必填 | 文件ID |
| fileList[*].filename | string | 必填 | 文件名 |
| fileList[*].type | number | 必填 | 0-文件 1-文件夹 |
| fileList[*].size | number | 必填 | 文件大小 |
| fileList[*].etag | boolean | 必填 | md5 |
| fileList[*].status | number | 必填 | 文件审核状态。 大于 100 为审核驳回文件 |
| fileList[*].parentFileId | number | 必填 | 目录ID |
| fileList[*].parentName | string | 必填 | 目录名 |
| fileList[*].category | number | 必填 | 文件分类：0-未知 1-音频 2-视频 3-图片 |
| fileList[*].contentType | number | 必填 | 文件类型 |

**行为与边界：** 该接口为旧版本，采用页码和显式排序，不能使用 V2 lastFileId。源返回表把 etag 写成 boolean，但响应示例为 MD5 string；示例还包含未列入返回表的 total。模型保留原始响应并将这些差异作为兼容用例；不要用示例字段冒充保证存在的 schema。初始兼容命令按单页查询，不将 total 缺失时的自动全页流程写成已验证能力。

**依据：** [API列表/文件管理/文件列表/获取文件列表（旧）.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8/%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8%EF%BC%88%E6%97%A7%EF%BC%89.md)。

### A.6 `file info`

**设计调用：**

```shell
pan123 file info --file-id ID
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v1/file/detail`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --file-id | `fileID` | number；必填；QueryString，大写 ID |

**源契约：QueryString 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileID | number | 必填 | 文件ID |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileID | number | 必填 | 文件ID |
| filename | string | 必填 | 文件名 |
| type | number | 必填 | 0-文件 1-文件夹 |
| size | number | 必填 | 文件大小 |
| etag | string | 必填 | md5 |
| status | number | 必填 | 文件审核状态。 大于 100 为审核驳回文件 |
| parentFileID | number | 必填 | 父级ID |
| createAt | string | 必填 | 文件创建时间 |
| trashed | number | 必填 | 该文件是否在回收站0否、1是 |

**行为与边界：** 返回 etag 是 MD5；type=1 是目录，详情支持文件夹包含文件大小；status>100 为审核驳回，trashed=1 为回收站。禁止把文件夹直接作为普通单文件下载。

**依据：** [API列表/文件管理/文件详情/获取单个文件详情.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85/%E8%8E%B7%E5%8F%96%E5%8D%95%E4%B8%AA%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85.md)。

### A.7 `file infos`

**设计调用：**

```shell
pan123 file infos --file-id ID --file-id ID [--request-file request.json]
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/file/infos`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| 重复 --file-id / --request-file 中 fileIds | `fileIds` | []number；必填；JSON Body |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileIds | []number | 是 | 文件id |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileList | array | 是 |  |
| fileList[*].fileId | number | 是 | 文件ID |
| fileList[*].filename | string | 是 | 文件名 |
| fileList[*].parentFileId | number | 是 | 目录ID |
| fileList[*].type | number | 是 | 0-文件 1-文件夹 |
| fileList[*].etag | string | 是 | md5 |
| fileList[*].size | number | 是 | 文件大小 |
| fileList[*].category | number | 是 | 文件分类：0-未知 1-音频 2-视频 3-图片 |
| fileList[*].status | number | 是 | 文件审核状态。 大于 100 为审核驳回文件 |
| fileList[*].punishFlag | number | 是 | 惩罚标记 |
| fileList[*].s3KeyFlag | string | 是 | 关联s3_key的初始用户标识 |
| fileList[*].storageNode | string | 是 | m0是ceph，m1以上为minio |
| fileList[*].trashed | number | 是 | 是否在回收站：[0：否，1：是] |
| fileList[*].createAt | string | 是 | 创建时间 |
| fileList[*].updateAt | number | 是 | 更新时间 |

**行为与边界：** 该页面没有明确单次最大数量，不能虚构一个官方上限。原字段表 updateAt 写 number，但示例是日期字符串，保留并兼容真实类型。--request-file 使用完整请求对象 {"fileIds":[...]}；与重复参数互斥。

**依据：** [API列表/文件管理/文件详情/获取多个文件详情.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85/%E8%8E%B7%E5%8F%96%E5%A4%9A%E4%B8%AA%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85.md)。

### A.8 `file mkdir`

**设计调用：**

```shell
pan123 file mkdir --name NAME --parent-id 0
```

**HTTP 契约：** `POST https://open-api.123pan.com/upload/v1/file/mkdir`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --name | `name` | string；必填；不能重名 |
| --parent-id | `parentID` | number；必填；根目录 0 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| name | string | 必填 | 目录名(注:不能重名) |
| parentID | number | 必填 | 父目录id，上传到根目录时填写 0 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| dirID | number | 必填 | 创建的目录ID |

**行为与边界：** 结果为 dirID。与上传 parentFileID、列表 parentFileId 的字段大小写不同，不能复用通用名称直接发送。创建超时结果未知时先查目录，不能盲目重试创建。

**依据：** [API列表/文件管理/上传/创建目录.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/%E5%88%9B%E5%BB%BA%E7%9B%AE%E5%BD%95.md)。

### A.9 `file rename`

**设计调用：**

```shell
pan123 file rename --file-id ID --name NAME
```

**HTTP 契约：** `PUT https://open-api.123pan.com/api/v1/file/name`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --file-id | `fileId` | number；必填 |
| --name | `fileName` | string；必填 |

**源契约：Body参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileId | number | 是 | 文件id |
| fileName | string | 是 | 文件名 |

**输出契约：** 源页未列业务 data schema；按通用包装返回成功/错误摘要，不自行增加业务返回字段。

**行为与边界：** 这是 PUT /api/v1/file/name，不是批量重命名的 POST /rename。源页面没有声明 data 返回字段；成功依据包装 code=0，可在高层操作后通过 file info 读回名称，不能伪造新文件 ID。

**依据：** [API列表/文件管理/重命名/单个文件重命名.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E9%87%8D%E5%91%BD%E5%90%8D/%E5%8D%95%E4%B8%AA%E6%96%87%E4%BB%B6%E9%87%8D%E5%91%BD%E5%90%8D.md)。

### A.10 `file rename-batch`

**设计调用：**

```shell
pan123 file rename-batch --request-file rename.json
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/file/rename`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --request-file 中 renameList | `renameList` | array；必填；成员为 "文件ID\|新的文件名" |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| renameList | array | 必填 | 数组,每个成员的格式为 文件ID\|新的文件名 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |  |
| --- | --- | --- | --- | --- |
| successList | array | 必填 | 成功文件列表 |  |
|  | fileID | number | 必填 | 文件Id |
|  | updateAt | string | 必填 | 更新时间 |
| failList | array | 必填 | 成功文件列表 |  |
|  | fileID | number | 必填 | 文件Id |
|  | message | string | 必填 | 错误原因 |

**行为与边界：** 一次最多 30 个文件；完整 Body 示例 {"renameList":["123|新的文件名.txt"]}。返回 successList 与 failList，必须分别呈现；顶层 code=0 仍可能有部分失败，任一 failList 项应返回部分失败退出码。源表误把 failList 描述写为成功文件列表，实际有 fileID/message，应按失败列表处理。

**依据：** [API列表/文件管理/重命名/批量文件重命名.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E9%87%8D%E5%91%BD%E5%90%8D/%E6%89%B9%E9%87%8F%E6%96%87%E4%BB%B6%E9%87%8D%E5%91%BD%E5%90%8D.md)。

### A.11 `file trash`

**设计调用：**

```shell
pan123 file trash --file-id ID [--file-id ID ...] --yes
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/file/trash`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| 重复 --file-id / --request-file 中 fileIDs | `fileIDs` | array；必填；最多 100 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileIDs | array | 必填 | 文件id数组,一次性最大不能超过 100 个文件 |

**输出契约：** 源页未列业务 data schema；按通用包装返回成功/错误摘要，不自行增加业务返回字段。

**行为与边界：** 将文件送入回收站；无永久删除接口可据此推出。非交互执行必须 --yes，交互确认时显示 ID 数量及操作含义；源页没有 data 返回字段。不要自动拆批后再声称整个批量请求原子成功。

**依据：** [API列表/文件管理/删除/删除文件至回收站.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E5%88%A0%E9%99%A4/%E5%88%A0%E9%99%A4%E6%96%87%E4%BB%B6%E8%87%B3%E5%9B%9E%E6%94%B6%E7%AB%99.md)。

### A.12 `file copy`

**设计调用：**

```shell
pan123 file copy --file-id ID --target-dir-id ID
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/file/copy`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --file-id | `fileId` | number；必填 |
| --target-dir-id | `targetDirId` | number；必填 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileId | number | 必填 | 文件id |
| targetDirId | number | 必填 | 要复制到的目标文件夹id |


**源契约：响应参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| sourceFileId | number | 必填 | 源文件id |
| targetFileId | number | 必填 | 新复制文件id |

**行为与边界：** 仅支持单个文件复制，返回 sourceFileId/targetFileId。超时可能已生成目标文件，不自动重放；需要通过目标目录读取核对。

**依据：** [API列表/文件管理/复制单个文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E5%A4%8D%E5%88%B6%E5%8D%95%E4%B8%AA%E6%96%87%E4%BB%B6.md)。

### A.13 `file copy-batch`

**设计调用：**

```shell
pan123 file copy-batch --file-id ID [--file-id ID ...] --target-dir-id ID [--wait]
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/file/async/copy`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| 重复 --file-id / --request-file 中 fileIds | `fileIds` | array；必填 |
| --target-dir-id | `targetDirId` | number；必填 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileIds | array | 必填 | 文件id数组 |
| targetDirId | number | 必填 | 要复制到的目标文件夹id |


**源契约：响应参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| taskId | number | 必填 | 任务id，后续用来查询任务进度 |

**行为与边界：** 单级最多 3000 个；返回 taskId 仅代表创建任务，不代表复制完成。--wait 是 CLI 高层循环调用 copy-progress，必须设置超时并保留 taskId；不同源文件层级的具体策略需联调，不扩大文档的单级上限。

**依据：** [API列表/文件管理/批量复制文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%89%B9%E9%87%8F%E5%A4%8D%E5%88%B6%E6%96%87%E4%BB%B6.md)。

### A.14 `file copy-progress`

**设计调用：**

```shell
pan123 file copy-progress --task-id ID [--wait]
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v1/file/async/copy/process`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --task-id | `taskId` | number；必填；GET 的 JSON Body |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| taskId | number | 必填 | 任务id |


**源契约：响应参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| taskId | number | 必填 | 任务id |
| status | number | 必填 | 任务状态：0-待处理 1-进行中 2-已完成 3-失败 |

**行为与边界：** 该页面表格和 curl/Python 示例都明确 GET 携带 JSON Body，必须使用允许 GET body 的底层 client.request("GET", json=...)，不得擅自改成 QueryString。返回 status=0 待处理、1 进行中、2 完成、3 失败；--wait 针对上述显式状态轮询，终态仅 2/3。

**依据：** [API列表/文件管理/批量复制文件进度.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%89%B9%E9%87%8F%E5%A4%8D%E5%88%B6%E6%96%87%E4%BB%B6%E8%BF%9B%E5%BA%A6.md)。

### A.15 `file recover`

**设计调用：**

```shell
pan123 file recover --file-id ID [--file-id ID ...]
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/file/recover`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| 重复 --file-id / --request-file 中 fileIDs | `fileIDs` | array；必填；最多 100 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileIDs | array | 必填 | 文件id数组,一次性最大不能超过 100 个文件 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| abnormalFileIDs | array | 必填 | 异常文件目录ID（父级目录不存在），可使用还原文件到指定目录接口；无异常文件则为空 |

**行为与边界：** 恢复至删除前位置。abnormalFileIDs 是父目录不存在的异常项，可由用户显式选择 recover-to；不能将异常结果自动转为恢复到根目录。异常 ID 非空应呈现部分失败。

**依据：** [API列表/文件管理/还原/从回收站恢复文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E8%BF%98%E5%8E%9F/%E4%BB%8E%E5%9B%9E%E6%94%B6%E7%AB%99%E6%81%A2%E5%A4%8D%E6%96%87%E4%BB%B6.md)。

### A.16 `file recover-to`

**设计调用：**

```shell
pan123 file recover-to --file-id ID [--file-id ID ...] --parent-id ID
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/file/recover/by_path`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| 重复 --file-id / --request-file 中 fileIDs | `fileIDs` | array；必填；最多 100 |
| --parent-id | `parentFileID` | integer；必填 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileIDs | array | 必填 | 文件id数组,一次性最大不能超过 100 个文件 |
| parentFileID | integer | 必填 | 指定目录id |

**输出契约：** 源页未列业务 data schema；按通用包装返回成功/错误摘要，不自行增加业务返回字段。

**行为与边界：** 恢复至明确指定目录；源页面未定义具体 data 字段，不虚构恢复列表；成功后通过 infos/列表核对位置及 trashed。

**依据：** [API列表/文件管理/还原/还原文件到指定目录.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E8%BF%98%E5%8E%9F/%E8%BF%98%E5%8E%9F%E6%96%87%E4%BB%B6%E5%88%B0%E6%8C%87%E5%AE%9A%E7%9B%AE%E5%BD%95.md)。

### A.17 `file move`

**设计调用：**

```shell
pan123 file move --file-id ID [--file-id ID ...] --parent-id 0
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/file/move`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| 重复 --file-id / --request-file 中 fileIDs | `fileIDs` | array；必填；单级最多 100 |
| --parent-id | `toParentFileID` | number；必填；根目录 0 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileIDs | array | 必填 | 文件id数组 |
| toParentFileID | number | 必填 | 要移动到的目标文件夹id，移动到根目录时填写 0 |

**输出契约：** 源页未列业务 data schema；按通用包装返回成功/错误摘要，不自行增加业务返回字段。

**行为与边界：** 源页面未定义 data 字段；成功后可读取 infos 比较 parentFileId。不要自动扩大单级移动数量限制。

**依据：** [API列表/文件管理/移动.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E7%A7%BB%E5%8A%A8.md)。

### A.18 `file safebox-unlock`

**设计调用：**

```shell
pan123 file safebox-unlock --password-stdin
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v1/safebox/id`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --password-stdin / PAN123_SAFEBOX_PASSWORD | `password` | string；必填；敏感 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| password | string | 必填 | 保险箱密码 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileId | number | 必填 | 保险箱文件 id |

**行为与边界：** 参数章节写 Body，但所有示例实际是 GET /api/v1/safebox/id?password=...。文档保留冲突：实现初始以示例 QueryString 为适配依据，必须联调确认；不能假设 Body 和 query 都有效。password 仅从 stdin/env 接收，URL/query 日志需完全脱敏，不回显或缓存保险箱密码。响应 fileId 为保险箱目录 ID；无文档声明解锁有效期，不能保证永久解锁。

**依据：** [API列表/文件管理/保险箱/解锁保险箱&获取保险箱id.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%BF%9D%E9%99%A9%E7%AE%B1/%E8%A7%A3%E9%94%81%E4%BF%9D%E9%99%A9%E7%AE%B1%26%E8%8E%B7%E5%8F%96%E4%BF%9D%E9%99%A9%E7%AE%B1id.md)。

### A.19 `file download（高层工作流）`

**设计调用：**

```shell
pan123 file download --file-id ID --output PATH [--overwrite --yes]
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v1/file/download_info；随后 GET 返回的 downloadUrl（源 API 未提供固定 CDN 域名）`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --file-id | `fileId` | number；必填；download_info QueryString |
| --output | `本地目标路径` | 本地参数；不发送 API |
| --overwrite --yes | `本地覆盖策略` | 本地参数；不发送 API |

**源契约：QueryString 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileId | number | 是 | 文件id |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| downloadUrl | string | 是 | 下载地址 |


**源契约：异常返回**

| code | 异常原因 | 示例message |
| --- | --- | --- |
| 5113 | 自用下载流量不足 | 您今日自用下载流量已超出1GB上限，升级VIP会员可无限流量下载 |
| 5066 | 文件不存在 | 文件不存在，检查传入fileId是否正确 |

**行为与边界：** 先 GET file/detail?fileID=... 核对 type/trashed/status/size/etag，再 GET download_info 获取 downloadUrl，最后由独立无 Bearer/Platform 客户端 GET 返回 URL，以流式方式写同目录 .part 文件。校验字节数及 MD5 后，默认按主文档的不覆盖策略发布，若目标已存在或发布时出现并发创建则失败；仅显式 --overwrite --yes 使用 replace 覆盖发布。download_info 业务码 5113 表示自用下载流量不足、5066 文件不存在；具体流量权益按账号与 API 返回处理，不把示例中 1GB 上限推广为所有账号。源文档未承诺 Range、URL 有效期或跨进程下载恢复，首版不承诺；重定向不得传播 API 凭据。

**依据：** [API列表/文件管理/下载.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8B%E8%BD%BD.md)。

### A.20 `file upload-api v1 create`

**设计调用：**

```shell
pan123 file upload-api v1 create --parent-id 0 --filename NAME --etag MD5 --size BYTES [--duplicate 1] [--contain-dir true] --session-out upload.json
```

**HTTP 契约：** `POST https://open-api.123pan.com/upload/v1/file/create`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --parent-id | `parentFileID` | number；必填 |
| --filename | `filename` | string；必填 |
| --etag | `etag` | string；必填；完整文件 MD5 |
| --size | `size` | number；必填；byte |
| --duplicate | `duplicate` | number；选填；1 保留两者，2 覆盖 |
| --contain-dir | `containDir` | bool；选填；默认 false |
| --session-out | 本地 session 文件输出 | 本地选填；非 API 参数；默认生成受保护文件并返回路径 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| parentFileID | number | 必填 | 父目录id，上传到根目录时填写 0 |
| filename | string | 必填 | 文件名要小于255个字符且不能包含以下任何字符："\/:*?\|><。（注：不能重名）containDir 为 true 时，传入路径+文件名，例如：/你好/123/测试文件.mp4 |
| etag | string | 必填 | 文件md5 |
| size | number | 必填 | 文件大小，单位为 byte 字节 |
| duplicate | number | 非必填 | 当有相同文件名时，文件处理策略（1保留两者，新文件名将自动添加后缀，2覆盖原文件） |
| containDir | bool | 非必填 | 上传文件是否包含路径，默认false |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileID | number | 非必填 | 文件ID。当123云盘已有该文件,则会发生秒传。此时会将文件ID字段返回。唯一 |
| preuploadID | string | 必填 | 预上传ID(如果 reuse 为 true 时,该字段不存在) |
| reuse | boolean | 必填 | 是否秒传，返回true时表示文件已上传成功 |
| sliceSize | number | 必填 | 分片大小，必须按此大小生成文件分片再上传 |

**行为与边界：** 开发者单文件上限为源文档的 10GB，未定义 GB 换算。文件名不是全空格，禁用字符以源说明为准；说明 <256 与字段表 <255 有差异，可保守本地限制 254 字符并以实际 API 核验。reuse=true 为秒传完成；否则保存 preuploadID/sliceSize 到权限受限 session 文件。duplicate=2 需 --yes。创建失败/超时结果未知不盲目重试。

**依据：** [API列表/文件管理/上传/V1（旧）/创建文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E5%88%9B%E5%BB%BA%E6%96%87%E4%BB%B6.md)。

### A.21 `file upload-api v1 url / file upload-api v1 put`

**设计调用：**

```shell
pan123 file upload-api v1 url --session-file upload.json --slice-no 1 --url-out signed-url.txt
pan123 file upload-api v1 put --upload-url-file signed-url.txt --slice part.bin
```

**HTTP 契约：** `POST https://open-api.123pan.com/upload/v1/file/get_upload_url；然后 PUT <响应 presignedURL 全地址>`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --session-file 中 preuploadID | `preuploadID` | string；必填；get_upload_url JSON Body |
| --slice-no | `sliceNo` | number；必填；从 1 开始 |
| --upload-url-file / --upload-url-stdin | `presignedURL` | 响应地址；PUT 目标，不是固定 API route |
| --slice | `PUT 原始二进制 Body` | 本地文件；不能发送文件路径字符串 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| preuploadID | string | 必填 | 预上传ID |
| sliceNo | number | 必填 | 分片序号，从1开始自增 |

**注：**多个分片需要循环此步骤自增sliceNo+1，获取对应分片的上传地址，然后PUT上传分片


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| presignedURL | string | 必填 | 上传地址 |


**源契约：获取上传地址示例**

**行为与边界：** url 命令将 presignedURL 写入 --url-out 指定的 0600 文件；省略时在应用 state 目录生成私有文件，stdout 仅给路径。put 的 --upload-url-file 与 --upload-url-stdin 互斥。该文件保存签名 URL capability，但不保存 token/client_secret。此类 URL 文件只供当前明确上传步骤，不承诺重启后会话仍有效。本页覆盖两个 HTTP 操作：带 Bearer/Platform 的 POST 获取 presignedURL，以及对该完整签名 URL 的 PUT application/octet-stream。PUT 绝不能附带 Authorization/Platform；响应 HTTP 200 且空 Body 为分片成功。每片分别获取 URL、按 create.sliceSize 分片，签名 query 不能改写或输出到普通日志。此页示例脚本部分把文件路径当作正文，不能照抄；实际必须读二进制。未知结果的 PUT 重放及 URL 失效恢复必须依据联调，不写成保证。

**依据：** [API列表/文件管理/上传/V1（旧）/获取上传地址&上传分片.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9C%B0%E5%9D%80%26%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md)。

### A.22 `file upload-api v1 parts`

**设计调用：**

```shell
pan123 file upload-api v1 parts --session-file upload.json
```

**HTTP 契约：** `POST https://open-api.123pan.com/upload/v1/file/list_upload_parts`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --session-file 中 preuploadID | `preuploadID` | string；必填 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| preuploadID | string | 必填 | 预备上传ID |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| parts | array | 必填 | 分片列表 |
| parts[*].partNumber | number | 必填 | 分片编号 |
| parts[*].size | number | 必填 | 分片大小 |
| parts[*].etag | string | 必填 | 分片md5 |

**行为与边界：** 列举云端 parts[*].partNumber/size/etag，用于最后一片完成后比对；文件小于 sliceSize 时源说明返回空。该接口未承诺任意上传中时点可可靠查分片，不能把它推广为已验证跨进程续传保证；示例 partNumber 为字符串而表格 number，需兼容可解析整数。

**依据：** [API列表/文件管理/上传/V1（旧）/列举已上传分片（非必需）.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E5%88%97%E4%B8%BE%E5%B7%B2%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87%EF%BC%88%E9%9D%9E%E5%BF%85%E9%9C%80%EF%BC%89.md)。

### A.23 `file upload-api v1 complete`

**设计调用：**

```shell
pan123 file upload-api v1 complete --session-file upload.json [--wait]
```

**HTTP 契约：** `POST https://open-api.123pan.com/upload/v1/file/upload_complete`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --session-file 中 preuploadID | `preuploadID` | string；必填 |

**源契约：建议:**

调用该接口前,请优先列举已上传的分片,在本地进行 md5 比对。


**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| preuploadID | string | 必填 | 预上传ID |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| async | bool | 必填 | 是否需要异步查询上传结果。false为无需异步查询,已经上传完毕。true 为需要异步查询上传结果。 |
| completed | bool | 必填 | 上传是否完成 |
| fileID | number | 必填 | 上传完成文件id |

**行为与边界：** 建议先 parts 对比分片 MD5。返回 async/completed/fileID；async=false 且 fileID 非零为文档完成条件，CLI 同时检查 completed，不一致视为待核实协议异常；async=true 时 --wait 调用独立的 v1 result 接口。不能套用 V2 同接口轮询。

**依据：** [API列表/文件管理/上传/V1（旧）/上传完毕.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E4%B8%8A%E4%BC%A0%E5%AE%8C%E6%AF%95.md)。

### A.24 `file upload-api v1 result`

**设计调用：**

```shell
pan123 file upload-api v1 result --session-file upload.json [--wait]
```

**HTTP 契约：** `POST https://open-api.123pan.com/upload/v1/file/upload_async_result`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --session-file 中 preuploadID | `preuploadID` | string；必填 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| preuploadID | string | 必填 | 预上传ID |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| completed | bool | 必填 | 上传合并是否完成,如果为false,请至少1秒后发起轮询 |
| fileID | number | 必填 | 上传完成返回对应fileID |

**行为与边界：** completed=false 时至少 1 秒后再查询；completed=true 时检查非零 fileID 并详情读回大小/MD5。--wait 是有界轮询，不把服务器 MD5 校验尚未完成当作成功。

**依据：** [API列表/文件管理/上传/V1（旧）/异步轮询获取上传结果.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E5%BC%82%E6%AD%A5%E8%BD%AE%E8%AF%A2%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E7%BB%93%E6%9E%9C.md)。

### A.25 `file upload-api v2 create`

**设计调用：**

```shell
pan123 file upload-api v2 create --parent-id 0 --filename NAME --etag MD5 --size BYTES [--duplicate 1] [--contain-dir true] --session-out upload.json
```

**HTTP 契约：** `POST https://open-api.123pan.com/upload/v2/file/create`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --parent-id | `parentFileID` | number；必填 |
| --filename | `filename` | string；必填 |
| --etag | `etag` | string；必填；完整文件 MD5 |
| --size | `size` | number；必填；byte |
| --duplicate | `duplicate` | number；选填；1 保留两者，2 覆盖 |
| --contain-dir | `containDir` | bool；选填；默认 false |
| --session-out | 本地 session 文件输出 | 本地选填；非 API 参数；默认生成受保护文件并返回路径 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| parentFileID | number | 必填 | 父目录id，上传到根目录时填写 0 |
| filename | string | 必填 | 文件名要小于255个字符且不能包含以下任何字符："\/:*?\|><。（注：不能重名）containDir 为 true 时，传入路径+文件名，例如：/你好/123/测试文件.mp4 |
| etag | string | 必填 | 文件md5 |
| size | number | 必填 | 文件大小，单位为 byte 字节 |
| duplicate | number | 非必填 | 当有相同文件名时，文件处理策略（1保留两者，新文件名将自动添加后缀，2覆盖原文件） |
| containDir | bool | 非必填 | 上传文件是否包含路径，默认false |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileID | number | 非必填 | 文件ID。当123云盘已有该文件,则会发生秒传。此时会将文件ID字段返回。唯一 |
| preuploadID | string | 必填 | 预上传ID(如果 reuse 为 true 时,该字段不存在) |
| reuse | boolean | 必填 | 是否秒传，返回true时表示文件已上传成功 |
| sliceSize | number | 必填 | 分片大小，必须按此大小生成文件分片再上传 |
| servers | array | 必填 | 上传地址 |

**行为与边界：** 与 V1 相同文件名/10GB/同名策略约束。reuse=true 结束；非秒传必须保存本次 preuploadID/sliceSize/servers，sliceSize 必须由服务端提供而不能由 --chunk-size 覆盖。示例 servers 出现 HTTP，与公共须知 HTTPS 冲突：实现只接受实际返回的受信 HTTPS 上传域名；仅 HTTP 时给出可诊断错误，待官方兼容核实，不把 HTTP Bearer 当作可执行默认。duplicate=2 需 --yes。

**依据：** [API列表/文件管理/上传/V2（推荐）/创建文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E5%88%9B%E5%BB%BA%E6%96%87%E4%BB%B6.md)。

### A.26 `file upload-api v2 slice`

**设计调用：**

```shell
pan123 file upload-api v2 slice --session-file upload.json --slice-no 1 --slice part.bin [--slice-md5 MD5]
```

**HTTP 契约：** `POST <本次 create.servers 中受信 HTTPS 域名>/upload/v2/file/slice`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --session-file 中 preuploadID | `preuploadID` | string；必填 |
| --slice-no | `sliceNo` | number；必填；从 1 开始 |
| --slice-md5 或 CLI 对分片计算 | `sliceMD5` | string；必填 |
| --slice | `slice` | file；必填；multipart 分片二进制流 |
| --session-file 中服务器 | `HTTP host` | 必须来自此次 create 响应 servers |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| preuploadID | string | 必填 | 预上传ID |
| sliceNo | number | 必填 | 分片序号，从1开始自增 |
| sliceMD5 | string | 必填 | 当前分片md5 |
| slice | file | 必填 | 分片二进制流 |


**源契约：返回数据**

无

**行为与边界：** 本步骤是带 Bearer + Platform 的 multipart POST，不适用 FAQ 的 V1 PUT 无鉴权规则。不要手工设置缺 boundary 的 Content-Type；交给 multipart 编码器。返回数据说明写无，而示例是 code=0/data=null，适配器必须依据实际 HTTP/业务响应验证，不假定空 200 必成功。首版串行、有界内存；源码没有 V2 列举分片、重复 slice 幂等、会话有效期保证，不能承诺跨进程恢复或未知结果自动重发。

**依据：** [API列表/文件管理/上传/V2（推荐）/上传分片.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md)。

### A.27 `file upload-api v2 complete`

**设计调用：**

```shell
pan123 file upload-api v2 complete --session-file upload.json [--wait]
```

**HTTP 契约：** `POST https://open-api.123pan.com/upload/v2/file/upload_complete`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --session-file 中 preuploadID | `preuploadID` | string；必填；JSON Body |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| preuploadID | string | 必填 | 预上传ID |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| completed | bool | 必填 | 上传是否完成 |
| fileID | number | 必填 | 上传完成文件id |

**行为与边界：** 请求返回控制面 https://open-api.123pan.com，不使用 servers 域名。completed=true 且 fileID 非零才完成；completed=false 时至少 1 秒后再次请求同一 complete endpoint，文档没有 V2 async_result。到达本地等待期限时记录 preuploadID 及待完成状态，不宣称远端失败或自动重新创建文件。

**依据：** [API列表/文件管理/上传/V2（推荐）/上传完毕.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E4%B8%8A%E4%BC%A0%E5%AE%8C%E6%AF%95.md)。

### A.28 `file upload-api v2 domains`

**设计调用：**

```shell
pan123 file upload-api v2 domains --domains-out domains.json
```

**HTTP 契约：** `GET https://open-api.123pan.com/upload/v2/file/domain`

无业务输入字段。`--domains-out` 是可选本地输出参数，不作为 HTTP 字段发送；默认写受保护路径，便于后续 `single --domains-file` 读取，stdout 不暴露原始 capability 信息。

**源契约：Body 参数**

无


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| data | array | 必填 | 上传域名，存在多个可以任选其一 |

**行为与边界：** 无请求 Body；返回 data 是上传域名数组而非对象。此接口用于 V2 单步上传。选取受信 HTTPS 地址；不能将其替代分片 create 返回的 servers，两个上传流程按各自文档路由。

**依据：** [API列表/文件管理/上传/V2（推荐）/获取上传域名.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9F%9F%E5%90%8D.md)。

### A.29 `file upload-api v2 single`

**设计调用：**

```shell
pan123 file upload-api v2 single --domains-file domains.json --parent-id 0 --filename NAME --etag MD5 --size BYTES --file PATH [--duplicate 1] [--contain-dir true]
```

**HTTP 契约：** `POST <GET /upload/v2/file/domain 返回的受信 HTTPS 上传域名>/upload/v2/file/single/create`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --parent-id | `parentFileID` | number；必填 |
| --filename | `filename` | string；必填 |
| --etag | `etag` | string；必填；完整文件 MD5 |
| --size | `size` | number；必填；byte |
| --file | `file` | file；必填；multipart 二进制流 |
| --duplicate | `duplicate` | number；选填；1 保留两者，2 覆盖 |
| --contain-dir | `containDir` | bool；选填；默认 false |
| --domains-file | `HTTP host` | 来自 domains 响应之一；本地元数据参数 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| parentFileID | number | 必填 | 父目录id，上传到根目录时填写 0 |
| filename | string | 必填 | 文件名要小于255个字符且不能包含以下任何字符："\/:*?\|><。（注：不能重名）containDir 为 true 时，传入路径+文件名，例如：/你好/123/测试文件.mp4 |
| etag | string | 必填 | 文件md5 |
| size | number | 必填 | 文件大小，单位为 byte 字节 |
| file | file | 必填 | 文件二进制流 |
| duplicate | number | 非必填 | 当有相同文件名时，文件处理策略（1保留两者，新文件名将自动添加后缀，2覆盖原文件） |
| containDir | bool | 非必填 | 上传文件是否包含路径，默认false |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileID | number | 必填 | 文件ID。当123云盘已有该文件,则会发生秒传。此时会将文件ID字段返回。唯一 |
| completed | bool | 必填 | 是否上传完成（如果 completed 为 true 时，则说明上传完成） |

**行为与边界：** 开发者单文件限制 1GB；源文件名约束同 create。一次 HTTP 请求即可完成小文件上传，返回 completed/fileID；completed=true 才按页内说明完成，仍核对 ID。不以此页面推导未列出的 single async 状态接口。选择单步是显式命令；首版高层 upload 使用分片流程以减少未知失败重放。duplicate=2 需 --yes。

**依据：** [API列表/文件管理/上传/V2（推荐）/单步上传.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E5%8D%95%E6%AD%A5%E4%B8%8A%E4%BC%A0.md)。

### A.30 `file upload-api v2 sha1-reuse`

**设计调用：**

```shell
pan123 file upload-api v2 sha1-reuse --parent-id 0 --filename NAME --sha1 HASH --size BYTES [--duplicate 1]
```

**HTTP 契约：** `POST https://open-api.123pan.com/upload/v2/file/sha1_reuse`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --parent-id | `parentFileID` | number；必填 |
| --filename | `filename` | string；必填 |
| --sha1 | `sha1` | string；必填；文件 SHA1 |
| --size | `size` | number；必填；byte |
| --duplicate | `duplicate` | number；选填；1 保留两者，2 覆盖 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| parentFileID | number | 必填 | 父目录id，上传到根目录时填写 0 |
| filename | string | 必填 | 文件名要小于255个字符且不能包含以下任何字符："\/:*?\|><。（注：不能重名） |
| sha1 | string | 必填 | 文件sha1 |
| size | number | 必填 | 文件大小，单位为 byte 字节 |
| duplicate | number | 非必填 | 当有相同文件名时，文件处理策略（1保留两者，新文件名将自动添加后缀，2覆盖原文件） |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileID | number | 非必填 | 文件ID。当123云盘已有该文件,则会发生秒传。此时会将文件ID字段返回。唯一 |
| reuse | boolean | 必填 | 是否秒传，返回true时表示文件已上传成功 |

**行为与边界：** reuse=true 表示秒传完成并可能返回 fileID；reuse=false 表示未秒传，页面未定义分片凭据，不把 false 当成功或编造 SHA1 上传分片流程。需要普通上传时由调用者另行选择 V2 create。文件名同 create 约束，duplicate=2 需 --yes。

**依据：** [API列表/文件管理/上传/sha1哈希值文件上传.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/sha1%E5%93%88%E5%B8%8C%E5%80%BC%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0.md)。

### A.31 `share create`

**设计调用：**

```shell
pan123 share create --name NAME --expire-days 7 --file-id ID [--file-id ID ...] [--share-pwd-stdin] [--traffic-switch 1] [--traffic-limit-switch 1] [--traffic-limit BYTES]
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/share/create`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --name | `shareName` | string；必填 |
| --expire-days | `shareExpire` | number；必填；1/7/30/0，0 永久 |
| 重复 --file-id，序列化为 CSV | `fileIDList` | string；必填；最多 100 个 ID |
| --share-pwd-stdin / PAN123_SHARE_PWD | `sharePwd` | string；选填；敏感提取码 |
| --traffic-switch | `trafficSwitch` | int；选填；1/2/3/4 |
| --traffic-limit-switch | `trafficLimitSwitch` | int；选填；1 关闭、2 开启 |
| --traffic-limit | `trafficLimit` | int64；选填；byte |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| shareName | string | 必填 | 分享链接 |
| shareExpire | number | 必填 | 分享链接有效期天数,该值为枚举固定只能填写:1、7、30、0填写0时代表永久分享 |
| fileIDList | string | 必填 | 分享文件ID列表,以逗号分割,最大只支持拼接100个文件ID,示例:1,2,3 |
| sharePwd | string | 选填 | 设置分享链接提取码 |
| trafficSwitch | int | 选填 | 分享提取流量包1 全部关闭2 打开游客免登录提取3 打开超流量用户提取4 全部开启 |
| trafficLimitSwitch | int | 选填 | 分享提取流量包流量限制开关1 关闭限制2 打开限制 |
| trafficLimit | int64 | 选填 | 分享提取流量包限制流量单位：字节 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| shareID | number | 必填 | 分享ID |
| shareKey | string | 必填 | 分享码，请填写你的 UID，将分享码拼接至链接末尾：https://{uid}.share.123pan.cn/123pan/{分享码}，拼接完成后访问，即可打开对应分享页面。 |

**行为与边界：** 返回 shareID/shareKey，完整地址按当前 user.info.uid 生成 https://{uid}.share.123pan.cn/123pan/{shareKey}，不从 client_id 推导 UID。提取码不写 argv/日志；无传入 traffic 选项时省略，不编造服务端默认。启用可能消耗流量的策略在文档中明确呈现，可由 --yes 确认策略变更。shareKey 链接就是本命令用户预期的分享结果，可显示；提取码默认脱敏。

**依据：** [API列表/分享管理/创建分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E5%88%9B%E5%BB%BA%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md)。

### A.32 `share list`

**设计调用：**

```shell
pan123 share list [--limit 100] [--last-share-id 0] [--all] [--json]
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v1/share/list`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --limit | `limit` | number；必填；最大 100；CLI 默认 100 |
| --last-share-id | `lastShareId` | number；选填；默认 0 |

**源契约：QueryString 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| limit | number | 必填 | 每页文件数量，最大不超过100 |
| lastShareId | number | 选填 | 翻页查询时需要填写，默认为 0 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |  |
| --- | --- | --- | --- | --- |
| lastShareId | number | 必填 | -1代表最后一页（无需再翻页查询）其他代表下一页开始的分享文件id，携带到请求参数中 |  |
| shareList | array | 必填 | 文件列表 |  |
|  | shareId | number | 必填 | 分享ID |
|  | shareKey | string | 必填 | 分享码，请填写你的 UID，将分享码拼接至链接末尾：https://{uid}.share.123pan.cn/123pan/{分享码}，拼接完成后访问，即可打开对应分享页面。 |
|  | shareName | string | 必填 | 分享链接名称 |
|  | expiration | string | 必填 | 过期时间 |
|  | expired | integer | 必填 | 是否失效0 未失效1 失效 |
|  | sharePwd | string | 必填 | 分享链接提取码 |
|  | trafficSwitch | integer | 必填 | 分享提取流量包1 全部关闭2 打开游客免登录提取3 打开超流量用户提取4 全部开启 |
|  | trafficLimitSwitch | integer | 必填 | 分享提取流量包流量限制开关1 关闭限制2 打开限制 |
|  | trafficLimit | number | 必填 | 分享提取流量包限制流量单位：字节 |
|  | bytesCharge | number | 必填 | 分享使用流量单位：字节 |
|  | previewCount | number | 必填 | 预览次数 |
|  | downloadCount | number | 必填 | 下载次数 |
|  | saveCount | number | 必填 | 转存次数 |

**行为与边界：** lastShareId=-1 为末页；--all 逐页传回服务端 cursor。返回项 sharePwd 默认遮蔽，--json 也按脱敏策略处理；schema 原字段保留但秘密不回显。shareId 与创建响应 shareID 大小写不同；费用/流量字段只解释已有来源，不推断额外计费规则。

**依据：** [API列表/分享管理/获取分享链接列表.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E8%8E%B7%E5%8F%96%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E5%88%97%E8%A1%A8.md)。

### A.33 `share update`

**设计调用：**

```shell
pan123 share update --share-id ID [--share-id ID ...] [--traffic-switch N] [--traffic-limit-switch N] [--traffic-limit BYTES] --yes
```

**HTTP 契约：** `PUT https://open-api.123pan.com/api/v1/share/list/info`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| 重复 --share-id / --request-file 中 shareIdList | `shareIdList` | []uint64；必填；最多 100 |
| --traffic-switch | `trafficSwitch` | int；选填；1/2/3/4 |
| --traffic-limit-switch | `trafficLimitSwitch` | int；选填；1/2 |
| --traffic-limit | `trafficLimit` | int64；选填；byte |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| shareIdList | []uint64 | 必填 | 分享链接ID列表，数组长度最大为100 |
| trafficSwitch | int | 选填 | 分享提取流量包1 全部关闭2 打开游客免登录提取3 打开超流量用户提取4 全部开启 |
| trafficLimitSwitch | int | 选填 | 分享提取流量包流量限制开关1 关闭限制2 打开限制 |
| trafficLimit | int64 | 选填 | 分享提取流量包限制流量单位：字节 |

**输出契约：** 源页未列业务 data schema；按通用包装返回成功/错误摘要，不自行增加业务返回字段。

**行为与边界：** 该接口只支持列出的流量策略变更；没有修改 shareName、sharePwd、有效期、删除分享的字段，不能通过本命令承诺这些功能。至少指定一个可更新字段；省略字段不发送 null/默认，防止意外改策略。返回表缺省，不伪造更新对象。

**依据：** [API列表/分享管理/修改分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E4%BF%AE%E6%94%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md)。

### A.34 `share payment create`

**设计调用：**

```shell
pan123 share payment create --name NAME --file-id ID [--file-id ID ...] --pay-amount YUAN [--is-reward 0] [--resource-desc TEXT] [--traffic-switch N] [--traffic-limit-switch N] [--traffic-limit BYTES] --yes
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/share/content-payment/create`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --name | `shareName` | string；必填；小于 35 字符且不能含特殊字符 |
| 重复 --file-id，序列化为 CSV | `fileIDList` | string；必填；最多 100 个 ID |
| --pay-amount | `payAmount` | integer；必填；整数元，1 到 1000 |
| --is-reward | `isReward` | integer；选填；0 否、1 是 |
| --resource-desc | `resourceDesc` | string；选填 |
| --traffic-switch | `trafficSwitch` | int；选填；1/2/3/4 |
| --traffic-limit-switch | `trafficLimitSwitch` | int；选填；1/2 |
| --traffic-limit | `trafficLimit` | int64；选填；byte |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| shareName | string | 必填 | 分享链接名称,链接名要小于35个字符且不能包含特殊字符 |
| fileIDList | string | 必填 | 分享文件ID列表,以逗号分割,最大只支持拼接100个文件ID,示例:1,2,3 |
| payAmount | integer | 必填 | 请输入整数\|最小金额1元\|最大金额 1000 元 |
| isReward | integer | 选填 | 是否开启打赏0 否1 是 |
| resourceDesc | string | 选填 | 资源描述 |
| trafficSwitch | int | 选填 | 分享提取流量包1 全部关闭2 打开游客免登录提取3 打开超流量用户提取4 全部开启 |
| trafficLimitSwitch | int | 选填 | 分享提取流量包流量限制开关1 关闭限制2 打开限制 |
| trafficLimit | int64 | 选填 | 分享提取流量包限制流量单位：字节 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| shareID | number | 必填 | 分享ID |
| shareKey | string | 必填 | 分享码，请填写你的 UID，将分享码拼接至链接末尾：https://{uid}.share.123pan.cn/123pan/{分享码}，拼接完成后访问，即可打开对应分享页面。 |

**行为与边界：** 创建付费分享需 --yes，预览显示金额（元）及文件集合。不得把 payAmount 当分或小数元；源文档未给特殊字符完整集合，已知约束先校验，剩余规则待 API 确认。返回 shareID/shareKey，可按当前 UID 生成完整分享 URL。不支持此页未列出的有效期、提取码字段。

**依据：** [API列表/分享管理/创建付费分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E5%88%9B%E5%BB%BA%E4%BB%98%E8%B4%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md)。

### A.35 `share payment list`

**设计调用：**

```shell
pan123 share payment list [--limit 100] [--last-share-id 0] [--all] [--json]
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v1/share/payment/list`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --limit | `limit` | number；必填；最大 100；CLI 默认 100 |
| --last-share-id | `lastShareId` | number；选填；默认 0 |

**源契约：QueryString 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| limit | number | 必填 | 每页文件数量，最大不超过100 |
| lastShareId | number | 选填 | 翻页查询时需要填写，默认为 0 |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |  |
| --- | --- | --- | --- | --- |
| lastShareId | number | 必填 | -1代表最后一页（无需再翻页查询）其他代表下一页开始的分享文件id，携带到请求参数中 |  |
| shareList | array | 必填 | 文件列表 |  |
|  | shareId | number | 必填 | 分享ID |
|  | shareKey | string | 必填 | 分享key，请填写你的 UID，将分享key拼接至链接末尾：https://{uid}.share.123pan.cn/123pan/{分享key}，拼接完成后访问，即可打开对应分享页面。 |
|  | shareName | string | 必填 | 分享链接名称 |
|  | payAmount | number | 必填 | 付费金额 |
|  | amount | number | 必填 | 分享收益 |
|  | expiration | string | 必填 | 过期时间 |
|  | expired | integer | 必填 | 是否失效0 未失效1 失效 |
|  | trafficSwitch | integer | 必填 | 分享提取流量包1 全部关闭2 打开游客免登录提取3 打开超流量用户提取4 全部开启 |
|  | trafficLimitSwitch | integer | 必填 | 分享提取流量包流量限制开关1 关闭限制2 打开限制 |
|  | trafficLimit | number | 必填 | 分享提取流量包限制流量单位：字节 |
|  | bytesCharge | number | 必填 | 分享使用流量单位：字节 |
|  | previewCount | number | 必填 | 预览次数 |
|  | downloadCount | number | 必填 | 下载次数 |
|  | saveCount | number | 必填 | 转存次数 |
|  | orderCnt | number | 必填 | 付费订单数量 |

**行为与边界：** 同普通分享按 lastShareId=-1 结束。payAmount/amount/orderCnt 为源字段，但收益、付费订单并不等于 CLI 自建财务统计系统，不引入文档外退款/结算接口。

**依据：** [API列表/分享管理/获取付费分享链接列表.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E8%8E%B7%E5%8F%96%E4%BB%98%E8%B4%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E5%88%97%E8%A1%A8.md)。

### A.36 `share payment update`

**设计调用：**

```shell
pan123 share payment update --share-id ID [--share-id ID ...] [--traffic-switch N] [--traffic-limit-switch N] [--traffic-limit BYTES] --yes
```

**HTTP 契约：** `PUT https://open-api.123pan.com/api/v1/share/list/payment/info`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| 重复 --share-id / --request-file 中 shareIdList | `shareIdList` | []uint64；必填；最多 100 |
| --traffic-switch | `trafficSwitch` | int；选填；1/2/3/4 |
| --traffic-limit-switch | `trafficLimitSwitch` | int；选填；1/2 |
| --traffic-limit | `trafficLimit` | int64；选填；byte |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| shareIdList | []uint64 | 必填 | 分享链接ID列表，数组长度最大为100 |
| trafficSwitch | int | 选填 | 分享提取流量包1 全部关闭2 打开游客免登录提取3 打开超流量用户提取4 全部开启 |
| trafficLimitSwitch | int | 选填 | 分享提取流量包流量限制开关1 关闭限制2 打开限制 |
| trafficLimit | int64 | 选填 | 分享提取流量包限制流量单位：字节 |

**输出契约：** 源页未列业务 data schema；按通用包装返回成功/错误摘要，不自行增加业务返回字段。

**行为与边界：** 页面只允许修改流量策略，不提供 payAmount、isReward、resourceDesc、shareName 变更字段。命令需至少一个变更值并 --yes；省略值不发送。无 data 返回表，不伪造付费分享对象。

**依据：** [API列表/分享管理/修改付费分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E4%BF%AE%E6%94%B9%E4%BB%98%E8%B4%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md)。

### A.37 `offline create`

**设计调用：**

```shell
pan123 offline create --url URL [--filename NAME] [--dir-id ID] [--callback-url URL] [--wait]
```

**HTTP 契约：** `POST https://open-api.123pan.com/api/v1/offline/download`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --url | `url` | string；必填；仅 http/https |
| --filename | `fileName` | string；选填；源说明需图像扩展名 |
| --dir-id | `dirID` | number；选填；不能 0 |
| --callback-url | `callBackUrl` | string；选填 |

**源契约：Body 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| url | string | 必填 | 下载资源地址(http/https) |
| fileName | string | 非必填 | 自定义文件名称 （需携带图片格式，支持格式：png, gif, jpeg, tiff, webp,jpg,tif,svg,bmp） |
| dirID | number | 非必填 | 选择下载到指定目录ID。 示例:10023注:不支持下载到根目录,默认会下载到名为"来自:离线下载"的目录中 |
| callBackUrl | string | 非必填 | 回调地址,当文件下载成功或者失败,均会通过回调地址通知。回调内容如下url: 下载资源地址status: 0 成功，1 失败fileReason：失败原因fileID:成功后,该文件在云盘上的ID请求类型：POST{"url": "http://dc.com/resource.jpg","status": 0,"failReason": "","fileID":100} |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| taskID | number | 必填 | 离线下载任务ID,可通过该ID,调用查询任务进度接口获取下载进度 |

**行为与边界：** 页面仅支持 HTTP/HTTPS，不引入 magnet、torrent、ed2k 等协议。dirID 不支持根目录；省略默认存入“来自:离线下载”。fileName 源说明支持 png/gif/jpeg/tiff/webp/jpg/tif/svg/bmp，不推广为任意文件改名保证。返回 taskID；--wait 调用 offline progress。回调由 123 云盘服务器 POST 到用户指定地址，CLI 不自建回调监听服务；回调说明写 fileReason，但内嵌 JSON 示例写 failReason，需兼容或核实，不能以回调样例发明鉴权/签名保障。回调 status=0 成功/1 失败与进度 status 枚举不同。资源 URL 可能含签名 query，调试日志应脱敏。

**依据：** [API列表/离线下载/创建离线下载任务.md](api-source/API%E5%88%97%E8%A1%A8/%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD/%E5%88%9B%E5%BB%BA%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD%E4%BB%BB%E5%8A%A1.md)。

### A.38 `offline progress`

**设计调用：**

```shell
pan123 offline progress --task-id ID [--wait]
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v1/offline/download/process`

| CLI 输入或状态来源 | 精确 wire 字段 | 类型、必填性及位置 |
| --- | --- | --- |
| --task-id | `taskID` | number；必填；QueryString |

**源契约：QueryString 参数**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| taskID | number | 必填 | 离线下载任务ID |


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| process | float | 必填 | 下载进度百分比,当文件下载失败,该进度将会归零 |
| status | int | 必填 | 下载状态:0进行中、1下载失败、2下载成功、3重试中 |

**行为与边界：** 返回 process 为百分比，但失败时归零，不能用 process=0 推断未开始；status=0 进行中、1 失败、2 成功、3 重试中。--wait 仅按 status=1/2 停止，0/3 继续有界等待；不要套用复制任务的枚举。源返回没有 fileID；不能伪造最终文件 ID，需回调或后续列表核验。

**依据：** [API列表/离线下载/获取离线下载进度.md](api-source/API%E5%88%97%E8%A1%A8/%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD/%E8%8E%B7%E5%8F%96%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD%E8%BF%9B%E5%BA%A6.md)。

### A.39 `user info`

**设计调用：**

```shell
pan123 user info [--json]
```

**HTTP 契约：** `GET https://open-api.123pan.com/api/v1/user/info`

无业务输入字段。

**源契约：Body 参数**

无


**源契约：返回数据**

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| uid | number | 必填 | 用户账号id |
| nickname | string | 必填 | 昵称 |
| headImage | string | 必填 | 头像 |
| passport | string | 必填 | 手机号码 |
| mail | string | 必填 | 邮箱 |
| spaceUsed | number | 必填 | 已用空间 |
| spacePermanent | number | 必填 | 永久空间 |
| spaceTemp | number | 必填 | 临时空间 |
| spaceTempExpr | string | 必填 | 临时空间到期日 |
| vip | bool | 必填 | 是否会员 |
| directTraffic | number | 必填 | 剩余直链流量 |
| isHideUID | bool | 必填 | 直链链接是否隐藏UID |
| httpsCount | number | 必填 | https数量 |
| vipInfo | array | 必填 | vip信息（非VIP该字段为null） |
| vipInfo.vipLevel | number | 必填 | 1，2，3 VIP SVIP 长期VIP |
| vipInfo.vipLabel | string | 必填 | VIP级别名称 |
| vipInfo.startTime | string | 必填 | 开始时间 |
| vipInfo.endTime | string | 必填 | 结束时间 |
| developerInfo.startTime | string | 必填 | 开发者权益开始时间 |
| developerInfo.endTime | string | 必填 | 开发者权益结束时间 |

**行为与边界：** 返回 UID、昵称、空间、直链流量、VIP 及开发者权益信息。passport/mail 是个人信息：默认表格和 JSON 按项目统一脱敏策略输出；确需完整值时用显式的敏感信息显示选项，不能无条件记录原始响应日志。vipInfo 源类型 array，非 VIP 为 null，字段表以 vipInfo.vipLevel 写嵌套，而示例为数组：模型按实际 array|null 保留。developerInfo 只列嵌套字段，允许真实响应缺失/不同，不推导额外开发者套餐管理 API。

**依据：** [API列表/用户管理/获取用户信息.md](api-source/API%E5%88%97%E8%A1%A8/%E7%94%A8%E6%88%B7%E7%AE%A1%E7%90%86/%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E4%BF%A1%E6%81%AF.md)。

### A.40 高层上传工作流及兼容流程

`pan123 file upload --file PATH --parent-id 0 [--name NAME] [--duplicate error|keep-both|overwrite] [--api-version v2]` 是编排命令，不是新增远端端点。默认 V2 分片；`list`、`upload`、`download` 可由主入口提供对应 `file` 子命令的简写别名。完整 MD5/大小由 CLI 从文件计算；不存在文件、目录、文件在校验期间改变、超限和非法名均在创建前失败；高层 `--duplicate` 默认 error（本地预检同名、不主动覆盖、省略源 duplicate 字段，竞态以 API 返回为准），keep-both 映射 wire duplicate=1，overwrite 映射 wire duplicate=2 并需 `--yes`；低层 upload-api 命令继续接受源 numeric 1/2。

| 流程 | 精确操作顺序 | 成功证据与故障处理 |
| --- | --- | --- |
| V2 分片（默认） | 读取源文件并计算 MD5 → create → reuse=true 则完成；否则按 sliceSize 串行计算分片 MD5 并 multipart slice → 同一控制面 complete | completed=true 且 fileID 非零，再 file info 读回大小与 MD5；completed=false 至少 1 秒后重复 complete。分片结果未知不自动重放；首版不承诺跨进程续传。 |
| V2 单步（显式低层命令） | domains → MD5/大小 → single multipart | 源页限制 1GB；completed true 后读回，不发明单步结果轮询 endpoint。 |
| V1 兼容 | create → 逐片 get_upload_url → 原始 binary PUT → 可选 parts 比对 → complete → async=true 时 result | PUT 不携带 token；result false 至少 1 秒后重查；完成后详情读回。会话期限/跨进程恢复仍需验证。 |
| SHA1 秒传尝试 | 计算 SHA1/大小 → sha1_reuse | reuse=false 只表明未命中，不返回上传 session，不伪造 SHA1 分片流程。 |

切片数与最后片长度按服务端 sliceSize 计算，避免整文件驻留内存；不固定示例的 16 MiB，也不在开发文档里承诺任意并发 QPS。源“概述”概括支持大文件断点/并行，但 V2 具体页面未给出会话期限与分片重复提交保障，此类能力必须经真实联调后才进入发布承诺。零字节文件、10GB 的精确 byte 边界、服务器 HTTP/HTTPS 差异均列入实施前验证清单。

流程依据：[API列表/文件管理/上传/V1（旧）/💡上传流程说明.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%F0%9F%92%A1%E4%B8%8A%E4%BC%A0%E6%B5%81%E7%A8%8B%E8%AF%B4%E6%98%8E.md)；[API列表/文件管理/上传/V2（推荐）/💡上传流程说明.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%F0%9F%92%A1%E4%B8%8A%E4%BC%A0%E6%B5%81%E7%A8%8B%E8%AF%B4%E6%98%8E.md)。

### A.41 本节来源覆盖清单

下表逐页映射本节所覆盖的命令来源。一个页面可对应多个实际 HTTP 动作或多个本地命令，因此页面数与命令数、端点数不同。

| manifest 序号 | 来源页面 | 命令映射 |
| --- | --- | --- |
| 5 | [接入指南/开发者接入/获取access_token.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E5%BC%80%E5%8F%91%E8%80%85%E6%8E%A5%E5%85%A5/%E8%8E%B7%E5%8F%96access_token.md) | `auth ensure / auth status / auth clear` |
| 7 | [接入指南/第三方挂载应用接入/授权地址.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E7%AC%AC%E4%B8%89%E6%96%B9%E6%8C%82%E8%BD%BD%E5%BA%94%E7%94%A8%E6%8E%A5%E5%85%A5/%E6%8E%88%E6%9D%83%E5%9C%B0%E5%9D%80.md) | `oauth authorize-url` |
| 8 | [接入指南/第三方挂载应用接入/授权code获取access_token.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E7%AC%AC%E4%B8%89%E6%96%B9%E6%8C%82%E8%BD%BD%E5%BA%94%E7%94%A8%E6%8E%A5%E5%85%A5/%E6%8E%88%E6%9D%83code%E8%8E%B7%E5%8F%96access_token.md) | `oauth exchange / oauth refresh` |
| 11 | [API列表/文件管理/上传/创建目录.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/%E5%88%9B%E5%BB%BA%E7%9B%AE%E5%BD%95.md) | `file mkdir` |
| 13 | [API列表/文件管理/上传/V1（旧）/创建文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E5%88%9B%E5%BB%BA%E6%96%87%E4%BB%B6.md) | `file upload-api v1 create` |
| 14 | [API列表/文件管理/上传/V1（旧）/获取上传地址&上传分片.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9C%B0%E5%9D%80%26%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md) | `file upload-api v1 url / file upload-api v1 put` |
| 15 | [API列表/文件管理/上传/V1（旧）/列举已上传分片（非必需）.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E5%88%97%E4%B8%BE%E5%B7%B2%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87%EF%BC%88%E9%9D%9E%E5%BF%85%E9%9C%80%EF%BC%89.md) | `file upload-api v1 parts` |
| 16 | [API列表/文件管理/上传/V1（旧）/上传完毕.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E4%B8%8A%E4%BC%A0%E5%AE%8C%E6%AF%95.md) | `file upload-api v1 complete` |
| 17 | [API列表/文件管理/上传/V1（旧）/异步轮询获取上传结果.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E5%BC%82%E6%AD%A5%E8%BD%AE%E8%AF%A2%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E7%BB%93%E6%9E%9C.md) | `file upload-api v1 result` |
| 19 | [API列表/文件管理/上传/V2（推荐）/创建文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E5%88%9B%E5%BB%BA%E6%96%87%E4%BB%B6.md) | `file upload-api v2 create` |
| 20 | [API列表/文件管理/上传/V2（推荐）/上传分片.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md) | `file upload-api v2 slice` |
| 21 | [API列表/文件管理/上传/V2（推荐）/上传完毕.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E4%B8%8A%E4%BC%A0%E5%AE%8C%E6%AF%95.md) | `file upload-api v2 complete` |
| 22 | [API列表/文件管理/上传/V2（推荐）/获取上传域名.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9F%9F%E5%90%8D.md) | `file upload-api v2 domains` |
| 23 | [API列表/文件管理/上传/V2（推荐）/单步上传.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E5%8D%95%E6%AD%A5%E4%B8%8A%E4%BC%A0.md) | `file upload-api v2 single` |
| 24 | [API列表/文件管理/上传/sha1哈希值文件上传.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/sha1%E5%93%88%E5%B8%8C%E5%80%BC%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0.md) | `file upload-api v2 sha1-reuse` |
| 25 | [API列表/文件管理/重命名/单个文件重命名.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E9%87%8D%E5%91%BD%E5%90%8D/%E5%8D%95%E4%B8%AA%E6%96%87%E4%BB%B6%E9%87%8D%E5%91%BD%E5%90%8D.md) | `file rename` |
| 26 | [API列表/文件管理/重命名/批量文件重命名.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E9%87%8D%E5%91%BD%E5%90%8D/%E6%89%B9%E9%87%8F%E6%96%87%E4%BB%B6%E9%87%8D%E5%91%BD%E5%90%8D.md) | `file rename-batch` |
| 27 | [API列表/文件管理/删除/删除文件至回收站.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E5%88%A0%E9%99%A4/%E5%88%A0%E9%99%A4%E6%96%87%E4%BB%B6%E8%87%B3%E5%9B%9E%E6%94%B6%E7%AB%99.md) | `file trash` |
| 29 | [API列表/文件管理/复制单个文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E5%A4%8D%E5%88%B6%E5%8D%95%E4%B8%AA%E6%96%87%E4%BB%B6.md) | `file copy` |
| 30 | [API列表/文件管理/批量复制文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%89%B9%E9%87%8F%E5%A4%8D%E5%88%B6%E6%96%87%E4%BB%B6.md) | `file copy-batch` |
| 31 | [API列表/文件管理/批量复制文件进度.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%89%B9%E9%87%8F%E5%A4%8D%E5%88%B6%E6%96%87%E4%BB%B6%E8%BF%9B%E5%BA%A6.md) | `file copy-progress` |
| 32 | [API列表/文件管理/还原/从回收站恢复文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E8%BF%98%E5%8E%9F/%E4%BB%8E%E5%9B%9E%E6%94%B6%E7%AB%99%E6%81%A2%E5%A4%8D%E6%96%87%E4%BB%B6.md) | `file recover` |
| 33 | [API列表/文件管理/还原/还原文件到指定目录.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E8%BF%98%E5%8E%9F/%E8%BF%98%E5%8E%9F%E6%96%87%E4%BB%B6%E5%88%B0%E6%8C%87%E5%AE%9A%E7%9B%AE%E5%BD%95.md) | `file recover-to` |
| 34 | [API列表/文件管理/文件详情/获取单个文件详情.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85/%E8%8E%B7%E5%8F%96%E5%8D%95%E4%B8%AA%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85.md) | `file info` |
| 35 | [API列表/文件管理/文件详情/获取多个文件详情.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85/%E8%8E%B7%E5%8F%96%E5%A4%9A%E4%B8%AA%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85.md) | `file infos` |
| 36 | [API列表/文件管理/文件列表/获取文件列表（推荐）.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8/%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89.md) | `file list（推荐 V2）` |
| 37 | [API列表/文件管理/文件列表/获取文件列表（旧）.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8/%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8%EF%BC%88%E6%97%A7%EF%BC%89.md) | `file list --api-version v1（兼容）` |
| 38 | [API列表/文件管理/保险箱/解锁保险箱&获取保险箱id.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%BF%9D%E9%99%A9%E7%AE%B1/%E8%A7%A3%E9%94%81%E4%BF%9D%E9%99%A9%E7%AE%B1%26%E8%8E%B7%E5%8F%96%E4%BF%9D%E9%99%A9%E7%AE%B1id.md) | `file safebox-unlock` |
| 39 | [API列表/文件管理/移动.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E7%A7%BB%E5%8A%A8.md) | `file move` |
| 40 | [API列表/文件管理/下载.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8B%E8%BD%BD.md) | `file download（高层工作流）` |
| 41 | [API列表/分享管理/创建分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E5%88%9B%E5%BB%BA%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md) | `share create` |
| 42 | [API列表/分享管理/获取分享链接列表.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E8%8E%B7%E5%8F%96%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E5%88%97%E8%A1%A8.md) | `share list` |
| 43 | [API列表/分享管理/修改分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E4%BF%AE%E6%94%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md) | `share update` |
| 44 | [API列表/分享管理/创建付费分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E5%88%9B%E5%BB%BA%E4%BB%98%E8%B4%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md) | `share payment create` |
| 45 | [API列表/分享管理/获取付费分享链接列表.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E8%8E%B7%E5%8F%96%E4%BB%98%E8%B4%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E5%88%97%E8%A1%A8.md) | `share payment list` |
| 46 | [API列表/分享管理/修改付费分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E4%BF%AE%E6%94%B9%E4%BB%98%E8%B4%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md) | `share payment update` |
| 47 | [API列表/离线下载/创建离线下载任务.md](api-source/API%E5%88%97%E8%A1%A8/%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD/%E5%88%9B%E5%BB%BA%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD%E4%BB%BB%E5%8A%A1.md) | `offline create` |
| 48 | [API列表/离线下载/获取离线下载进度.md](api-source/API%E5%88%97%E8%A1%A8/%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD/%E8%8E%B7%E5%8F%96%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD%E8%BF%9B%E5%BA%A6.md) | `offline progress` |
| 49 | [API列表/用户管理/获取用户信息.md](api-source/API%E5%88%97%E8%A1%A8/%E7%94%A8%E6%88%B7%E7%AE%A1%E7%90%86/%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E4%BF%A1%E6%81%AF.md) | `user info` |

另行计为概述/接入/规则/导航的来源页（10 页，不伪造端点）：

| manifest 序号 | 来源页面 | 用途 |
| --- | --- | --- |
| 1 | [简介/概述.md](api-source/%E7%AE%80%E4%BB%8B/%E6%A6%82%E8%BF%B0.md) | 能力概述；断点/并行概括不能替代具体契约 |
| 2 | [简介/更新记录.md](api-source/%E7%AE%80%E4%BB%8B/%E6%9B%B4%E6%96%B0%E8%AE%B0%E5%BD%95.md) | 更新记录；确定 API 新旧标签 |
| 3 | [接入指南/开发者接入/接入流程.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E5%BC%80%E5%8F%91%E8%80%85%E6%8E%A5%E5%85%A5/%E6%8E%A5%E5%85%A5%E6%B5%81%E7%A8%8B.md) | 开发者接入流程；权益包与本机凭据来源 |
| 4 | [接入指南/开发者接入/开发须知.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E5%BC%80%E5%8F%91%E8%80%85%E6%8E%A5%E5%85%A5/%E5%BC%80%E5%8F%91%E9%A1%BB%E7%9F%A5.md) | 公共 HTTPS、鉴权、包装、设备 token 及限流规则 |
| 6 | [接入指南/第三方挂载应用接入/授权须知.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E7%AC%AC%E4%B8%89%E6%96%B9%E6%8C%82%E8%BD%BD%E5%BA%94%E7%94%A8%E6%8E%A5%E5%85%A5/%E6%8E%88%E6%9D%83%E9%A1%BB%E7%9F%A5.md) | 第三方 OAuth 应用资质与独立限流规则 |
| 9 | [接入指南/优秀实践.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E4%BC%98%E7%A7%80%E5%AE%9E%E8%B7%B5.md) | 优秀实践外链索引；不扩大 CLI 承诺 |
| 10 | [接入指南/💡常见问题.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%F0%9F%92%A1%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98.md) | FAQ；V1 PUT 空 200 与无 token 特例 |
| 12 | [API列表/文件管理/上传/V1（旧）/💡上传流程说明.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%F0%9F%92%A1%E4%B8%8A%E4%BC%A0%E6%B5%81%E7%A8%8B%E8%AF%B4%E6%98%8E.md) | V1 上传编排顺序 |
| 18 | [API列表/文件管理/上传/V2（推荐）/💡上传流程说明.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%F0%9F%92%A1%E4%B8%8A%E4%BC%A0%E6%B5%81%E7%A8%8B%E8%AF%B4%E6%98%8E.md) | V2 上传编排顺序 |
| 28 | [API列表/文件管理/复制.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E5%A4%8D%E5%88%B6.md) | 只有“复制”标题的导航空页；不是独立 API |

**覆盖核对：** 本节覆盖 manifest 第 1–49 页：39 个命令/协议来源页 + 10 个概述/接入/规则/流程/导航页。第 7 页为授权 URL 协议，第 8 页一条 token endpoint 包含 exchange 与 refresh 两个 grant；第 14 页包含一条固定 OpenAPI POST 及一个返回地址的 PUT；第 28 页没有 API 内容。V2 complete 的重复轮询没有额外 endpoint。


本文约定独立项目入口为 `pan123`。全部端点已注册实现；普通文件核心链路已通过账户联调，其他领域尚未执行真实验证。所有接口事实来自随项目保存的 `260910` API 文档快照（manifest 记录采集时间为 2026-09-11 08:58:08，北京时间）；文档中的冲突和缺失单独列出，不能据此宣称已经验证了服务器行为。

## 直链、图床与转码的补充约定

| 项目 | 契约 |
| --- | --- |
| 开放 API 域名 | `https://open-api.123pan.com`。下文标记为 `OPEN` |
| 开放 API 请求头 | `Authorization: Bearer <access_token>`、`Platform: open_platform`；有 JSON 请求体时加 `Content-Type: application/json` |
| URL/二进制传输 | 预签名 PUT、CDN 下载使用独立无凭据客户端；不继承 Authorization、Platform、Cookie，也不在重定向时补加这些头 |
| 参数命名 | 命令行使用 kebab-case；序列化严格保留源文档字段大小写，如 `fileId`、`fileID`、`IpList`、`Status`，不能统一改写 |
| 嵌套/批量请求 | `--request-file PATH` 读取 UTF-8 JSON；`--request-file -` 从 stdin 读取。与描述同一字段的普通旗标冲突时报参数错误，不静默覆盖 |
| 敏感参数 | access_token、预上传 ID、签名 URL、含签名的资源 URL、回调 URL 的敏感查询串通过环境变量、私有配置文件、请求文件或 stdin 提供；不要求放在 argv 中 |
| 结构化输出 | `--json` 在 stdout 输出统一 JSON 结果；进度、等待和诊断只写 stderr。API 返回的 `data` 可能为 object、array、string、null，不强制都是 object |
| URL 输出 | 专用 URL 命令可返回用户主动请求的完整链接；调试日志和错误信息必须去除签名查询串。URL 命令结果也可能包含令牌，应由调用方保护输出文件 |
| 确认 | 删除、禁用、黑名单替换、图床可能覆盖的迁移/复制及开始转码等命令，在非交互脚本中必须带 `--yes`；交互预览目标后确认。`--yes` 为 CLI 本地旗标，不能传给 API |
| 单次与等待 | 默认单次请求。`--wait` 仅在本节明确规定的轮询命令上开放，同时允许 `--wait-timeout SECONDS`；超时使用单调时钟，返回非零退出码 |
| POST 查询 | `image list`、`transcode folder-info/resolutions/records/result` 等虽然读取数据，实际 HTTP 方法仍为 POST，不能按“只读”自动改为 GET |
| 未文档化限制 | 原文没有声明的分页上限、TTL、重试幂等性、时区和计费单价不能自行补成 API 事实。HTTP 200 仍需检查业务 `code` |

## 直链命令索引

| 完整命令 | 用途 | 方法 / 域名 / 路径 | 主要输入 |
| --- | --- | --- | --- |
| `pan123 directlink url` | 获取文件直链 | GET OPEN `/api/v1/direct-link/url` | `--file-id` |
| `pan123 directlink enable` | 启用文件夹直链空间 | POST OPEN `/api/v1/direct-link/enable` | `--file-id`、`--yes` |
| `pan123 directlink disable` | 禁用文件夹直链空间 | POST OPEN `/api/v1/direct-link/disable` | `--file-id`、`--yes` |
| `pan123 directlink cache-refresh` | 刷新直链缓存 | POST OPEN `/api/v1/direct-link/cache/refresh` | `--yes`，API 无参数 |
| `pan123 directlink traffic-logs` | 查询近三天流量日志 | GET OPEN `/api/v1/direct-link/log` | `--page-num --page-size --start-time --end-time` |
| `pan123 directlink offline-logs` | 查询近 30 天离线日志 | GET OPEN `/api/v1/direct-link/offline/logs` | `--start-hour --end-hour --page-num --page-size` |
| `pan123 directlink blacklist list` | 获取 IP 黑名单和开关状态 | GET OPEN `/api/v1/developer/config/forbide-ip/list` | 无 |
| `pan123 directlink blacklist update` | 提交 IP 黑名单 | POST OPEN `/api/v1/developer/config/forbide-ip/update` | `--request-file`、`--yes` |
| `pan123 directlink blacklist switch` | 设置黑名单开关 | POST OPEN `/api/v1/developer/config/forbide-ip/switch` | `--status {1,2}`、`--yes` |

### directlink url

获取文件链接，不下载文件。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E8%8E%B7%E5%8F%96%E7%9B%B4%E9%93%BE%E9%93%BE%E6%8E%A5.md)

| API 输入 | 类型 | 必填 | 位置 / CLI | 约束 |
| --- | --- | --- | --- | --- |
| `fileID` | number，CLI 使用整数 | 是 | Query / `--file-id INTEGER` | 目标文件 ID |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `url` | string | 是 | 文件直链 |

原文将参数表标题写成 Body，但 curl、Java、JavaScript、Python 都使用 `?fileID=...`；设计按 Query 实现，并保存这一差异作为联调用例。API 没有给出链接 TTL 或直接空间校验规则，不承诺永久有效。

### directlink enable / disable

两条命令分别使用 POST `/api/v1/direct-link/enable` 与 POST `/api/v1/direct-link/disable`，均向 OPEN 发送 JSON。[启用源文档](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E5%90%AF%E7%94%A8%E7%9B%B4%E9%93%BE%E7%A9%BA%E9%97%B4.md)、[禁用源文档](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E7%A6%81%E7%94%A8%E7%9B%B4%E9%93%BE%E7%A9%BA%E9%97%B4.md)

| API 输入 | 类型 | 必填 | CLI | 约束 |
| --- | --- | --- | --- | --- |
| `fileID` | number，CLI 使用整数 | 是 | `--file-id INTEGER` | **文件夹** ID，不能把文件 ID 当文件夹使用 |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `filename` | string | 是 | 成功启用/禁用的文件夹名称 |

CLI 预览操作与目标 ID；脚本使用 `--yes`。返回文件夹名是服务端成功响应，不证明链接传播或 CDN 行为已完成。

### directlink cache-refresh

POST OPEN `/api/v1/direct-link/cache/refresh`，API 无请求参数。设计发送空 JSON 对象 `{}`，与 Java/Python 示例一致。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E7%9B%B4%E9%93%BE%E7%BC%93%E5%AD%98%E5%88%B7%E6%96%B0.md)

| 响应字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `code` | number | 是 | 通用业务码 |
| `message` | string | 是 | 通用响应说明 |
| `data` | object | 是 | 示例为 `{}`，未定义内部字段 |

`--yes` 仅用于本地确认。源文档没有文件/目录过滤参数，也没有刷新范围、额度、传播时间或查询刷新状态接口，CLI 不提供虚构的 `--file-id` 或 `--wait`。

### directlink traffic-logs

GET OPEN `/api/v1/direct-link/log`，参数放 Query。需要开发者权益，只支持近三天日志。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E8%8E%B7%E5%8F%96%E7%9B%B4%E9%93%BE%E6%B5%81%E9%87%8F%E6%97%A5%E5%BF%97.md)

| API 输入 | 类型 | 必填 | CLI | 约束 |
| --- | --- | --- | --- | --- |
| `pageNum` | number / integer | 是 | `--page-num INTEGER` | 页码；CLI 默认 1，原文未明示起始值 |
| `pageSize` | number / integer | 是 | `--page-size INTEGER` | 每页大小；CLI 默认 100，原文未声明上限 |
| `startTime` | string | 是 | `--start-time TEXT` | 格式 `YYYY-MM-DD HH:mm:ss` |
| `endTime` | string | 是 | `--end-time TEXT` | 同上，结束时间不得早于开始时间 |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `total` | number | 是 | 总数 |
| `list` | array | 是 | 日志数组 |
| `list[].uniqueID` | string | 是 | 唯一 ID |
| `list[].fileName` | string | 是 | 文件名 |
| `list[].fileSize` | number | 是 | 文件大小，字节 |
| `list[].filePath` | string | 是 | 文件路径 |
| `list[].directLinkURL` | string | 是 | 直链 URL |
| `list[].fileSource` | number | 是 | 1 全部文件，2 图床 |
| `list[].totalTraffic` | number | 是 | 流量，字节 |

时间输入由 httpx Query 编码一次；不能照抄 Python 示例中的 `%2520` 形成重复 URL 编码。原文未声明服务端时区，CLI 文档需要说明输入按服务端要求原样发送，在账户联调确认前不自动换算时区。表格和 JSON 保留完整分页元数据。

### directlink offline-logs

GET OPEN `/api/v1/direct-link/offline/logs`。需要开发者权益，只支持近 30 天数据。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E8%8E%B7%E5%8F%96%E7%9B%B4%E9%93%BE%E7%A6%BB%E7%BA%BF%E6%97%A5%E5%BF%97.md)

| API 输入 | 类型 | 必填 | CLI | 约束 |
| --- | --- | --- | --- | --- |
| `startHour` | string | 是 | `--start-hour TEXT` | `YYYYMMDDHH`，10 位小时精度 |
| `endHour` | string | 是 | `--end-hour TEXT` | 同上 |
| `pageNum` | number / integer | 是 | `--page-num INTEGER` | 从 1 开始，CLI 默认 1 |
| `pageSize` | number / integer | 是 | `--page-size INTEGER` | CLI 默认 100，原文未给上限 |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `total` | number | 是 | 总数 |
| `list` | array | 是 | 日志文件数组 |
| `list[].id` | 原文 string，示例 number | 是 | 唯一 ID；兼容输入类型后作为不透明 ID 输出 |
| `list[].fileName` | string | 是 | 日志文件名 |
| `list[].fileSize` | number | 是 | 字节数 |
| `list[].logTimeRange` | string | 是 | 日志时间范围 |
| `list[].downloadURL` | string | 是 | 日志文件下载地址 |

**参数位置存在冲突**：参数表为 QueryString，但所有示例均使用带 JSON body 的 GET。设计规范先保留表中的 Query 位置，实施时必须以专门的只读联调确定 Query/GET JSON body，结论写入契约测试；不能在失败后自动双发不同形式。HTTPX 若最终采用 GET JSON body，应使用 `client.request("GET", ..., json=payload)`，不能假设 `.get()` 支持 `json=`。样例出现 `total=0` 与非空 list；因此不依据 total 单独丢弃 list。返回日志下载链接，默认不替用户批量下载日志。

### directlink blacklist list / update / switch

路径必须保留官方拼写 **`forbide-ip`**。[列表源文档](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/IP%E9%BB%91%E5%90%8D%E5%8D%95%E9%85%8D%E7%BD%AE/ip%E9%BB%91%E5%90%8D%E5%8D%95%E5%88%97%E8%A1%A8.md)、[更新源文档](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/IP%E9%BB%91%E5%90%8D%E5%8D%95%E9%85%8D%E7%BD%AE/%E6%9B%B4%E6%96%B0ip%E9%BB%91%E5%90%8D%E5%8D%95%E5%88%97%E8%A1%A8.md)、[开关源文档](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/IP%E9%BB%91%E5%90%8D%E5%8D%95%E9%85%8D%E7%BD%AE/%E5%BC%80%E5%90%AF%E5%85%B3%E9%97%ADip%E9%BB%91%E5%90%8D%E5%8D%95.md)

| 命令 | 方法和路径 | API 输入 | 类型 / 必填 | CLI |
| --- | --- | --- | --- | --- |
| `blacklist list` | GET `/api/v1/developer/config/forbide-ip/list` | 无 | 无 | 无 |
| `blacklist update` | POST `/api/v1/developer/config/forbide-ip/update` | JSON `IpList` | array / 是 | `--request-file PATH`，内容为 `{"IpList":["192.0.2.1"]}`；可设计重复 `--ip` 形成同一数组 |
| `blacklist switch` | POST `/api/v1/developer/config/forbide-ip/switch` | JSON `Status` | number / 是 | `--status 1` 启用、`--status 2` 禁用 |

| 命令 | data 字段 | 类型 | 原文必填 / 含义 |
| --- | --- | --- | --- |
| `list` | `ipList` | array | 是，IP 地址列表 |
| `list` | `status` | number | 是，1 启用、2 禁用 |
| `update` | 未定义 | 示例 object `{}` | 成功无特定返回数据 |
| `switch` | `Done` | boolean | 是，操作是否完成 |

update 最多 2000 个 IPv4 地址；CLI 校验单个 IPv4，不自行加入 CIDR、IPv6 或域名支持。更新/开关需要开发者权益。更新是否全量替换未在原文明示，CLI 按“提交整个目标列表”的风险处理并要求 `--yes`；不宣称追加语义。输入 `IpList/Status` 与输出 `ipList/status/Done` 的大小写不同，必须按端点分别映射。

## 图床命令索引

图床为独立 OSS 业务，ID 是字符串，根目录常用空字符串。不能复用云盘的 integer ID 或根目录 `0` 规则。

| 完整命令 | 用途 | 方法 / 域名 / 路径 |
| --- | --- | --- |
| `pan123 image upload` | 本地图片上传完整工作流 | OSS V1 create → get_upload_url → 预签名 PUT → complete → async_result |
| `pan123 image mkdir` | 创建图床目录 | POST OPEN `/upload/v1/oss/file/mkdir` |
| `pan123 image list` | 获取图床列表 | POST OPEN `/api/v1/oss/file/list` |
| `pan123 image info` | 获取图片/目录详情 | GET OPEN `/api/v1/oss/file/detail` |
| `pan123 image move` | 批量移动图片 | POST OPEN `/api/v1/oss/file/move` |
| `pan123 image delete` | 批量删除图片 | POST OPEN `/api/v1/oss/file/delete` |
| `pan123 image source-copy` | 从云盘复制图片到图床 | POST OPEN `/api/v1/oss/source/copy` |
| `pan123 image source-copy-progress` | 查询复制任务 | GET OPEN `/api/v1/oss/source/copy/process` |
| `pan123 image source-copy-failures` | 查询复制失败文件 | GET OPEN `/api/v1/oss/source/copy/fail` |
| `pan123 image offline-create` | 从 HTTP(S) 资源迁入图床 | POST OPEN `/api/v1/oss/offline/download` |
| `pan123 image offline-progress` | 查询图床离线迁移进度 | GET OPEN `/api/v1/oss/offline/download/process` |
| `pan123 image upload-api create` | 创建 OSS 预上传 | POST OPEN `/upload/v1/oss/file/create` |
| `pan123 image upload-api get-url` | 获取某一分片上传地址 | POST OPEN `/upload/v1/oss/file/get_upload_url` |
| `pan123 image upload-api put-slice` | 上传分片二进制 | PUT 返回的 `presignedURL`，无 OPEN 认证头 |
| `pan123 image upload-api complete` | 通知 OSS 上传完成 | POST OPEN `/upload/v1/oss/file/upload_complete` |
| `pan123 image upload-api async-result` | 查询异步合并结果 | POST OPEN `/upload/v1/oss/file/upload_async_result` |

### image upload / upload-api create

高层命令为 `pan123 image upload --file PATH [--parent-id STRING] [--name NAME] [--complete-timeout SECONDS]`。父目录省略时 CLI 发送空字符串根目录；仅接收一个本地普通文件，计算文件大小和 MD5，不要求用户自己传入哈希。底层 create 可使用标量旗标或 `--request-file` 直接提供下面的元数据。[创建源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E5%88%9B%E5%BB%BA%E6%96%87%E4%BB%B6.md)、[上传工作流](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%F0%9F%92%A1%E4%B8%8A%E4%BC%A0%E6%B5%81%E7%A8%8B%E8%AF%B4%E6%98%8E.md)

create 为 POST OPEN `/upload/v1/oss/file/create`，JSON。底层命令支持 `--session-out PATH`；省略时在当前 OAuth/developer 账户缓存目录生成随机名称的受保护 session 文件。非秒传结果写入 preuploadID、sliceSize、文件 MD5/大小及主文档规定的身份与来源元数据；stdout/`--json` 只返回文件路径、reuse、非敏感文件 ID 和摘要，不默认打印 preuploadID。秒传不生成不能使用的预上传会话。后续 get-url / complete / async-result 可使用 `--session-file PATH` 从该文件提取本端点需要的字段，或用受保护 `--request-file PATH` 提供精确请求对象；session 元数据不作为 API Body 发送。

create JSON 字段：

| API 输入 | 类型 | 必填 | 底层 CLI | 约束 |
| --- | --- | --- | --- | --- |
| `parentFileID` | string | 是 | `--parent-id STRING` | 根目录发送 `""`；高层默认根目录 |
| `filename` | string | 是 | `--filename NAME` | 小于 255 字符，禁止双引号、反斜杠、斜杠、冒号、星号、问号、竖线、尖括号；不能重名 |
| `etag` | string | 是 | `--etag MD5` | 整个文件 MD5；高层自动计算 |
| `size` | number / integer | 是 | `--size BYTES` | 字节数；高层自动计算 |
| `type` | number | 是 | 无，固定发送 `1` | 图床业务类型，不是返回记录中的文件/目录类型 |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `fileID` | string | 否 | 秒传或完成后的 OSS 文件 ID |
| `reuse` | boolean | 是 | true 为秒传完成 |
| `preuploadID` | string | 原表是，reuse=true 可缺失 | 预上传 ID |
| `sliceSize` | number | 原表是，秒传无需使用 | 必须遵守的分片大小 |

工作流采用 OSS V1，不改写为云盘 V2；`reuse=true` 时直接核验 `fileID`，不能强制要求预上传字段。非秒传按服务端 sliceSize 顺序分片，每片获取 URL 后 PUT 原始二进制，最后 complete，根据 async 分支轮询 async_result。临时分片使用内存上限和可落盘存储，避免示例中一次 `read()` 整个文件。每次 PUT 无 Authorization/Platform；普通 OSS API 请求仍有认证头。

原流程建议“列举已上传分片”，但这一图床目录中**没有对应端点规格**；不能编造 `/upload/v1/oss/file/list_upload_parts`，也不能未经证实复用云盘 V1 list-parts。图床上传不承诺已有分片恢复或自动重放 PUT，直到幂等和列举能力被验证。完成后用 `image info` 回读 etag/size；参数位置冲突需先解决，之后才能作为上传验收证据。

### image upload-api get-url / put-slice

get-url 为 POST OPEN `/upload/v1/oss/file/get_upload_url`。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9C%B0%E5%9D%80%26%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md)

| API 输入 | 类型 | 必填 | CLI | 约束 |
| --- | --- | --- | --- | --- |
| `preuploadID` | string | 是 | `--session-file` 提取或 `--request-file` 中字段 | 避免放入命令历史/进程参数 |
| `sliceNo` | number / integer | 是 | `--slice-no INTEGER` 或请求文件 | 从 1 自增 |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `presignedURL` | string | 是 | 某一分片 PUT 地址 |
| `isMultipart` | boolean | 仅示例出现 | 示例为 false；原表未说明含义，不能据此发明分支 |

get-url 支持 `--url-out PATH`，将准确的 `{"presignedURL":"..."}` 对象写入受保护 URL_FILE；省略时在当前账户缓存下创建随机名称文件，并记录其会话/分片来源。stdout/`--json` 只返回 URL_FILE 路径、sliceNo 与脱敏元数据，不打印完整签名地址。该 URL_FILE 可直接作为 put-slice 的 `--request-file`，因此分步命令不依赖从普通 stdout 复制能力地址。输入 get-url 的 session-file 与 request-file 互斥；需要手工精确 wire 请求时，可自行在受保护请求文件中提供 preuploadID / sliceNo。

`put-slice --request-file URL_FILE --slice-file LOCAL_PART` 是 CLI 二进制传输命令；URL_FILE 读取 `{"presignedURL":"..."}`。HTTP 方法 PUT，域名/路径完整使用返回 URL，Body 为分片原始 bytes，`Content-Type: application/octet-stream`。**没有 `Authorization` 和 `Platform`**，也不是 multipart/form-data。源文档没有定义 PUT 成功响应的 JSON 结构；按 HTTP 成功状态处理，不使用开放 API `code` envelope 解码对象存储响应。不根据示例 Java/Python 的路径文本字符串发送文件名本身，必须发送实际文件 bytes。

### image upload-api complete / async-result

complete 使用 POST OPEN `/upload/v1/oss/file/upload_complete`；async-result 使用 POST OPEN `/upload/v1/oss/file/upload_async_result`。[完成源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E4%B8%8A%E4%BC%A0%E5%AE%8C%E6%AF%95.md)、[异步结果源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E5%BC%82%E6%AD%A5%E8%BD%AE%E8%AF%A2%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E7%BB%93%E6%9E%9C.md)

| API 输入 | 类型 | 必填 | CLI |
| --- | --- | --- | --- |
| JSON `preuploadID` | string | 是 | `--session-file` 提取或 `--request-file` 中字段 |

| 命令 | data 字段 | 类型 | 原文必填 / 含义 |
| --- | --- | --- | --- |
| complete | `fileID` | string | 否，completed=true 时为真实 ID |
| complete | `async` | boolean | 是，true 需要请求 async-result |
| complete | `completed` | boolean | 是，上传是否完成 |
| async-result | `completed` | boolean | 是，是否合并完成 |
| async-result | `fileID` | string | 是，成功的 OSS 文件 ID |

complete 默认单次请求，不把“发送通知成功”当成文件上传成功。高层 upload 自动根据 `async` 调度异步结果；底层 async-result 可带 `--wait --wait-timeout SECONDS`，`completed=false` 时至少等待 1 秒。仅在 completed=true 且 fileID 非空时报告成功。原工作流对 string fileID 使用“不为0”的表述，与类型不一致；设计以非空字符串验证，并在联调确认异常值。若 complete 返回 async=false、completed=false，源文档没有解释这一组合，必须报协议异常，不能虚构后续轮询状态。

### image mkdir

POST OPEN `/upload/v1/oss/file/mkdir`。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E5%88%9B%E5%BB%BA%E7%9B%AE%E5%BD%95.md)

| API 输入 | 类型 | 必填 | CLI | 约束 |
| --- | --- | --- | --- | --- |
| `name` | 原表 `[]string`，示例 string | 是 | 可重复 `--name NAME` / `--request-file` | 目录名不能重名；类型冲突见下文 |
| `parentID` | string | 是 | `--parent-id STRING` | 根目录为空字符串；CLI 默认根目录 |
| `type` | number | 是 | 无，固定 `1` | 图床 |

| data 字段 | 类型 | 来源 | 含义 |
| --- | --- | --- | --- |
| `list` | array | 示例 | 创建结果数组 |
| `list[].filename` | string | 示例 | 目录名 |
| `list[].dirID` | string | 示例 | 目录 ID |

原文没有返回参数表；上述结构仅由示例得出，不能声明其字段必填。请求 name 类型是接口联调前置项：表写 string[]、所有示例写 scalar string。设计的重复旗标内部先保存 names，实施需确认 API 接受的真实结构；不擅自循环单个请求制造部分创建结果。请求文件保留用户选择的 wire 结构，不能被通用参数层强制转换。

### image list

POST OPEN `/api/v1/oss/file/list`，JSON Body，即使读取列表也不能改为 GET。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%89%87%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%89%87%E5%88%97%E8%A1%A8.md)

| API 输入 | 类型 | 必填 | CLI | 约束 |
| --- | --- | --- | --- | --- |
| `parentFileId` | string | 否 | `--parent-id STRING` | 默认为空，筛选根目录 |
| `limit` | number / integer | 是 | `--limit INTEGER` | 1–100，CLI 默认 100 |
| `startTime` | number / integer | 否 | `--start-time INTEGER` | Unix 秒时间戳；不同于直链日志的日期文本 |
| `endTime` | number / integer | 否 | `--end-time INTEGER` | Unix 秒时间戳 |
| `lastFileId` | string | 否 | `--last-file-id STRING` | 首次省略；后续用服务端返回游标 |
| `type` | number | 是 | 无，固定 `1` | 图床业务类型 |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `lastFileId` | string | 是 | `"-1"` 为末页；不是 integer `-1` |
| `fileList` | array | 是 | 文件/目录数组 |
| `fileList[].fileId` | string | 是 | OSS ID |
| `fileList[].filename` | string | 是 | 名称 |
| `fileList[].type` | number | 是 | 原表误写“0-文件 1-文件”；detail 表及目录示例支持 0 文件、1 目录，需联调核实 |
| `fileList[].size` | number | 是 | 文件大小 |
| `fileList[].etag` | string | 是 | MD5，目录可为空 |
| `fileList[].status` | number | 是 | 大于 100 为审核驳回 |
| `fileList[].createAt`、`updateAt` | string | 是 | 创建/更新时间 |
| `fileList[].downloadURL` | string | 是 | 下载链接，目录示例为空 |
| `fileList[].userSelfURL` | string | 是 | 自定义域名链接 |
| `fileList[].totalTraffic` | number | 是 | 流量统计 |
| `fileList[].parentFileId` | string | 是 | 父级 ID |
| `fileList[].parentFilename` | string | 是 | 父级名称 |
| `fileList[].extension` | string | 是 | 扩展名 |

示例额外含 `s3KeyFlag:string`、`storageNode:string`、`ossIndex:number`，未列为规范必填，JSON 输出保留未知字段。CLI 可带 `--all` 循环游标，末页条件严格比较 `"-1"`；检测重复游标，不能因本页无可见项提前停止。时间范围不自动推断。分页结果应保留服务端游标供脚本继续读取。

### image info

GET OPEN `/api/v1/oss/file/detail`。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%89%87%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%89%87%E8%AF%A6%E6%83%85.md)

| API 输入 | 类型 | 必填 | CLI | 位置 |
| --- | --- | --- | --- | --- |
| `fileID` | string | 是 | `--file-id STRING` | 原表 QueryString；全部示例 GET JSON body |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `fileId` | string | 是 | ID；输入为 `fileID`，输出为 `fileId` |
| `filename` | string | 是 | 名称 |
| `type` | number | 是 | 0 文件，1 目录 |
| `size` | number | 是 | 文件大小 |
| `etag` | string | 是 | MD5 |
| `status` | number | 是 | 大于 100 为审核驳回 |
| `createAt`、`updateAt` | string | 是 | 创建/更新时间 |
| `downloadURL`、`userSelfURL` | string | 是 | 下载链接、自定义域名链接 |
| `totalTraffic` | number | 是 | 流量统计 |
| `parentFileId`、`parentFilename` | string | 是 | 父级 ID / 名称 |
| `extension` | string | 是 | 扩展名 |

示例额外字段 `s3KeyFlag:string`、`storageNode:string`、`ossIndex:number` 保留。Query/GET JSON body 的规范冲突与 directlink offline-logs 同类，正式发布前须只读联调确认，禁止自动双发。本命令只返回详情；没有独立“图床下载”API，可由用户取 downloadURL 后用公共无认证下载器获取，且不得将 OPEN bearer 附带给 CDN。

### image move / delete

move 使用 POST OPEN `/api/v1/oss/file/move`；delete 使用 POST OPEN `/api/v1/oss/file/delete`。[移动源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E7%A7%BB%E5%8A%A8%E5%9B%BE%E7%89%87.md)、[删除源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%88%A0%E9%99%A4%E5%9B%BE%E7%89%87.md)

| 命令 | API 输入 | 类型 | 必填 | CLI / 约束 |
| --- | --- | --- | --- | --- |
| 两者 | `fileIDs` | array；示例元素 string | 是 | `--request-file PATH` 或重复 `--file-id STRING`；最多 100 个 |
| move | `toParentFileID` | string | 是 | `--parent-id STRING`，不得为空，因此不支持移动到空字符串根目录 |

成功示例 `data:null`，没有返回字段规格。删除脚本必须 `--yes`；移动也可统一要求 `--yes` 显示操作计划。原文没有说明图床删除是否经过回收站，不能称为“可恢复删除”，也不能发明 restore 或 rename 端点。CLI 不自动将超过 100 个 ID 拆批，因为拆批可能产生未确认的部分执行语义。

### image source-copy

POST OPEN `/api/v1/oss/source/copy`，JSON。复制云盘文件/目录内图片到图床，可能覆盖已有相同 etag+size 图片，要求 `--yes`。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%A4%8D%E5%88%B6%E4%BA%91%E7%9B%98%E5%9B%BE%E7%89%87/%E5%88%9B%E5%BB%BA%E5%A4%8D%E5%88%B6%E4%BB%BB%E5%8A%A1.md)

| API 输入 | 类型 | 必填 | CLI | 约束 |
| --- | --- | --- | --- | --- |
| `fileIDs` | string[] | 是 | `--request-file` 或重复 `--file-id STRING` | 即使来源云盘 ID 为数字，这个 API 的数组元素也按 string；最多 100 个输入 ID |
| `toParentFileID` | string | 是 | `--parent-id STRING` | 图床目标目录；根目录为空字符串 |
| `sourceType` | 原表 string，示例 number | 是 | 无，来源固定云盘 `1`；wire 类型待联调 | 不允许直接把云盘枚举假设成其他来源 |
| `type` | number | 是 | 无，固定 `1` | 图床业务 |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `taskID` | string | 是 | 复制任务 ID |

最多 3 个可创建任务，前一任务完成后处理下一任务。每个任务最多 1000 张图片、目录最多 15 层、图片大小限制原文为 100M，支持 png/gif/jpeg/tiff/webp/jpg/tif/svg/bmp；原文没有将 100M 定义为确定的十进制或二进制字节值。sourceType 的 wire 类型冲突须保存到接口风险清单，不能默默选择后宣称兼容。创建返回 taskID 仅表示任务受理，复制完成需查询状态和失败列表。

### image source-copy-progress / source-copy-failures

progress 为 GET OPEN `/api/v1/oss/source/copy/process`；failures 为 GET OPEN `/api/v1/oss/source/copy/fail`。[任务详情源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%A4%8D%E5%88%B6%E4%BA%91%E7%9B%98%E5%9B%BE%E7%89%87/%E8%8E%B7%E5%8F%96%E5%A4%8D%E5%88%B6%E4%BB%BB%E5%8A%A1%E8%AF%A6%E6%83%85.md)、[失败列表源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%A4%8D%E5%88%B6%E4%BA%91%E7%9B%98%E5%9B%BE%E7%89%87/%E8%8E%B7%E5%8F%96%E5%A4%8D%E5%88%B6%E5%A4%B1%E8%B4%A5%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8.md)

| 命令 | API 输入 | 类型 | 必填 | CLI / 位置 |
| --- | --- | --- | --- | --- |
| 两者 | `taskID` | string | 是 | `--task-id STRING` / Query；failures 示例使用 GET JSON body |
| failures | `limit` | number / integer | 是 | `--limit INTEGER`，最大 100，CLI 默认 100 |
| failures | `page` | number / integer | 是 | `--page INTEGER`，CLI 默认 1；原文未明确起始值 |

| 命令 | data 字段 | 类型 | 原文必填 / 含义 |
| --- | --- | --- | --- |
| progress | `status` | integer | 是：1 进行中、2 结束、3 失败、4 等待 |
| progress | `failMsg` | string | 是：失败原因 |
| failures | `total` | number | 是：总数 |
| failures | `list` | array 或示例 null | 是：失败项列表；null 可规范化为空集合供表格展示，JSON 保留原响应 |
| failures | `list[].fileId` | number | 原表未清晰标注必填：来源文件 ID |
| failures | `list[].filename` | string | 原表未清晰标注必填：文件名 |

失败列表仅记录**符合格式和大小条件**的图片复制失败，不能把无失败项解释为所有原始输入都已复制。status=2 的官方含义是“结束”，CLI 不把它直接改名为“全部成功”，应提示查看 failures。默认单次查询；可带 `--wait --wait-timeout SECONDS`，只轮询已文档化的 process 端点，status=1/4 继续、status=2/3 停止。原文没有规定轮询周期，设计采用 **CLI 本地默认间隔 2 秒**，不是平台官方要求。status=2 只代表结束，不保证没有失败项；结束后仍应检查 failures。failures 的 Query/GET JSON body 冲突同样需要只读联调；参数位置不能由通用 GET 行为自动推断。

### image offline-create / offline-progress

create 为 POST OPEN `/api/v1/oss/offline/download`；progress 为 GET OPEN `/api/v1/oss/offline/download/process`。[创建源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%9B%BE%E5%BA%8A%E7%A6%BB%E7%BA%BF%E8%BF%81%E7%A7%BB/%E5%88%9B%E5%BB%BA%E7%A6%BB%E7%BA%BF%E8%BF%81%E7%A7%BB%E4%BB%BB%E5%8A%A1.md)、[进度源文档](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%9B%BE%E5%BA%8A%E7%A6%BB%E7%BA%BF%E8%BF%81%E7%A7%BB/%E8%8E%B7%E5%8F%96%E7%A6%BB%E7%BA%BF%E8%BF%81%E7%A7%BB%E4%BB%BB%E5%8A%A1.md)

| create JSON 输入 | 类型 | 必填 | CLI | 约束 |
| --- | --- | --- | --- | --- |
| `url` | string | 是 | `--request-file` 中字段；无敏感查询时可 `--url TEXT` | 仅 HTTP/HTTPS |
| `fileName` | string | 否 | `--filename NAME` | 自定义名称要含支持的图片扩展名 |
| `dirID` | string | 否 | `--dir-id STRING` | 不支持根目录；省略时到“来自:离线下载”目录 |
| `callBackUrl` | string | 否 | `--request-file` 中字段；无敏感查询时可 `--callback-url URL` | 成功/失败均会 POST 通知 |
| `type` | number | 是 | 无，固定 `1` | 图床 |

| 命令 | data 字段 / 输入 | 类型 | 必填 / 含义 |
| --- | --- | --- | --- |
| create 响应 | `taskID` | number | 是，离线任务 ID |
| progress Query | `taskID` | number / integer | 是，CLI `--task-id INTEGER`；不是 source-copy 的 string taskID |
| progress 响应 | `status` | integer | 是：0 进行中、1 失败、2 成功、3 重试中 |
| progress 响应 | `process` | integer | 是：0–100 的进度百分比 |

图片格式与 source-copy 相同，限制原文为 100M。存在相同 etag+size 图片会覆盖，create 要求 `--yes`。原文回调说明先写 `fileReason`，JSON 示例写 `failReason`；回调接收器应兼容两者并保留原报文，不能声称已确认哪一个是规范字段。回调示例 `fileID` 为 number，而 OSS 文件 ID 在其他接口为 string，也要联调确认。回调不是 CLI 的入站 HTTP 服务，首版不内置监听器。progress 默认单次，可带 `--wait --wait-timeout SECONDS`：status=0/3 继续、status=1/2 停止，失败不以 process=0 推断未开始。原文未定义轮询间隔，设计采用 **CLI 本地默认间隔 2 秒**，不是平台官方要求；只轮询已有 process 端点，不重发 create。

## 视频转码命令索引

| 完整命令 | 用途 | 方法 / 域名 / 路径 |
| --- | --- | --- |
| `pan123 transcode source-list` | 云盘中的视频源文件列表 | GET OPEN `/api/v2/file/list`，固定 `category=2` |
| `pan123 transcode folder-list` | 转码空间文件列表 | GET OPEN `/api/v2/file/list`，固定 `businessType=2` |
| `pan123 transcode folder-info` | 获取转码空间目录 ID | POST OPEN `/api/v1/transcode/folder/info` |
| `pan123 transcode from-cloud` | 把云盘源视频送入转码空间 | POST OPEN `/api/v1/transcode/upload/from_cloud_disk` |
| `pan123 transcode upload` | 本地视频上传转码空间 | 文档明确为云盘 V1 上传工作流，create 的 parentFileID 必须为转码目录 |
| `pan123 transcode resolutions` | 查询可转码分辨率 | POST OPEN `/api/v1/transcode/video/resolutions` |
| `pan123 transcode run` | 启动转码 | POST OPEN `/api/v1/transcode/video` |
| `pan123 transcode records` | 查询单视频转码记录 | POST OPEN `/api/v1/transcode/video/record` |
| `pan123 transcode result` | 查询单视频转码结果文件 | POST OPEN `/api/v1/transcode/video/result` |
| `pan123 transcode list` | 三方挂载应用授权转码列表 | GET OPEN `/api/v1/video/transcode/list` |
| `pan123 transcode delete` | 删除原视频或原视频及转码文件 | POST OPEN `/api/v1/transcode/delete` |
| `pan123 transcode download-url` | 获取原视频下载地址 | POST OPEN `/api/v1/transcode/file/download` |
| `pan123 transcode segment-url` | 获取某个 m3u8 / ts 地址 | POST OPEN `/api/v1/transcode/m3u8_ts/download` |
| `pan123 transcode all-download-urls` | 准备全部转码文件的压缩包地址 | POST OPEN `/api/v1/transcode/file/download/all` |

`all-download-urls` 名称用于与命令命名约定保持一致，实际 API 返回**一个打包 ZIP 地址**，不返回地址数组。视频导入、上传和 run 是不同步骤；导入成功不能解释为已经转码成功。

### transcode source-list / folder-list

共用 GET OPEN `/api/v2/file/list`，但固定参数不同。[云盘视频源列表](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E4%B8%8A%E4%BC%A0%E8%A7%86%E9%A2%91/%E4%BA%91%E7%9B%98%E4%B8%8A%E4%BC%A0/%E8%8E%B7%E5%8F%96%E4%BA%91%E7%9B%98%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6.md)、[转码空间列表](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E8%BD%AC%E7%A0%81%E7%A9%BA%E9%97%B4%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8.md)

| Query 输入 | 类型 | 必填 | CLI | 约束 |
| --- | --- | --- | --- | --- |
| `parentFileId` | number / integer | 是 | `--parent-id INTEGER` | 根目录 0，CLI 默认 0 |
| `limit` | number / integer | 是 | `--limit INTEGER` | 最大 100，CLI 默认 100 |
| `searchData` | string | 否 | `--search TEXT` | 搜索时忽略 parentFileId，全局查找 |
| `searchMode` | number | 否 | `--search-mode {0,1}` | 0 分词模糊搜索；1 完整文件名精确搜索 |
| `lastFileId` | number / integer | 否 | `--last-file-id INTEGER` | 首次省略，后续传服务端游标 |
| `category` | number | source-list 是 | source-list 无旗标，固定 `2` | 视频分类 |
| `businessType` | number | folder-list 是 | folder-list 无旗标，固定 `2` | 转码空间 |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `lastFileId` | number | 是 | `-1` 最后一页 |
| `fileList` | array | 是 | 源文件或空间文件数组 |
| `fileList[].fileId`、`parentFileId` | number | 是 | 文件/父目录 ID |
| `fileList[].filename` | string | 是 | 名称 |
| `fileList[].type` | number | 是 | 0 文件、1 目录 |
| `fileList[].size` | number | 是 | 文件大小 |
| `fileList[].etag` | string | 是 | MD5 |
| `fileList[].status` | number | 是 | 大于 100 为审核驳回 |
| `fileList[].category` | number | 是 | 0 未知、1 音频、2 视频、3 图片 |
| `fileList[].trashed` | number | folder-list 表列为必填 | 0 不在回收站、1 在回收站；source-list 表未列，需兼容附加字段 |

folder-list 示例额外含 `punishFlag:number`、`s3KeyFlag:string`、`storageNode:string`、`createAt:string`、`updateAt:string`，保留到 JSON。源文档没有证明“视频列表”中的目录过滤行为，不能只因 category=2 就假设没有文件夹。`--all` 使用数字游标循环；回收站过滤沿用主文件列表策略，不能在看到被过滤空页时停止。两条命令不能同时自动加 category=2 和 businessType=2，固定过滤条件应与各自源文档一致。

### transcode folder-info / upload / from-cloud

folder-info 为 POST OPEN `/api/v1/transcode/folder/info`，无 Body 参数；成功 data 为 `{"fileID": INTEGER}`，fileID 原文必填。[空间目录源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E8%BD%AC%E7%A0%81%E7%A9%BA%E9%97%B4%E6%96%87%E4%BB%B6%E5%A4%B9%E4%BF%A1%E6%81%AF.md)

`pan123 transcode upload --file PATH [--name NAME]` 是高层本地上传工作流，必须使用源文档指定的 **`/upload/v1/file/create`**，将返回的转码空间目录 ID 填入 `parentFileID`，随后按云盘 V1 get_upload_url → 预签名 PUT → upload_complete → upload_async_result 流程完成；不能假设“V2 更推荐”就擅自替换视频空间接入协议。[本地上传指南](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E4%B8%8A%E4%BC%A0%E8%A7%86%E9%A2%91/%E6%9C%AC%E5%9C%B0%E4%B8%8A%E4%BC%A0/%E4%B8%8A%E4%BC%A0%E6%B5%81%E7%A8%8B.md)、[V1 上传流程](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%F0%9F%92%A1%E4%B8%8A%E4%BC%A0%E6%B5%81%E7%A8%8B%E8%AF%B4%E6%98%8E.md)

| 本地工作流差异 | 类型 | 必填 | CLI / 规则 |
| --- | --- | --- | --- |
| create JSON `parentFileID` | number | 是 | 自动从 folder-info 获取或 `--parent-id INTEGER` 明确指定已确认的转码目录；不能默认 0 |
| 本地文件 | path | CLI 必需 | `--file PATH`；其他 V1 create 元数据由上传器计算，远程名称使用高层 `--name NAME` |

本地视频上传无独立新 API，完整 V1 请求/响应字段以文件上传章节为准；此处只规定转码目录差异。完成后回读大小/MD5，返回导入文件 ID；不自动 run，避免未经明确请求消耗转码权益。

from-cloud 为 POST OPEN `/api/v1/transcode/upload/from_cloud_disk`。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E4%B8%8A%E4%BC%A0%E8%A7%86%E9%A2%91/%E4%BA%91%E7%9B%98%E4%B8%8A%E4%BC%A0/%E4%BB%8E%E4%BA%91%E7%9B%98%E7%A9%BA%E9%97%B4%E4%B8%8A%E4%BC%A0.md)

| JSON 输入 | 类型 | 必填 | CLI / 规则 |
| --- | --- | --- | --- |
| 顶层数组 | array<object> | 是 | `--request-file PATH`，不是包在 `{"fileId":[...]}` 里 |
| `[].fileId` | number / integer | 是 | 每个对象一个云盘文件 ID；最多 100 个对象；可重复 `--file-id INTEGER` 由 CLI 构造对象数组 |

请求文件内容示例：

```json
[{"fileId": 2875051}, {"fileId": 2875052}]
```

原表写 `fileId:[]objet`，而示例为顶层对象数组；设计遵循明确的示例形状并登记类型拼写错误。返回仅写“上传成功”文字提示，没有结构化结果数组、转码文件 ID 映射或任务进度字段。因此受理后不能凭空返回新的空间 ID，也不能自动等待或开始转码；通过 folder-list/用户选定的新空间文件继续操作。

### transcode resolutions

POST OPEN `/api/v1/transcode/video/resolutions`，JSON `fileId`。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6%E5%8F%AF%E8%BD%AC%E7%A0%81%E7%9A%84%E5%88%86%E8%BE%A8%E7%8E%87.md)

| API 输入 | 类型 | 必填 | CLI |
| --- | --- | --- | --- |
| `fileId` | number / integer | 是 | `--file-id INTEGER` |

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `IsGetResolution` | boolean | 是 | **true 正在获取；false 获取结束** |
| `Resolutions` | string | 是 | 可用分辨率，示例 `480p,720p,1080p` |
| `NowOrFinishedResolutions` | string | 否 | 已经转码或正在转码的分辨率，避免重复提交 |
| `CodecNames` | string | 是 | 编码，如 H.264 |
| `VideoTime` | number | 是 | 时长，秒 |

支持 `--wait --wait-timeout SECONDS`，根据原文建议每 10 秒查询一次，到 IsGetResolution=false 结束。false 且列表为空时不能臆造支持分辨率。表格展示可解析逗号分隔值，JSON 保留源字段和大小写。不要把 IsGetResolution=true 误判为已经获取成功。

### transcode run

POST OPEN `/api/v1/transcode/video`，JSON。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81%E6%93%8D%E4%BD%9C.md)

| API 输入 | 类型 | 必填 | CLI | 规则 |
| --- | --- | --- | --- | --- |
| `fileId` | number / integer | 是 | `--file-id INTEGER` | 转码空间文件 ID |
| `codecName` | string | 是 | `--codec-name TEXT` | 使用 resolutions 返回的编码信息，不随意填写 |
| `videoTime` | number | 是 | `--video-time NUMBER` | 秒，取查询结果；不能把本机估算值当服务器事实 |
| `resolutions` | string | 是 | `--resolutions TEXT` | 逗号分隔，例如 `1080P,720P`；**P 大写**；排除已转码/正在转码分辨率 |

成功示例 `data` 为 string“已成功开始转码，请在转码结果中查询”，不返回 taskID。run 要求 `--yes`，预览 ID、时长、编码、目标分辨率；不自动重复转码已有分辨率，不因为网络超时重放 POST。run 的默认行为是启动请求一次，查询结果是 records/result 的后续操作；源文档未规定 run 的等待间隔，首版不提供 `run --wait` 或宣称即时完成。

### transcode records

POST OPEN `/api/v1/transcode/video/record`，JSON `fileId:number` 必填，CLI `--file-id INTEGER`。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E6%9F%A5%E8%AF%A2%E8%BD%AC%E7%A0%81%E4%BF%A1%E6%81%AF/%E6%9F%A5%E8%AF%A2%E6%9F%90%E4%B8%AA%E8%A7%86%E9%A2%91%E7%9A%84%E8%BD%AC%E7%A0%81%E8%AE%B0%E5%BD%95.md)

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `UserTranscodeVideoRecordList` | array | 是 | 记录列表 |
| `[].create_at` | string | 是 | 创建时间 |
| `[].resolution` | string | 是 | 分辨率 |
| `[].status` | number | 是 | 1 准备、2 转码中、3–254 失败、255 成功；失败时长会自动回退 |
| `[].link` | string | 否 | 成功后的 m3u8 链接，未完成可能为空 |

单次查询，不提供没有文档依据的等待周期。状态语义专用于此端点，不能拿三方 list 的 `254=部分成功` 解释这里的 254。

### transcode result

POST OPEN `/api/v1/transcode/video/result`，JSON `fileId:number` 必填，CLI `--file-id INTEGER`。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E6%9F%A5%E8%AF%A2%E8%BD%AC%E7%A0%81%E4%BF%A1%E6%81%AF/%E6%9F%A5%E8%AF%A2%E6%9F%90%E4%B8%AA%E8%A7%86%E9%A2%91%E7%9A%84%E8%BD%AC%E7%A0%81%E7%BB%93%E6%9E%9C.md)

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `UserTranscodeVideoList` | array | 是 | 每个分辨率结果 |
| `[].Uid` | number | 是 | 用户 ID |
| `[].Resolution` | string | 是 | 分辨率 |
| `[].Status` | number | 是 | 1 准备、2 处理中、3–254 失败、255 成功 |
| `[].Files` | array | 原表未标注 | 转码文件列表 |
| `[].Files[].FileName` | string | 是 | m3u8/ts 文件名称 |
| `[].Files[].FileSize` | string | 是 | **格式化文本**，示例 `497.17KB`；不是精确字节数 |
| `[].Files[].Resolution` | string | 是 | 文件分辨率 |
| `[].Files[].CreateAt` | string | 是 | 文件创建时间 |
| `[].Files[].Url` | string | 是 | m3u8 播放地址；ts 没有播放地址，示例为空 |

示例还出现结果 `Id:number`、`CreateAt:string`、`UpdateAt:string`，未在表中定义必填，保留未知字段。需要下载 ts 时必须继续调用 segment-url，不能拼接空 Url。FileSize 为格式化字符串，不能用它进行精确 size/MD5 验收。

### transcode list

GET OPEN `/api/v1/video/transcode/list`，Query `fileId:number` 必填，CLI `--file-id INTEGER`。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E4%BF%A1%E6%81%AF/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81%E5%88%97%E8%A1%A8%EF%BC%88%E4%B8%89%E6%96%B9%E6%8C%82%E8%BD%BD%E5%BA%94%E7%94%A8%E6%8E%88%E6%9D%83%E4%BD%BF%E7%94%A8%EF%BC%89.md)

**访问边界**：仅限三方挂载应用授权 access_token。调用契约为 `pan123 --auth-mode oauth transcode list --file-id INTEGER`，从对应身份的受保护 OAuth 缓存读取 token；通过主文档的 oauth authorize-url / exchange / refresh 流程获取和维护。使用开发者 client_id/client_secret 换取的 token 不能被文档承诺具有此接口权限；未配置对应 OAuth 授权时给出明确的能力/权限错误，不自动改用 developer 身份。不提供原始 token argv，也不另立与主文档不一致的原始 token 环境变量/普通配置入口。

| data 字段 | 类型 | 原文必填 | 含义 |
| --- | --- | --- | --- |
| `status` | number | 是 | 1 待转码、3 失败、254 部分成功、255 全部成功 |
| `list` | array | 是 | 转码列表 |
| `list[].url` | string | 是 | 地址 |
| `list[].resolution` | string | 是 | 分辨率 |
| `list[].duration` | float | 是 | 转码后时长，秒 |
| `list[].height` | number | 是 | 高度 |
| `list[].status` | number | 是 | 原文仅定义 255 全部成功 |
| `list[].mc` | string | 是 | 存储集群 |
| `list[].bitRate` | number | 是 | 码率，原文未注明单位 |
| `list[].progress` | number | 是 | 转码进度，示例 100；原表未规定取值范围 |
| `list[].updateAt` | string | 是 | 更新时间 |

这个 endpoint 与 `transcode result/records` 不是同一状态机，不能合并枚举或自动后备调用来绕过授权。

### transcode delete

POST OPEN `/api/v1/transcode/delete`，JSON。[源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E5%88%A0%E9%99%A4%E8%A7%86%E9%A2%91/%E5%88%A0%E9%99%A4%E8%BD%AC%E7%A0%81%E8%A7%86%E9%A2%91.md)

| API 输入 | 类型 | 必填 | CLI | 规则 |
| --- | --- | --- | --- | --- |
| `fileId` | number / integer | 是 | `--file-id INTEGER` | 目标空间文件 |
| `businessType` | number | 是 | 无，固定 `2` | 转码业务 |
| `trashed` | number | 是 | `--trashed {1,2}`，必须显式指定 | 1 删除原文件；2 删除原文件+转码后文件 |

`--yes` 必须与显式删除范围一起使用，预览不得仅显示“删除视频”而遗漏原文件/衍生文件范围。data 示例为 string“删除文件成功”；原文未说明恢复能力，不把字段名 trashed 解释成可回收。没有批量删除请求结构，不擅自增加一次提交多个 ID。

### transcode download-url / segment-url / all-download-urls

三者返回下载链接，**不直接写本地文件**。[原视频源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD/%E5%8E%9F%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD.md)、[单转码文件源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD/%E5%8D%95%E4%B8%AA%E8%BD%AC%E7%A0%81%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD%EF%BC%88m3u8%E6%88%96ts%EF%BC%89.md)、[全转码 ZIP 源文档](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD/%E6%9F%90%E4%B8%AA%E8%A7%86%E9%A2%91%E5%85%A8%E9%83%A8%E8%BD%AC%E7%A0%81%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD.md)

| 命令 | 方法 / 路径 | JSON 输入 | 类型 | 必填 | CLI |
| --- | --- | --- | --- | --- | --- |
| download-url | POST `/api/v1/transcode/file/download` | `fileId` | number / integer | 是 | `--file-id INTEGER` |
| segment-url | POST `/api/v1/transcode/m3u8_ts/download` | `fileId` | number / integer | 是 | `--file-id INTEGER` |
| segment-url | 同上 | `resolution` | string | 是 | `--resolution TEXT` |
| segment-url | 同上 | `type` | number | 是 | `--type {1,2}`；1 m3u8，2 ts |
| segment-url | 同上 | `tsName` | string | type=2 条件必填 | `--ts-name TEXT`；从 result 获得名称 |
| all-download-urls | POST `/api/v1/transcode/file/download/all` | `fileId` | number / integer | 是 | `--file-id INTEGER` |
| all-download-urls | 同上 | `zipName` | string | 是 | `--zip-name NAME`，服务端生成压缩包名称 |

| 命令 | data 字段 | 类型 | 原文必填 / 含义 |
| --- | --- | --- | --- |
| 三者 | `downloadUrl` | string | 是；空间满时可为空 |
| 三者 | `isFull` | boolean | 是；空间满时没有下载地址，需用户处理权益/容量 |
| all-download-urls | `isDownloading` | boolean | 是；true 仍在准备，false 完毕 |

all-download-urls 支持 `--wait --wait-timeout SECONDS`，按照原文建议 10 秒轮询。停止规则：isFull=true 为容量阻塞；isDownloading=false、isFull=false 且 downloadUrl 非空才是地址就绪。其他不一致组合报协议错误，不输出空链接为成功。download-url 与 segment-url 无轮询说明，不添加 `--wait`。

tsName 存在示例差异：result 文件名是 `000.ts`，下载示例使用 `001`；是否需移除 `.ts` 未说明，实施前联调确认，禁止不经确认盲目截扩展名。resolution 示例为 `1080P`，按指定格式传递。zipName 示例为 `good.mp4`，API 没规定必须 `.zip`，不要自行规定或强制改名。原文未提供 ZIP/分片的精确 MD5 和 bytes，不能声称这些链接具备与普通云盘下载相同的 size+MD5 验证材料；若后续添加本地下载，应保持无认证 CDN 客户端、`.part`、不覆盖输出和中断处理，并明确实际可用的校验来源。

## 本节覆盖与实施前检查

| 文档域 | 原始页面 | Endpoint 规格页 | 独立 workflow 页 | 本节映射 |
| --- | --- | --- | --- | --- |
| 直链 | 9 | 9 | 0 | 9 条 endpoint 命令 |
| 图床 | 15 | 14 | 1 | 14 条 OPEN endpoint 命令 + 预签名 PUT 子命令 + upload 工作流 |
| 视频转码 | 14 | 13 | 1 | 13 条 endpoint 语义命令 + V1 本地 upload 工作流 |
| 合计 | 38 | 36 | 2 | 全部页面覆盖；同一 GET file/list 为两条业务命令，唯一 method/path 计数不能直接等同规格页数 |

图床 get_upload_url 页还定义一次动态对象存储 PUT，因此执行操作覆盖数比 OPEN endpoint 规格页多 1。视频 source-list/folder-list 共用 GET `/api/v2/file/list`，也与主文件管理章节重叠；不能把重复路径计算成新服务器 endpoint。本文未虚构图床 rename/restore/list-parts、转码任务取消、来源导入映射、独立本地视频上传 endpoint 或未授权的三方授权获取 API。

| 检查项 | 发布前验收 |
| --- | --- |
| 来源完整性 | 38 页面都能从本节链接打开；请求方法/路径/固定参数与源文档逐项对照 |
| GET 参数冲突 | directlink offline-logs、image info、image source-copy-failures 分别确认 Query 或 GET JSON body，并留下只读请求/响应证据；不自动双发 |
| 请求类型冲突 | image mkdir name scalar/array、image source-copy sourceType string/number、from-cloud 顶层数组形状有契约测试 |
| 字段类型与空响应 | 区分图床字符串 ID、普通整数 ID、string taskID 与 number taskID；接受 delete/move data:null；保留失败列表 list:null 与额外字段 |
| 状态机 | 不同端点 status 枚举分别建模；IsGetResolution=true 为处理中；copy status=2 仅代表结束；255 含义按具体 endpoint |
| 存储边界 | 空根目录字符串只在允许的 OSS 端点使用；image move 目标不允许空；image offline-create 不支持根目录；转码上传 parentFileID 必须为转码空间 |
| 二进制授权隔离 | OSS presigned PUT 以及所有 URL 后续下载没有 Authorization/Platform；签名 URL 不进入普通日志 |
| 轮询 | OSS async-result 至少 1 秒；视频 transcode resolutions / all-download-urls 建议 10 秒；image source-copy/offline progress 的 CLI 本地默认间隔 2 秒，非官方要求 |
| 批量与确认 | image move/delete/input source-copy IDs ≤100；source-copy 总图片≤1000/层级≤15/最多3任务；from-cloud≤100对象；blacklist≤2000 IPv4；危险脚本有yes |
| 权限与权益 | 开发者直链/日志/黑名单能力和三方授权 list 单独验证；不宣称开发者 token 支持全部 endpoint |
| 业务验收 | 图床上传→详情回读 size/MD5；转码本地 V1 上传目录正确→查询 resolutions→明确请求 run→records/result；复制/离线任务受理与完成分开记录 |

本节的原文冲突是开发前需要解决的接口契约问题，不能用“全功能已完成”掩盖。当前交付为完整设计与源证据索引，不执行上传、复制、迁移、删除、权益操作或黑名单修改。
