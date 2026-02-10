"use client";

import { 
  Type, 
  Layout, 
  Columns, 
  Timer, 
  GitBranch, 
  Table2, 
  Grid3X3, 
  Image as ImageIcon,
  Quote,
  BarChart3,
  BookOpen
} from "lucide-react";

// 布局类型定义
export const LAYOUT_TYPES = [
  { 
    id: "title", 
    name: "标题页", 
    icon: Type, 
    description: "大标题 + 副标题，适合封面",
    fields: ["title", "subtitle"]
  },
  { 
    id: "content", 
    name: "内容页", 
    icon: Layout, 
    description: "标题 + 正文/要点",
    fields: ["title", "text", "bullets"]
  },
  { 
    id: "two-column", 
    name: "双栏对比", 
    icon: Columns, 
    description: "左右两栏对比布局",
    fields: ["title", "left", "right"]
  },
  { 
    id: "timeline", 
    name: "时间轴", 
    icon: Timer, 
    description: "水平时间线展示历程",
    fields: ["title", "events"]
  },
  { 
    id: "process", 
    name: "流程图", 
    icon: GitBranch, 
    description: "步骤流程展示",
    fields: ["title", "steps"]
  },
  { 
    id: "comparison", 
    name: "对比表", 
    icon: Table2, 
    description: "多维度对比",
    fields: ["title", "items"]
  },
  { 
    id: "grid", 
    name: "网格展示", 
    icon: Grid3X3, 
    description: "2x2或3x3网格",
    fields: ["title", "items"]
  },
  { 
    id: "image-text", 
    name: "图文混排", 
    icon: ImageIcon, 
    description: "图片 + 文字",
    fields: ["title", "image_url", "text"]
  },
  { 
    id: "quote", 
    name: "引用页", 
    icon: Quote, 
    description: "大段引用展示",
    fields: ["quote", "author", "title"]
  },
  { 
    id: "data", 
    name: "数据展示", 
    icon: BarChart3, 
    description: "突出数字和统计",
    fields: ["title", "stats"]
  },
  { 
    id: "section", 
    name: "章节页", 
    icon: BookOpen, 
    description: "章节分隔页",
    fields: ["title", "description"]
  },
];

// 获取布局信息
export function getLayoutInfo(type: string) {
  return LAYOUT_TYPES.find(l => l.id === type) || LAYOUT_TYPES[1];
}

// 检查布局是否支持某字段
export function layoutSupportsField(layoutType: string, field: string): boolean {
  const layout = getLayoutInfo(layoutType);
  return layout.fields.includes(field);
}
