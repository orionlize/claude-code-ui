# 快速启动指南 - WebSocket 实时日志功能

## 一、后端设置

### 1. 安装依赖
```bash
cd server
pip install Flask-SocketIO==5.3.6 python-socketio==5.11.4
```

### 2. 启动服务器
```bash
python main.py
```

服务器现在会在 `http://localhost:5000` 上运行，并支持 WebSocket 连接。

## 二、前端设置

### 1. 安装依赖
```bash
cd async-code-web
npm install socket.io-client
```

### 2. 配置环境变量
```bash
# 创建或编辑 .env.local 文件
echo "NEXT_PUBLIC_API_URL=http://localhost:5000" > .env.local
```

### 3. 启动开发服务器
```bash
npm run dev
```

前端现在会在 `http://localhost:3000` 上运行。

## 三、使用实时日志功能

1. 在浏览器中打开 `http://localhost:3000`
2. 创建一个新的异步任务
3. 任务开始运行后，进入任务详情页面
4. 你会看到：
   - 一个绿色的 "Live" 徽章，表示已连接到 WebSocket
   - 一个 "Show Logs" 按钮
5. 点击 "Show Logs" 查看实时日志流
6. 日志会以终端风格（绿色文字）实时显示

## 四、验证功能

### 后端日志中应该看到：
```
📡 Starting log stream for task X
🔌 Client connected: abc123
📡 Session abc123 subscribed to task X
📤 Broadcast log to N subscribers for task X
```

### 前端浏览器控制台中应该看到：
```
[WebSocket] Connecting to... http://localhost:5000
[WebSocket] Connected with ID: abc123
[WebSocket] Subscribing to task X
[WebSocket] Successfully subscribed to task X
```

## 五、故障排除

### 问题：看不到 "Live" 徽章
**解决方案**：
- 确认后端服务器正在运行
- 检查浏览器控制台是否有连接错误
- 验证 `NEXT_PUBLIC_API_URL` 配置正确

### 问题：点击 "Show Logs" 没有日志显示
**解决方案**：
- 确认任务状态为 "running"
- 等待几秒钟，日志可能需要一点时间开始流式传输
- 检查后端日志确认容器已启动

### 问题：日志停止更新
**解决方案**：
- 这是正常的，任务完成后日志流会停止
- 刷新页面可以看到完整的日志历史

## 六、功能特性

✅ **实时日志流** - 任务运行时实时显示容器日志
✅ **自动滚动** - 日志视图自动滚动到最新内容
✅ **终端风格** - 深色背景、绿色文字，模拟真实终端
✅ **状态指示** - "Live" 徽章表示实时连接
✅ **可折叠** - 可以展开和收起日志视图
✅ **历史查看** - 任务完成后仍可查看日志

## 七、技术细节

- **协议**：WebSocket (Socket.IO)
- **端口**：5000 (后端), 3000 (前端)
- **传输**：支持 WebSocket 和轮询降级
- **重连**：自动重连，最多 5 次

## 八、下一步

详细文档请参阅：
- [WEBSOCKET_LOGS.md](./WEBSOCKET_LOGS.md) - 完整功能文档
- [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - 实现总结

---

🎉 **享受实时日志流功能！**