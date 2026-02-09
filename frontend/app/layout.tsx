import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Slides - AI PPT Generator",
  description: "用 AI 快速生成专业 PPT，让创意飞起来",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">{children}</body>
    </html>
  );
}
