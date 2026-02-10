"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, User, LayoutDashboard, Sparkles, LogOut, Settings, Key, ChevronDown } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();

  // 点击外部关闭下拉菜单
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const isHomePage = pathname === "/";

  const navItems = isHomePage ? [
    { name: "功能", href: "#features" },
    { name: "模板", href: "#templates" },
  ] : [];

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50 px-4 sm:px-6 lg:px-8 py-4"
    >
      <div className="max-w-6xl mx-auto">
        <div className="glass rounded-2xl px-6 py-3 flex items-center justify-between"
        >
          {/* Logo */}
          <Link href="/">
            <motion.div
              whileHover={{ scale: 1.05 }}
              className="font-display text-xl font-bold text-gradient"
            >
              AI Slides
            </motion.div>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-6">
            {navItems.map((item) => (
              <motion.a
                key={item.name}
                href={item.href}
                whileHover={{ y: -2 }}
                className="text-sm text-white/80 hover:text-white transition-colors"
              >
                {item.name}
              </motion.a>
            ))}

            {isAuthenticated ? (
              <>
                <Link 
                  href="/generate"
                  className="flex items-center gap-1.5 text-sm text-white/80 hover:text-white transition-colors"
                >
                  <Sparkles className="w-4 h-4" />
                  AI 生成
                </Link>
                <Link 
                  href="/dashboard"
                  className="flex items-center gap-1.5 text-sm text-white/80 hover:text-white transition-colors"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  我的 PPT
                </Link>
                {/* 用户下拉菜单 */}
                <div className="relative ml-2 pl-4 border-l border-white/20" ref={userMenuRef}>
                  <button
                    onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                    className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-white/10 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-sm text-white/80 max-w-[100px] truncate">
                      {user?.username || user?.email?.split('@')[0]}
                    </span>
                    <ChevronDown className={`w-4 h-4 text-white/60 transition-transform ${isUserMenuOpen ? 'rotate-180' : ''}`} />
                  </button>

                  {/* 下拉菜单 */}
                  <AnimatePresence>
                    {isUserMenuOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: -8, scale: 0.96 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -8, scale: 0.96 }}
                        transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                        className="absolute right-0 top-full mt-3 w-56 rounded-2xl overflow-hidden shadow-2xl shadow-purple-900/30 border border-white/20"
                        style={{
                          background: 'rgba(255, 255, 255, 0.75)',
                          backdropFilter: 'blur(24px) saturate(180%)',
                          WebkitBackdropFilter: 'blur(24px) saturate(180%)',
                        }}
                      >
                        {/* 用户信息头部 */}
                        <div className="relative px-4 py-4 bg-gradient-to-br from-purple-500/20 to-pink-500/20 border-b border-white/20">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center shadow-lg">
                              <User className="w-5 h-5 text-white" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-semibold text-gray-900 truncate">{user?.username || user?.email?.split('@')[0]}</p>
                              <p className="text-xs text-gray-600 truncate">{user?.email}</p>
                            </div>
                          </div>
                        </div>

                        {/* 菜单项 */}
                        <div className="p-2 space-y-1">
                          <Link 
                            href="/settings"
                            onClick={() => setIsUserMenuOpen(false)}
                            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-white/60 hover:text-purple-600 transition-all duration-200 group"
                          >
                            <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center group-hover:bg-purple-200 transition-colors">
                              <Settings className="w-4 h-4 text-purple-600" />
                            </div>
                            <span className="font-medium">账号设置</span>
                          </Link>

                          <Link 
                            href="/settings"
                            onClick={() => setIsUserMenuOpen(false)}
                            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-gray-700 hover:bg-white/60 hover:text-purple-600 transition-all duration-200 group"
                          >
                            <div className="w-8 h-8 rounded-lg bg-pink-100 flex items-center justify-center group-hover:bg-pink-200 transition-colors">
                              <Key className="w-4 h-4 text-pink-600" />
                            </div>
                            <span className="font-medium">修改密码</span>
                          </Link>
                        </div>

                        {/* 分隔线和退出 */}
                        <div className="border-t border-gray-200/50 p-2">
                          <button
                            onClick={() => {
                              logout();
                              setIsUserMenuOpen(false);
                            }}
                            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-red-600 hover:bg-red-50 transition-all duration-200 w-full group"
                          >
                            <div className="w-8 h-8 rounded-lg bg-red-100 flex items-center justify-center group-hover:bg-red-200 transition-colors">
                              <LogOut className="w-4 h-4 text-red-600" />
                            </div>
                            <span className="font-medium">退出登录</span>
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </>
            ) : (
              <Link href="/login">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.98 }}
                  className="bg-white/10 hover:bg-white/20 text-white px-5 py-2 rounded-full text-sm font-medium transition-colors"
                >
                  登录
                </motion.button>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 text-white/80"
          >
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden mt-2 glass rounded-2xl p-4"
          >
            <div className="flex flex-col gap-3"
            >
              {navItems.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  className="text-white/80 hover:text-white py-2 transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  {item.name}
                </a>
              ))}

              {isAuthenticated ? (
                <>
                  <Link
                    href="/generate"
                    className="flex items-center gap-2 text-white/80 hover:text-white py-2"
                    onClick={() => setIsOpen(false)}
                  >
                    <Sparkles className="w-4 h-4" />
                    AI 生成
                  </Link>
                  <Link
                    href="/dashboard"
                    className="flex items-center gap-2 text-white/80 hover:text-white py-2"
                    onClick={() => setIsOpen(false)}
                  >
                    <LayoutDashboard className="w-4 h-4" />
                    我的 PPT
                  </Link>
                  <div className="border-t border-white/10 my-2 pt-2">
                    <div className="px-2 py-1 text-xs text-white/50 mb-1">账号</div>
                    <Link
                      href="/settings"
                      className="flex items-center gap-2 text-white/80 hover:text-white py-2"
                      onClick={() => setIsOpen(false)}
                    >
                      <Settings className="w-4 h-4" />
                      账号设置
                    </Link>
                    <Link
                      href="/settings"
                      className="flex items-center gap-2 text-white/80 hover:text-white py-2"
                      onClick={() => setIsOpen(false)}
                    >
                      <Key className="w-4 h-4" />
                      修改密码
                    </Link>
                    <button
                      onClick={() => {
                        logout();
                        setIsOpen(false);
                      }}
                      className="flex items-center gap-2 text-red-300 py-2"
                    >
                      <LogOut className="w-4 h-4" />
                      退出登录
                    </button>
                  </div>
                </>
              ) : (
                <Link
                  href="/login"
                  onClick={() => setIsOpen(false)}
                >
                  <button className="w-full bg-white/10 text-white py-3 rounded-xl mt-2 font-medium">
                    登录
                  </button>
                </Link>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  );
}
