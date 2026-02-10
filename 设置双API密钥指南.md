# 设置双 API 密钥指南

## 适用场景

当你有两个不同的 yunwu.ai API Key：
- **文本 Key**: 只能使用 `gemini-3-flash-preview` 生成文字
- **图片 Key**: 只能使用 `gemini-3-pro-image-preview` 生成图片

## 设置步骤

### 第一步：登录网站

1. 打开网站并登录你的账户
2. 点击右上角头像 → **设置**
3. 进入 **API Keys** 页面

### 第二步：添加文本生成 Key

1. 点击 **添加 API Key** 按钮
2. 填写信息：
   - **名称**: `Yunwu 文本生成` (或任意名称)
   - **提供商**: 选择 `云屋 AI (yunwu.ai)`
   - **API Key**: 粘贴你的**文本生成 Key**
3. 点击 **保存**

### 第三步：添加图片生成 Key

1. 再次点击 **添加 API Key** 按钮
2. 填写信息：
   - **名称**: `Yunwu 图片生成` (或任意名称)
   - **提供商**: 选择 `云屋 AI - 图片生成专用` 🖼️
   - **API Key**: 粘贴你的**图片生成 Key**
3. 点击 **保存**

### 第四步：验证配置

1. 确保两个 Key 的状态都是 **启用** (绿色)
2. 可以设置其中一个为 **默认**（推荐设置文本 Key 为默认）

### 第五步：重启服务

1. 重启后端服务：
   ```bash
   # 停止当前服务
   Ctrl+C
   
   # 重新启动
   python -m app.main
   ```

2. 重启 Celery Worker：
   ```bash
   # 停止当前 worker
   Ctrl+C
   
   # 重新启动
   celery -A app.tasks worker --pool=solo -l info
   ```

## 验证设置

### 方法 1：查看日志

生成一个 PPT，观察 Celery Worker 日志：
```
[Generation] Using dedicated image API key from database
```

如果看到这条日志，说明成功使用了图片专用 Key。

### 方法 2：运行测试

```bash
cd AI-PPT-Generator-clone/backend

# 测试完整流程
python test_data_flow.py
```

输入两个不同的 Key，确认都能正常工作。

## 常见问题

### Q: 添加 Key 时提示 "不支持的提供商"

**解决**: 确保前端已重新构建，且后端已重启。

```bash
# 前端
cd frontend
npm run build

# 后端
cd backend
python -m app.main
```

### Q: 图片没有生成

**排查步骤**:
1. 检查 Celery Worker 是否在运行
2. 查看 Worker 日志是否有 `[Generation] Using dedicated image API key from database`
3. 确认图片 Key 的状态是 **active**
4. 运行 `python test_image_generation.py` 测试图片 Key 是否有效

### Q: 只想用一个 Key

如果你只有一个同时支持文本和图片的 Key：
1. 只添加一个提供商为 `云屋 AI (yunwu.ai)` 的 Key
2. 系统会自动使用同一个 Key 进行文本和图片生成

## 技术说明

### 提供商标识

| 显示名称 | 内部标识 | 用途 |
|---------|---------|------|
| 云屋 AI (yunwu.ai) | `yunwu` | 文本生成 |
| 云屋 AI - 图片生成专用 | `yunwu-image` | 图片生成 |

### 优先级规则

系统按以下顺序选择图片生成 Key：
1. 数据库中 `provider = 'yunwu-image'` 的 Key
2. 环境变量 `IMAGE_API_KEY`
3. 使用与文本相同的 Key

### 数据库存储

两个 Key 都存储在 `user_api_keys` 表中，通过 `provider` 字段区分：
- `yunwu`: 文本生成 Key
- `yunwu-image`: 图片生成 Key
