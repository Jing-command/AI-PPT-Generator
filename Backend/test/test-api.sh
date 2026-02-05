#!/bin/bash
# AI PPT 功能测试脚本

BASE_URL="http://localhost:8000/api/v1"

echo "🧪 开始测试 AI PPT 功能..."

# 1. 注册
echo "📧 Step 1: 注册用户"
REGISTER=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test_'$(date +%s)'@example.com","password":"test123456","name":"测试用户"}')
echo "注册结果: $REGISTER"

# 2. 登录
echo "🔑 Step 2: 登录"
EMAIL=$(echo $REGISTER | grep -o '"email":"[^"]*"' | cut -d'"' -f4)
LOGIN=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"test123456\"}")
TOKEN=$(echo $LOGIN | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
echo "获取 Token: ${TOKEN:0:20}..."

# 3. 添加 API Key
echo "🔐 Step 3: 添加 API Key"
API_KEY=$(curl -s -X POST "$BASE_URL/api-keys" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试Key","api_key":"sk-test123456","provider":"openai","is_default":true}')
echo "API Key 添加结果: $API_KEY"

# 4. 创建 PPT
echo "📊 Step 4: 创建空白 PPT"
PPT=$(curl -s -X POST "$BASE_URL/ppt" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"测试PPT"}')
PPT_ID=$(echo $PPT | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
echo "PPT ID: $PPT_ID"

# 5. 添加幻灯片
echo "📄 Step 5: 添加幻灯片"
SLIDE=$(curl -s -X POST "$BASE_URL/ppt/$PPT_ID/slides" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"content","content":{"title":"第一页","text":"这是内容"}}')
echo "添加幻灯片结果: $SLIDE"

# 6. 获取 PPT 列表
echo "📋 Step 6: 获取 PPT 列表"
LIST=$(curl -s "$BASE_URL/ppt" \
  -H "Authorization: Bearer $TOKEN")
echo "PPT 列表: $(echo $LIST | grep -o '"id"' | wc -l) 个"

# 7. 获取模板列表
echo "🎨 Step 7: 获取模板列表"
TEMPLATES=$(curl -s "$BASE_URL/templates")
echo "模板数量: $(echo $TEMPLATES | grep -o '"id"' | wc -l) 个"

echo ""
echo "✅ 基础功能测试完成!"
echo ""
echo "其他测试命令:"
echo "  提交导出任务: curl -X POST $BASE_URL/ppt/$PPT_ID/export -H \"Authorization: Bearer $TOKEN\" -H \"Content-Type: application/json\" -d '{\"format\":\"pptx\"}'"
echo "  查看健康状态: curl $BASE_URL/health"
echo ""
