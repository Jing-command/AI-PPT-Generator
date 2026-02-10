"use client";

import { motion } from "framer-motion";
import { Key, User, Bell, Shield } from "lucide-react";
import { useState } from "react";
import FloatingShapes from "@/components/FloatingShapes";
import Navbar from "@/components/Navbar";
import { useAuthGuard } from "@/components/AuthGuard";
import APIKeySettings from "./components/APIKeySettings";
import ProfileSettings from "./components/ProfileSettings";
import SecuritySettings from "./components/SecuritySettings";

const TABS = [
  { id: "api-keys", name: "API Keys", icon: Key },
  { id: "profile", name: "个人资料", icon: User },
  { id: "notifications", name: "通知", icon: Bell },
  { id: "security", name: "安全", icon: Shield },
];

export default function SettingsPage() {
  const { isLoading: authLoading } = useAuthGuard(true);
  const [activeTab, setActiveTab] = useState("api-keys");

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* 背景 */}
      <div 
        className="fixed inset-0 animate-gradient"
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #8b5cf6 50%, #ec4899 75%, #f43f5e 100%)',
          backgroundSize: '400% 400%',
        }}
      />
      <div className="fixed inset-0 bg-gradient-to-b from-transparent via-transparent to-black/20" />
      <FloatingShapes />

      <div className="relative z-10">
        <Navbar />

        <div className="pt-24 pb-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <h1 className="text-3xl font-bold text-gradient">设置</h1>
              <p className="text-white/70 mt-1">管理你的账户和偏好设置</p>
            </motion.div>

            <div className="flex flex-col lg:flex-row gap-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="lg:w-64 flex-shrink-0"
              >
                <div className="glass rounded-2xl p-2 space-y-1">
                  {TABS.map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl ${
                          activeTab === tab.id
                            ? 'bg-white/20 text-white'
                            : 'text-white/70 hover:bg-white/10 hover:text-white'
                        }`}
                      >
                        <Icon className="w-5 h-5" />
                        <span className="font-medium">{tab.name}</span>
                      </button>
                    );
                  })}
                </div>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="flex-1"
              >
                <div className="glass rounded-2xl p-6">
                  {activeTab === "api-keys" && <APIKeySettings />}
                  {activeTab === "profile" && <ProfileSettings />}
                  {activeTab === "notifications" && (
                    <div className="text-center py-12 text-white/60">
                      通知设置即将推出...
                    </div>
                  )}
                  {activeTab === "security" && <SecuritySettings />}
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
