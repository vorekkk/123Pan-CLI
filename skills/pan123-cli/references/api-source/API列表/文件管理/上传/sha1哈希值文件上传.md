# sha1哈希值文件上传

API： POST 域名 + /upload/v2/file/sha1\_reuse

说明：

-   文件名要小于256个字符且不能包含以下任何字符："\\/:\*?|><
-   文件名不能全部是空格

## Header 参数

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| Authorization | string | 必填 | 鉴权access_token |
| Platform | string | 必填 | 固定为:open_platform |

## Body 参数

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| parentFileID | number | 必填 | 父目录id，上传到根目录时填写 0 |
| filename | string | 必填 | 文件名要小于255个字符且不能包含以下任何字符："\/:*?\|><。（注：不能重名） |
| sha1 | string | 必填 | 文件sha1 |
| size | number | 必填 | 文件大小，单位为 byte 字节 |
| duplicate | number | 非必填 | 当有相同文件名时，文件处理策略（1保留两者，新文件名将自动添加后缀，2覆盖原文件） |

## 返回数据

| 名称 | 类型 | 是否必填 | 说明 |
| --- | --- | --- | --- |
| fileID | number | 非必填 | 文件ID。当123云盘已有该文件,则会发生秒传。此时会将文件ID字段返回。唯一 |
| reuse | boolean | 必填 | 是否秒传，返回true时表示文件已上传成功 |

## 示例

**请求示例**

```shell
curl --location 'https://open-api.123pan.com/upload/v2/file/sha1_reuse' \
--header 'Content-Type: application/json' \
--header 'Platform: open_platform' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)' \
--data '{
    "parentFileID": 0,
    "filename": "测试文件.mp4",
    "sha1": "4b5c549c4abd0a079caf92d6cad24127",
    "size": 50650928
}'
```

```java
OkHttpClient client = new OkHttpClient().newBuilder()
  .build();
MediaType mediaType = MediaType.parse("application/json");
RequestBody body = RequestBody.create(mediaType, "{\n    \"parentFileID\": 0,\n    \"filename\": \"测试文件.mp4\",\n    \"sha1\": \"4b5c549c4abd0a079caf92d6cad24127\",\n    \"size\": 50650928\n}");
Request request = new Request.Builder()
  .url("https://open-api.123pan.com/upload/v2/file/sha1_reuse")
  .method("POST", body)
  .addHeader("Content-Type", "application/json")
  .addHeader("Platform", "open_platform")
  .addHeader("Authorization", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)")
  .build();
Response response = client.newCall(request).execute();
```

```javascript
var settings = {
  "url": "https://open-api.123pan.com/upload/v2/file/sha1_reuse",
  "method": "POST",
  "timeout": 0,
  "headers": {
    "Content-Type": "application/json",
    "Platform": "open_platform",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)"
  },
  "data": JSON.stringify({
    "parentFileID": 0,
    "filename": "测试文件.mp4",
    "sha1": "4b5c549c4abd0a079caf92d6cad24127",
    "size": 50650928
  }),
};

$.ajax(settings).done(function (response) {
  console.log(response);
});
```

```javascript
const axios = require('axios');
let data = JSON.stringify({
  "parentFileID": 0,
  "filename": "测试文件.mp4",
  "sha1": "4b5c549c4abd0a079caf92d6cad24127",
  "size": 50650928
});

let config = {
  method: 'post',
  maxBodyLength: Infinity,
  url: 'https://open-api.123pan.com/upload/v2/file/sha1_reuse',
  headers: { 
    'Content-Type': 'application/json', 
    'Platform': 'open_platform', 
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
  },
  data : data
};

axios.request(config)
.then((response) => {
  console.log(JSON.stringify(response.data));
})
.catch((error) => {
  console.log(error);
});
```

```python
import http.client
import json

conn = http.client.HTTPSConnection("open-api.123pan.com")
payload = json.dumps({
    "parentFileID": 0,
    "filename": "测试文件.mp4",
    "sha1": "4b5c549c4abd0a079caf92d6cad24127",
    "size": 50650928
})
headers = {
    'Content-Type': 'application/json',
    'Platform': 'open_platform',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJl...(过长省略)'
}
conn.request("POST", "/upload/v2/file/sha1_reuse", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
```

**响应示例**

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "fileID": 0,
    "reuse": false
  }
  "x-traceID": "2f41bbb4-93ab-459b-8dab-2204d3b3ff66_kong-db-5898fdd8c6-wnv6h"
}
```
