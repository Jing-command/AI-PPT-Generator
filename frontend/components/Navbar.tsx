"use client";

import { motion } from "framer-motion";
import { Menu, X, User, LayoutDashboard, Sparkles, LogOut } from "lucide-react";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();

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
                <div className="flex items-center gap-3 ml-2 pl-4 border-l border-white/20">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                      <User className="w-4 h-4" />
                    </div>
                    <span className="text-sm text-white/80">{user?.username || user?.email}</span>
                  </div>
                  <button
                    onClick={logout}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    title="退出"
                  >
                    <LogOut className="w-4 h-4 text-white/60" />
                  </button>
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
                  <button
                    onClick={() => {
                      logout();
                      setIsOpen(false);
                    }}
                    className="flex items-center gap-2 text-white/80 hover:text-white py-2"
                  >
                    <LogOut className="w-4 h-4" />
                    退出登录
                  </button>
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
