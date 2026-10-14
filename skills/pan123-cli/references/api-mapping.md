# API 与 CLI 映射

官方资料快照 2026-09-11；真实验证范围见各路由备注。此表由 catalog 自动生成。

## pan123 auth ensure

`POST /api/v1/access_token`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --client-id | clientID | str | True | None | {} |
| stdin / 流程注入 | clientSecret | str | True | None | {} |
- [官方快照：接入指南/开发者接入/获取access_token.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E5%BC%80%E5%8F%91%E8%80%85%E6%8E%A5%E5%85%A5/%E8%8E%B7%E5%8F%96access_token.md)
真实验证：`verified`；

## pan123 oauth exchange

`POST /api/v1/oauth2/access_token`，参数位置 `query`；只读 `False`；确认 `False`。

固定请求字段：`{"grant_type": "authorization_code"}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --client-id | client_id | str | True | None | {} |
| stdin / 流程注入 | client_secret | str | True | None | {} |
| stdin / 流程注入 | code | str | True | None | {} |
| --redirect-uri | redirect_uri | str | True | None | {} |
- [官方快照：接入指南/第三方挂载应用接入/授权code获取access_token.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E7%AC%AC%E4%B8%89%E6%96%B9%E6%8C%82%E8%BD%BD%E5%BA%94%E7%94%A8%E6%8E%A5%E5%85%A5/%E6%8E%88%E6%9D%83code%E8%8E%B7%E5%8F%96access_token.md)
真实验证：`not_verified`；需要第三方应用资格，未执行真实验证

## pan123 oauth refresh

`POST /api/v1/oauth2/access_token`，参数位置 `query`；只读 `False`；确认 `False`。

固定请求字段：`{"grant_type": "refresh_token"}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --client-id | client_id | str | True | None | {} |
| stdin / 流程注入 | client_secret | str | True | None | {} |
| stdin / 流程注入 | refresh_token | str | True | None | {} |
- [官方快照：接入指南/第三方挂载应用接入/授权code获取access_token.md](api-source/%E6%8E%A5%E5%85%A5%E6%8C%87%E5%8D%97/%E7%AC%AC%E4%B8%89%E6%96%B9%E6%8C%82%E8%BD%BD%E5%BA%94%E7%94%A8%E6%8E%A5%E5%85%A5/%E6%8E%88%E6%9D%83code%E8%8E%B7%E5%8F%96access_token.md)
真实验证：`not_verified`；需要第三方应用资格，未执行真实验证

## pan123 file list

`GET /api/v2/file/list`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileId | int | True | 0 | {"minimum": 0} |
| --limit | limit | int | True | 100 | {"minimum": 1, "maximum": 100} |
| --search | searchData | str | False | None | {} |
| --last-file-id | lastFileId | int | False | None | {"minimum": 0} |
- [官方快照：API列表/文件管理/文件列表/获取文件列表（推荐）.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8/%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89.md)
真实验证：`verified`；

## pan123 file list-v1

`GET /api/v1/file/list`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileId | int | True | 0 | {"minimum": 0} |
| --page | page | int | True | 1 | {"minimum": 1} |
| --limit | limit | int | True | 100 | {"minimum": 1, "maximum": 100} |
| --order-by | orderBy | str | True | file_id | {} |
| --order-direction | orderDirection | str | True | asc | {"choices": ["asc", "desc"]} |
| --trashed | trashed | bool | False | None | {} |
| --search | searchData | str | False | None | {} |
- [官方快照：API列表/文件管理/文件列表/获取文件列表（旧）.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8/%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8%EF%BC%88%E6%97%A7%EF%BC%89.md)
真实验证：`not_verified`；只读端点：已实现并离线验证，本轮未纳入真实账户验证

## pan123 file info

`GET /api/v1/file/detail`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileID | int | True | None | {"minimum": 1} |
- [官方快照：API列表/文件管理/文件详情/获取单个文件详情.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85/%E8%8E%B7%E5%8F%96%E5%8D%95%E4%B8%AA%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85.md)
真实验证：`verified`；

## pan123 file infos

`POST /api/v1/file/infos`，参数位置 `json`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileIds | ints | True | None | {} |
- [官方快照：API列表/文件管理/文件详情/获取多个文件详情.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85/%E8%8E%B7%E5%8F%96%E5%A4%9A%E4%B8%AA%E6%96%87%E4%BB%B6%E8%AF%A6%E6%83%85.md)
真实验证：`not_verified`；只读端点：已实现并离线验证，本轮未纳入真实账户验证

## pan123 file mkdir

`POST /upload/v1/file/mkdir`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --name | name | str | True | None | {} |
| --parent-id | parentID | int | True | None | {"minimum": 0} |
- [官方快照：API列表/文件管理/上传/创建目录.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/%E5%88%9B%E5%BB%BA%E7%9B%AE%E5%BD%95.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file rename

`PUT /api/v1/file/name`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
| --name | fileName | str | True | None | {} |
- [官方快照：API列表/文件管理/重命名/单个文件重命名.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E9%87%8D%E5%91%BD%E5%90%8D/%E5%8D%95%E4%B8%AA%E6%96%87%E4%BB%B6%E9%87%8D%E5%91%BD%E5%90%8D.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file rename-batch

`POST /api/v1/file/rename`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | renameList | strs | True | None | {"max_items": 30} |
- [官方快照：API列表/文件管理/重命名/批量文件重命名.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E9%87%8D%E5%91%BD%E5%90%8D/%E6%89%B9%E9%87%8F%E6%96%87%E4%BB%B6%E9%87%8D%E5%91%BD%E5%90%8D.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file trash

`POST /api/v1/file/trash`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileIDs | ints | True | None | {"max_items": 100} |
- [官方快照：API列表/文件管理/删除/删除文件至回收站.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E5%88%A0%E9%99%A4/%E5%88%A0%E9%99%A4%E6%96%87%E4%BB%B6%E8%87%B3%E5%9B%9E%E6%94%B6%E7%AB%99.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file copy

`POST /api/v1/file/copy`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
| --target-dir-id | targetDirId | int | True | None | {"minimum": 0} |
- [官方快照：API列表/文件管理/复制单个文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E5%A4%8D%E5%88%B6%E5%8D%95%E4%B8%AA%E6%96%87%E4%BB%B6.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file copy-batch

`POST /api/v1/file/async/copy`，参数位置 `json`；只读 `False`；确认 `False`。

等待配置：`{"command": ["file", "copy-progress"]}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileIds | ints | True | None | {"max_items": 3000} |
| --target-dir-id | targetDirId | int | True | None | {"minimum": 0} |
- [官方快照：API列表/文件管理/批量复制文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%89%B9%E9%87%8F%E5%A4%8D%E5%88%B6%E6%96%87%E4%BB%B6.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file copy-progress

`GET /api/v1/file/async/copy/process`，参数位置 `json`；只读 `True`；确认 `False`。

等待配置：`{"field": "status", "pending": [0, 1], "success": [2], "failure": [3], "interval": 2}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --task-id | taskId | int | True | None | {"minimum": 1} |
- [官方快照：API列表/文件管理/批量复制文件进度.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E6%89%B9%E9%87%8F%E5%A4%8D%E5%88%B6%E6%96%87%E4%BB%B6%E8%BF%9B%E5%BA%A6.md)
真实验证：`not_verified`；只读端点：已实现并离线验证，本轮未纳入真实账户验证

## pan123 file recover

`POST /api/v1/file/recover`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileIDs | ints | True | None | {"max_items": 100} |
- [官方快照：API列表/文件管理/还原/从回收站恢复文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E8%BF%98%E5%8E%9F/%E4%BB%8E%E5%9B%9E%E6%94%B6%E7%AB%99%E6%81%A2%E5%A4%8D%E6%96%87%E4%BB%B6.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file recover-to

`POST /api/v1/file/recover/by_path`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileIDs | ints | True | None | {"max_items": 100} |
| --parent-id | parentFileID | int | True | None | {"minimum": 0} |
- [官方快照：API列表/文件管理/还原/还原文件到指定目录.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E8%BF%98%E5%8E%9F/%E8%BF%98%E5%8E%9F%E6%96%87%E4%BB%B6%E5%88%B0%E6%8C%87%E5%AE%9A%E7%9B%AE%E5%BD%95.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file move

`POST /api/v1/file/move`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileIDs | ints | True | None | {"max_items": 100} |
| --parent-id | toParentFileID | int | True | None | {"minimum": 0} |
- [官方快照：API列表/文件管理/移动.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E7%A7%BB%E5%8A%A8.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file safebox-unlock

`GET /api/v1/safebox/id`，参数位置 `query`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | password | str | True | None | {} |
- [官方快照：API列表/文件管理/保险箱/解锁保险箱&获取保险箱id.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%BF%9D%E9%99%A9%E7%AE%B1/%E8%A7%A3%E9%94%81%E4%BF%9D%E9%99%A9%E7%AE%B1%26%E8%8E%B7%E5%8F%96%E4%BF%9D%E9%99%A9%E7%AE%B1id.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file download-url

`GET /api/v1/file/download_info`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
- [官方快照：API列表/文件管理/下载.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8B%E8%BD%BD.md)
真实验证：`verified`；

## pan123 file upload-api v1 create

`POST /upload/v1/file/create`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileID | int | True | None | {"minimum": 0} |
| --filename | filename | str | True | None | {} |
| --etag | etag | str | True | None | {} |
| --size | size | int | True | None | {"minimum": 0} |
| --duplicate | duplicate | int | False | None | {"choices": [1, 2]} |
| --contain-dir | containDir | bool | False | None | {} |
- [官方快照：API列表/文件管理/上传/V1（旧）/创建文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E5%88%9B%E5%BB%BA%E6%96%87%E4%BB%B6.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file upload-api v1 url

`POST /upload/v1/file/get_upload_url`，参数位置 `json`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | preuploadID | str | True | None | {} |
| --slice-no | sliceNo | int | True | None | {"minimum": 1} |
- [官方快照：API列表/文件管理/上传/V1（旧）/获取上传地址&上传分片.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9C%B0%E5%9D%80%26%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md)
真实验证：`not_verified`；只读端点：已实现并离线验证，本轮未纳入真实账户验证

## pan123 file upload-api v1 put

`PUT <presignedURL>`，参数位置 `binary`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | presignedURL | str | True | None | {} |
- [官方快照：API列表/文件管理/上传/V1（旧）/获取上传地址&上传分片.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9C%B0%E5%9D%80%26%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md)
## pan123 file upload-api v1 parts

`POST /upload/v1/file/list_upload_parts`，参数位置 `json`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | preuploadID | str | True | None | {} |
- [官方快照：API列表/文件管理/上传/V1（旧）/列举已上传分片（非必需）.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E5%88%97%E4%B8%BE%E5%B7%B2%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87%EF%BC%88%E9%9D%9E%E5%BF%85%E9%9C%80%EF%BC%89.md)
真实验证：`not_verified`；只读端点：已实现并离线验证，本轮未纳入真实账户验证

## pan123 file upload-api v1 result

`POST /upload/v1/file/upload_async_result`，参数位置 `json`；只读 `True`；确认 `False`。

等待配置：`{"field": "completed", "pending": [false], "success": [true], "failure": [], "interval": 1}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | preuploadID | str | True | None | {} |
- [官方快照：API列表/文件管理/上传/V1（旧）/异步轮询获取上传结果.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E5%BC%82%E6%AD%A5%E8%BD%AE%E8%AF%A2%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E7%BB%93%E6%9E%9C.md)
真实验证：`not_verified`；只读端点：已实现并离线验证，本轮未纳入真实账户验证

## pan123 file upload-api v1 complete

`POST /upload/v1/file/upload_complete`，参数位置 `json`；只读 `False`；确认 `False`。

等待配置：`{"field": "completed", "pending": [false], "success": [true], "failure": [], "interval": 1}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | preuploadID | str | True | None | {} |
- [官方快照：API列表/文件管理/上传/V1（旧）/上传完毕.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V1%EF%BC%88%E6%97%A7%EF%BC%89/%E4%B8%8A%E4%BC%A0%E5%AE%8C%E6%AF%95.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file upload-api v2 create

`POST /upload/v2/file/create`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileID | int | True | None | {"minimum": 0} |
| --filename | filename | str | True | None | {} |
| --etag | etag | str | True | None | {} |
| --size | size | int | True | None | {"minimum": 0} |
| --duplicate | duplicate | int | False | None | {"choices": [1, 2]} |
| --contain-dir | containDir | bool | False | None | {} |
- [官方快照：API列表/文件管理/上传/V2（推荐）/创建文件.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E5%88%9B%E5%BB%BA%E6%96%87%E4%BB%B6.md)
真实验证：`verified`；

## pan123 file upload-api v2 slice

`POST /upload/v2/file/slice`，参数位置 `multipart`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | preuploadID | str | True | None | {} |
| --slice-no | sliceNo | int | True | None | {"minimum": 1} |
| --slice-md5 | sliceMD5 | str | True | None | {} |
| --slice | slice | str | True | None | {} |
- [官方快照：API列表/文件管理/上传/V2（推荐）/上传分片.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md)
真实验证：`verified`；

## pan123 file upload-api v2 domains

`GET /upload/v2/file/domain`，参数位置 `query`；只读 `True`；确认 `False`。

- [官方快照：API列表/文件管理/上传/V2（推荐）/获取上传域名.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9F%9F%E5%90%8D.md)
真实验证：`not_verified`；只读端点：已实现并离线验证，本轮未纳入真实账户验证

## pan123 file upload-api v2 single

`POST /upload/v2/file/single/create`，参数位置 `multipart`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileID | int | True | None | {"minimum": 0} |
| --filename | filename | str | True | None | {} |
| --etag | etag | str | True | None | {} |
| --size | size | int | True | None | {"minimum": 0} |
| --duplicate | duplicate | int | False | None | {"choices": [1, 2]} |
| --contain-dir | containDir | bool | False | None | {} |
| --file | file | str | True | None | {} |
- [官方快照：API列表/文件管理/上传/V2（推荐）/单步上传.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E5%8D%95%E6%AD%A5%E4%B8%8A%E4%BC%A0.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file upload-api v2 sha1-reuse

`POST /upload/v2/file/sha1_reuse`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileID | int | True | None | {"minimum": 0} |
| --filename | filename | str | True | None | {} |
| --sha1 | sha1 | str | True | None | {} |
| --size | size | int | True | None | {"minimum": 0} |
| --duplicate | duplicate | int | False | None | {"choices": [1, 2]} |
- [官方快照：API列表/文件管理/上传/sha1哈希值文件上传.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/sha1%E5%93%88%E5%B8%8C%E5%80%BC%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0.md)
真实验证：`not_verified`；为避免改动用户数据，未对真实账户执行该变更操作

## pan123 file upload-api v2 complete

`POST /upload/v2/file/upload_complete`，参数位置 `json`；只读 `False`；确认 `False`。

等待配置：`{"field": "completed", "pending": [false], "success": [true], "failure": [], "interval": 1}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | preuploadID | str | True | None | {} |
- [官方快照：API列表/文件管理/上传/V2（推荐）/上传完毕.md](api-source/API%E5%88%97%E8%A1%A8/%E6%96%87%E4%BB%B6%E7%AE%A1%E7%90%86/%E4%B8%8A%E4%BC%A0/V2%EF%BC%88%E6%8E%A8%E8%8D%90%EF%BC%89/%E4%B8%8A%E4%BC%A0%E5%AE%8C%E6%AF%95.md)
真实验证：`verified`；

## pan123 share create

`POST /api/v1/share/create`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --name | shareName | str | True | None | {} |
| --expire-days | shareExpire | int | True | None | {"choices": [1, 7, 30, 0]} |
| --file-id | fileIDList | ints | True | None | {"max_items": 100} |
| stdin / 流程注入 | sharePwd | str | False | None | {} |
| --traffic-switch | trafficSwitch | int | False | None | {"choices": [1, 2, 3, 4]} |
| --traffic-limit-switch | trafficLimitSwitch | int | False | None | {"choices": [1, 2]} |
| --traffic-limit | trafficLimit | int | False | None | {"minimum": 0, "maximum": 9223372036854775807} |
- [官方快照：API列表/分享管理/创建分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E5%88%9B%E5%BB%BA%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md)
真实验证：`not_verified`；需要真实分享与付费分享额度/权限，未执行真实验证

## pan123 share payment create

`POST /api/v1/share/content-payment/create`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --name | shareName | str | True | None | {} |
| --file-id | fileIDList | ints | True | None | {"max_items": 100} |
| --pay-amount | payAmount | int | True | None | {"minimum": 1, "maximum": 1000} |
| --is-reward | isReward | int | False | None | {"choices": [0, 1]} |
| --resource-desc | resourceDesc | str | False | None | {} |
| --traffic-switch | trafficSwitch | int | False | None | {"choices": [1, 2, 3, 4]} |
| --traffic-limit-switch | trafficLimitSwitch | int | False | None | {"choices": [1, 2]} |
| --traffic-limit | trafficLimit | int | False | None | {"minimum": 0, "maximum": 9223372036854775807} |
- [官方快照：API列表/分享管理/创建付费分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E5%88%9B%E5%BB%BA%E4%BB%98%E8%B4%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md)
真实验证：`not_verified`；需要真实分享与付费分享额度/权限，未执行真实验证

## pan123 share list

`GET /api/v1/share/list`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --limit | limit | int | True | 100 | {"minimum": 1, "maximum": 100} |
| --last-share-id | lastShareId | int | False | 0 | {"minimum": 0} |
- [官方快照：API列表/分享管理/获取分享链接列表.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E8%8E%B7%E5%8F%96%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E5%88%97%E8%A1%A8.md)
真实验证：`not_verified`；需要真实分享与付费分享额度/权限，未执行真实验证

## pan123 share update

`PUT /api/v1/share/list/info`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --share-id | shareIdList | ints | True | None | {"max_items": 100} |
| --traffic-switch | trafficSwitch | int | False | None | {"choices": [1, 2, 3, 4]} |
| --traffic-limit-switch | trafficLimitSwitch | int | False | None | {"choices": [1, 2]} |
| --traffic-limit | trafficLimit | int | False | None | {"minimum": 0, "maximum": 9223372036854775807} |
- [官方快照：API列表/分享管理/修改分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E4%BF%AE%E6%94%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md)
真实验证：`not_verified`；需要真实分享与付费分享额度/权限，未执行真实验证

## pan123 share payment list

`GET /api/v1/share/payment/list`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --limit | limit | int | True | 100 | {"minimum": 1, "maximum": 100} |
| --last-share-id | lastShareId | int | False | 0 | {"minimum": 0} |
- [官方快照：API列表/分享管理/获取付费分享链接列表.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E8%8E%B7%E5%8F%96%E4%BB%98%E8%B4%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E5%88%97%E8%A1%A8.md)
真实验证：`not_verified`；需要真实分享与付费分享额度/权限，未执行真实验证

## pan123 share payment update

`PUT /api/v1/share/list/payment/info`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --share-id | shareIdList | ints | True | None | {"max_items": 100} |
| --traffic-switch | trafficSwitch | int | False | None | {"choices": [1, 2, 3, 4]} |
| --traffic-limit-switch | trafficLimitSwitch | int | False | None | {"choices": [1, 2]} |
| --traffic-limit | trafficLimit | int | False | None | {"minimum": 0, "maximum": 9223372036854775807} |
- [官方快照：API列表/分享管理/修改付费分享链接.md](api-source/API%E5%88%97%E8%A1%A8/%E5%88%86%E4%BA%AB%E7%AE%A1%E7%90%86/%E4%BF%AE%E6%94%B9%E4%BB%98%E8%B4%B9%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5.md)
真实验证：`not_verified`；需要真实分享与付费分享额度/权限，未执行真实验证

## pan123 offline create

`POST /api/v1/offline/download`，参数位置 `json`；只读 `False`；确认 `False`。

等待配置：`{"command": ["offline", "progress"]}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --url | url | str | True | None | {} |
| --filename | fileName | str | False | None | {} |
| --dir-id | dirID | int | False | None | {"minimum": 1} |
| --callback-url | callBackUrl | str | False | None | {} |
- [官方快照：API列表/离线下载/创建离线下载任务.md](api-source/API%E5%88%97%E8%A1%A8/%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD/%E5%88%9B%E5%BB%BA%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD%E4%BB%BB%E5%8A%A1.md)
真实验证：`not_verified`；需建立真实离线下载任务，未执行真实验证

## pan123 offline progress

`GET /api/v1/offline/download/process`，参数位置 `query`；只读 `True`；确认 `False`。

等待配置：`{"field": "status", "pending": [0, 3], "success": [2], "failure": [1], "interval": 2}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --task-id | taskID | int | True | None | {"minimum": 1} |
- [官方快照：API列表/离线下载/获取离线下载进度.md](api-source/API%E5%88%97%E8%A1%A8/%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD/%E8%8E%B7%E5%8F%96%E7%A6%BB%E7%BA%BF%E4%B8%8B%E8%BD%BD%E8%BF%9B%E5%BA%A6.md)
真实验证：`not_verified`；需建立真实离线下载任务，未执行真实验证

## pan123 user info

`GET /api/v1/user/info`，参数位置 `query`；只读 `True`；确认 `False`。

- [官方快照：API列表/用户管理/获取用户信息.md](api-source/API%E5%88%97%E8%A1%A8/%E7%94%A8%E6%88%B7%E7%AE%A1%E7%90%86/%E8%8E%B7%E5%8F%96%E7%94%A8%E6%88%B7%E4%BF%A1%E6%81%AF.md)
真实验证：`verified`；

## pan123 directlink url

`GET /api/v1/direct-link/url`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileID | int | True | None | {"minimum": 1} |
- [官方快照：API列表/直链/获取直链链接.md](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E8%8E%B7%E5%8F%96%E7%9B%B4%E9%93%BE%E9%93%BE%E6%8E%A5.md)
真实验证：`not_verified`；需要直链权益，未执行真实验证

## pan123 directlink enable

`POST /api/v1/direct-link/enable`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileID | int | True | None | {"minimum": 1} |
- [官方快照：API列表/直链/启用直链空间.md](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E5%90%AF%E7%94%A8%E7%9B%B4%E9%93%BE%E7%A9%BA%E9%97%B4.md)
真实验证：`not_verified`；需要直链权益，未执行真实验证

## pan123 directlink disable

`POST /api/v1/direct-link/disable`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileID | int | True | None | {"minimum": 1} |
- [官方快照：API列表/直链/禁用直链空间.md](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E7%A6%81%E7%94%A8%E7%9B%B4%E9%93%BE%E7%A9%BA%E9%97%B4.md)
真实验证：`not_verified`；需要直链权益，未执行真实验证

## pan123 directlink cache-refresh

`POST /api/v1/direct-link/cache/refresh`，参数位置 `json`；只读 `False`；确认 `True`。

- [官方快照：API列表/直链/直链缓存刷新.md](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E7%9B%B4%E9%93%BE%E7%BC%93%E5%AD%98%E5%88%B7%E6%96%B0.md)
真实验证：`not_verified`；需要直链权益，未执行真实验证

## pan123 directlink traffic-logs

`GET /api/v1/direct-link/log`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --page-num | pageNum | int | True | 1 | {"minimum": 1} |
| --page-size | pageSize | int | True | 100 | {"minimum": 1} |
| --start-time | startTime | str | True | None | {} |
| --end-time | endTime | str | True | None | {} |
- [官方快照：API列表/直链/获取直链流量日志.md](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E8%8E%B7%E5%8F%96%E7%9B%B4%E9%93%BE%E6%B5%81%E9%87%8F%E6%97%A5%E5%BF%97.md)
真实验证：`not_verified`；需要直链权益，未执行真实验证

## pan123 directlink offline-logs

`GET /api/v1/direct-link/offline/logs`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --start-hour | startHour | str | True | None | {} |
| --end-hour | endHour | str | True | None | {} |
| --page-num | pageNum | int | True | 1 | {"minimum": 1} |
| --page-size | pageSize | int | True | 100 | {"minimum": 1} |
- [官方快照：API列表/直链/获取直链离线日志.md](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/%E8%8E%B7%E5%8F%96%E7%9B%B4%E9%93%BE%E7%A6%BB%E7%BA%BF%E6%97%A5%E5%BF%97.md)
真实验证：`not_verified`；需要直链权益，未执行真实验证

## pan123 directlink blacklist list

`GET /api/v1/developer/config/forbide-ip/list`，参数位置 `query`；只读 `True`；确认 `False`。

- [官方快照：API列表/直链/IP黑名单配置/ip黑名单列表.md](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/IP%E9%BB%91%E5%90%8D%E5%8D%95%E9%85%8D%E7%BD%AE/ip%E9%BB%91%E5%90%8D%E5%8D%95%E5%88%97%E8%A1%A8.md)
真实验证：`not_verified`；需要直链权益，未执行真实验证

## pan123 directlink blacklist update

`POST /api/v1/developer/config/forbide-ip/update`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --ip | IpList | strs | True | None | {"max_items": 2000} |
- [官方快照：API列表/直链/IP黑名单配置/更新ip黑名单列表.md](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/IP%E9%BB%91%E5%90%8D%E5%8D%95%E9%85%8D%E7%BD%AE/%E6%9B%B4%E6%96%B0ip%E9%BB%91%E5%90%8D%E5%8D%95%E5%88%97%E8%A1%A8.md)
真实验证：`not_verified`；需要直链权益，未执行真实验证

## pan123 directlink blacklist switch

`POST /api/v1/developer/config/forbide-ip/switch`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --status | Status | int | True | None | {"choices": [1, 2]} |
- [官方快照：API列表/直链/IP黑名单配置/开启关闭ip黑名单.md](api-source/API%E5%88%97%E8%A1%A8/%E7%9B%B4%E9%93%BE/IP%E9%BB%91%E5%90%8D%E5%8D%95%E9%85%8D%E7%BD%AE/%E5%BC%80%E5%90%AF%E5%85%B3%E9%97%ADip%E9%BB%91%E5%90%8D%E5%8D%95.md)
真实验证：`not_verified`；需要直链权益，未执行真实验证

## pan123 image upload-api create

`POST /upload/v1/oss/file/create`，参数位置 `json`；只读 `False`；确认 `False`。

固定请求字段：`{"type": 1}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileID | str | True |  | {} |
| --filename | filename | str | True | None | {} |
| --etag | etag | str | True | None | {} |
| --size | size | int | True | None | {"minimum": 0} |
- [官方快照：API列表/图床/上传图片/创建文件.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E5%88%9B%E5%BB%BA%E6%96%87%E4%BB%B6.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image upload-api get-url

`POST /upload/v1/oss/file/get_upload_url`，参数位置 `json`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | preuploadID | str | True | None | {} |
| --slice-no | sliceNo | int | True | None | {"minimum": 1} |
- [官方快照：API列表/图床/上传图片/获取上传地址&上传分片.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9C%B0%E5%9D%80%26%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image upload-api put-slice

`PUT <presignedURL>`，参数位置 `binary`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | presignedURL | str | True | None | {} |
- [官方快照：API列表/图床/上传图片/获取上传地址&上传分片.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E5%9C%B0%E5%9D%80%26%E4%B8%8A%E4%BC%A0%E5%88%86%E7%89%87.md)
## pan123 image upload-api complete

`POST /upload/v1/oss/file/upload_complete`，参数位置 `json`；只读 `False`；确认 `False`。

等待配置：`{"field": "completed", "pending": [false], "success": [true], "failure": [], "interval": 1}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | preuploadID | str | True | None | {} |
- [官方快照：API列表/图床/上传图片/上传完毕.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E4%B8%8A%E4%BC%A0%E5%AE%8C%E6%AF%95.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image upload-api async-result

`POST /upload/v1/oss/file/upload_async_result`，参数位置 `json`；只读 `True`；确认 `False`。

等待配置：`{"field": "completed", "pending": [false], "success": [true], "failure": [], "interval": 1}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| stdin / 流程注入 | preuploadID | str | True | None | {} |
- [官方快照：API列表/图床/上传图片/异步轮询获取上传结果.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E5%BC%82%E6%AD%A5%E8%BD%AE%E8%AF%A2%E8%8E%B7%E5%8F%96%E4%B8%8A%E4%BC%A0%E7%BB%93%E6%9E%9C.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image mkdir

`POST /upload/v1/oss/file/mkdir`，参数位置 `json`；只读 `False`；确认 `False`。

固定请求字段：`{"type": 1}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --name | name | strs | True | None | {} |
| --parent-id | parentID | str | True |  | {} |
- [官方快照：API列表/图床/上传图片/创建目录.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E4%B8%8A%E4%BC%A0%E5%9B%BE%E7%89%87/%E5%88%9B%E5%BB%BA%E7%9B%AE%E5%BD%95.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image list

`POST /api/v1/oss/file/list`，参数位置 `json`；只读 `True`；确认 `False`。

固定请求字段：`{"type": 1}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileId | str | False |  | {} |
| --limit | limit | int | True | 100 | {"minimum": 1, "maximum": 100} |
| --start-time | startTime | int | False | None | {"minimum": 0} |
| --end-time | endTime | int | False | None | {"minimum": 0} |
| --last-file-id | lastFileId | str | False | None | {} |
- [官方快照：API列表/图床/获取图片信息/获取图片列表.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%89%87%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%89%87%E5%88%97%E8%A1%A8.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image info

`GET /api/v1/oss/file/detail`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileID | str | True | None | {} |
- [官方快照：API列表/图床/获取图片信息/获取图片详情.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%89%87%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E5%9B%BE%E7%89%87%E8%AF%A6%E6%83%85.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image move

`POST /api/v1/oss/file/move`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileIDs | strs | True | None | {"max_items": 100} |
| --parent-id | toParentFileID | str | True | None | {} |
- [官方快照：API列表/图床/移动图片.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E7%A7%BB%E5%8A%A8%E5%9B%BE%E7%89%87.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image delete

`POST /api/v1/oss/file/delete`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileIDs | strs | True | None | {"max_items": 100} |
- [官方快照：API列表/图床/删除图片.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%88%A0%E9%99%A4%E5%9B%BE%E7%89%87.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image source-copy

`POST /api/v1/oss/source/copy`，参数位置 `json`；只读 `False`；确认 `False`。

固定请求字段：`{"sourceType": 1, "type": 1}`

等待配置：`{"command": ["image", "source-copy-progress"]}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileIDs | strs | True | None | {"max_items": 100} |
| --parent-id | toParentFileID | str | True |  | {} |
- [官方快照：API列表/图床/复制云盘图片/创建复制任务.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%A4%8D%E5%88%B6%E4%BA%91%E7%9B%98%E5%9B%BE%E7%89%87/%E5%88%9B%E5%BB%BA%E5%A4%8D%E5%88%B6%E4%BB%BB%E5%8A%A1.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image source-copy-progress

`GET /api/v1/oss/source/copy/process`，参数位置 `query`；只读 `True`；确认 `False`。

等待配置：`{"field": "status", "pending": [1, 4], "success": [2], "failure": [3], "interval": 2}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --task-id | taskID | str | True | None | {} |
- [官方快照：API列表/图床/复制云盘图片/获取复制任务详情.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%A4%8D%E5%88%B6%E4%BA%91%E7%9B%98%E5%9B%BE%E7%89%87/%E8%8E%B7%E5%8F%96%E5%A4%8D%E5%88%B6%E4%BB%BB%E5%8A%A1%E8%AF%A6%E6%83%85.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image source-copy-failures

`GET /api/v1/oss/source/copy/fail`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --task-id | taskID | str | True | None | {} |
| --limit | limit | int | True | 100 | {"minimum": 1, "maximum": 100} |
| --page | page | int | True | 1 | {"minimum": 1} |
- [官方快照：API列表/图床/复制云盘图片/获取复制失败文件列表.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%A4%8D%E5%88%B6%E4%BA%91%E7%9B%98%E5%9B%BE%E7%89%87/%E8%8E%B7%E5%8F%96%E5%A4%8D%E5%88%B6%E5%A4%B1%E8%B4%A5%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image offline-create

`POST /api/v1/oss/offline/download`，参数位置 `json`；只读 `False`；确认 `False`。

固定请求字段：`{"type": 1}`

等待配置：`{"command": ["image", "offline-progress"]}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --url | url | str | True | None | {} |
| --filename | fileName | str | False | None | {} |
| --dir-id | dirID | str | False | None | {} |
| --callback-url | callBackUrl | str | False | None | {} |
- [官方快照：API列表/图床/图床离线迁移/创建离线迁移任务.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%9B%BE%E5%BA%8A%E7%A6%BB%E7%BA%BF%E8%BF%81%E7%A7%BB/%E5%88%9B%E5%BB%BA%E7%A6%BB%E7%BA%BF%E8%BF%81%E7%A7%BB%E4%BB%BB%E5%8A%A1.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 image offline-progress

`GET /api/v1/oss/offline/download/process`，参数位置 `query`；只读 `True`；确认 `False`。

等待配置：`{"field": "status", "pending": [0, 3], "success": [2], "failure": [1], "interval": 2}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --task-id | taskID | int | True | None | {"minimum": 1} |
- [官方快照：API列表/图床/图床离线迁移/获取离线迁移任务.md](api-source/API%E5%88%97%E8%A1%A8/%E5%9B%BE%E5%BA%8A/%E5%9B%BE%E5%BA%8A%E7%A6%BB%E7%BA%BF%E8%BF%81%E7%A7%BB/%E8%8E%B7%E5%8F%96%E7%A6%BB%E7%BA%BF%E8%BF%81%E7%A7%BB%E4%BB%BB%E5%8A%A1.md)
真实验证：`not_verified`；需要图床权益，未执行真实验证

## pan123 transcode source-list

`GET /api/v2/file/list`，参数位置 `query`；只读 `True`；确认 `False`。

固定请求字段：`{"category": 2}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileId | int | True | 0 | {"minimum": 0} |
| --limit | limit | int | True | 100 | {"minimum": 1, "maximum": 100} |
| --search | searchData | str | False | None | {} |
| --last-file-id | lastFileId | int | False | None | {"minimum": 0} |
| --search-mode | searchMode | int | False | None | {"choices": [0, 1]} |
- [官方快照：API列表/视频转码/上传视频/云盘上传/获取云盘视频文件.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E4%B8%8A%E4%BC%A0%E8%A7%86%E9%A2%91/%E4%BA%91%E7%9B%98%E4%B8%8A%E4%BC%A0/%E8%8E%B7%E5%8F%96%E4%BA%91%E7%9B%98%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6.md)
真实验证：`verified`；

## pan123 transcode folder-list

`GET /api/v2/file/list`，参数位置 `query`；只读 `True`；确认 `False`。

固定请求字段：`{"businessType": 2}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --parent-id | parentFileId | int | True | 0 | {"minimum": 0} |
| --limit | limit | int | True | 100 | {"minimum": 1, "maximum": 100} |
| --search | searchData | str | False | None | {} |
| --last-file-id | lastFileId | int | False | None | {"minimum": 0} |
| --search-mode | searchMode | int | False | None | {"choices": [0, 1]} |
- [官方快照：API列表/视频转码/获取视频信息/获取转码空间文件列表.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E8%BD%AC%E7%A0%81%E7%A9%BA%E9%97%B4%E6%96%87%E4%BB%B6%E5%88%97%E8%A1%A8.md)
真实验证：`verified`；

## pan123 transcode folder-info

`POST /api/v1/transcode/folder/info`，参数位置 `json`；只读 `True`；确认 `False`。

- [官方快照：API列表/视频转码/获取视频信息/获取转码空间文件夹信息.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E8%BD%AC%E7%A0%81%E7%A9%BA%E9%97%B4%E6%96%87%E4%BB%B6%E5%A4%B9%E4%BF%A1%E6%81%AF.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode from-cloud

`POST /api/v1/transcode/upload/from_cloud_disk`，参数位置 `json`；只读 `False`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | ints | True | None | {"max_items": 100} |
- [官方快照：API列表/视频转码/上传视频/云盘上传/从云盘空间上传.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E4%B8%8A%E4%BC%A0%E8%A7%86%E9%A2%91/%E4%BA%91%E7%9B%98%E4%B8%8A%E4%BC%A0/%E4%BB%8E%E4%BA%91%E7%9B%98%E7%A9%BA%E9%97%B4%E4%B8%8A%E4%BC%A0.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode resolutions

`POST /api/v1/transcode/video/resolutions`，参数位置 `json`；只读 `True`；确认 `False`。

等待配置：`{"field": "IsGetResolution", "pending": [true], "success": [false], "failure": [], "interval": 10}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
- [官方快照：API列表/视频转码/获取视频信息/获取视频文件可转码的分辨率.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E4%BF%A1%E6%81%AF/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6%E5%8F%AF%E8%BD%AC%E7%A0%81%E7%9A%84%E5%88%86%E8%BE%A8%E7%8E%87.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode run

`POST /api/v1/transcode/video`，参数位置 `json`；只读 `False`；确认 `True`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
| --codec-name | codecName | str | True | None | {} |
| --video-time | videoTime | float | True | None | {"minimum": 0} |
| --resolutions | resolutions | str | True | None | {} |
- [官方快照：API列表/视频转码/视频转码/视频转码操作.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81%E6%93%8D%E4%BD%9C.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode records

`POST /api/v1/transcode/video/record`，参数位置 `json`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
- [官方快照：API列表/视频转码/查询转码信息/查询某个视频的转码记录.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E6%9F%A5%E8%AF%A2%E8%BD%AC%E7%A0%81%E4%BF%A1%E6%81%AF/%E6%9F%A5%E8%AF%A2%E6%9F%90%E4%B8%AA%E8%A7%86%E9%A2%91%E7%9A%84%E8%BD%AC%E7%A0%81%E8%AE%B0%E5%BD%95.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode result

`POST /api/v1/transcode/video/result`，参数位置 `json`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
- [官方快照：API列表/视频转码/查询转码信息/查询某个视频的转码结果.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E6%9F%A5%E8%AF%A2%E8%BD%AC%E7%A0%81%E4%BF%A1%E6%81%AF/%E6%9F%A5%E8%AF%A2%E6%9F%90%E4%B8%AA%E8%A7%86%E9%A2%91%E7%9A%84%E8%BD%AC%E7%A0%81%E7%BB%93%E6%9E%9C.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode download-url

`POST /api/v1/transcode/file/download`，参数位置 `json`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
- [官方快照：API列表/视频转码/视频文件下载/原文件下载.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD/%E5%8E%9F%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode list

`GET /api/v1/video/transcode/list`，参数位置 `query`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
- [官方快照：API列表/视频转码/获取视频信息/视频转码列表（三方挂载应用授权使用）.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%8E%B7%E5%8F%96%E8%A7%86%E9%A2%91%E4%BF%A1%E6%81%AF/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81%E5%88%97%E8%A1%A8%EF%BC%88%E4%B8%89%E6%96%B9%E6%8C%82%E8%BD%BD%E5%BA%94%E7%94%A8%E6%8E%88%E6%9D%83%E4%BD%BF%E7%94%A8%EF%BC%89.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode delete

`POST /api/v1/transcode/delete`，参数位置 `json`；只读 `False`；确认 `True`。

固定请求字段：`{"businessType": 2}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
| --trashed | trashed | int | True | None | {"choices": [1, 2]} |
- [官方快照：API列表/视频转码/删除视频/删除转码视频.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E5%88%A0%E9%99%A4%E8%A7%86%E9%A2%91/%E5%88%A0%E9%99%A4%E8%BD%AC%E7%A0%81%E8%A7%86%E9%A2%91.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode segment-url

`POST /api/v1/transcode/m3u8_ts/download`，参数位置 `json`；只读 `True`；确认 `False`。

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
| --resolution | resolution | str | True | None | {} |
| --type | type | int | True | None | {"choices": [1, 2]} |
| --ts-name | tsName | str | False | None | {} |
- [官方快照：API列表/视频转码/视频文件下载/单个转码文件下载（m3u8或ts）.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD/%E5%8D%95%E4%B8%AA%E8%BD%AC%E7%A0%81%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD%EF%BC%88m3u8%E6%88%96ts%EF%BC%89.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

## pan123 transcode all-download-urls

`POST /api/v1/transcode/file/download/all`，参数位置 `json`；只读 `False`；确认 `False`。

等待配置：`{"field": "isDownloading", "pending": [true], "success": [false], "failure": [], "interval": 10}`

| CLI 参数 | API 字段 | 类型 | 必填 | 默认 | 限制 |
|---|---|---|---|---|---|
| --file-id | fileId | int | True | None | {"minimum": 1} |
| --zip-name | zipName | str | True | None | {} |
- [官方快照：API列表/视频转码/视频文件下载/某个视频全部转码文件下载.md](api-source/API%E5%88%97%E8%A1%A8/%E8%A7%86%E9%A2%91%E8%BD%AC%E7%A0%81/%E8%A7%86%E9%A2%91%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD/%E6%9F%90%E4%B8%AA%E8%A7%86%E9%A2%91%E5%85%A8%E9%83%A8%E8%BD%AC%E7%A0%81%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD.md)
真实验证：`not_verified`；需要转码权益或第三方应用授权，未执行真实验证

