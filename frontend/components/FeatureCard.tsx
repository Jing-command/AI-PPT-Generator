"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  subtitle: string;
  delay?: number;
}

export default function FeatureCard({ icon, title, subtitle, delay = 0 }: FeatureCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.9 + delay, duration: 0.5 }}
      whileHover={{ y: -8, scale: 1.02 }}
      className="group glass-card rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:bg-white/15 hover:shadow-2xl hover:shadow-purple-900/20"
    >
      <motion.div
        whileHover={{ rotate: [0, -10, 10, 0] }}
        transition={{ duration: 0.5 }}
        className="mb-4"
      >
        {icon}
      </motion.div>
      
      <h3 className="text-lg font-semibold mb-2 leading-tight">{title}</h3>
      <p className="text-sm text-white/60">{subtitle}</p>
    </motion.div>
  );
}
