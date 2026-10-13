# Official 123Pan CLI implementation plan

> **For agentic workers:** Execute the tasks below with focused parallel implementers and a whole-project review. Use test-driven-development for business behavior and verification-before-completion for completion claims. The user's instruction is to implement the existing design now.

**Goal:** Deliver the standalone Python CLI with all 72 documented OpenAPI routes, safe file transfer workflows and Windows/macOS/Linux installation instructions.

**Architecture:** Typed endpoint metadata drives argparse and request validation. One official API client shares a protected local token manager; file upload/download services use separate authenticated or unauthenticated transport paths. Commands return one JSON document or readable output with progress on stderr.

**Tech Stack:** Python >=3.12, argparse, HTTPX, Rich, platformdirs, filelock, python-dotenv; pytest, Ruff, mypy, build, setuptools.

**Spec:** ../../123Pan-CLI技术栈与开发文档.md and ../../CLI完整命令参考.md.

## Global constraints

- Official control base URL is https://open-api.123pan.com; no self-hosted gateway, stoken or Appwrite identity.
- `pan123` and `python -m pan123_cli` expose the same commands; list/upload/download are root aliases.
- Secrets never become value-bearing argv parameters or normal logs. A command has at most one stdin consumer.
- Parameter location, wire field casing, ID types and method must follow each endpoint's source, including GET JSON body exceptions.
- HTTP and business code both determine success; OAuth bare token objects, presigned PUT and CDN streams have separate adapters.
- Uploads are sequential with bounded memory; complete+file ID+readback verify success. Mutations with unknown results are not automatically replayed.
- Downloads preserve `.part` on failure, verify size/MD5 and publish without overwriting by default.
- Linux/macOS/Windows x86_64 and ARM64 are target environments; actual verified environments must be reported separately.

## Shared interfaces

- `errors.Pan123Error(kind, message, *, exit_code=None, http_status=None, api_code=None, trace_id=None, retryable=False, details=None)` stores these fields and exposes `as_dict()`.
- `config.Settings`: client_id/client_secret, auth_mode, oauth_client_id/oauth_client_secret/oauth_redirect_uri, cache_dir, api_timeout=30, transfer_timeout=120, token_refresh_skew_seconds=300, read_max_retries=3; property `fingerprint` identifies the current auth mode/account/secret.
- `config.load_settings(overrides: Mapping[str, Any], environ: Mapping[str,str]|None=None) -> Settings` reads only explicit env-file, applies precedence and validates inputs; missing credentials are validated only for actions that need them.
- `cache.write_private_json(path: Path, data: Any)`, `cache.read_private_json(path: Path) -> Any` write atomically with private access.
- `auth.TokenManager(settings: Settings, client: httpx.Client|None=None)` provides get_token(), invalidate(token=None), status(), clear(), authorize_url(client_id=None,redirect_uri=None,state=None), exchange(code,state,client_id=None,redirect_uri=None,client_secret=None), refresh(refresh_token=None,client_secret=None), close(). Auth methods return safe metadata only.
- `catalog.Field(wire, flag, kind='str', required=False, default=None, choices=None, minimum=None, maximum=None, max_items=None, help='')`; supported kinds str/int/float/bool/ints/strs/json. flag=None means no value-bearing CLI option.
- `catalog.Endpoint(command: tuple[str,...], method, path, location='json', fields=(), fixed={}, confirmation=False, read_only=False, auth_mode=None, special=None, source_paths=(), wait=None)`; `ENDPOINTS` is the full route catalog. `payload_for(endpoint, values: Mapping, request_data=None) -> Any` validates exact body/query fields, fixed fields, arrays, conditional/nested schemas. No unknown request keys.
- `client.ApiClient(settings, token_manager=None, http_client=None, transfer_client=None)` provides `request(method,path,*,params=None,json=None,retryable=False,authenticated=True) -> Any`, `upload_slice(server,*,data,files) -> Any`, `put_external(url,fileobj)`, `stream_download(url)` context manager, close(). request returns API data, not the whole envelope.
- `services.listing.list_files(client, *, parent_id=0, limit=100, cursor=None, search=None, all_pages=False, include_trashed=False, api_version='v2', **extra) -> dict`.
- `services.uploading.upload_file(client, file:Path, *, parent_id=0,name=None,duplicate='error',api_version='v2',business='file',complete_timeout=300,progress=None) -> dict`.
- `services.uploading.dispatch_upload(client, command:tuple[str,...], payload:dict, options:Mapping) -> Any` implements all low-level file/image upload actions, protected session/domain/URL files and V2 single/SHA1 workflows.
- `services.downloading.download_file(client,file_id:int,output:Path|None=None,*,overwrite=False,progress=None) -> dict`.

## Review focus

1. HTTP 200 business failure and different response envelopes must not silently succeed (client tests).
2. Filtered-empty pages and repeated cursors must not lose files or loop (listing tests).
3. Secret-bearing HTTP exception strings, OAuth refresh races and account cache separation (auth/client tests).
4. A racing file creator, target symlinks, wrong MD5, interrupted transfer and disk failures (download/upload tests).
5. Nontrivial request shapes: CSV versus array, nested arrays, GET body, upper-case blacklist keys and auth-only transcode commands (catalog/CLI tests).

## Task 1: Packaging and command runner (parent)

Files: pyproject.toml, src/pan123_cli/{__init__,__main__,cli,output,client}.py, tests/test_cli.py, tests/test_client.py.

- [ ] Write and run failing offline help/JSON argument error and HTTP business-error tests.
- [ ] Add package metadata, independent virtual environment and typed CLI parser/output/client modules.
- [ ] Wire the catalog and services as they arrive; verify no credential or network requirement for help/version.
- [ ] Validate read-only retries, response schemas, official domain-only routing and no auth on CDN/PUT.

## Task 2: Configuration, cache and auth (parallel implementer)

Files: src/pan123_cli/{errors,config,cache,auth}.py and utils/urls.py; tests/test_{config,auth,urls}.py.

- [ ] Test precedence, explicit env-file, aware expiry, credential change, refresh locks and OAuth state/rotation before implementing.
- [ ] Implement the shared interfaces; keep secret repr/output redacted and metadata files private.
- [ ] Verify missing configuration and local status/clear behavior without unintended network/file mutations.

## Task 3: Full route catalog and request validation (parallel implementer)

Files: src/pan123_cli/catalog.py, command_specs/*.py if needed; tests/test_catalog.py.

- [ ] Write independently sourced exact payload cases and assert all 72 routes represented.
- [ ] Map every command to exact method/path/location/types; retain schemas for shared route variants.
- [ ] Implement validation of required/conditional/nested inputs, array limits, fixed parameters and special handlers.
- [ ] Verify all documented domains, including legacy, OAuth and transmission protocol commands.

## Task 4: Listing and transfer services (parallel implementer)

Files: src/pan123_cli/services/{listing,uploading,downloading}.py; utils/files.py; tests/test_{list,upload,download}.py.

- [ ] Test multi-page/filtered-empty/repeated-cursor behavior and byte-level transfer boundaries before implementation.
- [ ] Implement V2 file, V1 file/OSS/video, single-step/SHA1 and low-level upload lifecycle.
- [ ] Implement stream download, MD5/size verification, interruption behavior and atomic no-clobber publication.
- [ ] Validate source mutation, temp storage cleanup, completion timeout and detail readback.

## Task 5: Integration, documentation and cross-platform CI (parent)

Files: README.md, docs/安装与使用.md, existing development/reference/coverage docs, .github/workflows/ci.yml, constraints files.

- [ ] Exercise every command's help and parameter validation via real parser and mocked transport.
- [ ] Update status to distinguish implemented/mock-verified/real-verified endpoint coverage.
- [ ] Add POSIX, PowerShell and cmd usage and install/uninstall; include native architecture support requirements.
- [ ] Add CI for Python 3.12/3.13/3.14 on supported desktop/server OSes and ARM runners where available.
- [ ] Run whole test suite, lint/type checks, build wheel/sdist and install wheel into fresh environments.
- [ ] Perform bounded live read verification if suitable local credentials exist; write tests only to an isolated newly-created test resource when authorized and supported. Do not alter sharing, paid settings, blacklist or user data to claim API coverage.
- [ ] Review actual code independently, fix actionable findings, commit and push verified implementation.

## Execution notes

The current checkout is clean at initial documentation commit ae7c9be. Work uses feature branch feat/official-cli in the independent project. Interface changes are announced to all implementers. Live platform and account validation limitations remain explicit; no platform success is inferred from another OS's tests.
