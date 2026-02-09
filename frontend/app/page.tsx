"use client";

import { motion } from "framer-motion";
import { Sparkles, Zap, Palette, PenTool, ArrowRight, Play } from "lucide-react";
import Link from "next/link";
import FloatingShapes from "@/components/FloatingShapes";
import FeatureCard from "@/components/FeatureCard";
import Navbar from "@/components/Navbar";

export default function Home() {
  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* 渐变背景 */}
      <div 
        className="fixed inset-0 animate-gradient"
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 25%, #8b5cf6 50%, #ec4899 75%, #f43f5e 100%)',
          backgroundSize: '400% 400%',
        }}
      />
      
      <div className="fixed inset-0 bg-gradient-to-b from-transparent via-transparent to-black/20" />
      
      {/* 浮动装饰 */}
      <FloatingShapes />
      
      {/* 内容 */}
      <div className="relative z-10">
        <Navbar />
        
        {/* Hero Section */}
        <section className="min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8 pt-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="text-center max-w-4xl mx-auto"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="inline-flex items-center gap-2 glass px-5 py-2.5 rounded-full mb-8"
            >
              <Sparkles className="w-4 h-4 text-yellow-300" />
              <span className="text-sm font-medium">让创意飞起来</span>
            </motion.div>
            
            {/* 主标题 */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="font-display text-6xl sm:text-7xl lg:text-8xl font-bold tracking-tight text-gradient mb-6"
            >
              AI SLIDES
            </motion.h1>
            
            {/* 副标题 */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5, duration: 0.6 }}
              className="text-lg sm:text-xl text-white/90 mb-4 max-w-xl mx-auto leading-relaxed"
            >
              输入你的想法，AI 秒变精美 PPT
            </motion.p>
            
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="text-base text-white/70 mb-10"
            >
              大学生、职场人都在用的 AI 神器
            </motion.p>
            
            {/* CTA 按钮 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.6 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <Link href="/generate">
                <motion.button
                  whileHover={{ scale: 1.05, y: -3 }}
                  whileTap={{ scale: 0.98 }}
                  className="group flex items-center gap-3 bg-white text-purple-600 px-8 py-4 rounded-full font-semibold text-lg shadow-2xl shadow-purple-900/30 hover:shadow-purple-900/50 transition-shadow"
                >
                  <Zap className="w-5 h-5 fill-current" />
                  立即开始
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </motion.button>
              </Link>
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center gap-2 glass px-6 py-4 rounded-full font-medium text-white/90 hover:bg-white/20 transition-colors"
              >
                <Play className="w-5 h-5" />
                观看演示
              </motion.button>
            </motion.div>
          </motion.div>
          
          {/* 功能卡片 */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9, duration: 0.8 }}
            className="mt-16 sm:mt-20 grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6 max-w-4xl mx-auto px-4"
          >
            <FeatureCard
              icon={<Zap className="w-7 h-7 text-yellow-300" />}
              title="一句话生成"
              subtitle="AI 自动排版"
              delay={0}
            />
            <FeatureCard
              icon={<Palette className="w-7 h-7 text-pink-300" />}
              title="海量模板"
              subtitle="涵盖各种场景"
              delay={0.1}
            />
            <FeatureCard
              icon={<PenTool className="w-7 h-7 text-cyan-300" />}
              title="智能编辑"
              subtitle="实时优化建议"
              delay={0.2}
            />
          </motion.div>
          
          {/* 滚动提示 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2, duration: 0.6 }}
            className="absolute bottom-8 left-1/2 -translate-x-1/2"
          >
            <motion.div
              animate={{ y: [0, 8, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
              className="w-6 h-10 rounded-full border-2 border-white/30 flex justify-center pt-2"
            >
              <motion.div
                animate={{ opacity: [1, 0.3, 1], y: [0, 8, 0] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
                className="w-1.5 h-1.5 bg-white rounded-full"
              />
            </motion.div>
          </motion.div>
        </section>
        
        {/* 功能展示区域 */}
        <section className="py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8 }}
              className="text-center mb-16"
            >
              <h2 className="font-display text-4xl sm:text-5xl font-bold mb-4 text-gradient">
                三步生成专业 PPT
              </h2>
              <p className="text-white/70 text-lg">简单到不可思议</p>
            </motion.div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                { step: "01", title: "输入主题", desc: "简单描述你想要的 PPT 内容" },
                { step: "02", title: "AI 生成", desc: "系统自动生成完整 PPT 内容" },
                { step: "03", title: "导出分享", desc: "支持 PPT、PDF、图片多种格式" },
              ].map((item, index) => (
                <motion.div
                  key={item.step}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.15, duration: 0.6 }}
                  className="glass-card rounded-3xl p-8 text-center group hover:bg-white/15 transition-all duration-300"
                >
                  <div className="text-6xl font-display font-bold text-white/20 mb-4 group-hover:text-white/30 transition-colors">
                    {item.step}
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
                  <p className="text-white/70">{item.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
        
        {/* 统计区域 */}
        <section className="py-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="glass rounded-3xl p-8 sm:p-12"
            >
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-8">
                {[
                  { value: "10万+", label: "用户信赖" },
                  { value: "50+", label: "精美模板" },
                  { value: "3分钟", label: "平均生成时间" },
                  { value: "99%", label: "满意度" },
                ].map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: index * 0.1, duration: 0.5 }}
                    className="text-center"
                  >
                    <div className="text-3xl sm:text-4xl font-display font-bold text-gradient mb-2">
                      {stat.value}
                    </div>
                    <div className="text-white/70 text-sm">{stat.label}</div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>
        
        {/* CTA 区域 */}
        <section className="py-24 px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="max-w-3xl mx-auto text-center"
          >
            <h2 className="font-display text-4xl sm:text-5xl font-bold mb-6 text-gradient">
              准备好让 PPT 制作变轻松了吗？
            </h2>
            <p className="text-white/70 text-lg mb-10">
              加入 10万+ 用户的行列，体验 AI 创作的魔力
            </p>
            
            <Link href="/generate">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.98 }}
                className="group flex items-center gap-3 bg-white text-purple-600 px-10 py-5 rounded-full font-semibold text-lg shadow-2xl shadow-purple-900/30 mx-auto"
              >
                <Sparkles className="w-5 h-5" />
                免费开始创作
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </motion.button>
            </Link>
          </motion.div>
        </section>
        
        {/* Footer */}
        <footer className="py-8 px-4 border-t border-white/10">
          <div className="max-w-6xl mx-auto text-center text-white/50 text-sm">
            <p>© 2024 AI Slides. 让每一次演讲都精彩。</p>
          </div>
        </footer>
      </div>
    </main>
  );
}
