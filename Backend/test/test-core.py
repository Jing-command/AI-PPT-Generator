#!/usr/bin/env python3
# 指定使用 Python 3 解释器运行此脚本
"""
AI PPT 核心功能测试（简化版）
用于测试项目的核心模块导入、Schema验证、加密服务等基础功能
"""

import sys  # 系统相关功能，用于路径操作和退出码
import os   # 操作系统接口，用于文件路径处理

# 添加项目根目录到 Python 路径
# __file__ 是当前脚本的路径
# os.path.abspath() 获取绝对路径
# os.path.dirname() 获取父目录，两次调用回到项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录插入到 sys.path 的开头，确保可以导入 app 模块
sys.path.insert(0, project_root)

def test_imports():
    """
    测试所有模块导入
    验证项目的所有核心模块是否能够正常导入，检查依赖关系是否完整
    """
    print("📦 测试模块导入...")
    
    # 定义需要测试的模块列表，格式：(显示名称, 模块路径)
    modules = [
        ('主应用', 'app.main'),                                      # FastAPI 主应用
        ('配置', 'app.config'),                                      # 应用配置
        ('数据库', 'app.database'),                                  # 数据库连接配置
        ('用户模型', 'app.models.user'),                             # 用户数据模型
        ('API Key模型', 'app.models.api_key'),                      # API密钥数据模型
        ('PPT模型', 'app.models.presentation'),                     # PPT演示文稿数据模型
        ('操作历史', 'app.models.operation_history'),               # 操作历史记录模型
        ('导出任务', 'app.models.export_task'),                     # 导出任务模型
        ('模板', 'app.models.template'),                            # PPT模板模型
        ('认证路由', 'app.routers.auth'),                           # 用户认证相关路由
        ('PPT路由', 'app.routers.ppt'),                             # PPT操作路由
        ('API Key路由', 'app.routers.api_keys'),                   # API密钥管理路由
        ('生成路由', 'app.routers.ppt_generation'),                # PPT生成路由
        ('导出路由', 'app.routers.export'),                         # 文件导出路由
        ('模板路由', 'app.routers.templates'),                      # 模板管理路由
        ('用户服务', 'app.services.user_service'),                  # 用户业务逻辑服务
        ('PPT服务', 'app.services.ppt_service'),                    # PPT业务逻辑服务
        ('API Key服务', 'app.services.api_key_service'),           # API密钥管理服务
        ('AI Provider', 'app.services.ai_provider'),               # AI提供商接口服务
        ('加密服务', 'app.services.encryption_service'),            # 数据加密服务
        ('导出服务', 'app.services.export_service'),                # 文件导出服务
        ('Celery任务', 'app.tasks'),                               # Celery异步任务入口
        ('导出任务', 'app.tasks.export_tasks'),                     # 导出相关异步任务
        ('生成任务', 'app.tasks.generation_tasks'),                 # 生成相关异步任务
    ]
    
    # 初始化计数器
    passed = 0  # 成功导入的模块数
    failed = 0  # 导入失败的模块数
    
    # 遍历所有模块进行导入测试
    for name, module in modules:
        try:
            # 动态导入模块，__import__() 是 Python 内置函数
            __import__(module)
            # 导入成功，打印成功标记
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            # 导入失败，打印错误信息（截取前50个字符）
            print(f"  ❌ {name}: {str(e)[:50]}")
            failed += 1
    
    # 返回成功和失败的数量
    return passed, failed


def test_schemas():
    """
    测试 Pydantic Schemas
    验证所有数据模型（Schema）是否能正确创建和验证数据
    Pydantic 用于数据验证和序列化
    """
    print("\n📋 测试 Pydantic Schemas...")
    
    # 导入用户相关的 Schema：创建用户、登录请求、JWT令牌
    from app.schemas.user import UserCreate, LoginRequest, Token
    # 导入演示文稿相关的 Schema
    from app.schemas.presentation import (
        GenerateRequest,          # 生成请求
        PresentationCreate,       # 创建演示文稿
        PresentationResponse,     # 演示文稿响应
        Slide,                    # 幻灯片
        SlideContent,             # 幻灯片内容
        ExportRequest             # 导出请求
    )
    # 导入 API 密钥相关的 Schema
    from app.schemas.api_key import APIKeyCreate, APIKeyResponse
    # 导入模板相关的 Schema
    from app.schemas.template import TemplateResponse
    
    # 存储所有测试结果的列表
    tests = []
    
    # 测试 1: UserCreate - 用户创建 Schema
    try:
        # 创建一个用户对象，包含邮箱、密码和姓名
        user = UserCreate(email="test@example.com", password="test123456", name="测试")
        # 断言：验证邮箱字段是否正确设置
        assert user.email == "test@example.com"
        # 测试通过，记录结果
        tests.append(("UserCreate", True))
    except Exception as e:
        # 测试失败，记录错误信息
        tests.append(("UserCreate", False, str(e)))
    
    # 测试 2: LoginRequest - 用户登录请求 Schema
    try:
        # 创建登录请求对象，包含邮箱和密码
        login = LoginRequest(email="test@example.com", password="test123456")
        # 验证邮箱字段
        assert login.email == "test@example.com"
        tests.append(("LoginRequest", True))
    except Exception as e:
        tests.append(("LoginRequest", False, str(e)))
    
    # 测试 3: Token - JWT令牌响应 Schema
    try:
        # 创建令牌对象，包含访问令牌、刷新令牌、令牌类型和过期时间
        token = Token(access_token="abc", refresh_token="def", token_type="bearer", expires_in=1800)
        # 验证令牌类型为 bearer
        assert token.token_type == "bearer"
        tests.append(("Token", True))
    except Exception as e:
        tests.append(("Token", False, str(e)))
    
    # 测试 4: GenerateRequest - PPT生成请求 Schema
    try:
        # 创建生成请求，包含提示词和幻灯片数量
        gen = GenerateRequest(prompt="这是一个测试用的提示词", num_slides=5)
        # 验证幻灯片数量
        assert gen.num_slides == 5
        tests.append(("GenerateRequest", True))
    except Exception as e:
        tests.append(("GenerateRequest", False, str(e)))
    
    # 测试 5: PresentationCreate - 创建演示文稿 Schema
    try:
        # 创建演示文稿对象，只需要标题
        ppt = PresentationCreate(title="测试PPT")
        # 验证标题字段
        assert ppt.title == "测试PPT"
        tests.append(("PresentationCreate", True))
    except Exception as e:
        tests.append(("PresentationCreate", False, str(e)))
    
    # 测试 6: Slide - 幻灯片 Schema（包含嵌套的 SlideContent）
    try:
        # 创建幻灯片，包含内容对象（SlideContent）
        slide = Slide(content=SlideContent(title="标题"))
        # 验证嵌套对象的标题字段
        assert slide.content.title == "标题"
        tests.append(("Slide", True))
    except Exception as e:
        tests.append(("Slide", False, str(e)))
    
    # 测试 7: APIKeyCreate - 创建API密钥 Schema
    try:
        # 创建API密钥对象，包含名称、密钥和提供商
        key = APIKeyCreate(name="测试", api_key="sk-test123456", provider="openai")
        # 验证提供商字段
        assert key.provider == "openai"
        tests.append(("APIKeyCreate", True))
    except Exception as e:
        tests.append(("APIKeyCreate", False, str(e)))
    
    # 测试 8: ExportRequest - 导出请求 Schema
    try:
        # 创建导出请求，指定导出格式为 pptx
        export = ExportRequest(format="pptx")
        # 验证格式字段
        assert export.format == "pptx"
        tests.append(("ExportRequest", True))
    except Exception as e:
        tests.append(("ExportRequest", False, str(e)))
    
    # 统计通过的测试数量（使用生成器表达式和 sum 函数）
    passed = sum(1 for t in tests if t[1])
    # 遍历所有测试结果并打印
    for name, ok, *args in tests:  # *args 用于捕获可能的错误信息
        # 根据测试结果选择图标
        status = "✅" if ok else "❌"
        print(f"  {status} {name}")
    
    # 返回通过数和失败数
    return passed, len(tests) - passed


def test_encryption():
    """
    测试加密服务
    验证 API 密钥的 AES-256 加密和解密功能是否正常工作
    """
    print("\n🔒 测试加密服务...")
    
    # 导入 API 密钥加密服务实例
    from app.services.encryption_service import api_key_encryption
    
    try:
        # 原始 API 密钥（模拟 OpenAI 的密钥格式）
        api_key = "sk-test123456789"
        # 加密：将明文密钥转换为密文
        encrypted = api_key_encryption.encrypt(api_key)
        # 解密：将密文还原为明文
        decrypted = api_key_encryption.decrypt(encrypted)
        
        # 断言 1：解密后的结果应该等于原始密钥
        assert api_key == decrypted, "加密/解密失败"
        # 断言 2：加密后的密文不应该等于原始密钥
        assert encrypted != api_key, "加密后应不同"
        # 测试通过
        print("  ✅ API Key 加密/解密正常")
        return 1, 0  # 1个通过，0个失败
    except Exception as e:
        # 测试失败，打印错误信息
        print(f"  ❌ 加密测试失败: {e}")
        return 0, 1  # 0个通过，1个失败


def test_ai_provider():
    """
    测试 AI Provider
    验证 AI 提供商工厂类是否能正确返回支持的提供商列表
    （如 OpenAI, Anthropic, Kimi, Aliyun, Tencent 等）
    """
    print("\n🤖 测试 AI Provider...")
    
    # 导入 AI 提供商工厂类
    from app.services.ai_provider import AIProviderFactory
    
    try:
        # 获取所有支持的 AI 提供商列表
        providers = AIProviderFactory.get_supported_providers()
        # 打印支持的提供商
        print(f"  ✅ 支持的提供商: {providers}")
        return 1, 0  # 测试通过
    except Exception as e:
        # 测试失败
        print(f"  ❌ AI Provider 测试失败: {e}")
        return 0, 1


def test_celery():
    """
    测试 Celery 配置
    验证 Celery 异步任务队列是否配置正确，所有任务函数是否能正常导入
    Celery 用于处理耗时的后台任务，如导出和生成任务
    """
    print("\n📬 测试 Celery 配置...")
    
    try:
        # 导入 Celery 应用实例
        from app.tasks import celery_app
        # 导入导出相关的异步任务
        from app.tasks.export_tasks import process_export_task, cleanup_old_exports
        # 导入生成相关的异步任务
        from app.tasks.generation_tasks import process_generation_task, cleanup_stalled_tasks
        
        # 所有导入成功，打印各个任务
        print("  ✅ Celery 应用导入正常")
        print(f"  ✅ 任务: process_export_task")         # 处理导出任务
        print(f"  ✅ 任务: process_generation_task")     # 处理生成任务
        print(f"  ✅ 任务: cleanup_old_exports")         # 清理旧的导出文件
        print(f"  ✅ 任务: cleanup_stalled_tasks")       # 清理停滞的任务
        return 4, 0  # 4个任务全部通过
    except Exception as e:
        # 导入失败
        print(f"  ❌ Celery 测试失败: {e}")
        return 0, 4  # 4个任务全部失败


def main():
    """
    主函数：执行所有测试并汇总结果
    返回值：0 表示所有测试通过，1 表示有测试失败
    """
    # 打印测试标题
    print("=" * 60)
    print("🧪 AI PPT Backend 核心功能测试")
    print("=" * 60)
    
    # 初始化总计数器
    total_passed = 0  # 总通过数
    total_failed = 0  # 总失败数
    
    # 测试 1: 模块导入测试
    # 验证所有核心模块是否能正常导入
    p, f = test_imports()
    total_passed += p  # 累加通过数
    total_failed += f  # 累加失败数
    
    # 测试 2: Schema 测试
    # 验证 Pydantic 数据模型是否正常工作
    p, f = test_schemas()
    total_passed += p
    total_failed += f
    
    # 测试 3: 加密测试
    # 验证 API 密钥加密/解密功能
    p, f = test_encryption()
    total_passed += p
    total_failed += f
    
    # 测试 4: AI Provider 测试
    # 验证 AI 提供商工厂类
    p, f = test_ai_provider()
    total_passed += p
    total_failed += f
    
    # 测试 5: Celery 测试
    # 验证异步任务配置
    p, f = test_celery()
    total_passed += p
    total_failed += f
    
    # 打印测试结果汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    print(f"  ✅ 通过: {total_passed}")
    print(f"  ❌ 失败: {total_failed}")
    # 计算成功率（通过数除以总数，乘以100，保留1位小数）
    print(f"  📈 成功率: {total_passed/(total_passed+total_failed)*100:.1f}%")
    print("=" * 60)
    
    # 根据测试结果给出不同的提示
    if total_failed == 0:
        # 所有测试通过
        print("\n🎉 所有测试通过！代码结构完整。")
        print("\n注意: 完整功能测试需要启动 PostgreSQL + Redis 服务")
        print("      运行: cd docker && docker-compose up -d")
        return 0  # 返回退出码 0 表示成功
    else:
        # 有测试失败
        print(f"\n⚠️  {total_failed} 个测试失败，请检查代码。")
        return 1  # 返回退出码 1 表示失败


# Python 脚本入口点
# 当直接运行此脚本时（不是被导入时），执行 main() 函数
if __name__ == "__main__":
    # sys.exit() 用于设置进程退出码
    # 退出码 0 表示成功，非0表示失败
    sys.exit(main())
