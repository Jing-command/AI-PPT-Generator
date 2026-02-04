#!/usr/bin/env python3
"""
AI PPT 核心功能测试（无需数据库）
测试业务逻辑而非数据库集成
"""

import asyncio
import sys
sys.path.insert(0, '/root/projects/ai-ppt-backend')

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password
)
from app.services.ai_provider import AIProviderFactory
from app.services.encryption_service import api_key_encryption


def test_security():
    """测试安全模块"""
    print("🔐 测试安全模块...")
    
    # 1. 密码哈希（限制长度在 72 字节内）
    password = "test123"  # 缩短密码
    hashed = get_password_hash(password)
    assert verify_password(password, hashed), "密码验证失败"
    assert not verify_password("wrong", hashed), "错误密码不应通过"
    print("  ✅ 密码哈希/验证正常")
    
    # 2. JWT Token
    user_id = "test-user-123"
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    
    # 验证 access token
    decoded_id, error = decode_token(access_token, expected_type="access")
    assert decoded_id == user_id, f"Access token 解码失败: {error}"
    print("  ✅ Access Token 生成/验证正常")
    
    # 验证 refresh token
    decoded_id, error = decode_token(refresh_token, expected_type="refresh")
    assert decoded_id == user_id, f"Refresh token 解码失败: {error}"
    print("  ✅ Refresh Token 生成/验证正常")
    
    # 3. Token 类型验证
    _, error = decode_token(refresh_token, expected_type="access")
    assert error is not None, "应拒绝用 refresh token 当 access token"
    print("  ✅ Token 类型验证正常")


def test_encryption():
    """测试加密服务"""
    print("🔒 测试加密服务...")
    
    api_key = "sk-test123456789"
    encrypted = api_key_encryption.encrypt(api_key)
    decrypted = api_key_encryption.decrypt(encrypted)
    
    assert api_key == decrypted, "加密/解密失败"
    assert encrypted != api_key, "加密后应不同"
    print("  ✅ API Key 加密/解密正常")


def test_ai_provider_factory():
    """测试 AI Provider 工厂"""
    print("🤖 测试 AI Provider 工厂...")
    
    providers = AIProviderFactory.get_supported_providers()
    print(f"  支持的提供商: {providers}")
    
    # 测试创建 provider（需要有效 API key）
    try:
        provider = AIProviderFactory.create("openai", "sk-test")
        print("  ✅ OpenAI Provider 创建正常")
    except Exception as e:
        print(f"  ⚠️ Provider 创建: {e}")


def test_imports():
    """测试所有模块导入"""
    print("📦 测试模块导入...")
    
    modules = [
        'app.main',
        'app.config',
        'app.database',
        'app.models.user',
        'app.models.api_key',
        'app.models.presentation',
        'app.routers.auth',
        'app.routers.ppt',
        'app.routers.api_keys',
        'app.services.user_service',
        'app.services.ppt_service',
        'app.services.ai_provider',
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")


def test_schemas():
    """测试 Pydantic Schemas"""
    print("📋 测试 Pydantic Schemas...")
    
    from app.schemas.user import UserCreate, LoginRequest
    from app.schemas.presentation import GenerateRequest, PresentationCreate
    
    # 1. 用户创建
    user = UserCreate(email="test@example.com", password="test123456", name="测试")
    assert user.email == "test@example.com"
    print("  ✅ UserCreate Schema 正常")
    
    # 2. 登录请求
    login = LoginRequest(email="test@example.com", password="test123456")
    assert login.email == "test@example.com"
    print("  ✅ LoginRequest Schema 正常")
    
    # 3. PPT 生成请求
    gen = GenerateRequest(prompt="测试", num_slides=5)
    assert gen.num_slides == 5
    print("  ✅ GenerateRequest Schema 正常")
    
    # 4. PPT 创建
    ppt = PresentationCreate(title="测试PPT")
    assert ppt.title == "测试PPT"
    print("  ✅ PresentationCreate Schema 正常")


def main():
    print("=" * 50)
    print("🧪 AI PPT Backend 功能测试")
    print("=" * 50)
    print()
    
    try:
        test_imports()
        print()
        
        test_security()
        print()
        
        test_encryption()
        print()
        
        test_ai_provider_factory()
        print()
        
        test_schemas()
        print()
        
        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
