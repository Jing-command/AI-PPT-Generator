import { Outlet, Link, useLocation } from 'react-router-dom'
import { FileText, LayoutTemplate, Settings, LogOut, User } from 'lucide-react'
import { useEffect } from 'react'
import { useAuthStore } from '@/stores'

export default function Layout() {
  const location = useLocation()
  const { user, logout, fetchCurrentUser } = useAuthStore()

  // 组件挂载时获取当前用户信息
  useEffect(() => {
    fetchCurrentUser()
  }, [fetchCurrentUser])

  const navigation = [
    { name: '我的PPT', href: '/', icon: FileText },
    { name: '模板', href: '/templates', icon: LayoutTemplate },
    { name: '设置', href: '/settings', icon: Settings },
  ]

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 侧边栏 */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <span className="font-semibold text-gray-900">AI PPT</span>
          </Link>
        </div>

        {/* 导航 */}
        <nav className="flex-1 px-4 py-4 space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${isActive 
                    ? 'bg-primary-50 text-primary-700' 
                    : 'text-gray-700 hover:bg-gray-100'}
                `}
              >
                <Icon className="w-5 h-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* 用户信息 */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-gray-500" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.name || user?.email}
              </p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>
          </div>
          
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            退出登录
          </button>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
