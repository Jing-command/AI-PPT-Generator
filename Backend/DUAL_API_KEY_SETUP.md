# 双 API Key 配置指南

## 概述

如果你的 yunwu.ai 账户有两个不同的 API Key：
- **文本 Key**: 只能使用 `gemini-3-flash-preview`（文字生成）
- **图片 Key**: 只能使用 `gemini-3-pro-image-preview`（图片生成）

本系统支持自动识别并使用这两个 Key。

## 配置方法

### 方法 1: 在网站上添加两个 API Key（推荐）

1. 登录网站，进入 **设置 > API Keys**
2. 添加第一个 Key（文本生成）：
   - **提供商**: `yunwu`
   - **API Key**: 你的文本生成 Key
   - **名称**: `Yunwu 文本生成`
3. 添加第二个 Key（图片生成）：
   - **提供商**: `yunwu-image`
   - **API Key**: 你的图片生成 Key
   - **名称**: `Yunwu 图片生成`

系统会自动识别 `yunwu-image` 作为图片生成专用 Key。

### 方法 2: 环境变量配置

如果你无法添加两个 Key，可以通过环境变量配置：

```bash
# Windows PowerShell
$env:YUNWU_API_KEY="你的文本生成Key"
$env:IMAGE_API_KEY="你的图片生成Key"

# Linux/Mac
export YUNWU_API_KEY="你的文本生成Key"
export IMAGE_API_KEY="你的图片生成Key"
```

### 方法 3: 使用同一个 Key

如果你的 Key 同时支持文本和图片生成，只需添加一个 Key：
- **提供商**: `yunwu`
- **API Key**: 你的 Key

系统会自动使用同一个 Key 进行文本和图片生成。

## 优先级规则

系统按以下优先级选择图片生成 Key：

1. **数据库中 `yunwu-image` 提供商的 Key**
2. **环境变量 `IMAGE_API_KEY`**
3. **与文本生成相同的 Key**

## 验证配置

添加 Key 后，运行测试脚本验证：

```bash
# 测试文本生成
python test_text_generation.py

# 测试图片生成
python test_image_generation.py

# 测试完整流程
python test_data_flow.py
```

## 日志输出

配置正确时，Celery Worker 会输出：

```
[Generation] Using dedicated image API key from database
# 或
[Generation] Using IMAGE_API_KEY from environment
# 或
[Generation] Using same API key for text and image generation
```

## 故障排查

### 问题：图片没有生成

**检查步骤：**

1. 查看 Celery Worker 日志中的 Key 选择信息
2. 确认 `yunwu-image` Key 已正确添加且状态为 `active`
3. 运行 `test_image_generation.py` 测试图片 Key 是否有效

### 问题：提示 "No valid API Key found"

**检查步骤：**

1. 确认 API Key 已添加到系统
2. 确认 Key 状态为 `active`
3. 检查 Key 的提供商是否正确（`yunwu` 或 `yunwu-image`）

### 问题：图片 Key 被用于文本生成

**原因**：系统只在 `generate_image` 方法中使用 `image_api_key`，其他方法使用 `api_key`。

**检查**：确保 `YunwuProvider` 正确初始化：
```python
provider = YunwuProvider(
    api_key=text_api_key,        # 用于文本生成
    image_api_key=image_api_key  # 用于图片生成
)
```

## 技术实现

### 后端代码结构

```python
# app/services/api_key_service.py
async def get_image_key(self, user_id, provider):
    # 1. 查找 {provider}-image 专用 Key
    # 2. 如果没有，返回默认 Key

# app/tasks/generation_tasks.py
image_key_record = await api_key_service.get_image_key(task.user_id, task.provider)
if image_key_record and image_key_record.id != key.id:
    image_api_key = decrypt(image_key_record.api_key_encrypted)
else:
    image_api_key = os.getenv("IMAGE_API_KEY") or api_key

provider = AIProviderFactory.create(task.provider, api_key, image_api_key)
```

### 前端配置界面

在 **设置 > API Keys** 页面，添加 Key 时：
- 提供商选择 `yunwu` 用于文本生成
- 提供商选择 `yunwu-image` 用于图片生成

两个 Key 都会显示在列表中，可以分别管理状态。
