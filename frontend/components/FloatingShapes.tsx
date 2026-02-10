"use client";

import { motion } from "framer-motion";

export default function FloatingShapes() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {/* 右上大光斑 - 使用 will-change 优化 */}
      <motion.div
        animate={{
          y: [0, -30, 0],
          x: [0, 15, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -top-20 -right-20 w-[500px] h-[500px] rounded-full will-change-transform"
        style={{
          background: 'radial-gradient(circle, rgba(255,215,0,0.4) 0%, rgba(255,107,157,0.2) 50%, transparent 70%)',
          filter: 'blur(40px)',
          transform: 'translateZ(0)',
        }}
      />
      
      {/* 左下光斑 */}
      <motion.div
        animate={{
          y: [0, 25, 0],
          x: [0, -20, 0],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1,
        }}
        className="absolute -bottom-40 -left-40 w-[600px] h-[600px] rounded-full will-change-transform"
        style={{
          background: 'radial-gradient(circle, rgba(147,51,234,0.3) 0%, rgba(236,72,153,0.15) 50%, transparent 70%)',
          filter: 'blur(50px)',
          transform: 'translateZ(0)',
        }}
      />
      
      {/* 中间小光斑 */}
      <motion.div
        animate={{
          y: [0, -20, 0],
          scale: [1, 1.15, 1],
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 0.5,
        }}
        className="absolute top-1/3 left-1/4 w-[300px] h-[300px] rounded-full will-change-transform"
        style={{
          background: 'radial-gradient(circle, rgba(99,102,241,0.3) 0%, transparent 70%)',
          filter: 'blur(30px)',
          transform: 'translateZ(0)',
        }}
      />
      
      {/* 右侧中光斑 */}
      <motion.div
        animate={{
          y: [0, 15, 0],
          x: [0, 10, 0],
        }}
        transition={{
          duration: 7,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2,
        }}
        className="absolute top-2/3 right-1/4 w-[350px] h-[350px] rounded-full will-change-transform"
        style={{
          background: 'radial-gradient(circle, rgba(244,63,94,0.25) 0%, transparent 70%)',
          filter: 'blur(35px)',
          transform: 'translateZ(0)',
        }}
      />
      
      {/* 几何装饰 - 圆形 - 使用 CSS 动画代替 Framer Motion */}
      <div 
        className="absolute top-32 right-20 w-24 h-24 border border-white/10 rounded-full animate-spin-slow"
        style={{ animation: 'spin 30s linear infinite' }}
      />
      
      <div 
        className="absolute bottom-40 left-20 w-16 h-16 border-2 border-white/5 rounded-lg rotate-45 animate-spin-reverse"
        style={{ animation: 'spin-reverse 25s linear infinite' }}
      />
      
      {/* 小圆点 - 减少动画复杂度 */}
      <motion.div
        animate={{
          y: [0, -50, 0],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-1/4 right-1/3 w-3 h-3 bg-white/30 rounded-full will-change-transform"
        style={{ transform: 'translateZ(0)' }}
      />
      
      <motion.div
        animate={{
          y: [0, 40, 0],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 3,
        }}
        className="absolute bottom-1/3 left-1/3 w-2 h-2 bg-yellow-300/40 rounded-full will-change-transform"
        style={{ transform: 'translateZ(0)' }}
      />
    </div>
  );
}
