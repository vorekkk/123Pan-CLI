"""Exact official OpenAPI command routes and preflight request validation.

The catalog is self contained when installed. source_paths refer to bundled project
reference material, not runtime file dependencies. flag names omit ``--``; scalar
values use argparse underscore destinations. Sensitive fields have no value-bearing
flag and are injected by the command runner under their precise wire name.
"""

from __future__ import annotations

import ipaddress
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from datetime import datetime
from typing import Any, NoReturn
from urllib.parse import urlsplit

from .errors import Pan123Error


@dataclass(frozen=True)
class Field:
    wire: str
    flag: str | None
    kind: str = "str"
    required: bool = False
    default: Any = None
    choices: tuple[Any, ...] | None = None
    minimum: int | float | None = None
    maximum: int | float | None = None
    max_items: int | None = None
    help: str = ""


@dataclass(frozen=True)
class Endpoint:
    command: tuple[str, ...]
    method: str
    path: str
    location: str = "json"
    fields: tuple[Field, ...] = ()
    fixed: Mapping[str, Any] = dataclass_field(default_factory=dict)
    confirmation: bool = False
    read_only: bool = False
    auth_mode: str | None = None
    special: str | None = None
    source_paths: tuple[str, ...] = ()
    wait: Mapping[str, Any] | None = None


F = Field
_SOURCES = {
    1: "简介/概述.md",
    2: "简介/更新记录.md",
    3: "接入指南/开发者接入/接入流程.md",
    4: "接入指南/开发者接入/开发须知.md",
    5: "接入指南/开发者接入/获取access_token.md",
    6: "接入指南/第三方挂载应用接入/授权须知.md",
    7: "接入指南/第三方挂载应用接入/授权地址.md",
    8: "接入指南/第三方挂载应用接入/授权code获取access_token.md",
    9: "接入指南/优秀实践.md",
    10: "接入指南/💡常见问题.md",
    11: "API列表/文件管理/上传/创建目录.md",
    12: "API列表/文件管理/上传/V1（旧）/💡上传流程说明.md",
    13: "API列表/文件管理/上传/V1（旧）/创建文件.md",
    14: "API列表/文件管理/上传/V1（旧）/获取上传地址&上传分片.md",
    15: "API列表/文件管理/上传/V1（旧）/列举已上传分片（非必需）.md",
    16: "API列表/文件管理/上传/V1（旧）/上传完毕.md",
    17: "API列表/文件管理/上传/V1（旧）/异步轮询获取上传结果.md",
    18: "API列表/文件管理/上传/V2（推荐）/💡上传流程说明.md",
    19: "API列表/文件管理/上传/V2（推荐）/创建文件.md",
    20: "API列表/文件管理/上传/V2（推荐）/上传分片.md",
    21: "API列表/文件管理/上传/V2（推荐）/上传完毕.md",
    22: "API列表/文件管理/上传/V2（推荐）/获取上传域名.md",
    23: "API列表/文件管理/上传/V2（推荐）/单步上传.md",
    24: "API列表/文件管理/上传/sha1哈希值文件上传.md",
    25: "API列表/文件管理/重命名/单个文件重命名.md",
    26: "API列表/文件管理/重命名/批量文件重命名.md",
    27: "API列表/文件管理/删除/删除文件至回收站.md",
    28: "API列表/文件管理/复制.md",
    29: "API列表/文件管理/复制单个文件.md",
    30: "API列表/文件管理/批量复制文件.md",
    31: "API列表/文件管理/批量复制文件进度.md",
    32: "API列表/文件管理/还原/从回收站恢复文件.md",
    33: "API列表/文件管理/还原/还原文件到指定目录.md",
    34: "API列表/文件管理/文件详情/获取单个文件详情.md",
    35: "API列表/文件管理/文件详情/获取多个文件详情.md",
    36: "API列表/文件管理/文件列表/获取文件列表（推荐）.md",
    37: "API列表/文件管理/文件列表/获取文件列表（旧）.md",
    38: "API列表/文件管理/保险箱/解锁保险箱&获取保险箱id.md",
    39: "API列表/文件管理/移动.md",
    40: "API列表/文件管理/下载.md",
    41: "API列表/分享管理/创建分享链接.md",
    42: "API列表/分享管理/获取分享链接列表.md",
    43: "API列表/分享管理/修改分享链接.md",
    44: "API列表/分享管理/创建付费分享链接.md",
    45: "API列表/分享管理/获取付费分享链接列表.md",
    46: "API列表/分享管理/修改付费分享链接.md",
    47: "API列表/离线下载/创建离线下载任务.md",
    48: "API列表/离线下载/获取离线下载进度.md",
    49: "API列表/用户管理/获取用户信息.md",
    50: "API列表/直链/IP黑名单配置/开启关闭ip黑名单.md",
    51: "API列表/直链/IP黑名单配置/更新ip黑名单列表.md",
    52: "API列表/直链/IP黑名单配置/ip黑名单列表.md",
    53: "API列表/直链/获取直链离线日志.md",
    54: "API列表/直链/获取直链流量日志.md",
    55: "API列表/直链/启用直链空间.md",
    56: "API列表/直链/获取直链链接.md",
    57: "API列表/直链/禁用直链空间.md",
    58: "API列表/直链/直链缓存刷新.md",
    59: "API列表/图床/上传图片/💡上传流程说明.md",
    60: "API列表/图床/上传图片/创建目录.md",
    61: "API列表/图床/上传图片/创建文件.md",
    62: "API列表/图床/上传图片/获取上传地址&上传分片.md",
    63: "API列表/图床/上传图片/上传完毕.md",
    64: "API列表/图床/上传图片/异步轮询获取上传结果.md",
    65: "API列表/图床/复制云盘图片/创建复制任务.md",
    66: "API列表/图床/复制云盘图片/获取复制任务详情.md",
    67: "API列表/图床/复制云盘图片/获取复制失败文件列表.md",
    68: "API列表/图床/移动图片.md",
    69: "API列表/图床/删除图片.md",
    70: "API列表/图床/获取图片信息/获取图片详情.md",
    71: "API列表/图床/获取图片信息/获取图片列表.md",
    72: "API列表/图床/图床离线迁移/创建离线迁移任务.md",
    73: "API列表/图床/图床离线迁移/获取离线迁移任务.md",
    74: "API列表/视频转码/上传视频/本地上传/上传流程.md",
    75: "API列表/视频转码/上传视频/云盘上传/获取云盘视频文件.md",
    76: "API列表/视频转码/上传视频/云盘上传/从云盘空间上传.md",
    77: "API列表/视频转码/获取视频信息/获取转码空间文件列表.md",
    78: "API列表/视频转码/获取视频信息/获取转码空间文件夹信息.md",
    79: "API列表/视频转码/获取视频信息/获取视频文件可转码的分辨率.md",
    80: "API列表/视频转码/获取视频信息/视频转码列表（三方挂载应用授权使用）.md",
    81: "API列表/视频转码/视频转码/视频转码操作.md",
    82: "API列表/视频转码/查询转码信息/查询某个视频的转码记录.md",
    83: "API列表/视频转码/查询转码信息/查询某个视频的转码结果.md",
    84: "API列表/视频转码/删除视频/删除转码视频.md",
    85: "API列表/视频转码/视频文件下载/原文件下载.md",
    86: "API列表/视频转码/视频文件下载/单个转码文件下载（m3u8或ts）.md",
    87: "API列表/视频转码/视频文件下载/某个视频全部转码文件下载.md",
}


def _endpoint(
    command: str, method: str, path: str, sources: tuple[int, ...], **kwargs: Any
) -> Endpoint:
    return Endpoint(
        tuple(command.split()),
        method,
        path,
        source_paths=tuple(_SOURCES[i] for i in sources),
        **kwargs,
    )


def _id(
    wire: str = "fileId", flag: str = "file-id", *, root: bool = False, required: bool = True
) -> Field:
    return F(wire, flag, "int", required, minimum=0 if root else 1)


def _ids(wire: str = "fileIDs", *, maximum: int | None = 100, string: bool = False) -> Field:
    return F(wire, "file-id", "strs" if string else "ints", True, max_items=maximum)


_LIST_V2 = (
    F("parentFileId", "parent-id", "int", True, 0, minimum=0),
    F("limit", "limit", "int", True, 100, minimum=1, maximum=100),
    F("searchData", "search"),
    F("lastFileId", "last-file-id", "int", minimum=0),
)
_UPLOAD_FILE = (
    _id("parentFileID", "parent-id", root=True),
    F("filename", "filename", required=True),
    F("etag", "etag", required=True),
    F("size", "size", "int", True, minimum=0),
    F("duplicate", "duplicate", "int", choices=(1, 2)),
    F("containDir", "contain-dir", "bool"),
)
_SESSION = (F("preuploadID", None, required=True),)
_TRAFFIC = (
    F("trafficSwitch", "traffic-switch", "int", choices=(1, 2, 3, 4)),
    F("trafficLimitSwitch", "traffic-limit-switch", "int", choices=(1, 2)),
    F("trafficLimit", "traffic-limit", "int", minimum=0, maximum=2**63 - 1),
)
_SHARE_IDS = F("shareIdList", "share-id", "ints", True, max_items=100)
_SHARE_FILES = F("fileIDList", "file-id", "ints", True, max_items=100)
_OFFLINE = (
    F("url", "url", required=True),
    F("fileName", "filename"),
    F("dirID", "dir-id", "int", minimum=1),
    F("callBackUrl", "callback-url"),
)
_OFFLINE_WAIT = {
    "field": "status",
    "pending": (0, 3),
    "success": (2,),
    "failure": (1,),
    "interval": 2,
}
_COPY_WAIT = {"field": "status", "pending": (0, 1), "success": (2,), "failure": (3,), "interval": 2}
_COMPLETED_WAIT = {
    "field": "completed",
    "pending": (False,),
    "success": (True,),
    "failure": (),
    "interval": 1,
}

ENDPOINTS: tuple[Endpoint, ...] = (
    _endpoint(
        "auth ensure",
        "POST",
        "/api/v1/access_token",
        (5,),
        fields=(F("clientID", "client-id", required=True), F("clientSecret", None, required=True)),
        auth_mode="developer",
        special="developer-token",
    ),
    _endpoint(
        "oauth exchange",
        "POST",
        "/api/v1/oauth2/access_token",
        (8,),
        location="query",
        fields=(
            F("client_id", "client-id", required=True),
            F("client_secret", None, required=True),
            F("code", None, required=True),
            F("redirect_uri", "redirect-uri", required=True),
        ),
        fixed={"grant_type": "authorization_code"},
        auth_mode="oauth",
        special="oauth-exchange",
    ),
    _endpoint(
        "oauth refresh",
        "POST",
        "/api/v1/oauth2/access_token",
        (8,),
        location="query",
        fields=(
            F("client_id", "client-id", required=True),
            F("client_secret", None, required=True),
            F("refresh_token", None, required=True),
        ),
        fixed={"grant_type": "refresh_token"},
        auth_mode="oauth",
        special="oauth-refresh",
    ),
    _endpoint(
        "file list",
        "GET",
        "/api/v2/file/list",
        (36,),
        location="query",
        fields=_LIST_V2,
        read_only=True,
        special="file-list-v2",
    ),
    _endpoint(
        "file list-v1",
        "GET",
        "/api/v1/file/list",
        (37,),
        location="query",
        fields=(
            F("parentFileId", "parent-id", "int", True, 0, minimum=0),
            F("page", "page", "int", True, 1, minimum=1),
            F("limit", "limit", "int", True, 100, minimum=1, maximum=100),
            F("orderBy", "order-by", required=True, default="file_id"),
            F(
                "orderDirection",
                "order-direction",
                required=True,
                default="asc",
                choices=("asc", "desc"),
            ),
            F("trashed", "trashed", "bool"),
            F("searchData", "search"),
        ),
        read_only=True,
        special="file-list-v1",
    ),
    _endpoint(
        "file info",
        "GET",
        "/api/v1/file/detail",
        (34,),
        location="query",
        fields=(_id("fileID"),),
        read_only=True,
    ),
    _endpoint(
        "file infos",
        "POST",
        "/api/v1/file/infos",
        (35,),
        fields=(_ids("fileIds", maximum=None),),
        read_only=True,
    ),
    _endpoint(
        "file mkdir",
        "POST",
        "/upload/v1/file/mkdir",
        (11,),
        fields=(F("name", "name", required=True), _id("parentID", "parent-id", root=True)),
    ),
    _endpoint(
        "file rename",
        "PUT",
        "/api/v1/file/name",
        (25,),
        fields=(_id(), F("fileName", "name", required=True)),
    ),
    _endpoint(
        "file rename-batch",
        "POST",
        "/api/v1/file/rename",
        (26,),
        fields=(F("renameList", None, "strs", True, max_items=30),),
    ),
    _endpoint(
        "file trash", "POST", "/api/v1/file/trash", (27,), fields=(_ids(),), confirmation=True
    ),
    _endpoint(
        "file copy",
        "POST",
        "/api/v1/file/copy",
        (29,),
        fields=(_id(), _id("targetDirId", "target-dir-id", root=True)),
    ),
    _endpoint(
        "file copy-batch",
        "POST",
        "/api/v1/file/async/copy",
        (30,),
        fields=(_ids("fileIds", maximum=3000), _id("targetDirId", "target-dir-id", root=True)),
        wait={"command": ("file", "copy-progress")},
    ),
    _endpoint(
        "file copy-progress",
        "GET",
        "/api/v1/file/async/copy/process",
        (31,),
        fields=(_id("taskId", "task-id"),),
        read_only=True,
        wait=_COPY_WAIT,
    ),
    _endpoint("file recover", "POST", "/api/v1/file/recover", (32,), fields=(_ids(),)),
    _endpoint(
        "file recover-to",
        "POST",
        "/api/v1/file/recover/by_path",
        (33,),
        fields=(_ids(), _id("parentFileID", "parent-id", root=True)),
    ),
    _endpoint(
        "file move",
        "POST",
        "/api/v1/file/move",
        (39,),
        fields=(_ids(), _id("toParentFileID", "parent-id", root=True)),
    ),
    _endpoint(
        "file safebox-unlock",
        "GET",
        "/api/v1/safebox/id",
        (38,),
        location="query",
        fields=(F("password", None, required=True),),
        special="safebox",
    ),
    _endpoint(
        "file download-url",
        "GET",
        "/api/v1/file/download_info",
        (40,),
        location="query",
        fields=(_id(),),
        read_only=True,
    ),
    _endpoint(
        "file upload-api v1 create",
        "POST",
        "/upload/v1/file/create",
        (13,),
        fields=_UPLOAD_FILE,
        special="upload-create",
    ),
    _endpoint(
        "file upload-api v1 url",
        "POST",
        "/upload/v1/file/get_upload_url",
        (14,),
        fields=(*_SESSION, F("sliceNo", "slice-no", "int", True, minimum=1)),
        read_only=True,
        special="upload-url",
    ),
    _endpoint(
        "file upload-api v1 put",
        "PUT",
        "<presignedURL>",
        (14,),
        location="binary",
        fields=(F("presignedURL", None, required=True),),
        special="upload-put",
    ),
    _endpoint(
        "file upload-api v1 parts",
        "POST",
        "/upload/v1/file/list_upload_parts",
        (15,),
        fields=_SESSION,
        read_only=True,
        special="upload-parts",
    ),
    _endpoint(
        "file upload-api v1 result",
        "POST",
        "/upload/v1/file/upload_async_result",
        (17,),
        fields=_SESSION,
        read_only=True,
        special="upload-result",
        wait=_COMPLETED_WAIT,
    ),
    _endpoint(
        "file upload-api v1 complete",
        "POST",
        "/upload/v1/file/upload_complete",
        (16,),
        fields=_SESSION,
        special="upload-complete",
        wait=_COMPLETED_WAIT,
    ),
    _endpoint(
        "file upload-api v2 create",
        "POST",
        "/upload/v2/file/create",
        (19,),
        fields=_UPLOAD_FILE,
        special="upload-create",
    ),
    _endpoint(
        "file upload-api v2 slice",
        "POST",
        "/upload/v2/file/slice",
        (20,),
        location="multipart",
        fields=(
            *_SESSION,
            F("sliceNo", "slice-no", "int", True, minimum=1),
            F("sliceMD5", "slice-md5", required=True),
            F("slice", "slice", required=True),
        ),
        special="upload-slice",
    ),
    _endpoint(
        "file upload-api v2 domains",
        "GET",
        "/upload/v2/file/domain",
        (22,),
        location="query",
        read_only=True,
        special="upload-domains",
    ),
    _endpoint(
        "file upload-api v2 single",
        "POST",
        "/upload/v2/file/single/create",
        (23,),
        location="multipart",
        fields=(*_UPLOAD_FILE, F("file", "file", required=True)),
        special="upload-single",
    ),
    _endpoint(
        "file upload-api v2 sha1-reuse",
        "POST",
        "/upload/v2/file/sha1_reuse",
        (24,),
        fields=(
            _id("parentFileID", "parent-id", root=True),
            F("filename", "filename", required=True),
            F("sha1", "sha1", required=True),
            F("size", "size", "int", True, minimum=0),
            F("duplicate", "duplicate", "int", choices=(1, 2)),
        ),
        special="upload-sha1",
    ),
    _endpoint(
        "file upload-api v2 complete",
        "POST",
        "/upload/v2/file/upload_complete",
        (21,),
        fields=_SESSION,
        special="upload-complete",
        wait=_COMPLETED_WAIT,
    ),
    _endpoint(
        "share create",
        "POST",
        "/api/v1/share/create",
        (41,),
        fields=(
            F("shareName", "name", required=True),
            F("shareExpire", "expire-days", "int", True, choices=(1, 7, 30, 0)),
            _SHARE_FILES,
            F("sharePwd", None),
            *_TRAFFIC,
        ),
    ),
    _endpoint(
        "share payment create",
        "POST",
        "/api/v1/share/content-payment/create",
        (44,),
        fields=(
            F("shareName", "name", required=True),
            _SHARE_FILES,
            F("payAmount", "pay-amount", "int", True, minimum=1, maximum=1000),
            F("isReward", "is-reward", "int", choices=(0, 1)),
            F("resourceDesc", "resource-desc"),
            *_TRAFFIC,
        ),
        confirmation=True,
    ),
    _endpoint(
        "share list",
        "GET",
        "/api/v1/share/list",
        (42,),
        location="query",
        fields=(
            F("limit", "limit", "int", True, 100, minimum=1, maximum=100),
            F("lastShareId", "last-share-id", "int", default=0, minimum=0),
        ),
        read_only=True,
        special="share-list",
    ),
    _endpoint(
        "share update",
        "PUT",
        "/api/v1/share/list/info",
        (43,),
        fields=(_SHARE_IDS, *_TRAFFIC),
        confirmation=True,
    ),
    _endpoint(
        "share payment list",
        "GET",
        "/api/v1/share/payment/list",
        (45,),
        location="query",
        fields=(
            F("limit", "limit", "int", True, 100, minimum=1, maximum=100),
            F("lastShareId", "last-share-id", "int", default=0, minimum=0),
        ),
        read_only=True,
        special="share-list",
    ),
    _endpoint(
        "share payment update",
        "PUT",
        "/api/v1/share/list/payment/info",
        (46,),
        fields=(_SHARE_IDS, *_TRAFFIC),
        confirmation=True,
    ),
    _endpoint(
        "offline create",
        "POST",
        "/api/v1/offline/download",
        (47,),
        fields=_OFFLINE,
        wait={"command": ("offline", "progress")},
    ),
    _endpoint(
        "offline progress",
        "GET",
        "/api/v1/offline/download/process",
        (48,),
        location="query",
        fields=(_id("taskID", "task-id"),),
        read_only=True,
        wait=_OFFLINE_WAIT,
    ),
    _endpoint("user info", "GET", "/api/v1/user/info", (49,), location="query", read_only=True),
    _endpoint(
        "directlink url",
        "GET",
        "/api/v1/direct-link/url",
        (56,),
        location="query",
        fields=(_id("fileID"),),
        read_only=True,
    ),
    _endpoint(
        "directlink enable",
        "POST",
        "/api/v1/direct-link/enable",
        (55,),
        fields=(_id("fileID"),),
        confirmation=True,
    ),
    _endpoint(
        "directlink disable",
        "POST",
        "/api/v1/direct-link/disable",
        (57,),
        fields=(_id("fileID"),),
        confirmation=True,
    ),
    _endpoint(
        "directlink cache-refresh",
        "POST",
        "/api/v1/direct-link/cache/refresh",
        (58,),
        confirmation=True,
    ),
    _endpoint(
        "directlink traffic-logs",
        "GET",
        "/api/v1/direct-link/log",
        (54,),
        location="query",
        fields=(
            F("pageNum", "page-num", "int", True, 1, minimum=1),
            F("pageSize", "page-size", "int", True, 100, minimum=1),
            F("startTime", "start-time", required=True),
            F("endTime", "end-time", required=True),
        ),
        read_only=True,
    ),
    _endpoint(
        "directlink offline-logs",
        "GET",
        "/api/v1/direct-link/offline/logs",
        (53,),
        location="query",
        fields=(
            F("startHour", "start-hour", required=True),
            F("endHour", "end-hour", required=True),
            F("pageNum", "page-num", "int", True, 1, minimum=1),
            F("pageSize", "page-size", "int", True, 100, minimum=1),
        ),
        read_only=True,
    ),
    _endpoint(
        "directlink blacklist list",
        "GET",
        "/api/v1/developer/config/forbide-ip/list",
        (52,),
        location="query",
        read_only=True,
    ),
    _endpoint(
        "directlink blacklist update",
        "POST",
        "/api/v1/developer/config/forbide-ip/update",
        (51,),
        fields=(F("IpList", "ip", "strs", True, max_items=2000),),
        confirmation=True,
    ),
    _endpoint(
        "directlink blacklist switch",
        "POST",
        "/api/v1/developer/config/forbide-ip/switch",
        (50,),
        fields=(F("Status", "status", "int", True, choices=(1, 2)),),
        confirmation=True,
    ),
    _endpoint(
        "image upload-api create",
        "POST",
        "/upload/v1/oss/file/create",
        (61,),
        fields=(
            F("parentFileID", "parent-id", required=True, default=""),
            F("filename", "filename", required=True),
            F("etag", "etag", required=True),
            F("size", "size", "int", True, minimum=0),
        ),
        fixed={"type": 1},
        special="upload-create",
    ),
    _endpoint(
        "image upload-api get-url",
        "POST",
        "/upload/v1/oss/file/get_upload_url",
        (62,),
        fields=(*_SESSION, F("sliceNo", "slice-no", "int", True, minimum=1)),
        read_only=True,
        special="upload-url",
    ),
    _endpoint(
        "image upload-api put-slice",
        "PUT",
        "<presignedURL>",
        (62,),
        location="binary",
        fields=(F("presignedURL", None, required=True),),
        special="upload-put",
    ),
    _endpoint(
        "image upload-api complete",
        "POST",
        "/upload/v1/oss/file/upload_complete",
        (63,),
        fields=_SESSION,
        special="upload-complete",
        wait=_COMPLETED_WAIT,
    ),
    _endpoint(
        "image upload-api async-result",
        "POST",
        "/upload/v1/oss/file/upload_async_result",
        (64,),
        fields=_SESSION,
        read_only=True,
        special="upload-result",
        wait=_COMPLETED_WAIT,
    ),
    _endpoint(
        "image mkdir",
        "POST",
        "/upload/v1/oss/file/mkdir",
        (60,),
        fields=(
            F("name", "name", "strs", True),
            F("parentID", "parent-id", required=True, default=""),
        ),
        fixed={"type": 1},
    ),
    _endpoint(
        "image list",
        "POST",
        "/api/v1/oss/file/list",
        (71,),
        fields=(
            F("parentFileId", "parent-id", default=""),
            F("limit", "limit", "int", True, 100, minimum=1, maximum=100),
            F("startTime", "start-time", "int", minimum=0),
            F("endTime", "end-time", "int", minimum=0),
            F("lastFileId", "last-file-id"),
        ),
        fixed={"type": 1},
        read_only=True,
        special="image-list",
    ),
    _endpoint(
        "image info",
        "GET",
        "/api/v1/oss/file/detail",
        (70,),
        location="query",
        fields=(F("fileID", "file-id", required=True),),
        read_only=True,
    ),
    _endpoint(
        "image move",
        "POST",
        "/api/v1/oss/file/move",
        (68,),
        fields=(_ids(string=True), F("toParentFileID", "parent-id", required=True)),
    ),
    _endpoint(
        "image delete",
        "POST",
        "/api/v1/oss/file/delete",
        (69,),
        fields=(_ids(string=True),),
        confirmation=True,
    ),
    _endpoint(
        "image source-copy",
        "POST",
        "/api/v1/oss/source/copy",
        (65,),
        fields=(_ids(string=True), F("toParentFileID", "parent-id", required=True, default="")),
        fixed={"sourceType": 1, "type": 1},
        wait={"command": ("image", "source-copy-progress")},
    ),
    _endpoint(
        "image source-copy-progress",
        "GET",
        "/api/v1/oss/source/copy/process",
        (66,),
        location="query",
        fields=(F("taskID", "task-id", required=True),),
        read_only=True,
        wait={
            "field": "status",
            "pending": (1, 4),
            "success": (2,),
            "failure": (3,),
            "interval": 2,
        },
    ),
    _endpoint(
        "image source-copy-failures",
        "GET",
        "/api/v1/oss/source/copy/fail",
        (67,),
        location="query",
        fields=(
            F("taskID", "task-id", required=True),
            F("limit", "limit", "int", True, 100, minimum=1, maximum=100),
            F("page", "page", "int", True, 1, minimum=1),
        ),
        read_only=True,
    ),
    _endpoint(
        "image offline-create",
        "POST",
        "/api/v1/oss/offline/download",
        (72,),
        fields=(
            F("url", "url", required=True),
            F("fileName", "filename"),
            F("dirID", "dir-id"),
            F("callBackUrl", "callback-url"),
        ),
        fixed={"type": 1},
        wait={"command": ("image", "offline-progress")},
    ),
    _endpoint(
        "image offline-progress",
        "GET",
        "/api/v1/oss/offline/download/process",
        (73,),
        location="query",
        fields=(_id("taskID", "task-id"),),
        read_only=True,
        wait=_OFFLINE_WAIT,
    ),
    _endpoint(
        "transcode source-list",
        "GET",
        "/api/v2/file/list",
        (75,),
        location="query",
        fields=(*_LIST_V2, F("searchMode", "search-mode", "int", choices=(0, 1))),
        fixed={"category": 2},
        read_only=True,
        special="file-list-v2",
    ),
    _endpoint(
        "transcode folder-list",
        "GET",
        "/api/v2/file/list",
        (77,),
        location="query",
        fields=(*_LIST_V2, F("searchMode", "search-mode", "int", choices=(0, 1))),
        fixed={"businessType": 2},
        read_only=True,
        special="file-list-v2",
    ),
    _endpoint(
        "transcode folder-info", "POST", "/api/v1/transcode/folder/info", (78,), read_only=True
    ),
    _endpoint(
        "transcode from-cloud",
        "POST",
        "/api/v1/transcode/upload/from_cloud_disk",
        (76,),
        fields=(_ids("fileId"),),
        special="transcode-import",
    ),
    _endpoint(
        "transcode resolutions",
        "POST",
        "/api/v1/transcode/video/resolutions",
        (79,),
        fields=(_id(),),
        read_only=True,
        wait={
            "field": "IsGetResolution",
            "pending": (True,),
            "success": (False,),
            "failure": (),
            "interval": 10,
        },
    ),
    _endpoint(
        "transcode run",
        "POST",
        "/api/v1/transcode/video",
        (81,),
        fields=(
            _id(),
            F("codecName", "codec-name", required=True),
            F("videoTime", "video-time", "float", True, minimum=0),
            F("resolutions", "resolutions", required=True),
        ),
        confirmation=True,
    ),
    _endpoint(
        "transcode records",
        "POST",
        "/api/v1/transcode/video/record",
        (82,),
        fields=(_id(),),
        read_only=True,
    ),
    _endpoint(
        "transcode result",
        "POST",
        "/api/v1/transcode/video/result",
        (83,),
        fields=(_id(),),
        read_only=True,
    ),
    _endpoint(
        "transcode download-url",
        "POST",
        "/api/v1/transcode/file/download",
        (85,),
        fields=(_id(),),
        read_only=True,
    ),
    _endpoint(
        "transcode list",
        "GET",
        "/api/v1/video/transcode/list",
        (80,),
        location="query",
        fields=(_id(),),
        read_only=True,
        auth_mode="oauth",
    ),
    _endpoint(
        "transcode delete",
        "POST",
        "/api/v1/transcode/delete",
        (84,),
        fields=(_id(), F("trashed", "trashed", "int", True, choices=(1, 2))),
        fixed={"businessType": 2},
        confirmation=True,
    ),
    _endpoint(
        "transcode segment-url",
        "POST",
        "/api/v1/transcode/m3u8_ts/download",
        (86,),
        fields=(
            _id(),
            F("resolution", "resolution", required=True),
            F("type", "type", "int", True, choices=(1, 2)),
            F("tsName", "ts-name"),
        ),
        read_only=True,
    ),
    _endpoint(
        "transcode all-download-urls",
        "POST",
        "/api/v1/transcode/file/download/all",
        (87,),
        fields=(_id(), F("zipName", "zip-name", required=True)),
        wait={
            "field": "isDownloading",
            "pending": (True,),
            "success": (False,),
            "failure": (),
            "interval": 10,
        },
        special="transcode-zip",
    ),
)


def _invalid(message: str) -> NoReturn:
    raise Pan123Error("validation", message, exit_code=2)


def _validate_field(spec: Field, value: Any, *, from_request: bool) -> Any:
    """Validate without coercing JSON strings/floats/bools into integer IDs."""
    label = f"--{spec.flag}" if spec.flag else spec.wire
    kind = spec.kind
    if kind == "int":
        if type(value) is not int:
            _invalid(f"{label} 必须是整数")
    elif kind == "float":
        try:
            finite = type(value) in (int, float) and math.isfinite(value)
        except OverflowError:
            finite = False
        if not finite:
            _invalid(f"{label} 必须是有限数字")
    elif kind == "bool":
        if type(value) is not bool:
            _invalid(f"{label} 必须是 true 或 false")
    elif kind == "str":
        if not isinstance(value, str):
            _invalid(f"{label} 必须是字符串")
    elif kind in {"ints", "strs"}:
        if not isinstance(value, list):
            _invalid(f"{label} 必须是数组")
        if not value and spec.wire != "IpList":
            _invalid(f"{label} 不能为空数组")
        if spec.max_items is not None and len(value) > spec.max_items:
            _invalid(f"{label} 最多 {spec.max_items} 项")
        for item in value:
            if kind == "ints" and (type(item) is not int or item < 1):
                _invalid(f"{label} 数组成员必须是正整数 ID")
            if kind == "strs" and (not isinstance(item, str) or not item.strip()):
                _invalid(f"{label} 数组成员必须是非空字符串")
        if len(value) != len(set(value)):
            _invalid(f"{label} 数组不能有重复项")
    elif kind == "json":
        if not isinstance(value, (list, dict)):
            _invalid(f"{label} 必须是 JSON 对象或数组")
    else:
        _invalid(f"未支持的字段类型 {kind}")
    if spec.choices is not None and value not in spec.choices:
        _invalid(f"{label} 不在允许的选项中")
    if spec.minimum is not None and value < spec.minimum:
        _invalid(f"{label} 不能小于 {spec.minimum}")
    if spec.maximum is not None and value > spec.maximum:
        _invalid(f"{label} 不能大于 {spec.maximum}")
    return value


def _filename(value: str, *, allow_path: bool = False) -> None:
    """Enforce the stricter <255 source-table rule; path mode validates parts."""
    parts = value.split("/") if allow_path else [value]
    if allow_path and parts and not parts[0]:
        parts = parts[1:]
    if not parts:
        _invalid("文件名不能为空")
    for part in parts:
        if not part.strip() or len(part) >= 255 or part in {".", ".."}:
            _invalid("文件名必须为非空名称且少于 255 个字符")
        if re.search(r'["\\/:*?|<>\x00-\x1f]', part):
            _invalid("文件名包含不允许的字符")


def _http_url(value: str, label: str) -> None:
    try:
        url = urlsplit(value)
        if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
            _invalid(f"{label} 必须是有效的 HTTP/HTTPS URL，不能含账号密码")
        _ = url.port
    except ValueError:
        _invalid(f"{label} 必须是有效的 HTTP/HTTPS URL")


def _validate_contract(endpoint: Endpoint, payload: dict[str, Any]) -> None:
    command = endpoint.command
    if command in {("share", "update"), ("share", "payment", "update")}:
        if not any(field.wire in payload for field in _TRAFFIC):
            _invalid("分享更新需要至少一个流量策略变更字段")
    if command == ("file", "rename-batch"):
        seen: set[int] = set()
        for item in payload["renameList"]:
            file_id, separator, name = item.partition("|")
            if (
                not separator
                or not file_id.isascii()
                or not file_id.isdecimal()
                or int(file_id) < 1
            ):
                _invalid("renameList 项必须使用 正整数文件ID|新文件名 格式")
            if int(file_id) in seen:
                _invalid("renameList 中不能重复同一文件 ID")
            seen.add(int(file_id))
            _filename(name)
    if command == ("file", "rename"):
        _filename(payload["fileName"])
    if command == ("file", "mkdir"):
        _filename(payload["name"])
    if command == ("image", "mkdir"):
        names = payload["name"] if isinstance(payload["name"], list) else [payload["name"]]
        for name in names:
            _filename(name)
    if "filename" in payload:
        _filename(payload["filename"], allow_path=payload.get("containDir") is True)
    if "etag" in payload and not re.fullmatch(r"[0-9a-fA-F]{32}", payload["etag"]):
        _invalid("etag 必须是 32 位十六进制 MD5")
    if "sha1" in payload and not re.fullmatch(r"[0-9a-fA-F]{40}", payload["sha1"]):
        _invalid("sha1 必须是 40 位十六进制哈希")
    if "sliceMD5" in payload and not re.fullmatch(r"[0-9a-fA-F]{32}", payload["sliceMD5"]):
        _invalid("sliceMD5 必须是 32 位十六进制 MD5")
    if command == ("directlink", "blacklist", "update"):
        for value in payload["IpList"]:
            try:
                ipaddress.IPv4Address(value)
            except ipaddress.AddressValueError:
                _invalid("IpList 仅接受 IPv4 地址，不能使用 IPv6、CIDR 或域名")
    if command == ("image", "move") and not payload["toParentFileID"].strip():
        _invalid("图床移动的目标目录 ID 不能为空")
    if command in {("offline", "create"), ("image", "offline-create")}:
        _http_url(payload["url"], "url")
        if "callBackUrl" in payload:
            _http_url(payload["callBackUrl"], "callBackUrl")
        if "fileName" in payload:
            _filename(payload["fileName"])
            extension = payload["fileName"].rsplit(".", 1)[-1].lower()
            if extension not in {"png", "gif", "jpeg", "tiff", "webp", "jpg", "tif", "svg", "bmp"}:
                _invalid("离线下载自定义名称需要源文档支持的图片扩展名")
        if command[0] == "image" and "dirID" in payload and not payload["dirID"].strip():
            _invalid("图床离线迁移不支持空根目录 ID")
    if command == ("share", "payment", "create"):
        if not payload["shareName"].strip() or len(payload["shareName"]) >= 35:
            _invalid("付费分享名称须非空且少于 35 字符")
        if re.search(r'["\\/:*?|<>\x00-\x1f]', payload["shareName"]):
            _invalid("付费分享名称包含特殊字符")
    if command == ("share", "create") and not payload["shareName"].strip():
        _invalid("分享名称不能为空")
    if (
        command == ("transcode", "segment-url")
        and payload["type"] == 2
        and not payload.get("tsName", "").strip()
    ):
        _invalid("下载 ts 文件时必须提供 --ts-name")
    if command == ("transcode", "run"):
        resolutions = payload["resolutions"].split(",")
        if not all(re.fullmatch(r"[1-9][0-9]*P", item) for item in resolutions):
            _invalid("转码 resolutions 必须使用逗号分隔且 P 大写，例如 1080P,720P")
        if len(set(resolutions)) != len(resolutions):
            _invalid("转码分辨率不能重复")
    if command in {("directlink", "traffic-logs"), ("directlink", "offline-logs")}:
        hour = command[-1] == "offline-logs"
        start_key, end_key = ("startHour", "endHour") if hour else ("startTime", "endTime")
        pattern = r"[0-9]{10}" if hour else r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}"
        fmt = "%Y%m%d%H" if hour else "%Y-%m-%d %H:%M:%S"
        for key in (start_key, end_key):
            if not re.fullmatch(pattern, payload[key]):
                _invalid(f"{key} 格式不正确")
        try:
            start = datetime.strptime(payload[start_key], fmt)
            end = datetime.strptime(payload[end_key], fmt)
        except ValueError:
            _invalid("日志时间不是有效的日期时间")
        if end < start:
            _invalid("结束时间不能早于开始时间")
    if command == ("image", "list") and "startTime" in payload and "endTime" in payload:
        if payload["endTime"] < payload["startTime"]:
            _invalid("结束时间不能早于开始时间")
    # Required strings may be empty only for explicitly documented OSS roots.
    root_strings = {"parentID", "parentFileID", "parentFileId"}
    if command == ("image", "source-copy"):
        root_strings.add("toParentFileID")
    for spec in endpoint.fields:
        if spec.required and isinstance(payload.get(spec.wire), str):
            if spec.wire not in root_strings and not payload[spec.wire].strip():
                _invalid(f"{spec.wire} 不能为空")


def payload_for(
    endpoint: Endpoint,
    values: Mapping[str, Any],
    request_data: Any = None,
) -> Any:
    """Return only validated exact wire fields, never local CLI option metadata.

    JSON request files are strict: no unknown fields, JSON-native types, or mixing
    value-bearing scalar fields with a request file. Sensitive fields (flag=None)
    can be injected into values under their exact wire name by trusted dispatch.
    """
    from_request = request_data is not None
    selected = {
        field.wire: values[field.flag.replace("-", "_")]
        for field in endpoint.fields
        if field.flag and values.get(field.flag.replace("-", "_")) is not None
    }
    injected = {
        field.wire: values[field.wire]
        for field in endpoint.fields
        if field.flag is None and values.get(field.wire) is not None
    }
    if from_request and selected:
        _invalid("--request-file 不能与本接口的标量或集合输入混用")
    if endpoint.command == ("transcode", "from-cloud"):
        if from_request:
            if not isinstance(request_data, list) or not request_data or len(request_data) > 100:
                _invalid("云盘导入请求必须是 1 到 100 项的顶层对象数组")
            result = []
            seen = set()
            for item in request_data:
                if not isinstance(item, dict) or set(item) != {"fileId"}:
                    _invalid("导入数组的每项只能包含 fileId")
                value = item["fileId"]
                _validate_field(_id(), value, from_request=True)
                if value in seen:
                    _invalid("导入文件 ID 不能重复")
                seen.add(value)
                result.append({"fileId": value})
            return result
        spec = endpoint.fields[0]
        ids = selected.get("fileId")
        if ids is None:
            _invalid("缺少 --file-id 或 --request-file")
        _validate_field(spec, ids, from_request=False)
        return [{"fileId": value} for value in ids]
    if from_request:
        if not isinstance(request_data, dict):
            _invalid("本接口请求必须是 JSON 对象")
        allowed = {field.wire for field in endpoint.fields} | set(endpoint.fixed)
        unknown = set(request_data) - allowed
        if unknown:
            _invalid(
                "请求文件含本接口未定义字段: " + ", ".join(sorted(str(key) for key in unknown))
            )
        payload = dict(request_data)
        for wire, value in injected.items():
            if wire in payload and payload[wire] != value:
                _invalid(f"{wire} 请求文件与注入值冲突")
            payload[wire] = value
    else:
        payload = {**selected, **injected}
    for wire, fixed in endpoint.fixed.items():
        if wire in payload and (type(payload[wire]) is not type(fixed) or payload[wire] != fixed):
            _invalid(f"{wire} 必须使用此业务的固定值")
        payload[wire] = fixed
    for spec in endpoint.fields:
        if spec.wire not in payload or payload[spec.wire] is None:
            if spec.default is not None:
                payload[spec.wire] = spec.default
            elif spec.required:
                label = f"--{spec.flag}" if spec.flag else spec.wire
                _invalid(f"缺少必填参数 {label}")
            else:
                payload.pop(spec.wire, None)
                continue
        value = payload[spec.wire]
        if spec.wire == "fileIDList":
            # The official wire value is a comma-separated string, while repeated
            # --file-id values are typed integer arrays at the CLI boundary.
            if from_request:
                if not isinstance(value, str) or not re.fullmatch(
                    r"[1-9][0-9]*(?:,[1-9][0-9]*)*", value
                ):
                    _invalid("fileIDList 必须是逗号分隔的正整数 ID 字符串")
                ids = [int(item) for item in value.split(",")]
            else:
                ids = value
            _validate_field(spec, ids, from_request=False)
            payload[spec.wire] = ",".join(str(item) for item in ids)
        elif endpoint.command == ("image", "mkdir") and spec.wire == "name":
            # Table declares []string while all examples use a scalar. Preserve
            # explicit request-file structure; one CLI --name follows examples.
            if isinstance(value, str):
                if not value.strip():
                    _invalid("name 不能为空")
            else:
                _validate_field(spec, value, from_request=from_request)
                if not from_request and len(value) == 1:
                    payload[spec.wire] = value[0]
        else:
            payload[spec.wire] = _validate_field(spec, value, from_request=from_request)
    _validate_contract(endpoint, payload)
    return payload
