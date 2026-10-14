# 实际 CLI 帮助全集

## pan123

```text
usage: pan123 [-h] [--json] [--verbose] [--no-progress] [--allow-fake-ip]
              [--yes] [--config CONFIG] [--env-file ENV_FILE]
              [--cache-dir CACHE_DIR] [--auth-mode {developer,oauth}]
              [--timeout TIMEOUT] [--transfer-timeout TRANSFER_TIMEOUT]
              [--version]
              {auth,oauth,file,share,offline,user,directlink,image,transcode,setup,skill} ...

123 云盘官方 OpenAPI 命令行工具

positional arguments:
  {auth,oauth,file,share,offline,user,directlink,image,transcode,setup,skill}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --version             show program's version number and exit
```

## pan123 auth

```text
usage: pan123 auth [-h] [--json] [--verbose] [--no-progress] [--allow-fake-ip]
                   [--yes] [--config CONFIG] [--env-file ENV_FILE]
                   [--cache-dir CACHE_DIR] [--auth-mode {developer,oauth}]
                   [--timeout TIMEOUT] [--transfer-timeout TRANSFER_TIMEOUT]
                   {ensure,status,clear} ...

positional arguments:
  {ensure,status,clear}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 auth ensure

```text
usage: pan123 auth ensure [-h] [--json] [--verbose] [--no-progress]
                          [--allow-fake-ip] [--yes] [--config CONFIG]
                          [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                          [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                          [--transfer-timeout TRANSFER_TIMEOUT]
                          [--client-id CLIENT_ID]
                          [--redirect-uri REDIRECT_URI] [--state STATE]
                          [--client-secret-stdin] [--code-stdin]
                          [--refresh-token-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --client-id CLIENT_ID
                        clientID
  --redirect-uri REDIRECT_URI
  --state STATE
  --client-secret-stdin
  --code-stdin
  --refresh-token-stdin
```

## pan123 auth status

```text
usage: pan123 auth status [-h] [--json] [--verbose] [--no-progress]
                          [--allow-fake-ip] [--yes] [--config CONFIG]
                          [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                          [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                          [--transfer-timeout TRANSFER_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 auth clear

```text
usage: pan123 auth clear [-h] [--json] [--verbose] [--no-progress]
                         [--allow-fake-ip] [--yes] [--config CONFIG]
                         [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                         [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                         [--transfer-timeout TRANSFER_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 oauth

```text
usage: pan123 oauth [-h] [--json] [--verbose] [--no-progress]
                    [--allow-fake-ip] [--yes] [--config CONFIG]
                    [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                    [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                    [--transfer-timeout TRANSFER_TIMEOUT]
                    {exchange,refresh,authorize-url} ...

positional arguments:
  {exchange,refresh,authorize-url}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 oauth exchange

```text
usage: pan123 oauth exchange [-h] [--json] [--verbose] [--no-progress]
                             [--allow-fake-ip] [--yes] [--config CONFIG]
                             [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                             [--auth-mode {developer,oauth}]
                             [--timeout TIMEOUT]
                             [--transfer-timeout TRANSFER_TIMEOUT]
                             [--client-id CLIENT_ID]
                             [--redirect-uri REDIRECT_URI] [--state STATE]
                             [--client-secret-stdin] [--code-stdin]
                             [--refresh-token-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --client-id CLIENT_ID
                        client_id
  --redirect-uri REDIRECT_URI
                        redirect_uri
  --state STATE
  --client-secret-stdin
  --code-stdin
  --refresh-token-stdin
```

## pan123 oauth refresh

```text
usage: pan123 oauth refresh [-h] [--json] [--verbose] [--no-progress]
                            [--allow-fake-ip] [--yes] [--config CONFIG]
                            [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                            [--auth-mode {developer,oauth}]
                            [--timeout TIMEOUT]
                            [--transfer-timeout TRANSFER_TIMEOUT]
                            [--client-id CLIENT_ID]
                            [--redirect-uri REDIRECT_URI] [--state STATE]
                            [--client-secret-stdin] [--code-stdin]
                            [--refresh-token-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --client-id CLIENT_ID
                        client_id
  --redirect-uri REDIRECT_URI
  --state STATE
  --client-secret-stdin
  --code-stdin
  --refresh-token-stdin
```

## pan123 oauth authorize-url

```text
usage: pan123 oauth authorize-url [-h] [--json] [--verbose] [--no-progress]
                                  [--allow-fake-ip] [--yes] [--config CONFIG]
                                  [--env-file ENV_FILE]
                                  [--cache-dir CACHE_DIR]
                                  [--auth-mode {developer,oauth}]
                                  [--timeout TIMEOUT]
                                  [--transfer-timeout TRANSFER_TIMEOUT]
                                  [--client-id CLIENT_ID]
                                  [--redirect-uri REDIRECT_URI]
                                  [--state STATE]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --client-id CLIENT_ID
  --redirect-uri REDIRECT_URI
  --state STATE
```

## pan123 file

```text
usage: pan123 file [-h] [--json] [--verbose] [--no-progress] [--allow-fake-ip]
                   [--yes] [--config CONFIG] [--env-file ENV_FILE]
                   [--cache-dir CACHE_DIR] [--auth-mode {developer,oauth}]
                   [--timeout TIMEOUT] [--transfer-timeout TRANSFER_TIMEOUT]
                   {list,info,infos,mkdir,rename,rename-batch,trash,copy,copy-batch,copy-progress,recover,recover-to,move,safebox-unlock,download-url,upload-api,upload,download} ...

positional arguments:
  {list,info,infos,mkdir,rename,rename-batch,trash,copy,copy-batch,copy-progress,recover,recover-to,move,safebox-unlock,download-url,upload-api,upload,download}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 file list

```text
usage: pan123 file list [-h] [--json] [--verbose] [--no-progress]
                        [--allow-fake-ip] [--yes] [--config CONFIG]
                        [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                        [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                        [--transfer-timeout TRANSFER_TIMEOUT]
                        [--request-file REQUEST_FILE] [--parent-id PARENT_ID]
                        [--limit LIMIT] [--search SEARCH]
                        [--last-file-id LAST_FILE_ID] [--api-version {v1,v2}]
                        [--page PAGE] [--order-by ORDER_BY]
                        [--order-direction ORDER_DIRECTION]
                        [--trashed TRASHED] [--all] [--include-trashed]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --parent-id PARENT_ID
                        parentFileId
  --limit LIMIT         limit
  --search SEARCH       searchData
  --last-file-id LAST_FILE_ID
                        lastFileId
  --api-version {v1,v2}
  --page PAGE
  --order-by ORDER_BY
  --order-direction ORDER_DIRECTION
  --trashed TRASHED
  --all
  --include-trashed
```

## pan123 file info

```text
usage: pan123 file info [-h] [--json] [--verbose] [--no-progress]
                        [--allow-fake-ip] [--yes] [--config CONFIG]
                        [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                        [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                        [--transfer-timeout TRANSFER_TIMEOUT]
                        [--request-file REQUEST_FILE] [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileID
```

## pan123 file infos

```text
usage: pan123 file infos [-h] [--json] [--verbose] [--no-progress]
                         [--allow-fake-ip] [--yes] [--config CONFIG]
                         [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                         [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                         [--transfer-timeout TRANSFER_TIMEOUT]
                         [--request-file REQUEST_FILE] [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileIds
```

## pan123 file mkdir

```text
usage: pan123 file mkdir [-h] [--json] [--verbose] [--no-progress]
                         [--allow-fake-ip] [--yes] [--config CONFIG]
                         [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                         [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                         [--transfer-timeout TRANSFER_TIMEOUT]
                         [--request-file REQUEST_FILE] [--name NAME]
                         [--parent-id PARENT_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --name NAME           name
  --parent-id PARENT_ID
                        parentID
```

## pan123 file rename

```text
usage: pan123 file rename [-h] [--json] [--verbose] [--no-progress]
                          [--allow-fake-ip] [--yes] [--config CONFIG]
                          [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                          [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                          [--transfer-timeout TRANSFER_TIMEOUT]
                          [--request-file REQUEST_FILE] [--file-id FILE_ID]
                          [--name NAME]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
  --name NAME           fileName
```

## pan123 file rename-batch

```text
usage: pan123 file rename-batch [-h] [--json] [--verbose] [--no-progress]
                                [--allow-fake-ip] [--yes] [--config CONFIG]
                                [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                [--auth-mode {developer,oauth}]
                                [--timeout TIMEOUT]
                                [--transfer-timeout TRANSFER_TIMEOUT]
                                [--request-file REQUEST_FILE]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
```

## pan123 file trash

```text
usage: pan123 file trash [-h] [--json] [--verbose] [--no-progress]
                         [--allow-fake-ip] [--yes] [--config CONFIG]
                         [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                         [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                         [--transfer-timeout TRANSFER_TIMEOUT]
                         [--request-file REQUEST_FILE] [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileIDs
```

## pan123 file copy

```text
usage: pan123 file copy [-h] [--json] [--verbose] [--no-progress]
                        [--allow-fake-ip] [--yes] [--config CONFIG]
                        [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                        [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                        [--transfer-timeout TRANSFER_TIMEOUT]
                        [--request-file REQUEST_FILE] [--file-id FILE_ID]
                        [--target-dir-id TARGET_DIR_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
  --target-dir-id TARGET_DIR_ID
                        targetDirId
```

## pan123 file copy-batch

```text
usage: pan123 file copy-batch [-h] [--json] [--verbose] [--no-progress]
                              [--allow-fake-ip] [--yes] [--config CONFIG]
                              [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                              [--auth-mode {developer,oauth}]
                              [--timeout TIMEOUT]
                              [--transfer-timeout TRANSFER_TIMEOUT]
                              [--request-file REQUEST_FILE]
                              [--file-id FILE_ID]
                              [--target-dir-id TARGET_DIR_ID] [--wait]
                              [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileIds
  --target-dir-id TARGET_DIR_ID
                        targetDirId
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 file copy-progress

```text
usage: pan123 file copy-progress [-h] [--json] [--verbose] [--no-progress]
                                 [--allow-fake-ip] [--yes] [--config CONFIG]
                                 [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                 [--auth-mode {developer,oauth}]
                                 [--timeout TIMEOUT]
                                 [--transfer-timeout TRANSFER_TIMEOUT]
                                 [--request-file REQUEST_FILE]
                                 [--task-id TASK_ID] [--wait]
                                 [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --task-id TASK_ID     taskId
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 file recover

```text
usage: pan123 file recover [-h] [--json] [--verbose] [--no-progress]
                           [--allow-fake-ip] [--yes] [--config CONFIG]
                           [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                           [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                           [--transfer-timeout TRANSFER_TIMEOUT]
                           [--request-file REQUEST_FILE] [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileIDs
```

## pan123 file recover-to

```text
usage: pan123 file recover-to [-h] [--json] [--verbose] [--no-progress]
                              [--allow-fake-ip] [--yes] [--config CONFIG]
                              [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                              [--auth-mode {developer,oauth}]
                              [--timeout TIMEOUT]
                              [--transfer-timeout TRANSFER_TIMEOUT]
                              [--request-file REQUEST_FILE]
                              [--file-id FILE_ID] [--parent-id PARENT_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileIDs
  --parent-id PARENT_ID
                        parentFileID
```

## pan123 file move

```text
usage: pan123 file move [-h] [--json] [--verbose] [--no-progress]
                        [--allow-fake-ip] [--yes] [--config CONFIG]
                        [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                        [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                        [--transfer-timeout TRANSFER_TIMEOUT]
                        [--request-file REQUEST_FILE] [--file-id FILE_ID]
                        [--parent-id PARENT_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileIDs
  --parent-id PARENT_ID
                        toParentFileID
```

## pan123 file safebox-unlock

```text
usage: pan123 file safebox-unlock [-h] [--json] [--verbose] [--no-progress]
                                  [--allow-fake-ip] [--yes] [--config CONFIG]
                                  [--env-file ENV_FILE]
                                  [--cache-dir CACHE_DIR]
                                  [--auth-mode {developer,oauth}]
                                  [--timeout TIMEOUT]
                                  [--transfer-timeout TRANSFER_TIMEOUT]
                                  [--request-file REQUEST_FILE]
                                  [--password-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --password-stdin
```

## pan123 file download-url

```text
usage: pan123 file download-url [-h] [--json] [--verbose] [--no-progress]
                                [--allow-fake-ip] [--yes] [--config CONFIG]
                                [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                [--auth-mode {developer,oauth}]
                                [--timeout TIMEOUT]
                                [--transfer-timeout TRANSFER_TIMEOUT]
                                [--request-file REQUEST_FILE]
                                [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
```

## pan123 file upload-api

```text
usage: pan123 file upload-api [-h] [--json] [--verbose] [--no-progress]
                              [--allow-fake-ip] [--yes] [--config CONFIG]
                              [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                              [--auth-mode {developer,oauth}]
                              [--timeout TIMEOUT]
                              [--transfer-timeout TRANSFER_TIMEOUT]
                              {v1,v2} ...

positional arguments:
  {v1,v2}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 file upload-api v1

```text
usage: pan123 file upload-api v1 [-h] [--json] [--verbose] [--no-progress]
                                 [--allow-fake-ip] [--yes] [--config CONFIG]
                                 [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                 [--auth-mode {developer,oauth}]
                                 [--timeout TIMEOUT]
                                 [--transfer-timeout TRANSFER_TIMEOUT]
                                 {create,url,put,parts,result,complete} ...

positional arguments:
  {create,url,put,parts,result,complete}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 file upload-api v1 create

```text
usage: pan123 file upload-api v1 create [-h] [--json] [--verbose]
                                        [--no-progress] [--allow-fake-ip]
                                        [--yes] [--config CONFIG]
                                        [--env-file ENV_FILE]
                                        [--cache-dir CACHE_DIR]
                                        [--auth-mode {developer,oauth}]
                                        [--timeout TIMEOUT]
                                        [--transfer-timeout TRANSFER_TIMEOUT]
                                        [--request-file REQUEST_FILE]
                                        [--parent-id PARENT_ID]
                                        [--filename FILENAME] [--etag ETAG]
                                        [--size SIZE] [--duplicate {1,2}]
                                        [--contain-dir CONTAIN_DIR]
                                        [--session-file SESSION_FILE]
                                        [--session-out SESSION_OUT]
                                        [--url-out URL_OUT]
                                        [--domains-out DOMAINS_OUT]
                                        [--domains-file DOMAINS_FILE]
                                        [--upload-url-file UPLOAD_URL_FILE]
                                        [--slice SLICE]
                                        [--slice-file SLICE_FILE]
                                        [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --parent-id PARENT_ID
                        parentFileID
  --filename FILENAME   filename
  --etag ETAG           etag
  --size SIZE           size
  --duplicate {1,2}     duplicate
  --contain-dir CONTAIN_DIR
                        containDir
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v1 url

```text
usage: pan123 file upload-api v1 url [-h] [--json] [--verbose] [--no-progress]
                                     [--allow-fake-ip] [--yes]
                                     [--config CONFIG] [--env-file ENV_FILE]
                                     [--cache-dir CACHE_DIR]
                                     [--auth-mode {developer,oauth}]
                                     [--timeout TIMEOUT]
                                     [--transfer-timeout TRANSFER_TIMEOUT]
                                     [--request-file REQUEST_FILE]
                                     [--slice-no SLICE_NO]
                                     [--session-file SESSION_FILE]
                                     [--session-out SESSION_OUT]
                                     [--url-out URL_OUT]
                                     [--domains-out DOMAINS_OUT]
                                     [--domains-file DOMAINS_FILE]
                                     [--upload-url-file UPLOAD_URL_FILE]
                                     [--slice SLICE] [--slice-file SLICE_FILE]
                                     [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --slice-no SLICE_NO   sliceNo
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v1 put

```text
usage: pan123 file upload-api v1 put [-h] [--json] [--verbose] [--no-progress]
                                     [--allow-fake-ip] [--yes]
                                     [--config CONFIG] [--env-file ENV_FILE]
                                     [--cache-dir CACHE_DIR]
                                     [--auth-mode {developer,oauth}]
                                     [--timeout TIMEOUT]
                                     [--transfer-timeout TRANSFER_TIMEOUT]
                                     [--request-file REQUEST_FILE]
                                     [--session-file SESSION_FILE]
                                     [--session-out SESSION_OUT]
                                     [--url-out URL_OUT]
                                     [--domains-out DOMAINS_OUT]
                                     [--domains-file DOMAINS_FILE]
                                     [--upload-url-file UPLOAD_URL_FILE]
                                     [--slice SLICE] [--slice-file SLICE_FILE]
                                     [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v1 parts

```text
usage: pan123 file upload-api v1 parts [-h] [--json] [--verbose]
                                       [--no-progress] [--allow-fake-ip]
                                       [--yes] [--config CONFIG]
                                       [--env-file ENV_FILE]
                                       [--cache-dir CACHE_DIR]
                                       [--auth-mode {developer,oauth}]
                                       [--timeout TIMEOUT]
                                       [--transfer-timeout TRANSFER_TIMEOUT]
                                       [--request-file REQUEST_FILE]
                                       [--session-file SESSION_FILE]
                                       [--session-out SESSION_OUT]
                                       [--url-out URL_OUT]
                                       [--domains-out DOMAINS_OUT]
                                       [--domains-file DOMAINS_FILE]
                                       [--upload-url-file UPLOAD_URL_FILE]
                                       [--slice SLICE]
                                       [--slice-file SLICE_FILE] [--file FILE]
                                       [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v1 result

```text
usage: pan123 file upload-api v1 result [-h] [--json] [--verbose]
                                        [--no-progress] [--allow-fake-ip]
                                        [--yes] [--config CONFIG]
                                        [--env-file ENV_FILE]
                                        [--cache-dir CACHE_DIR]
                                        [--auth-mode {developer,oauth}]
                                        [--timeout TIMEOUT]
                                        [--transfer-timeout TRANSFER_TIMEOUT]
                                        [--request-file REQUEST_FILE] [--wait]
                                        [--wait-timeout WAIT_TIMEOUT]
                                        [--session-file SESSION_FILE]
                                        [--session-out SESSION_OUT]
                                        [--url-out URL_OUT]
                                        [--domains-out DOMAINS_OUT]
                                        [--domains-file DOMAINS_FILE]
                                        [--upload-url-file UPLOAD_URL_FILE]
                                        [--slice SLICE]
                                        [--slice-file SLICE_FILE]
                                        [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --wait
  --wait-timeout WAIT_TIMEOUT
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v1 complete

```text
usage: pan123 file upload-api v1 complete [-h] [--json] [--verbose]
                                          [--no-progress] [--allow-fake-ip]
                                          [--yes] [--config CONFIG]
                                          [--env-file ENV_FILE]
                                          [--cache-dir CACHE_DIR]
                                          [--auth-mode {developer,oauth}]
                                          [--timeout TIMEOUT]
                                          [--transfer-timeout TRANSFER_TIMEOUT]
                                          [--request-file REQUEST_FILE]
                                          [--wait]
                                          [--wait-timeout WAIT_TIMEOUT]
                                          [--session-file SESSION_FILE]
                                          [--session-out SESSION_OUT]
                                          [--url-out URL_OUT]
                                          [--domains-out DOMAINS_OUT]
                                          [--domains-file DOMAINS_FILE]
                                          [--upload-url-file UPLOAD_URL_FILE]
                                          [--slice SLICE]
                                          [--slice-file SLICE_FILE]
                                          [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --wait
  --wait-timeout WAIT_TIMEOUT
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v2

```text
usage: pan123 file upload-api v2 [-h] [--json] [--verbose] [--no-progress]
                                 [--allow-fake-ip] [--yes] [--config CONFIG]
                                 [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                 [--auth-mode {developer,oauth}]
                                 [--timeout TIMEOUT]
                                 [--transfer-timeout TRANSFER_TIMEOUT]
                                 {create,slice,domains,single,sha1-reuse,complete} ...

positional arguments:
  {create,slice,domains,single,sha1-reuse,complete}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 file upload-api v2 create

```text
usage: pan123 file upload-api v2 create [-h] [--json] [--verbose]
                                        [--no-progress] [--allow-fake-ip]
                                        [--yes] [--config CONFIG]
                                        [--env-file ENV_FILE]
                                        [--cache-dir CACHE_DIR]
                                        [--auth-mode {developer,oauth}]
                                        [--timeout TIMEOUT]
                                        [--transfer-timeout TRANSFER_TIMEOUT]
                                        [--request-file REQUEST_FILE]
                                        [--parent-id PARENT_ID]
                                        [--filename FILENAME] [--etag ETAG]
                                        [--size SIZE] [--duplicate {1,2}]
                                        [--contain-dir CONTAIN_DIR]
                                        [--session-file SESSION_FILE]
                                        [--session-out SESSION_OUT]
                                        [--url-out URL_OUT]
                                        [--domains-out DOMAINS_OUT]
                                        [--domains-file DOMAINS_FILE]
                                        [--upload-url-file UPLOAD_URL_FILE]
                                        [--slice SLICE]
                                        [--slice-file SLICE_FILE]
                                        [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --parent-id PARENT_ID
                        parentFileID
  --filename FILENAME   filename
  --etag ETAG           etag
  --size SIZE           size
  --duplicate {1,2}     duplicate
  --contain-dir CONTAIN_DIR
                        containDir
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v2 slice

```text
usage: pan123 file upload-api v2 slice [-h] [--json] [--verbose]
                                       [--no-progress] [--allow-fake-ip]
                                       [--yes] [--config CONFIG]
                                       [--env-file ENV_FILE]
                                       [--cache-dir CACHE_DIR]
                                       [--auth-mode {developer,oauth}]
                                       [--timeout TIMEOUT]
                                       [--transfer-timeout TRANSFER_TIMEOUT]
                                       [--request-file REQUEST_FILE]
                                       [--slice-no SLICE_NO]
                                       [--slice-md5 SLICE_MD5] [--slice SLICE]
                                       [--session-file SESSION_FILE]
                                       [--session-out SESSION_OUT]
                                       [--url-out URL_OUT]
                                       [--domains-out DOMAINS_OUT]
                                       [--domains-file DOMAINS_FILE]
                                       [--upload-url-file UPLOAD_URL_FILE]
                                       [--slice-file SLICE_FILE] [--file FILE]
                                       [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --slice-no SLICE_NO   sliceNo
  --slice-md5 SLICE_MD5
                        sliceMD5
  --slice SLICE         slice
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v2 domains

```text
usage: pan123 file upload-api v2 domains [-h] [--json] [--verbose]
                                         [--no-progress] [--allow-fake-ip]
                                         [--yes] [--config CONFIG]
                                         [--env-file ENV_FILE]
                                         [--cache-dir CACHE_DIR]
                                         [--auth-mode {developer,oauth}]
                                         [--timeout TIMEOUT]
                                         [--transfer-timeout TRANSFER_TIMEOUT]
                                         [--request-file REQUEST_FILE]
                                         [--session-file SESSION_FILE]
                                         [--session-out SESSION_OUT]
                                         [--url-out URL_OUT]
                                         [--domains-out DOMAINS_OUT]
                                         [--domains-file DOMAINS_FILE]
                                         [--upload-url-file UPLOAD_URL_FILE]
                                         [--slice SLICE]
                                         [--slice-file SLICE_FILE]
                                         [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v2 single

```text
usage: pan123 file upload-api v2 single [-h] [--json] [--verbose]
                                        [--no-progress] [--allow-fake-ip]
                                        [--yes] [--config CONFIG]
                                        [--env-file ENV_FILE]
                                        [--cache-dir CACHE_DIR]
                                        [--auth-mode {developer,oauth}]
                                        [--timeout TIMEOUT]
                                        [--transfer-timeout TRANSFER_TIMEOUT]
                                        [--request-file REQUEST_FILE]
                                        [--parent-id PARENT_ID]
                                        [--filename FILENAME] [--etag ETAG]
                                        [--size SIZE] [--duplicate {1,2}]
                                        [--contain-dir CONTAIN_DIR]
                                        [--file FILE]
                                        [--session-file SESSION_FILE]
                                        [--session-out SESSION_OUT]
                                        [--url-out URL_OUT]
                                        [--domains-out DOMAINS_OUT]
                                        [--domains-file DOMAINS_FILE]
                                        [--upload-url-file UPLOAD_URL_FILE]
                                        [--slice SLICE]
                                        [--slice-file SLICE_FILE]
                                        [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --parent-id PARENT_ID
                        parentFileID
  --filename FILENAME   filename
  --etag ETAG           etag
  --size SIZE           size
  --duplicate {1,2}     duplicate
  --contain-dir CONTAIN_DIR
                        containDir
  --file FILE           file
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --upload-url-stdin
```

## pan123 file upload-api v2 sha1-reuse

```text
usage: pan123 file upload-api v2 sha1-reuse [-h] [--json] [--verbose]
                                            [--no-progress] [--allow-fake-ip]
                                            [--yes] [--config CONFIG]
                                            [--env-file ENV_FILE]
                                            [--cache-dir CACHE_DIR]
                                            [--auth-mode {developer,oauth}]
                                            [--timeout TIMEOUT]
                                            [--transfer-timeout TRANSFER_TIMEOUT]
                                            [--request-file REQUEST_FILE]
                                            [--parent-id PARENT_ID]
                                            [--filename FILENAME]
                                            [--sha1 SHA1] [--size SIZE]
                                            [--duplicate {1,2}]
                                            [--session-file SESSION_FILE]
                                            [--session-out SESSION_OUT]
                                            [--url-out URL_OUT]
                                            [--domains-out DOMAINS_OUT]
                                            [--domains-file DOMAINS_FILE]
                                            [--upload-url-file UPLOAD_URL_FILE]
                                            [--slice SLICE]
                                            [--slice-file SLICE_FILE]
                                            [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --parent-id PARENT_ID
                        parentFileID
  --filename FILENAME   filename
  --sha1 SHA1           sha1
  --size SIZE           size
  --duplicate {1,2}     duplicate
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload-api v2 complete

```text
usage: pan123 file upload-api v2 complete [-h] [--json] [--verbose]
                                          [--no-progress] [--allow-fake-ip]
                                          [--yes] [--config CONFIG]
                                          [--env-file ENV_FILE]
                                          [--cache-dir CACHE_DIR]
                                          [--auth-mode {developer,oauth}]
                                          [--timeout TIMEOUT]
                                          [--transfer-timeout TRANSFER_TIMEOUT]
                                          [--request-file REQUEST_FILE]
                                          [--wait]
                                          [--wait-timeout WAIT_TIMEOUT]
                                          [--session-file SESSION_FILE]
                                          [--session-out SESSION_OUT]
                                          [--url-out URL_OUT]
                                          [--domains-out DOMAINS_OUT]
                                          [--domains-file DOMAINS_FILE]
                                          [--upload-url-file UPLOAD_URL_FILE]
                                          [--slice SLICE]
                                          [--slice-file SLICE_FILE]
                                          [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --wait
  --wait-timeout WAIT_TIMEOUT
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 file upload

```text
usage: pan123 file upload [-h] [--json] [--verbose] [--no-progress]
                          [--allow-fake-ip] [--yes] [--config CONFIG]
                          [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                          [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                          [--transfer-timeout TRANSFER_TIMEOUT] --file FILE
                          [--parent-id PARENT_ID] [--name NAME]
                          [--duplicate {error,keep-both,overwrite}]
                          [--api-version {v1,v2}]
                          [--complete-timeout COMPLETE_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --file FILE
  --parent-id PARENT_ID
  --name NAME
  --duplicate {error,keep-both,overwrite}
  --api-version {v1,v2}
  --complete-timeout COMPLETE_TIMEOUT
```

## pan123 file download

```text
usage: pan123 file download [-h] [--json] [--verbose] [--no-progress]
                            [--allow-fake-ip] [--yes] [--config CONFIG]
                            [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                            [--auth-mode {developer,oauth}]
                            [--timeout TIMEOUT]
                            [--transfer-timeout TRANSFER_TIMEOUT]
                            --file-id FILE_ID [--output OUTPUT] [--overwrite]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --file-id FILE_ID
  --output OUTPUT
  --overwrite
```

## pan123 share

```text
usage: pan123 share [-h] [--json] [--verbose] [--no-progress]
                    [--allow-fake-ip] [--yes] [--config CONFIG]
                    [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                    [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                    [--transfer-timeout TRANSFER_TIMEOUT]
                    {create,payment,list,update} ...

positional arguments:
  {create,payment,list,update}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 share create

```text
usage: pan123 share create [-h] [--json] [--verbose] [--no-progress]
                           [--allow-fake-ip] [--yes] [--config CONFIG]
                           [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                           [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                           [--transfer-timeout TRANSFER_TIMEOUT]
                           [--request-file REQUEST_FILE] [--name NAME]
                           [--expire-days {1,7,30,0}] [--file-id FILE_ID]
                           [--traffic-switch {1,2,3,4}]
                           [--traffic-limit-switch {1,2}]
                           [--traffic-limit TRAFFIC_LIMIT]
                           [--share-password-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --name NAME           shareName
  --expire-days {1,7,30,0}
                        shareExpire
  --file-id FILE_ID     fileIDList
  --traffic-switch {1,2,3,4}
                        trafficSwitch
  --traffic-limit-switch {1,2}
                        trafficLimitSwitch
  --traffic-limit TRAFFIC_LIMIT
                        trafficLimit
  --share-password-stdin, --share-pwd-stdin
```

## pan123 share payment

```text
usage: pan123 share payment [-h] [--json] [--verbose] [--no-progress]
                            [--allow-fake-ip] [--yes] [--config CONFIG]
                            [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                            [--auth-mode {developer,oauth}]
                            [--timeout TIMEOUT]
                            [--transfer-timeout TRANSFER_TIMEOUT]
                            {create,list,update} ...

positional arguments:
  {create,list,update}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 share payment create

```text
usage: pan123 share payment create [-h] [--json] [--verbose] [--no-progress]
                                   [--allow-fake-ip] [--yes] [--config CONFIG]
                                   [--env-file ENV_FILE]
                                   [--cache-dir CACHE_DIR]
                                   [--auth-mode {developer,oauth}]
                                   [--timeout TIMEOUT]
                                   [--transfer-timeout TRANSFER_TIMEOUT]
                                   [--request-file REQUEST_FILE] [--name NAME]
                                   [--file-id FILE_ID]
                                   [--pay-amount PAY_AMOUNT]
                                   [--is-reward {0,1}]
                                   [--resource-desc RESOURCE_DESC]
                                   [--traffic-switch {1,2,3,4}]
                                   [--traffic-limit-switch {1,2}]
                                   [--traffic-limit TRAFFIC_LIMIT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --name NAME           shareName
  --file-id FILE_ID     fileIDList
  --pay-amount PAY_AMOUNT
                        payAmount
  --is-reward {0,1}     isReward
  --resource-desc RESOURCE_DESC
                        resourceDesc
  --traffic-switch {1,2,3,4}
                        trafficSwitch
  --traffic-limit-switch {1,2}
                        trafficLimitSwitch
  --traffic-limit TRAFFIC_LIMIT
                        trafficLimit
```

## pan123 share payment list

```text
usage: pan123 share payment list [-h] [--json] [--verbose] [--no-progress]
                                 [--allow-fake-ip] [--yes] [--config CONFIG]
                                 [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                 [--auth-mode {developer,oauth}]
                                 [--timeout TIMEOUT]
                                 [--transfer-timeout TRANSFER_TIMEOUT]
                                 [--request-file REQUEST_FILE] [--limit LIMIT]
                                 [--last-share-id LAST_SHARE_ID] [--all]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --limit LIMIT         limit
  --last-share-id LAST_SHARE_ID
                        lastShareId
  --all
```

## pan123 share payment update

```text
usage: pan123 share payment update [-h] [--json] [--verbose] [--no-progress]
                                   [--allow-fake-ip] [--yes] [--config CONFIG]
                                   [--env-file ENV_FILE]
                                   [--cache-dir CACHE_DIR]
                                   [--auth-mode {developer,oauth}]
                                   [--timeout TIMEOUT]
                                   [--transfer-timeout TRANSFER_TIMEOUT]
                                   [--request-file REQUEST_FILE]
                                   [--share-id SHARE_ID]
                                   [--traffic-switch {1,2,3,4}]
                                   [--traffic-limit-switch {1,2}]
                                   [--traffic-limit TRAFFIC_LIMIT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --share-id SHARE_ID   shareIdList
  --traffic-switch {1,2,3,4}
                        trafficSwitch
  --traffic-limit-switch {1,2}
                        trafficLimitSwitch
  --traffic-limit TRAFFIC_LIMIT
                        trafficLimit
```

## pan123 share list

```text
usage: pan123 share list [-h] [--json] [--verbose] [--no-progress]
                         [--allow-fake-ip] [--yes] [--config CONFIG]
                         [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                         [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                         [--transfer-timeout TRANSFER_TIMEOUT]
                         [--request-file REQUEST_FILE] [--limit LIMIT]
                         [--last-share-id LAST_SHARE_ID] [--all]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --limit LIMIT         limit
  --last-share-id LAST_SHARE_ID
                        lastShareId
  --all
```

## pan123 share update

```text
usage: pan123 share update [-h] [--json] [--verbose] [--no-progress]
                           [--allow-fake-ip] [--yes] [--config CONFIG]
                           [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                           [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                           [--transfer-timeout TRANSFER_TIMEOUT]
                           [--request-file REQUEST_FILE] [--share-id SHARE_ID]
                           [--traffic-switch {1,2,3,4}]
                           [--traffic-limit-switch {1,2}]
                           [--traffic-limit TRAFFIC_LIMIT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --share-id SHARE_ID   shareIdList
  --traffic-switch {1,2,3,4}
                        trafficSwitch
  --traffic-limit-switch {1,2}
                        trafficLimitSwitch
  --traffic-limit TRAFFIC_LIMIT
                        trafficLimit
```

## pan123 offline

```text
usage: pan123 offline [-h] [--json] [--verbose] [--no-progress]
                      [--allow-fake-ip] [--yes] [--config CONFIG]
                      [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                      [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                      [--transfer-timeout TRANSFER_TIMEOUT]
                      {create,progress} ...

positional arguments:
  {create,progress}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 offline create

```text
usage: pan123 offline create [-h] [--json] [--verbose] [--no-progress]
                             [--allow-fake-ip] [--yes] [--config CONFIG]
                             [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                             [--auth-mode {developer,oauth}]
                             [--timeout TIMEOUT]
                             [--transfer-timeout TRANSFER_TIMEOUT]
                             [--request-file REQUEST_FILE] [--url URL]
                             [--filename FILENAME] [--dir-id DIR_ID]
                             [--callback-url CALLBACK_URL] [--wait]
                             [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --url URL             url
  --filename FILENAME   fileName
  --dir-id DIR_ID       dirID
  --callback-url CALLBACK_URL
                        callBackUrl
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 offline progress

```text
usage: pan123 offline progress [-h] [--json] [--verbose] [--no-progress]
                               [--allow-fake-ip] [--yes] [--config CONFIG]
                               [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                               [--auth-mode {developer,oauth}]
                               [--timeout TIMEOUT]
                               [--transfer-timeout TRANSFER_TIMEOUT]
                               [--request-file REQUEST_FILE]
                               [--task-id TASK_ID] [--wait]
                               [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --task-id TASK_ID     taskID
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 user

```text
usage: pan123 user [-h] [--json] [--verbose] [--no-progress] [--allow-fake-ip]
                   [--yes] [--config CONFIG] [--env-file ENV_FILE]
                   [--cache-dir CACHE_DIR] [--auth-mode {developer,oauth}]
                   [--timeout TIMEOUT] [--transfer-timeout TRANSFER_TIMEOUT]
                   {info} ...

positional arguments:
  {info}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 user info

```text
usage: pan123 user info [-h] [--json] [--verbose] [--no-progress]
                        [--allow-fake-ip] [--yes] [--config CONFIG]
                        [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                        [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                        [--transfer-timeout TRANSFER_TIMEOUT]
                        [--request-file REQUEST_FILE]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
```

## pan123 directlink

```text
usage: pan123 directlink [-h] [--json] [--verbose] [--no-progress]
                         [--allow-fake-ip] [--yes] [--config CONFIG]
                         [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                         [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                         [--transfer-timeout TRANSFER_TIMEOUT]
                         {url,enable,disable,cache-refresh,traffic-logs,offline-logs,blacklist} ...

positional arguments:
  {url,enable,disable,cache-refresh,traffic-logs,offline-logs,blacklist}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 directlink url

```text
usage: pan123 directlink url [-h] [--json] [--verbose] [--no-progress]
                             [--allow-fake-ip] [--yes] [--config CONFIG]
                             [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                             [--auth-mode {developer,oauth}]
                             [--timeout TIMEOUT]
                             [--transfer-timeout TRANSFER_TIMEOUT]
                             [--request-file REQUEST_FILE] [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileID
```

## pan123 directlink enable

```text
usage: pan123 directlink enable [-h] [--json] [--verbose] [--no-progress]
                                [--allow-fake-ip] [--yes] [--config CONFIG]
                                [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                [--auth-mode {developer,oauth}]
                                [--timeout TIMEOUT]
                                [--transfer-timeout TRANSFER_TIMEOUT]
                                [--request-file REQUEST_FILE]
                                [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileID
```

## pan123 directlink disable

```text
usage: pan123 directlink disable [-h] [--json] [--verbose] [--no-progress]
                                 [--allow-fake-ip] [--yes] [--config CONFIG]
                                 [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                 [--auth-mode {developer,oauth}]
                                 [--timeout TIMEOUT]
                                 [--transfer-timeout TRANSFER_TIMEOUT]
                                 [--request-file REQUEST_FILE]
                                 [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileID
```

## pan123 directlink cache-refresh

```text
usage: pan123 directlink cache-refresh [-h] [--json] [--verbose]
                                       [--no-progress] [--allow-fake-ip]
                                       [--yes] [--config CONFIG]
                                       [--env-file ENV_FILE]
                                       [--cache-dir CACHE_DIR]
                                       [--auth-mode {developer,oauth}]
                                       [--timeout TIMEOUT]
                                       [--transfer-timeout TRANSFER_TIMEOUT]
                                       [--request-file REQUEST_FILE]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
```

## pan123 directlink traffic-logs

```text
usage: pan123 directlink traffic-logs [-h] [--json] [--verbose]
                                      [--no-progress] [--allow-fake-ip]
                                      [--yes] [--config CONFIG]
                                      [--env-file ENV_FILE]
                                      [--cache-dir CACHE_DIR]
                                      [--auth-mode {developer,oauth}]
                                      [--timeout TIMEOUT]
                                      [--transfer-timeout TRANSFER_TIMEOUT]
                                      [--request-file REQUEST_FILE]
                                      [--page-num PAGE_NUM]
                                      [--page-size PAGE_SIZE]
                                      [--start-time START_TIME]
                                      [--end-time END_TIME]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --page-num PAGE_NUM   pageNum
  --page-size PAGE_SIZE
                        pageSize
  --start-time START_TIME
                        startTime
  --end-time END_TIME   endTime
```

## pan123 directlink offline-logs

```text
usage: pan123 directlink offline-logs [-h] [--json] [--verbose]
                                      [--no-progress] [--allow-fake-ip]
                                      [--yes] [--config CONFIG]
                                      [--env-file ENV_FILE]
                                      [--cache-dir CACHE_DIR]
                                      [--auth-mode {developer,oauth}]
                                      [--timeout TIMEOUT]
                                      [--transfer-timeout TRANSFER_TIMEOUT]
                                      [--request-file REQUEST_FILE]
                                      [--start-hour START_HOUR]
                                      [--end-hour END_HOUR]
                                      [--page-num PAGE_NUM]
                                      [--page-size PAGE_SIZE]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --start-hour START_HOUR
                        startHour
  --end-hour END_HOUR   endHour
  --page-num PAGE_NUM   pageNum
  --page-size PAGE_SIZE
                        pageSize
```

## pan123 directlink blacklist

```text
usage: pan123 directlink blacklist [-h] [--json] [--verbose] [--no-progress]
                                   [--allow-fake-ip] [--yes] [--config CONFIG]
                                   [--env-file ENV_FILE]
                                   [--cache-dir CACHE_DIR]
                                   [--auth-mode {developer,oauth}]
                                   [--timeout TIMEOUT]
                                   [--transfer-timeout TRANSFER_TIMEOUT]
                                   {list,update,switch} ...

positional arguments:
  {list,update,switch}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 directlink blacklist list

```text
usage: pan123 directlink blacklist list [-h] [--json] [--verbose]
                                        [--no-progress] [--allow-fake-ip]
                                        [--yes] [--config CONFIG]
                                        [--env-file ENV_FILE]
                                        [--cache-dir CACHE_DIR]
                                        [--auth-mode {developer,oauth}]
                                        [--timeout TIMEOUT]
                                        [--transfer-timeout TRANSFER_TIMEOUT]
                                        [--request-file REQUEST_FILE]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
```

## pan123 directlink blacklist update

```text
usage: pan123 directlink blacklist update [-h] [--json] [--verbose]
                                          [--no-progress] [--allow-fake-ip]
                                          [--yes] [--config CONFIG]
                                          [--env-file ENV_FILE]
                                          [--cache-dir CACHE_DIR]
                                          [--auth-mode {developer,oauth}]
                                          [--timeout TIMEOUT]
                                          [--transfer-timeout TRANSFER_TIMEOUT]
                                          [--request-file REQUEST_FILE]
                                          [--ip IP]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --ip IP               IpList
```

## pan123 directlink blacklist switch

```text
usage: pan123 directlink blacklist switch [-h] [--json] [--verbose]
                                          [--no-progress] [--allow-fake-ip]
                                          [--yes] [--config CONFIG]
                                          [--env-file ENV_FILE]
                                          [--cache-dir CACHE_DIR]
                                          [--auth-mode {developer,oauth}]
                                          [--timeout TIMEOUT]
                                          [--transfer-timeout TRANSFER_TIMEOUT]
                                          [--request-file REQUEST_FILE]
                                          [--status {1,2}]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --status {1,2}        Status
```

## pan123 image

```text
usage: pan123 image [-h] [--json] [--verbose] [--no-progress]
                    [--allow-fake-ip] [--yes] [--config CONFIG]
                    [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                    [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                    [--transfer-timeout TRANSFER_TIMEOUT]
                    {upload-api,mkdir,list,info,move,delete,source-copy,source-copy-progress,source-copy-failures,offline-create,offline-progress,upload} ...

positional arguments:
  {upload-api,mkdir,list,info,move,delete,source-copy,source-copy-progress,source-copy-failures,offline-create,offline-progress,upload}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 image upload-api

```text
usage: pan123 image upload-api [-h] [--json] [--verbose] [--no-progress]
                               [--allow-fake-ip] [--yes] [--config CONFIG]
                               [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                               [--auth-mode {developer,oauth}]
                               [--timeout TIMEOUT]
                               [--transfer-timeout TRANSFER_TIMEOUT]
                               {create,get-url,put-slice,complete,async-result} ...

positional arguments:
  {create,get-url,put-slice,complete,async-result}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 image upload-api create

```text
usage: pan123 image upload-api create [-h] [--json] [--verbose]
                                      [--no-progress] [--allow-fake-ip]
                                      [--yes] [--config CONFIG]
                                      [--env-file ENV_FILE]
                                      [--cache-dir CACHE_DIR]
                                      [--auth-mode {developer,oauth}]
                                      [--timeout TIMEOUT]
                                      [--transfer-timeout TRANSFER_TIMEOUT]
                                      [--request-file REQUEST_FILE]
                                      [--parent-id PARENT_ID]
                                      [--filename FILENAME] [--etag ETAG]
                                      [--size SIZE]
                                      [--session-file SESSION_FILE]
                                      [--session-out SESSION_OUT]
                                      [--url-out URL_OUT]
                                      [--domains-out DOMAINS_OUT]
                                      [--domains-file DOMAINS_FILE]
                                      [--upload-url-file UPLOAD_URL_FILE]
                                      [--slice SLICE]
                                      [--slice-file SLICE_FILE] [--file FILE]
                                      [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --parent-id PARENT_ID
                        parentFileID
  --filename FILENAME   filename
  --etag ETAG           etag
  --size SIZE           size
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 image upload-api get-url

```text
usage: pan123 image upload-api get-url [-h] [--json] [--verbose]
                                       [--no-progress] [--allow-fake-ip]
                                       [--yes] [--config CONFIG]
                                       [--env-file ENV_FILE]
                                       [--cache-dir CACHE_DIR]
                                       [--auth-mode {developer,oauth}]
                                       [--timeout TIMEOUT]
                                       [--transfer-timeout TRANSFER_TIMEOUT]
                                       [--request-file REQUEST_FILE]
                                       [--slice-no SLICE_NO]
                                       [--session-file SESSION_FILE]
                                       [--session-out SESSION_OUT]
                                       [--url-out URL_OUT]
                                       [--domains-out DOMAINS_OUT]
                                       [--domains-file DOMAINS_FILE]
                                       [--upload-url-file UPLOAD_URL_FILE]
                                       [--slice SLICE]
                                       [--slice-file SLICE_FILE] [--file FILE]
                                       [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --slice-no SLICE_NO   sliceNo
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 image upload-api put-slice

```text
usage: pan123 image upload-api put-slice [-h] [--json] [--verbose]
                                         [--no-progress] [--allow-fake-ip]
                                         [--yes] [--config CONFIG]
                                         [--env-file ENV_FILE]
                                         [--cache-dir CACHE_DIR]
                                         [--auth-mode {developer,oauth}]
                                         [--timeout TIMEOUT]
                                         [--transfer-timeout TRANSFER_TIMEOUT]
                                         [--request-file REQUEST_FILE]
                                         [--session-file SESSION_FILE]
                                         [--session-out SESSION_OUT]
                                         [--url-out URL_OUT]
                                         [--domains-out DOMAINS_OUT]
                                         [--domains-file DOMAINS_FILE]
                                         [--upload-url-file UPLOAD_URL_FILE]
                                         [--slice SLICE]
                                         [--slice-file SLICE_FILE]
                                         [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 image upload-api complete

```text
usage: pan123 image upload-api complete [-h] [--json] [--verbose]
                                        [--no-progress] [--allow-fake-ip]
                                        [--yes] [--config CONFIG]
                                        [--env-file ENV_FILE]
                                        [--cache-dir CACHE_DIR]
                                        [--auth-mode {developer,oauth}]
                                        [--timeout TIMEOUT]
                                        [--transfer-timeout TRANSFER_TIMEOUT]
                                        [--request-file REQUEST_FILE] [--wait]
                                        [--wait-timeout WAIT_TIMEOUT]
                                        [--session-file SESSION_FILE]
                                        [--session-out SESSION_OUT]
                                        [--url-out URL_OUT]
                                        [--domains-out DOMAINS_OUT]
                                        [--domains-file DOMAINS_FILE]
                                        [--upload-url-file UPLOAD_URL_FILE]
                                        [--slice SLICE]
                                        [--slice-file SLICE_FILE]
                                        [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --wait
  --wait-timeout WAIT_TIMEOUT
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 image upload-api async-result

```text
usage: pan123 image upload-api async-result [-h] [--json] [--verbose]
                                            [--no-progress] [--allow-fake-ip]
                                            [--yes] [--config CONFIG]
                                            [--env-file ENV_FILE]
                                            [--cache-dir CACHE_DIR]
                                            [--auth-mode {developer,oauth}]
                                            [--timeout TIMEOUT]
                                            [--transfer-timeout TRANSFER_TIMEOUT]
                                            [--request-file REQUEST_FILE]
                                            [--wait]
                                            [--wait-timeout WAIT_TIMEOUT]
                                            [--session-file SESSION_FILE]
                                            [--session-out SESSION_OUT]
                                            [--url-out URL_OUT]
                                            [--domains-out DOMAINS_OUT]
                                            [--domains-file DOMAINS_FILE]
                                            [--upload-url-file UPLOAD_URL_FILE]
                                            [--slice SLICE]
                                            [--slice-file SLICE_FILE]
                                            [--file FILE] [--upload-url-stdin]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --wait
  --wait-timeout WAIT_TIMEOUT
  --session-file SESSION_FILE
  --session-out SESSION_OUT
  --url-out URL_OUT
  --domains-out DOMAINS_OUT
  --domains-file DOMAINS_FILE
  --upload-url-file UPLOAD_URL_FILE
  --slice SLICE
  --slice-file SLICE_FILE
  --file FILE
  --upload-url-stdin
```

## pan123 image mkdir

```text
usage: pan123 image mkdir [-h] [--json] [--verbose] [--no-progress]
                          [--allow-fake-ip] [--yes] [--config CONFIG]
                          [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                          [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                          [--transfer-timeout TRANSFER_TIMEOUT]
                          [--request-file REQUEST_FILE] [--name NAME]
                          [--parent-id PARENT_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --name NAME           name
  --parent-id PARENT_ID
                        parentID
```

## pan123 image list

```text
usage: pan123 image list [-h] [--json] [--verbose] [--no-progress]
                         [--allow-fake-ip] [--yes] [--config CONFIG]
                         [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                         [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                         [--transfer-timeout TRANSFER_TIMEOUT]
                         [--request-file REQUEST_FILE] [--parent-id PARENT_ID]
                         [--limit LIMIT] [--start-time START_TIME]
                         [--end-time END_TIME] [--last-file-id LAST_FILE_ID]
                         [--all] [--include-trashed]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --parent-id PARENT_ID
                        parentFileId
  --limit LIMIT         limit
  --start-time START_TIME
                        startTime
  --end-time END_TIME   endTime
  --last-file-id LAST_FILE_ID
                        lastFileId
  --all
  --include-trashed
```

## pan123 image info

```text
usage: pan123 image info [-h] [--json] [--verbose] [--no-progress]
                         [--allow-fake-ip] [--yes] [--config CONFIG]
                         [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                         [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                         [--transfer-timeout TRANSFER_TIMEOUT]
                         [--request-file REQUEST_FILE] [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileID
```

## pan123 image move

```text
usage: pan123 image move [-h] [--json] [--verbose] [--no-progress]
                         [--allow-fake-ip] [--yes] [--config CONFIG]
                         [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                         [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                         [--transfer-timeout TRANSFER_TIMEOUT]
                         [--request-file REQUEST_FILE] [--file-id FILE_ID]
                         [--parent-id PARENT_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileIDs
  --parent-id PARENT_ID
                        toParentFileID
```

## pan123 image delete

```text
usage: pan123 image delete [-h] [--json] [--verbose] [--no-progress]
                           [--allow-fake-ip] [--yes] [--config CONFIG]
                           [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                           [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                           [--transfer-timeout TRANSFER_TIMEOUT]
                           [--request-file REQUEST_FILE] [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileIDs
```

## pan123 image source-copy

```text
usage: pan123 image source-copy [-h] [--json] [--verbose] [--no-progress]
                                [--allow-fake-ip] [--yes] [--config CONFIG]
                                [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                [--auth-mode {developer,oauth}]
                                [--timeout TIMEOUT]
                                [--transfer-timeout TRANSFER_TIMEOUT]
                                [--request-file REQUEST_FILE]
                                [--file-id FILE_ID] [--parent-id PARENT_ID]
                                [--wait] [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileIDs
  --parent-id PARENT_ID
                        toParentFileID
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 image source-copy-progress

```text
usage: pan123 image source-copy-progress [-h] [--json] [--verbose]
                                         [--no-progress] [--allow-fake-ip]
                                         [--yes] [--config CONFIG]
                                         [--env-file ENV_FILE]
                                         [--cache-dir CACHE_DIR]
                                         [--auth-mode {developer,oauth}]
                                         [--timeout TIMEOUT]
                                         [--transfer-timeout TRANSFER_TIMEOUT]
                                         [--request-file REQUEST_FILE]
                                         [--task-id TASK_ID] [--wait]
                                         [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --task-id TASK_ID     taskID
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 image source-copy-failures

```text
usage: pan123 image source-copy-failures [-h] [--json] [--verbose]
                                         [--no-progress] [--allow-fake-ip]
                                         [--yes] [--config CONFIG]
                                         [--env-file ENV_FILE]
                                         [--cache-dir CACHE_DIR]
                                         [--auth-mode {developer,oauth}]
                                         [--timeout TIMEOUT]
                                         [--transfer-timeout TRANSFER_TIMEOUT]
                                         [--request-file REQUEST_FILE]
                                         [--task-id TASK_ID] [--limit LIMIT]
                                         [--page PAGE]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --task-id TASK_ID     taskID
  --limit LIMIT         limit
  --page PAGE           page
```

## pan123 image offline-create

```text
usage: pan123 image offline-create [-h] [--json] [--verbose] [--no-progress]
                                   [--allow-fake-ip] [--yes] [--config CONFIG]
                                   [--env-file ENV_FILE]
                                   [--cache-dir CACHE_DIR]
                                   [--auth-mode {developer,oauth}]
                                   [--timeout TIMEOUT]
                                   [--transfer-timeout TRANSFER_TIMEOUT]
                                   [--request-file REQUEST_FILE] [--url URL]
                                   [--filename FILENAME] [--dir-id DIR_ID]
                                   [--callback-url CALLBACK_URL] [--wait]
                                   [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --url URL             url
  --filename FILENAME   fileName
  --dir-id DIR_ID       dirID
  --callback-url CALLBACK_URL
                        callBackUrl
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 image offline-progress

```text
usage: pan123 image offline-progress [-h] [--json] [--verbose] [--no-progress]
                                     [--allow-fake-ip] [--yes]
                                     [--config CONFIG] [--env-file ENV_FILE]
                                     [--cache-dir CACHE_DIR]
                                     [--auth-mode {developer,oauth}]
                                     [--timeout TIMEOUT]
                                     [--transfer-timeout TRANSFER_TIMEOUT]
                                     [--request-file REQUEST_FILE]
                                     [--task-id TASK_ID] [--wait]
                                     [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --task-id TASK_ID     taskID
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 image upload

```text
usage: pan123 image upload [-h] [--json] [--verbose] [--no-progress]
                           [--allow-fake-ip] [--yes] [--config CONFIG]
                           [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                           [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                           [--transfer-timeout TRANSFER_TIMEOUT] --file FILE
                           [--parent-id PARENT_ID] [--name NAME]
                           [--duplicate {error,keep-both,overwrite}]
                           [--api-version {v1,v2}]
                           [--complete-timeout COMPLETE_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --file FILE
  --parent-id PARENT_ID
  --name NAME
  --duplicate {error,keep-both,overwrite}
  --api-version {v1,v2}
  --complete-timeout COMPLETE_TIMEOUT
```

## pan123 transcode

```text
usage: pan123 transcode [-h] [--json] [--verbose] [--no-progress]
                        [--allow-fake-ip] [--yes] [--config CONFIG]
                        [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                        [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                        [--transfer-timeout TRANSFER_TIMEOUT]
                        {source-list,folder-list,folder-info,from-cloud,resolutions,run,records,result,download-url,list,delete,segment-url,all-download-urls,upload} ...

positional arguments:
  {source-list,folder-list,folder-info,from-cloud,resolutions,run,records,result,download-url,list,delete,segment-url,all-download-urls,upload}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 transcode source-list

```text
usage: pan123 transcode source-list [-h] [--json] [--verbose] [--no-progress]
                                    [--allow-fake-ip] [--yes]
                                    [--config CONFIG] [--env-file ENV_FILE]
                                    [--cache-dir CACHE_DIR]
                                    [--auth-mode {developer,oauth}]
                                    [--timeout TIMEOUT]
                                    [--transfer-timeout TRANSFER_TIMEOUT]
                                    [--request-file REQUEST_FILE]
                                    [--parent-id PARENT_ID] [--limit LIMIT]
                                    [--search SEARCH]
                                    [--last-file-id LAST_FILE_ID]
                                    [--search-mode {0,1}] [--all]
                                    [--include-trashed]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --parent-id PARENT_ID
                        parentFileId
  --limit LIMIT         limit
  --search SEARCH       searchData
  --last-file-id LAST_FILE_ID
                        lastFileId
  --search-mode {0,1}   searchMode
  --all
  --include-trashed
```

## pan123 transcode folder-list

```text
usage: pan123 transcode folder-list [-h] [--json] [--verbose] [--no-progress]
                                    [--allow-fake-ip] [--yes]
                                    [--config CONFIG] [--env-file ENV_FILE]
                                    [--cache-dir CACHE_DIR]
                                    [--auth-mode {developer,oauth}]
                                    [--timeout TIMEOUT]
                                    [--transfer-timeout TRANSFER_TIMEOUT]
                                    [--request-file REQUEST_FILE]
                                    [--parent-id PARENT_ID] [--limit LIMIT]
                                    [--search SEARCH]
                                    [--last-file-id LAST_FILE_ID]
                                    [--search-mode {0,1}] [--all]
                                    [--include-trashed]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --parent-id PARENT_ID
                        parentFileId
  --limit LIMIT         limit
  --search SEARCH       searchData
  --last-file-id LAST_FILE_ID
                        lastFileId
  --search-mode {0,1}   searchMode
  --all
  --include-trashed
```

## pan123 transcode folder-info

```text
usage: pan123 transcode folder-info [-h] [--json] [--verbose] [--no-progress]
                                    [--allow-fake-ip] [--yes]
                                    [--config CONFIG] [--env-file ENV_FILE]
                                    [--cache-dir CACHE_DIR]
                                    [--auth-mode {developer,oauth}]
                                    [--timeout TIMEOUT]
                                    [--transfer-timeout TRANSFER_TIMEOUT]
                                    [--request-file REQUEST_FILE]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
```

## pan123 transcode from-cloud

```text
usage: pan123 transcode from-cloud [-h] [--json] [--verbose] [--no-progress]
                                   [--allow-fake-ip] [--yes] [--config CONFIG]
                                   [--env-file ENV_FILE]
                                   [--cache-dir CACHE_DIR]
                                   [--auth-mode {developer,oauth}]
                                   [--timeout TIMEOUT]
                                   [--transfer-timeout TRANSFER_TIMEOUT]
                                   [--request-file REQUEST_FILE]
                                   [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
```

## pan123 transcode resolutions

```text
usage: pan123 transcode resolutions [-h] [--json] [--verbose] [--no-progress]
                                    [--allow-fake-ip] [--yes]
                                    [--config CONFIG] [--env-file ENV_FILE]
                                    [--cache-dir CACHE_DIR]
                                    [--auth-mode {developer,oauth}]
                                    [--timeout TIMEOUT]
                                    [--transfer-timeout TRANSFER_TIMEOUT]
                                    [--request-file REQUEST_FILE]
                                    [--file-id FILE_ID] [--wait]
                                    [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 transcode run

```text
usage: pan123 transcode run [-h] [--json] [--verbose] [--no-progress]
                            [--allow-fake-ip] [--yes] [--config CONFIG]
                            [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                            [--auth-mode {developer,oauth}]
                            [--timeout TIMEOUT]
                            [--transfer-timeout TRANSFER_TIMEOUT]
                            [--request-file REQUEST_FILE] [--file-id FILE_ID]
                            [--codec-name CODEC_NAME]
                            [--video-time VIDEO_TIME]
                            [--resolutions RESOLUTIONS]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
  --codec-name CODEC_NAME
                        codecName
  --video-time VIDEO_TIME
                        videoTime
  --resolutions RESOLUTIONS
                        resolutions
```

## pan123 transcode records

```text
usage: pan123 transcode records [-h] [--json] [--verbose] [--no-progress]
                                [--allow-fake-ip] [--yes] [--config CONFIG]
                                [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                                [--auth-mode {developer,oauth}]
                                [--timeout TIMEOUT]
                                [--transfer-timeout TRANSFER_TIMEOUT]
                                [--request-file REQUEST_FILE]
                                [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
```

## pan123 transcode result

```text
usage: pan123 transcode result [-h] [--json] [--verbose] [--no-progress]
                               [--allow-fake-ip] [--yes] [--config CONFIG]
                               [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                               [--auth-mode {developer,oauth}]
                               [--timeout TIMEOUT]
                               [--transfer-timeout TRANSFER_TIMEOUT]
                               [--request-file REQUEST_FILE]
                               [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
```

## pan123 transcode download-url

```text
usage: pan123 transcode download-url [-h] [--json] [--verbose] [--no-progress]
                                     [--allow-fake-ip] [--yes]
                                     [--config CONFIG] [--env-file ENV_FILE]
                                     [--cache-dir CACHE_DIR]
                                     [--auth-mode {developer,oauth}]
                                     [--timeout TIMEOUT]
                                     [--transfer-timeout TRANSFER_TIMEOUT]
                                     [--request-file REQUEST_FILE]
                                     [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
```

## pan123 transcode list

```text
usage: pan123 transcode list [-h] [--json] [--verbose] [--no-progress]
                             [--allow-fake-ip] [--yes] [--config CONFIG]
                             [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                             [--auth-mode {developer,oauth}]
                             [--timeout TIMEOUT]
                             [--transfer-timeout TRANSFER_TIMEOUT]
                             [--request-file REQUEST_FILE] [--file-id FILE_ID]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
```

## pan123 transcode delete

```text
usage: pan123 transcode delete [-h] [--json] [--verbose] [--no-progress]
                               [--allow-fake-ip] [--yes] [--config CONFIG]
                               [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                               [--auth-mode {developer,oauth}]
                               [--timeout TIMEOUT]
                               [--transfer-timeout TRANSFER_TIMEOUT]
                               [--request-file REQUEST_FILE]
                               [--file-id FILE_ID] [--trashed {1,2}]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
  --trashed {1,2}       trashed
```

## pan123 transcode segment-url

```text
usage: pan123 transcode segment-url [-h] [--json] [--verbose] [--no-progress]
                                    [--allow-fake-ip] [--yes]
                                    [--config CONFIG] [--env-file ENV_FILE]
                                    [--cache-dir CACHE_DIR]
                                    [--auth-mode {developer,oauth}]
                                    [--timeout TIMEOUT]
                                    [--transfer-timeout TRANSFER_TIMEOUT]
                                    [--request-file REQUEST_FILE]
                                    [--file-id FILE_ID]
                                    [--resolution RESOLUTION] [--type {1,2}]
                                    [--ts-name TS_NAME]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
  --resolution RESOLUTION
                        resolution
  --type {1,2}          type
  --ts-name TS_NAME     tsName
```

## pan123 transcode all-download-urls

```text
usage: pan123 transcode all-download-urls [-h] [--json] [--verbose]
                                          [--no-progress] [--allow-fake-ip]
                                          [--yes] [--config CONFIG]
                                          [--env-file ENV_FILE]
                                          [--cache-dir CACHE_DIR]
                                          [--auth-mode {developer,oauth}]
                                          [--timeout TIMEOUT]
                                          [--transfer-timeout TRANSFER_TIMEOUT]
                                          [--request-file REQUEST_FILE]
                                          [--file-id FILE_ID]
                                          [--zip-name ZIP_NAME] [--wait]
                                          [--wait-timeout WAIT_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --request-file REQUEST_FILE
                        UTF-8 JSON 请求文件；- 表示 stdin
  --file-id FILE_ID     fileId
  --zip-name ZIP_NAME   zipName
  --wait
  --wait-timeout WAIT_TIMEOUT
```

## pan123 transcode upload

```text
usage: pan123 transcode upload [-h] [--json] [--verbose] [--no-progress]
                               [--allow-fake-ip] [--yes] [--config CONFIG]
                               [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                               [--auth-mode {developer,oauth}]
                               [--timeout TIMEOUT]
                               [--transfer-timeout TRANSFER_TIMEOUT]
                               --file FILE [--parent-id PARENT_ID]
                               [--name NAME]
                               [--duplicate {error,keep-both,overwrite}]
                               [--api-version {v1,v2}]
                               [--complete-timeout COMPLETE_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --file FILE
  --parent-id PARENT_ID
  --name NAME
  --duplicate {error,keep-both,overwrite}
  --api-version {v1,v2}
  --complete-timeout COMPLETE_TIMEOUT
```

## pan123 setup

```text
usage: pan123 setup [-h] [--json] [--verbose] [--no-progress]
                    [--allow-fake-ip] [--yes] [--config CONFIG]
                    [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                    [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                    [--transfer-timeout TRANSFER_TIMEOUT]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 skill

```text
usage: pan123 skill [-h] [--json] [--verbose] [--no-progress]
                    [--allow-fake-ip] [--yes] [--config CONFIG]
                    [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                    [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                    [--transfer-timeout TRANSFER_TIMEOUT]
                    {install,status,uninstall} ...

positional arguments:
  {install,status,uninstall}

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
```

## pan123 skill install

```text
usage: pan123 skill install [-h] [--json] [--verbose] [--no-progress]
                            [--allow-fake-ip] [--yes] [--config CONFIG]
                            [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                            [--auth-mode {developer,oauth}]
                            [--timeout TIMEOUT]
                            [--transfer-timeout TRANSFER_TIMEOUT]
                            [--agent {codex,claude,cursor}]
                            [--scope {user,project}] [--dest DEST] [--force]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --agent {codex,claude,cursor}
  --scope {user,project}
  --dest DEST           完整 Skill 目标目录（包含 pan123-cli 文件夹）
  --force               备份已存在内容后更新或卸载
```

## pan123 skill status

```text
usage: pan123 skill status [-h] [--json] [--verbose] [--no-progress]
                           [--allow-fake-ip] [--yes] [--config CONFIG]
                           [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                           [--auth-mode {developer,oauth}] [--timeout TIMEOUT]
                           [--transfer-timeout TRANSFER_TIMEOUT]
                           [--agent {codex,claude,cursor}]
                           [--scope {user,project}] [--dest DEST] [--force]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --agent {codex,claude,cursor}
  --scope {user,project}
  --dest DEST           完整 Skill 目标目录（包含 pan123-cli 文件夹）
  --force               备份已存在内容后更新或卸载
```

## pan123 skill uninstall

```text
usage: pan123 skill uninstall [-h] [--json] [--verbose] [--no-progress]
                              [--allow-fake-ip] [--yes] [--config CONFIG]
                              [--env-file ENV_FILE] [--cache-dir CACHE_DIR]
                              [--auth-mode {developer,oauth}]
                              [--timeout TIMEOUT]
                              [--transfer-timeout TRANSFER_TIMEOUT]
                              [--agent {codex,claude,cursor}]
                              [--scope {user,project}] [--dest DEST] [--force]

options:
  -h, --help            show this help message and exit
  --json
  --verbose
  --no-progress
  --allow-fake-ip
  --yes
  --config CONFIG
  --env-file ENV_FILE
  --cache-dir CACHE_DIR
  --auth-mode {developer,oauth}
  --timeout TIMEOUT
  --transfer-timeout TRANSFER_TIMEOUT
  --agent {codex,claude,cursor}
  --scope {user,project}
  --dest DEST           完整 Skill 目标目录（包含 pan123-cli 文件夹）
  --force               备份已存在内容后更新或卸载
```
