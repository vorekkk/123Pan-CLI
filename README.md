# 123Pan CLI

123 云盘开放 API 命令行工具的独立工程。工程目录为 `/Users/vorek/Coding Project/123Pan-CLI`，源码、环境和文档均独立管理。

当前阶段：开发文档与完整命令设计已整理，CLI 源码尚未实现；当前不能执行 pan123 或安装发行包。

## GitHub 仓库

仓库：[vorekkk/123Pan-CLI](https://github.com/vorekkk/123Pan-CLI)，可见性为私有，主分支为 `main`。

```bash
git clone https://github.com/vorekkk/123Pan-CLI.git
cd 123Pan-CLI
```

## 开发文档

- [技术栈与开发文档](./docs/123Pan-CLI技术栈与开发文档.md)：Python、argparse、HTTPX、模块结构、鉴权、缓存、上传、下载、测试与发布。
- [完整 CLI 命令参考](./docs/CLI完整命令参考.md)：鉴权/OAuth、文件管理、分享、离线下载、用户、直链、图床、视频转码，逐项映射 API 的参数、位置、返回值与约束。
- [API 覆盖清单](./docs/API覆盖清单.json)：87 篇来源、74 篇接口文档、72 个独立 method/path，记录文档覆盖和后续实现/验收状态。
- [API 原始来源清单](./docs/api-source/_manifest.json)：实际采集时间为 2026-09-11，原始官方资料快照已随工程独立保存。

## 官方直连接入

控制接口固定为 `https://open-api.123pan.com`；本机 clientID / clientSecret 获取官方 accessToken，再携带 Bearer / Platform 调用业务 API。上传使用官方返回的 servers / presignedURL，下载使用官方返回的 downloadUrl。调用链路不经过自部署网关，也不生成或使用 stoken / Appwrite JWT。

## 开发原则

开发者凭据留在本机，CLI 直连 `https://open-api.123pan.com`；默认开发者鉴权，第三方限定接口使用单独 OAuth 授权。所有 API 的完整命令已纳入设计，列表、上传、下载优先打通，随后按开发文档完成其他领域。

配置、虚拟环境、依赖、源码、测试与构建均在本工程管理。当前交付只包含文档与来源资料；源码布局、安装命令和开发阶段见技术文档，开发与验证均使用本工程独立运行环境。

文档已标明快照冲突和需要真实账户核验的行为；文档覆盖不等于 API 代码或联调已经完成。
