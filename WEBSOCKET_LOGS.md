# WebSocket 实时日志流功能

## 功能概述

这个项目现在支持通过 WebSocket 实时展示异步任务的执行日志。当任务正在运行时，用户可以实时查看容器内的所有日志输出。

## 架构说明

### 后端 (Python/Flask)

1. **WebSocket Manager** (`server/websocket_manager.py`)
   - 管理 WebSocket 连接
   - 处理任务订阅/取消订阅
   - 广播日志消息到订阅的客户端

2. **Flask-SocketIO** (`server/main.py`)
   - 集成 Socket.IO 到 Flask 应用
   - 处理 WebSocket 事件：connect, disconnect, subscribe_task, unsubscribe_task
   - 支持跨域连接

3. **日志流式传输** (`server/utils/code_task_v2.py`)
   - 在容器执行时启动日志流线程
   - 实时从 Docker 容器获取日志
   - 通过 WebSocket 广播日志行

### 前端 (Next.js/React)

1. **WebSocket Service** (`async-code-web/lib/websocket-service.ts`)
   - 封装 Socket.IO 客户端
   - 提供订阅/取消订阅任务的方法
   - 处理连接状态和错误

2. **任务详情页面** (`async-code-web/app/tasks/[id]/page.tsx`)
   - 显示实时日志流
   - 终端风格的日志展示
   - 自动滚动到最新日志
   - 支持展开/收起日志视图

## 安装步骤

### 后端

1. 安装新的依赖：

```bash
cd server
pip install -r requirements.txt
```

新增的依赖：
- `Flask-SocketIO==5.3.6`
- `python-socketio==5.11.4`

2. 配置环境变量（如果需要修改默认配置）：

```bash
cp .env.example .env
# 编辑 .env 文件
```

3. 启动服务器：

```bash
python main.py
```

服务器将在 `http://localhost:5000` 启动，并启用 WebSocket 支持。

### 前端

1. 安装新的依赖：

```bash
cd async-code-web
npm install
```

新增的依赖：
- `socket.io-client`

2. 配置环境变量：

```bash
cp .env.local.example .env.local
# 编辑 .env.local 文件，设置 NEXT_PUBLIC_API_URL
```

3. 启动开发服务器：

```bash
npm run dev
```

## 使用方法

1. 创建一个新的异步任务

2. 任务开始运行后，导航到任务详情页面

3. 页面会自动连接到 WebSocket 并订阅该任务的日志

4. 点击 "Show Logs" 按钮查看实时日志流

5. 日志会以终端风格显示，绿色文字表示日志内容

6. 日志视图会自动滚动到最新内容

## WebSocket 事件

### 客户端发送的事件

- `subscribe_task`: 订阅特定任务的日志
  ```json
  {
    "task_id": 123
  }
  ```

- `unsubscribe_task`: 取消订阅任务
  ```json
  {
    "task_id": 123
  }
  ```

### 服务器发送的事件

- `connected`: 连接成功确认
  ```json
  {
    "status": "connected",
    "sid": "session_id"
  }
  ```

- `subscribed`: 订阅成功确认
  ```json
  {
    "task_id": 123,
    "message": "Subscribed to task 123"
  }
  ```

- `task_log`: 实时日志消息
  ```json
  {
    "task_id": 123,
    "log": "Container log line...",
    "timestamp": 1234567890.123
  }
  ```

- `task_status`: 任务状态更新
  ```json
  {
    "task_id": 123,
    "status": "running",
    "message": "Container started, executing task..."
  }
  ```

## 技术特点

### 可靠性

- **自动重连**: 客户端会尝试自动重连，最多 5 次
- **优雅降级**: 如果 WebSocket 不可用，前端仍可通过轮询获取任务状态
- **资源清理**: 连接断开时自动清理订阅

### 性能

- **流式传输**: 日志通过 Docker 的流式 API 实时获取
- **节流控制**: 每条日志之间有轻微延迟（10ms），避免过载
- **按需订阅**: 只在任务运行时且用户打开日志视图时传输数据

### 用户体验

- **终端风格**: 深色背景、绿色文字，模拟真实终端
- **自动滚动**: 日志视图自动滚动到最新内容
- **状态指示**: 显示 "Live" 徽章表示实时连接
- **可折叠**: 日志视图可以展开和收起

## 故障排除

### WebSocket 连接失败

1. 检查后端是否正在运行
2. 检查 `NEXT_PUBLIC_API_URL` 环境变量是否正确
3. 查看浏览器控制台的错误消息
4. 确认防火墙没有阻止 WebSocket 连接

### 日志不显示

1. 确认任务状态为 "running"
2. 点击 "Show Logs" 按钮
3. 检查浏览器控制台是否有 WebSocket 相关错误
4. 查看后端日志确认日志流线程是否正常启动

### 性能问题

如果日志流导致性能问题：

1. 增加日志节流延迟（在 `code_task_v2.py` 中修改 `time.sleep(0.01)`）
2. 限制日志视图的最大行数
3. 使用虚拟滚动优化大量日志的渲染

## 未来改进

- [ ] 添加日志搜索和过滤功能
- [ ] 支持日志下载
- [ ] 添加日志高亮和语法分析
- [ ] 支持多个任务的并发日志流
- [ ] 添加日志统计和分析功能
- [ ] 支持日志持久化到数据库