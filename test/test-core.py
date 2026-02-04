#!/usr/bin/env python3
"""
AI PPT 核心功能测试（简化版）
"""

import sys
sys.path.insert(0, '/root/projects/ai-ppt-backend')

def test_imports():
    """测试所有模块导入"""
    print("📦 测试模块导入...")
    
    modules = [
        ('主应用', 'app.main'),
        ('配置', 'app.config'),
        ('数据库', 'app.database'),
        ('用户模型', 'app.models.user'),
        ('API Key模型', 'app.models.api_key'),
        ('PPT模型', 'app.models.presentation'),
        ('操作历史', 'app.models.operation_history'),
        ('导出任务', 'app.models.export_task'),
        ('模板', 'app.models.template'),
        ('认证路由', 'app.routers.auth'),
        ('PPT路由', 'app.routers.ppt'),
        ('API Key路由', 'app.routers.api_keys'),
        ('生成路由', 'app.routers.ppt_generation'),
        ('导出路由', 'app.routers.export'),
        ('模板路由', 'app.routers.templates'),
        ('用户服务', 'app.services.user_service'),
        ('PPT服务', 'app.services.ppt_service'),
        ('API Key服务', 'app.services.api_key_service'),
        ('AI Provider', 'app.services.ai_provider'),
        ('加密服务', 'app.services.encryption_service'),
        ('导出服务', 'app.services.export_service'),
        ('Celery任务', 'app.tasks'),
        ('导出任务', 'app.tasks.export_tasks'),
        ('生成任务', 'app.tasks.generation_tasks'),
    ]
    
    passed = 0
    failed = 0
    
    for name, module in modules:
        try:
            __import__(module)
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:50]}")
            failed += 1
    
    return passed, failed


def test_schemas():
    """测试 Pydantic Schemas"""
    print("\n📋 测试 Pydantic Schemas...")
    
    from app.schemas.user import UserCreate, LoginRequest, Token
    from app.schemas.presentation import (
        GenerateRequest, PresentationCreate, PresentationResponse,
        Slide, SlideContent, ExportRequest
    )
    from app.schemas.api_key import APIKeyCreate, APIKeyResponse
    from app.schemas.template import TemplateResponse
    
    tests = []
    
    # 1. UserCreate
    try:
        user = UserCreate(email="test@example.com", password="test123456", name="测试")
        assert user.email == "test@example.com"
        tests.append(("UserCreate", True))
    except Exception as e:
        tests.append(("UserCreate", False, str(e)))
    
    # 2. LoginRequest
    try:
        login = LoginRequest(email="test@example.com", password="test123456")
        assert login.email == "test@example.com"
        tests.append(("LoginRequest", True))
    except Exception as e:
        tests.append(("LoginRequest", False, str(e)))
    
    # 3. Token
    try:
        token = Token(access_token="abc", refresh_token="def", token_type="bearer", expires_in=1800)
        assert token.token_type == "bearer"
        tests.append(("Token", True))
    except Exception as e:
        tests.append(("Token", False, str(e)))
    
    # 4. GenerateRequest
    try:
        gen = GenerateRequest(prompt="这是一个测试用的提示词", num_slides=5)
        assert gen.num_slides == 5
        tests.append(("GenerateRequest", True))
    except Exception as e:
        tests.append(("GenerateRequest", False, str(e)))
    
    # 5. PresentationCreate
    try:
        ppt = PresentationCreate(title="测试PPT")
        assert ppt.title == "测试PPT"
        tests.append(("PresentationCreate", True))
    except Exception as e:
        tests.append(("PresentationCreate", False, str(e)))
    
    # 6. Slide
    try:
        slide = Slide(content=SlideContent(title="标题"))
        assert slide.content.title == "标题"
        tests.append(("Slide", True))
    except Exception as e:
        tests.append(("Slide", False, str(e)))
    
    # 7. APIKeyCreate
    try:
        key = APIKeyCreate(name="测试", api_key="sk-test123456", provider="openai")
        assert key.provider == "openai"
        tests.append(("APIKeyCreate", True))
    except Exception as e:
        tests.append(("APIKeyCreate", False, str(e)))
    
    # 8. ExportRequest
    try:
        export = ExportRequest(format="pptx")
        assert export.format == "pptx"
        tests.append(("ExportRequest", True))
    except Exception as e:
        tests.append(("ExportRequest", False, str(e)))
    
    passed = sum(1 for t in tests if t[1])
    for name, ok, *args in tests:
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
    
    return passed, len(tests) - passed


def test_encryption():
    """测试加密服务"""
    print("\n🔒 测试加密服务...")
    
    from app.services.encryption_service import api_key_encryption
    
    try:
        api_key = "sk-test123456789"
        encrypted = api_key_encryption.encrypt(api_key)
        decrypted = api_key_encryption.decrypt(encrypted)
        
        assert api_key == decrypted, "加密/解密失败"
        assert encrypted != api_key, "加密后应不同"
        print("  ✅ API Key 加密/解密正常")
        return 1, 0
    except Exception as e:
        print(f"  ❌ 加密测试失败: {e}")
        return 0, 1


def test_ai_provider():
    """测试 AI Provider"""
    print("\n🤖 测试 AI Provider...")
    
    from app.services.ai_provider import AIProviderFactory
    
    try:
        providers = AIProviderFactory.get_supported_providers()
        print(f"  ✅ 支持的提供商: {providers}")
        return 1, 0
    except Exception as e:
        print(f"  ❌ AI Provider 测试失败: {e}")
        return 0, 1


def test_celery():
    """测试 Celery 配置"""
    print("\n📬 测试 Celery 配置...")
    
    try:
        from app.tasks import celery_app
        from app.tasks.export_tasks import process_export_task, cleanup_old_exports
        from app.tasks.generation_tasks import process_generation_task, cleanup_stalled_tasks
        
        print("  ✅ Celery 应用导入正常")
        print(f"  ✅ 任务: process_export_task")
        print(f"  ✅ 任务: process_generation_task")
        print(f"  ✅ 任务: cleanup_old_exports")
        print(f"  ✅ 任务: cleanup_stalled_tasks")
        return 4, 0
    except Exception as e:
        print(f"  ❌ Celery 测试失败: {e}")
        return 0, 4


def main():
    print("=" * 60)
    print("🧪 AI PPT Backend 核心功能测试")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    
    # 1. 模块导入测试
    p, f = test_imports()
    total_passed += p
    total_failed += f
    
    # 2. Schema 测试
    p, f = test_schemas()
    total_passed += p
    total_failed += f
    
    # 3. 加密测试
    p, f = test_encryption()
    total_passed += p
    total_failed += f
    
    # 4. AI Provider 测试
    p, f = test_ai_provider()
    total_passed += p
    total_failed += f
    
    # 5. Celery 测试
    p, f = test_celery()
    total_passed += p
    total_failed += f
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    print(f"  ✅ 通过: {total_passed}")
    print(f"  ❌ 失败: {total_failed}")
    print(f"  📈 成功率: {total_passed/(total_passed+total_failed)*100:.1f}%")
    print("=" * 60)
    
    if total_failed == 0:
        print("\n🎉 所有测试通过！代码结构完整。")
        print("\n注意: 完整功能测试需要启动 PostgreSQL + Redis 服务")
        print("      运行: cd docker && docker-compose up -d")
        return 0
    else:
        print(f"\n⚠️  {total_failed} 个测试失败，请检查代码。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
