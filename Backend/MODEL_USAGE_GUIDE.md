# 模型使用指南 - gemini-3-flash vs gemini-3-pro-image

## 概述

本项目使用两个不同的 Gemini 模型，分别用于不同的场景：

| 用途 | 模型名称 | API 类型 | 端点 |
|------|---------|---------|------|
| **文本生成** | gemini-3-flash-preview | OpenAI 兼容 | `/v1/chat/completions` |
| **图片生成** | gemini-3-pro-image-preview | Gemini 原生 | `/v1beta/models/gemini-3-pro-image-preview:generateContent` |

## 使用场景

### 1. 文本生成 (gemini-3-flash-preview)

**使用场景：**
- PPT 大纲生成 (`generate_ppt_outline`)
- 幻灯片内容生成 (`generate_slide_content`)
- 图片提示词生成 (`generate_image_prompt`)

**API 格式：** OpenAI 兼容
```python
response = await self.client.chat.completions.create(
    model="gemini-3-flash-preview",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=8000
)
```

**特点：**
- 速度快，适合对话和文本生成
- 支持长文本输出（最多 8000 tokens）
- JSON 格式输出

### 2. 图片生成 (gemini-3-pro-image-preview)

**使用场景：**
- 根据提示词生成 PPT 配图 (`generate_image`)
- 为标题页生成背景图
- 为章节页生成配图

**API 格式：** Gemini 原生（非 OpenAI 兼容）
```python
api_url = "https://yunwu.ai/v1beta/models/gemini-3-pro-image-preview:generateContent"

payload = {
    "contents": [{
        "role": "user",
        "parts": [{"text": prompt}]
    }],
    "generationConfig": {
        "responseModalities": ["Text", "Image"]
    }
}
```

**特点：**
- 专门用于图像生成
- 返回 base64 编码的图片数据
- 生成时间较长（30-120秒）
- 支持多模态输出（图片+文字描述）

## 代码中的区分

### 类常量定义
```python
class YunwuProvider(AIProviderBase):
    TEXT_MODEL = "gemini-3-flash-preview"      # 文本模型
    IMAGE_MODEL = "gemini-3-pro-image-preview" # 图片模型
```

### 文本生成调用
```python
# 方法: generate_ppt_outline, generate_slide_content, generate_image_prompt
response = await self.client.chat.completions.create(
    model=self.TEXT_MODEL,  # gemini-3-flash-preview
    ...
)
```

### 图片生成调用
```python
# 方法: generate_image
api_url = f"https://yunwu.ai/v1beta/models/{self.IMAGE_MODEL}:generateContent"

async with httpx.AsyncClient(timeout=120.0) as client:
    response = await client.post(api_url, json=payload, headers=headers)
    # 解析 inlineData 获取图片
```

## 日志输出示例

正常工作时应该看到：

```
[YunwuProvider] Text model: gemini-3-flash-preview
[YunwuProvider] Image model: gemini-3-pro-image-preview

[TextGen] Using model: gemini-3-flash-preview for outline generation
[TextGen] Using model: gemini-3-flash-preview for content generation

[ImageGen] Using model: gemini-3-pro-image-preview
[ImageGen] Prompt: Professional business illustration...
[ImageGen] Found image data: image/png, 15234 chars
```

## 常见问题

### Q: 为什么图片生成不能用 OpenAI 格式？
A: gemini-3-pro-image-preview 是 Gemini 原生模型，目前 yunwu.ai 只提供了 Gemini 原生 API 端点，没有 OpenAI 兼容端点。

### Q: 两个模型可以用同一个 API key 吗？
A: 可以。只要你的 yunwu.ai API key 有权限访问这两个模型，就可以使用同一个 key。

### Q: 图片生成失败怎么办？
A: 检查以下几点：
1. API key 是否有 gemini-3-pro-image-preview 的访问权限
2. 账户余额是否充足
3. 请求是否超时（图片生成需要 30-120 秒）

### Q: 如何更换模型？
A: 修改 `YunwuProvider` 类中的常量：
```python
TEXT_MODEL = "其他文本模型"
IMAGE_MODEL = "其他图片模型"
```

## 测试

运行测试脚本验证两个模型：

```bash
# 测试文本生成
python test_text_generation.py

# 测试图片生成
python test_image_generation.py

# 测试完整流程
python test_data_flow.py
```
