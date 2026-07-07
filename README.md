# AIHumanWarning 后端 API 文档

## 项目概述

AI 视频监控预警系统后端，基于 **Flask 3.1.1** 构建。接入 RTSP 视频流，定时抓取视频帧并调用 LLM 视觉能力分析画面是否满足预警条件。

### 技术栈

| 技术 | 说明 |
|------|------|
| Flask 3.1.1 | Web 框架 |
| Flask-SQLAlchemy 3.1.1 | ORM 数据库 |
| Flask-Migrate 4.1.0 | 数据库迁移 |
| Flask-JWT-Extended 4.7.1 | JWT 认证 |
| APScheduler >=3.10 | 定时任务调度 |
| OpenCV (cv2) | 视频帧捕获 |
| OpenAI Python SDK | LLM API 调用 |
| SQLite | 数据库引擎 |

### 基础 URL

```
http://<host>:5000/api/v1
```

### 通用响应格式

所有响应均为 JSON 格式：

```json
{
  "code": 200,
  "message": "ok",
  "data": null
}
```

### 通用错误码

| HTTP 状态码 | message | 说明 |
|-------------|---------|------|
| 400 | bad request | 请求错误 |
| 401 | unauthorized | 未认证 |
| 403 | forbidden | 无权限 |
| 404 | not found | 资源不存在 |
| 405 | method not allowed | 方法不允许 |
| 422 | unprocessable entity | 请求无法处理 |
| 500 | internal server error | 服务器内部错误 |

---

## 目录

- [1. 认证 API](#1-认证-api)
  - [1.1 注册](#11-注册)
  - [1.2 登录](#12-登录)
  - [1.3 修改密码](#13-修改密码)
- [2. 视频流 API](#2-视频流-api)
  - [2.1 获取流列表](#21-获取流列表)
  - [2.2 添加视频流](#22-添加视频流)
  - [2.3 删除视频流](#23-删除视频流)
  - [2.4 编辑视频流](#24-编辑视频流)
  - [2.5 获取检测记录](#25-获取检测记录)
  - [2.6 获取截图](#26-获取截图)
  - [2.7 实时视频流](#27-实时视频流)
- [3. LLM 配置 API](#3-llm-配置-api)
  - [3.1 获取 LLM 配置](#31-获取-llm-配置)
  - [3.2 修改 LLM 配置](#32-修改-llm-配置)
- [4. 数据库模型](#4-数据库模型)
  - [4.1 User](#41-user)
  - [4.2 Stream](#42-stream)
  - [4.3 StreamRecord](#43-streamrecord)

---

## 1. 认证 API

### 1.1 注册

> **限制：系统仅允许注册一个用户。**

```
POST /api/v1/auth/register
```

认证方式：**无需认证**

**请求体 (JSON)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码（明文） |

**请求示例：**

```json
{
  "username": "admin",
  "password": "123456"
}
```

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "registered successfully",
  "data": {}
}
```

**错误响应：**

| 状态码 | message | 说明 |
|--------|---------|------|
| 400 | only one user allowed! | 用户已存在（最多一个用户） |
| 409 | username already exists | 用户名已存在 |

---

### 1.2 登录

```
POST /api/v1/auth/login
```

认证方式：**无需认证**

**请求体 (JSON)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码（明文） |

**请求示例：**

```json
{
  "username": "admin",
  "password": "123456"
}
```

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "ok",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

> Token 有效期：**24 小时**。后续请求需在 `Authorization` 头携带此 Token。

**错误响应 (401)：**

```json
{
  "code": 401,
  "message": "invalid credentials",
  "data": null
}
```

---

### 1.3 修改密码

```
POST /api/v1/auth/change_password
```

认证方式：**`Authorization: Bearer <token>`**

**请求体 (JSON)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| password | string | 是 | 新密码 |

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "ok",
  "data": null
}
```

**错误响应 (401)：**

```json
{
  "code": 401,
  "message": "user not exists",
  "data": null
}
```

---

## 2. 视频流 API

### 2.1 获取流列表

```
GET /api/v1/streams/
```

认证方式：**`Authorization: Bearer <token>`**

**请求参数：** 无

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "ok",
  "data": [
    {
      "id": 1,
      "name": "门口摄像头",
      "rtsp_link": "rtsp://192.168.1.100:554/stream1",
      "user_id": 1,
      "prompt": "检测画面中是否有人闯入",
      "sec": 30,
      "enable": true
    }
  ]
}
```

---

### 2.2 添加视频流

```
POST /api/v1/streams/add
```

认证方式：**`Authorization: Bearer <token>`**

**请求体 (JSON)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 流名称 |
| rtsp_link | string | 是 | RTSP 地址（唯一） |
| prompt | string | 是 | 检测提示词 |
| sec | int | 是 | 检测间隔（秒） |
| enable | bool | 是 | 是否启用 |

**请求示例：**

```json
{
  "name": "门口摄像头",
  "rtsp_link": "rtsp://192.168.1.100:554/stream1",
  "prompt": "检测画面中是否有人闯入",
  "sec": 30,
  "enable": true
}
```

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "ok",
  "data": null
}
```

**错误响应 (400)：**

```json
{
  "code": 400,
  "message": "添加失败，错误:UNIQUE constraint failed: streams.rtsp_link",
  "data": null
}
```

> 添加成功后，系统会自动启动该流的定时检测任务。

---

### 2.3 删除视频流

```
POST /api/v1/streams/delete
```

认证方式：**`Authorization: Bearer <token>`**

**请求体 (JSON)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | 是 | 视频流 ID |

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "ok",
  "data": "删除成功"
}
```

> 删除成功后，系统会自动停止该流的定时检测任务。

---

### 2.4 编辑视频流

```
POST /api/v1/streams/edit
```

认证方式：**`Authorization: Bearer <token>`**

**请求体 (JSON)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int | **是** | 视频流 ID |
| name | string | 否 | 流名称 |
| rtsp_link | string | 否 | RTSP 地址 |
| prompt | string | 否 | 检测提示词 |
| sec | int | 否 | 检测间隔（秒） |
| enable | bool | 否 | 是否启用 |

> 只需传入需要修改的字段。

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "ok",
  "data": null
}
```

**错误响应：**

| 状态码 | message | 说明 |
|--------|---------|------|
| 400 | please set stream id | 未提供流 ID |
| 400 | stream not found | 流不存在 |

---

### 2.5 获取检测记录

```
GET /api/v1/streams/<id>/records
```

认证方式：**`Authorization: Bearer <token>`**

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 视频流 ID |

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "ok",
  "data": [
    {
      "id": 1,
      "stream_id": 1,
      "user_id": 1,
      "prompt": "检测画面中是否有人闯入",
      "status": true,
      "reason": "检测到有人闯入",
      "image_url": "http://host:5000/api/v1/streams/1/records/image/AIHWCAP_1_2026-07-07_12-00-00.png"
    }
  ]
}
```

> `status` 字段：`true` 表示预警成立，`false` 表示不成立。
> `image_url` 返回的是完整的绝对 URL，可直接访问查看截图。

**错误响应 (400)：**

```json
{
  "code": 400,
  "message": "stream not found",
  "data": null
}
```

---

### 2.6 获取截图

```
GET /api/v1/streams/<id>/records/image/<filename>
```

认证方式：**`Authorization: Bearer <token>`**

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 视频流 ID |
| filename | string | 截图文件名 |

> 响应为图片文件（PNG），可直接在浏览器中打开或嵌入 `<img>` 标签。

备注：一般不直接使用这个接口，这个接口只是为了服务获取检测记录接口中的图片链接。
---

### 2.7 实时视频流

```
GET /api/v1/streams/<id>/live_stream
```

认证方式：
**查询参数方式：** `?token=<JWT>`

**路径参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | int | 视频流 ID |

**响应内容类型：** `multipart/x-mixed-replace; boundary=frame`（**MJPEG 流**）

> 持续推送实时视频帧，直到客户端断开连接。适用于 `<img>` 标签直接展示实时画面。

**HTML 使用示例：**

```html
<img src="http://host:5000/api/v1/streams/1/live_stream?token=eyJhbGciOiJIUzI1NiIs..." />
```

---

## 3. LLM 配置 API

### 3.1 获取 LLM 配置

```
GET /api/v1/llm_info/
```

认证方式：**`Authorization: Bearer <token>`**

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "ok",
  "data": {
    "baseurl": "https://api-inference.modelscope.cn/v1",
    "apikey": "sk-xxxxxxxxxxxxxxxxxxxx",
    "modelname": "Qwen/Qwen3.5-122B-A10B"
  }
}
```

---

### 3.2 修改 LLM 配置

```
POST /api/v1/llm_info/edit
```

认证方式：**`Authorization: Bearer <token>`**

**请求体 (JSON)：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| baseurl | string | 否 | LLM API 基础地址 |
| apikey | string | 否 | API 密钥 |
| modelname | string | 否 | 模型名称 |

> 只需传入需要修改的字段。

**请求示例：**

```json
{
  "baseurl": "https://api.openai.com/v1",
  "apikey": "sk-newapikey",
  "modelname": "gpt-4o"
}
```

**成功响应 (200)：**

```json
{
  "code": 200,
  "message": "ok",
  "data": null
}
```

---

## 4. 数据库模型

### 4.1 User (`users` 表)

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, 自增 | — | 用户 ID |
| username | String(80) | UNIQUE, NOT NULL | — | 用户名 |
| password_hash | String(256) | NOT NULL | — | 密码哈希 |
| llm_baseurl | String(256) | NOT NULL | `https://api-inference.modelscope.cn/v1` | LLM API 地址 |
| llm_apikey | String(256) | NOT NULL | `sk-xxxxxxxxxxxxxxxxxxxx` | API 密钥 |
| llm_modelname | String(256) | NOT NULL | `Qwen/Qwen3.5-122B-A10B` | 模型名称 |

**关联关系：**
- `streams`：一对多 → `Stream`
- `stream_records`：一对多 → `StreamRecord`

### 4.2 Stream (`streams` 表)

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | Integer | PK, 自增 | — | 流 ID |
| name | String(80) | NOT NULL | — | 流名称 |
| rtsp_link | String(80) | UNIQUE, NOT NULL | — | RTSP 地址 |
| user_id | Integer | FK → users.id, NOT NULL | — | 所属用户 ID |
| prompt | String(80) | NOT NULL | — | 检测提示词 |
| sec | Integer | NOT NULL | — | 检测间隔（秒） |
| enable | Boolean | — | true | 是否启用 |

**关联关系：**
- `records`：一对多 → `StreamRecord`

### 4.3 StreamRecord (`stream_records` 表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | Integer | PK, 自增 | 记录 ID |
| stream_id | Integer | FK → streams.id, NOT NULL | 关联流 ID |
| user_id | Integer | FK → users.id, NOT NULL | 所属用户 ID |
| prompt | String(80) | NOT NULL | 检测时使用的提示词 |
| status | Boolean | NOT NULL | 检测结果（true=预警成立） |
| reason | String(80) | NOT NULL | LLM 返回的理由 |
| image_url | String(256) | NOT NULL | 截图文件名 |

---

## 附录

### Token 认证方式

所有需要认证的接口统一使用 **Bearer Token** 认证：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 启动服务

```bash
python run.py
```

服务默认监听 `0.0.0.0:5000`，开发模式开启 debug。

### 定时检测任务说明

系统启动后，对于所有 `enable=true` 的视频流，会自动创建定时任务。每个任务按 `sec` 秒为间隔执行以下流程：

1. 通过 OpenCV 打开 RTSP 流，读取一帧画面
2. 将帧缩放（最大 1080px）后保存为 PNG 截图
3. 调用 LLM 视觉模型分析图片
4. LLM 返回格式：第一行为理由（≤20字），第二行为 `yes` / `no`
5. 根据结果创建 `StreamRecord` 记录
