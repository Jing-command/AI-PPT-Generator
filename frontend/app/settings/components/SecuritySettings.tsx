"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { 
  Lock, 
  Eye, 
  EyeOff, 
  Save, 
  Loader2, 
  CheckCircle2,
  AlertCircle,
  Shield
} from "lucide-react";
import { userAPI } from "@/lib/api";

export default function SecuritySettings() {
  const [formData, setFormData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [showPassword, setShowPassword] = useState({
    current: false,
    new: false,
    confirm: false,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSave = async () => {
    setMessage(null);
    
    // 验证
    if (formData.new_password !== formData.confirm_password) {
      setMessage({ type: 'error', text: '两次输入的新密码不一致' });
      return;
    }
    
    if (formData.new_password.length < 8) {
      setMessage({ type: 'error', text: '新密码至少需要 8 位' });
      return;
    }
    
    setIsSaving(true);
    
    try {
      await userAPI.updatePassword({
        current_password: formData.current_password,
        new_password: formData.new_password,
      });
      
      setMessage({ type: 'success', text: '密码修改成功' });
      setFormData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
    } catch (err: any) {
      setMessage({ 
        type: 'error', 
        text: err.message || '当前密码错误'
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="text-xl font-semibold">安全设置</h2>
          <p className="text-sm text-white/60">修改密码保护账户安全</p>
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

      {/* 密码表单 */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">当前密码</label>
          <div className="relative">
            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type={showPassword.current ? "text" : "password"}
              value={formData.current_password}
              onChange={(e) => setFormData({ ...formData, current_password: e.target.value })}
              placeholder="输入当前密码"
              className="w-full px-4 py-3 pl-11 pr-11 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40"
            />
            <button
              type="button"
              onClick={() => setShowPassword({ ...showPassword, current: !showPassword.current })}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 p-1 hover:bg-white/10 rounded transition-colors"
            >
              {showPassword.current ? (
                <EyeOff className="w-4 h-4 text-white/40" />
              ) : (
                <Eye className="w-4 h-4 text-white/40" />
              )}
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">新密码</label>
          <div className="relative">
            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type={showPassword.new ? "text" : "password"}
              value={formData.new_password}
              onChange={(e) => setFormData({ ...formData, new_password: e.target.value })}
              placeholder="至少 8 位字符"
              className="w-full px-4 py-3 pl-11 pr-11 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40"
            />
            <button
              type="button"
              onClick={() => setShowPassword({ ...showPassword, new: !showPassword.new })}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 p-1 hover:bg-white/10 rounded transition-colors"
            >
              {showPassword.new ? (
                <EyeOff className="w-4 h-4 text-white/40" />
              ) : (
                <Eye className="w-4 h-4 text-white/40" />
              )}
            </button>
          </div>
          
          <div className="mt-2 flex gap-2">
            {['弱', '中', '强'].map((level, i) => (
              <div
                key={level}
                className={`flex-1 h-1 rounded-full ${
                  formData.new_password.length >= (i + 1) * 3
                    ? formData.new_password.length >= 12
                      ? 'bg-green-500'
                      : formData.new_password.length >= 8
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                    : 'bg-white/10'
                }`}
              />
            ))}
          </div>
          <p className="text-xs text-white/40 mt-1">密码强度: {
            formData.new_password.length >= 12 ? '强' : 
            formData.new_password.length >= 8 ? '中' : '弱'
          }</p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">确认新密码</label>
          <div className="relative">
            <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type={showPassword.confirm ? "text" : "password"}
              value={formData.confirm_password}
              onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
              placeholder="再次输入新密码"
              className="w-full px-4 py-3 pl-11 pr-11 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40"
            />
            <button
              type="button"
              onClick={() => setShowPassword({ ...showPassword, confirm: !showPassword.confirm })}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 p-1 hover:bg-white/10 rounded transition-colors"
            >
              {showPassword.confirm ? (
                <EyeOff className="w-4 h-4 text-white/40" />
              ) : (
                <Eye className="w-4 h-4 text-white/40" />
              )}
            </button>
          </div>
          
          {formData.confirm_password && formData.new_password !== formData.confirm_password && (
            <p className="text-xs text-red-400 mt-1">两次输入的密码不一致</p>
          )}
        </div>

        <div className="pt-4">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleSave}
            disabled={isSaving || !formData.current_password || !formData.new_password || !formData.confirm_password}
            className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3 bg-white text-purple-600 rounded-xl font-medium disabled:opacity-50"
          >
            {isSaving ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                修改中...
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                修改密码
              </>
            )}
          </motion.button>
        </div>
      </div>

      {/* 安全提示 */}
      <div className="mt-8 p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/20">
        <h4 className="text-sm font-medium text-yellow-300 mb-2">安全建议</h4>
        <ul className="text-sm text-white/60 space-y-1 list-disc list-inside">
          <li>使用至少 8 位字符的密码</li>
          <li>包含大小写字母、数字和特殊符号</li>
          <li>避免使用与其他网站相同的密码</li>
          <li>定期更换密码提高安全性</li>
        </ul>
      </div>
    </div>
  );
}
