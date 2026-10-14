# 123Pan CLI

直接调用 123 云盘官方 OpenAPI 的独立命令行工具，当前版本 **0.1.0**。支持 Python 3.12+，面向 macOS、Windows、Linux 的 x86_64 / ARM64。

已实现官方快照的 **72 个独立 HTTP 接口**及其命令变体，涵盖认证、OAuth、文件管理、分享、离线下载、用户信息、直链、图床、视频转码。普通文件的列表、上传、分片、秒传、下载已完成真实账户验证；其他业务域的真实验证状态见覆盖清单。

## 安装

仓库公开。推荐用 `uv` 或 `pipx` 一行安装：它自动建立隔离环境，并把 `pan123` 放进 PATH，不需要克隆或手动建虚拟环境。

```bash
uv tool install git+https://github.com/vorekkk/123Pan-CLI.git
pan123 --help
```

`pipx install git+https://github.com/vorekkk/123Pan-CLI.git` 等价可用。若偏好源码目录，也可以克隆后用虚拟环境安装：

```bash
git clone https://github.com/vorekkk/123Pan-CLI.git
cd 123Pan-CLI
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/pan123 --help
```

Windows 源码安装使用 `py -3 -m venv .venv`，前缀分别为 `.venv\Scripts\python.exe` 与 `.venv\Scripts\pan123.exe`。详细的 PowerShell、cmd、pipx、wheel 用法见[安装与使用](./docs/安装与使用.md)。此版本是 Python 包，未提供无需 Python 的独立可执行程序；也尚未发布到 PyPI，因此安装命令需要带 `git+` 地址。

## 开始使用

将 `.env.example` 复制为 `.env`，在本机填写 `PAN123_CLIENT_ID` / `PAN123_CLIENT_SECRET`。也兼容现有的 `CLIENT_ID` / `CLIENT_SECRET`；凭据文件不会进入 Git。CLI 只读取明确指定的 env-file。

```bash
.venv/bin/pan123 --env-file .env auth ensure
.venv/bin/pan123 --env-file .env file list --parent-id 0 --all --json
.venv/bin/pan123 --env-file .env file upload --file './报告.pdf' --parent-id 123456
.venv/bin/pan123 --env-file .env file download --file-id 123456 --output './报告副本.pdf'
```

示例 ID 需换为自己的目录或文件 ID。`list`、`upload`、`download` 是根命令别名；所有帮助页面均可离线查看。变更命令按帮助要求确认或使用 `--yes`。stdout JSON 便于脚本消费，进度写入 stderr，下载在大小与 MD5 校验通过后才发布正式文件。

控制接口固定为 `https://open-api.123pan.com`；上传、下载连接官方返回的 HTTPS 地址。凭据保存在本机，OAuth 令牌单独管理。

若本机代理使用 Fake-IP DNS（198.18.0.0/15），可明确加入 `--allow-fake-ip`，或设置 `PAN123_ALLOW_FAKE_IP=true`。默认仍要求公开 DNS 地址，并保持原始主机的 TLS 证书验证。

## 文档

- [安装与使用](./docs/安装与使用.md)：所有平台安装、配置和常用命令。
- [完整 CLI 命令参考](./docs/CLI完整命令参考.md)：各业务域的输入、API 字段与约束；运行参数以 `--help` 为准。
- [技术栈与开发文档](./docs/123Pan-CLI技术栈与开发文档.md)：模块、鉴权、传输、测试与发布。
- [API 覆盖清单](./docs/API覆盖清单.json)：87 篇资料、74 篇接口文档、72 个独立接口的实现与验证状态。
- [真实联调记录](./docs/真实联调记录.md)及[实施进度](./docs/实施进度.md)。
- [官方资料快照](./docs/api-source/_manifest.json)：采集于 2026-09-11；配额与权限仍以当前官方和账号返回为准。

## 开发

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
.venv/bin/python -m ruff format --check src tests
.venv/bin/python -m mypy src/pan123_cli
.venv/bin/python -m build
.venv/bin/python scripts/check_wheel.py
```

GitHub Actions 配置 Python 3.12 / 3.13 / 3.14 的四个操作系统 runner，另有 Linux / Windows ARM64 的手动验证。实际结果见[实施进度](./docs/实施进度.md)。
