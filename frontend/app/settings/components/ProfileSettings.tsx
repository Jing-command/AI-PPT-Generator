"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { 
  User, 
  Mail, 
  Save, 
  Loader2, 
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { userAPI } from "@/lib/api";

interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
}

export default function ProfileSettings() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  const [formData, setFormData] = useState({
    name: "",
    email: "",
  });

  // 加载用户信息
  useEffect(() => {
    const loadUser = async () => {
      try {
        const data = await userAPI.getMe();
        setUser(data);
        setFormData({
          name: data.name || "",
          email: data.email || "",
        });
      } catch (err) {
        console.error("加载用户信息失败:", err);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadUser();
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    setMessage(null);
    
    try {
      const updateData: { name?: string; email?: string } = {};
      
      if (formData.name !== user?.name) {
        updateData.name = formData.name;
      }
      if (formData.email !== user?.email) {
        updateData.email = formData.email;
      }
      
      if (Object.keys(updateData).length === 0) {
        setMessage({ type: 'success', text: '没有需要保存的更改' });
        setIsSaving(false);
        return;
      }
      
      const updated = await userAPI.updateMe(updateData);
      setUser(updated);
      setMessage({ type: 'success', text: '个人信息已更新' });
    } catch (err: any) {
      setMessage({ 
        type: 'error', 
        text: err.message || '更新失败，请检查邮箱是否已被使用'
      });
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-white/50" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
          <User className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">个人资料</h2>
          <p className="text-sm text-white/60">管理你的基本信息</p>
        </div>
      </div>

      {/* 提示消息 */}
      {message && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-4 rounded-xl flex items-center gap-2 ${
            message.type === 'success' 
              ? 'bg-green-500/20 border border-green-500/30 text-green-200' 
              : 'bg-red-500/20 border border-red-500/30 text-red-200'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          {message.text}
        </motion.div>
      )}

      {/* 表单 */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">用户名</label>
          <div className="relative">
            <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="你的昵称"
              className="w-full px-4 py-3 pl-11 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">邮箱</label>
          <div className="relative">
            <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="your@email.com"
              className="w-full px-4 py-3 pl-11 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40"
            />
          </div>
          <p className="text-xs text-white/40 mt-1">邮箱用于登录和接收通知</p>
        </div>

        <div className="pt-4">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3 bg-white text-purple-600 rounded-xl font-medium disabled:opacity-50"
          >
            {isSaving ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                保存中...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                保存更改
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* 账户信息 */}
      {user && (
        <div className="mt-8 pt-8 border-t border-white/10">
          <h3 className="text-sm font-medium text-white/60 mb-4">账户信息</h3>
          <div className="space-y-2 text-sm">
            <p className="text-white/50">
              注册时间: {new Date(user.created_at).toLocaleDateString('zh-CN')}
            </p>
            <p className="text-white/50">
              用户 ID: {user.id}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
