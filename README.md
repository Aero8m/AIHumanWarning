# AIHumanWarning

基于视觉大模型的视频监控智能分析系统。通过连接 RTSP 摄像头，定时抓取画面并调用视觉 LLM 判断是否满足预设条件，实现自动化监控告警。

## 功能特性

- **RTSP 摄像头管理** — 添加、编辑、删除监控流
- **定时抓帧分析** — 通过 APScheduler 定时截图，调用视觉 LLM 分析
- **LLM 灵活配置** — 支持自定义 API Base URL、API Key 和模型名称（默认使用 ModelScope Qwen3.5-122B-A10B）
- **记录查询** — 查看每条监控流的分析历史记录及对应截图
- **MJPEG 实时预览** — 浏览器中实时查看摄像头画面
- **JWT 认证** — 单用户登录认证
- **Docker 部署** — 提供 Dockerfile 支持容器化运行

## 技术栈

**后端：**
- Flask + Flask-SQLAlchemy + Flask-Migrate + Flask-JWT-Extended
- APScheduler（后台定时任务）
- OpenCV（图像处理）
- OpenAI SDK（视觉 LLM 调用）

**前端：**
- 原生 HTML/CSS/JavaScript（内置于 `app/frontend/`）

## 快速开始

### 环境要求

- Python >= 3.10
- pip

### 安装与运行

```bash
git clone <repo-url>
cd AIHumanWarning
pip install -r requirements.txt
flask db upgrade
python run.py
```

服务启动后访问 `http://localhost:5000`。

### 使用 Docker

```bash
docker build -t aihumanwarning .
docker run -p 5000:5000 aihumanwarning
```

## API 文档

所有 API 均位于 `/api/v1/` 前缀下，需要认证的接口需在请求头携带 `Authorization: Bearer <token>`。

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/auth/register` | 注册（仅允许一个用户） |
| POST | `/api/v1/auth/login` | 登录，返回 JWT Token |
| POST | `/api/v1/auth/change_password` | 修改密码（需认证） |

### 摄像头流管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/streams/` | 获取当前用户的所有监控流 |
| POST | `/api/v1/streams/add` | 添加监控流 |
| POST | `/api/v1/streams/edit` | 编辑监控流 |
| POST | `/api/v1/streams/delete` | 删除监控流 |
| GET | `/api/v1/streams/<id>/records` | 获取监控流分析记录 |
| GET | `/api/v1/streams/<id>/live_stream` | MJPEG 实时视频流 |
| POST | `/api/v1/streams/<id>/records/delete` | 删除某条分析记录 |

### LLM 配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/llm_info/` | 获取 LLM 配置 |
| POST | `/api/v1/llm_info/edit` | 修改 LLM 配置 |

### 通用响应格式

```json
{
  "code": 200,
  "message": "ok",
  "data": { ... }
}
```

## 配置

通过环境变量或直接修改 `app/config.py`：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | Flask 密钥 | `dev-secret-key` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///data/data.db` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | `jwt-secret-key` |
| `JWT_ACCESS_TOKEN_EXPIRES` | Token 过期时间 | 24 小时 |

## 项目结构

```
AIHumanWarning/
├── app/
│   ├── api/
│   │   └── v1/          # API v1 路由（auth, streams, llm_info）
│   ├── frontend/        # 前端页面
│   ├── utils/           # 工具函数（响应处理、错误处理）
│   ├── __init__.py      # 应用工厂
│   ├── config.py        # 配置类
│   ├── extensions.py    # Flask 扩展初始化
│   ├── models.py        # 数据模型（User, Stream, StreamRecord）
│   └── scheduler.py     # 后台定时任务
├── data/                # 数据目录（数据库、截图）
├── migrations/          # 数据库迁移
├── Dockerfile
├── boot.sh              # 容器启动脚本
├── requirements.txt
└── run.py               # 入口文件
```
