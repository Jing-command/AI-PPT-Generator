"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Key, 
  Plus, 
  Trash2, 
  Check, 
  X, 
  Loader2, 
  Shield,
  AlertCircle,
  Eye,
  EyeOff,
  RefreshCw,
  CheckCircle2,
  XCircle
} from "lucide-react";
import { useAPIKeys } from "@/hooks/useAPIKeys";

const PROVIDERS = [
  { id: "openai", name: "OpenAI", icon: "🤖" },
  { id: "moonshot", name: "Moonshot (Kimi)", icon: "🌙" },
  { id: "anthropic", name: "Anthropic (Claude)", icon: "🧠" },
  { id: "gemini", name: "Google Gemini", icon: "✨" },
  { id: "qwen", name: "通义千问", icon: "🌟" },
  { id: "ernie", name: "文心一言", icon: "📚" },
  { id: "deepseek", name: "DeepSeek", icon: "🔮" },
  { id: "yunwu", name: "云屋 AI (yunwu.ai)", icon: "☁️" },
  { id: "yunwu-image", name: "云屋 AI - 图片生成专用", icon: "🖼️" },
];

export default function APIKeySettings() {
  const { 
    apiKeys, 
    isLoading, 
    error, 
    createAPIKey, 
    updateAPIKey, 
    deleteAPIKey,
    verifyAPIKey 
  } = useAPIKeys();
  
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [verifyingId, setVerifyingId] = useState<string | null>(null);
  const [showKeyId, setShowKeyId] = useState<string | null>(null);
  
  // 表单状态
  const [formData, setFormData] = useState({
    name: "",
    provider: "openai",
    api_key: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError("");
    
    if (!formData.name.trim() || !formData.api_key.trim()) {
      setFormError("请填写所有必填项");
      return;
    }
    
    setIsSubmitting(true);
    try {
      await createAPIKey(formData);
      setShowAddForm(false);
      setFormData({ name: "", provider: "openai", api_key: "" });
    } catch (err: any) {
      setFormError(err.message || "添加失败");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggleActive = async (keyId: string, currentStatus: boolean) => {
    try {
      await updateAPIKey(keyId, { is_active: !currentStatus });
    } catch (err) {
      console.error("更新失败:", err);
    }
  };

  const handleSetDefault = async (keyId: string) => {
    try {
      await updateAPIKey(keyId, { is_default: true });
    } catch (err) {
      console.error("设置默认失败:", err);
    }
  };

  const handleVerify = async (keyId: string) => {
    setVerifyingId(keyId);
    try {
      await verifyAPIKey(keyId);
    } catch (err) {
      console.error("验证失败:", err);
    } finally {
      setTimeout(() => setVerifyingId(null), 2000);
    }
  };

  const handleDelete = async (keyId: string) => {
    if (!confirm("确定要删除这个 API Key 吗？")) return;
    try {
      await deleteAPIKey(keyId);
    } catch (err) {
      console.error("删除失败:", err);
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
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
            <Key className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-semibold">API Key 管理</h2>
            <p className="text-sm text-white/60">管理你的 AI 提供商 API Keys</p>
          </div>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowAddForm(true)}
          className="flex items-center gap-2 bg-white text-purple-600 px-4 py-2 rounded-full font-medium text-sm"
        >
          <Plus className="w-4 h-4" />
          添加 Key
        </motion.button>
      </div>

      {/* 提示信息 */}
      <div className="glass rounded-xl p-4 flex items-start gap-3">
        <Shield className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
        <div className="text-sm text-white/70">
          <p className="mb-1"><strong className="text-white">安全提示：</strong></p>
          <p>• API Keys 使用 AES-256 加密存储</p>
          <p>• 只有你能查看自己的 Keys</p>
          <p>• 建议为不同用途创建不同的 Key</p>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/20 border border-red-500/30 text-red-200 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* API Key 列表 */}
      <div className="space-y-3">
        {apiKeys.length === 0 ? (
          <div className="text-center py-12 glass rounded-2xl">
            <Key className="w-12 h-12 mx-auto text-white/30 mb-4" />
            <p className="text-white/60">还没有添加 API Key</p>
            <p className="text-white/40 text-sm mt-1">添加后才能使用 AI 生成功能</p>
          </div>
        ) : (
          apiKeys.map((key, index) => (
            <motion.div
              key={key.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="glass-card rounded-xl p-4 hover:bg-white/10 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">
                      {PROVIDERS.find(p => p.id === key.provider)?.icon || "🔑"}
                    </span>
                    <span className="font-medium">{key.name}</span>
                    {key.is_default && (
                      <span className="px-2 py-0.5 rounded-full bg-green-500/20 text-green-300 text-xs">
                        默认
                      </span>
                    )}
                    {!key.is_active && (
                      <span className="px-2 py-0.5 rounded-full bg-gray-500/20 text-gray-400 text-xs">
                        已禁用
                      </span>
                    )}
                  </div>
                  
                  <div className="text-sm text-white/60 space-y-1">
                    <p>提供商: {PROVIDERS.find(p => p.id === key.provider)?.name || key.provider}</p>
                    <p>添加时间: {new Date(key.created_at).toLocaleDateString('zh-CN')}</p>
                    {key.last_used_at && (
                      <p>上次使用: {new Date(key.last_used_at).toLocaleDateString('zh-CN')}</p>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  {/* 验证按钮 */}
                  <button
                    onClick={() => handleVerify(key.id)}
                    disabled={verifyingId === key.id}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                    title="验证"
                  >
                    {verifyingId === key.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4 text-white/60" />
                    )}
                  </button>
                  
                  {/* 设为默认 */}
                  {!key.is_default && key.is_active && (
                    <button
                      onClick={() => handleSetDefault(key.id)}
                      className="px-3 py-1.5 text-xs rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
                    >
                      设为默认
                    </button>
                  )}
                  
                  {/* 启用/禁用切换 */}
                  <button
                    onClick={() => handleToggleActive(key.id, key.is_active)}
                    className={`w-10 h-6 rounded-full transition-colors relative ${
                      key.is_active ? 'bg-green-500' : 'bg-gray-600'
                    }`}
                  >
                    <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                      key.is_active ? 'left-5' : 'left-1'
                    }`} />
                  </button>
                  
                  {/* 删除 */}
                  <button
                    onClick={() => handleDelete(key.id)}
                    className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                  >
                    <Trash2 className="w-4 h-4 text-white/60 group-hover:text-red-400" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))
        )}
      </div>

      {/* 添加表单弹窗 */}
      <AnimatePresence>
        {showAddForm && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
              onClick={() => !isSubmitting && setShowAddForm(false)}
            />
            
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
            >
              <div className="glass rounded-2xl p-6 w-full max-w-md pointer-events-auto"
              >
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold">添加 API Key</h3>
                  <button
                    onClick={() => setShowAddForm(false)}
                    disabled={isSubmitting}
                    className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {formError && (
                  <div className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/30 text-red-200 text-sm">
                    {formError}
                  </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">名称 *</label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="例如：OpenAI 主账号"
                      className="w-full px-4 py-2.5 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">提供商 *</label>
                    <select
                      value={formData.provider}
                      onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
                      className="w-full px-4 py-2.5 rounded-lg bg-white/10 border border-white/20 text-white focus:outline-none focus:border-white/40"
                    >
                      {PROVIDERS.map((p) => (
                        <option key={p.id} value={p.id} className="bg-gray-800">
                          {p.icon} {p.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">API Key *</label>
                    <input
                      type="password"
                      value={formData.api_key}
                      onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                      placeholder="sk-..."
                      className="w-full px-4 py-2.5 rounded-lg bg-white/10 border border-white/20 text-white placeholder-white/40 focus:outline-none focus:border-white/40"
                    />
                    <p className="text-xs text-white/40 mt-1">你的 Key 会被安全加密存储</p>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={() => setShowAddForm(false)}
                      disabled={isSubmitting}
                      className="flex-1 py-2.5 rounded-lg glass hover:bg-white/20 transition-colors"
                    >
                      取消
                    </button>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="flex-1 py-2.5 rounded-lg bg-white text-purple-600 font-medium disabled:opacity-50"
                    >
                      {isSubmitting ? (
                        <Loader2 className="w-5 h-5 animate-spin mx-auto" />
                      ) : (
                        '添加'
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
