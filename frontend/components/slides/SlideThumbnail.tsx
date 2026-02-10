"use client";

import { motion } from "framer-motion";
import { getLayoutInfo } from "./layouts";

interface SlideThumbnailProps {
  slide: any;
  index: number;
  isActive: boolean;
  onClick: () => void;
  editingContent?: { [key: string]: any };
}

export function SlideThumbnail({
  slide,
  index,
  isActive,
  onClick,
  editingContent,
}: SlideThumbnailProps) {
  const content = { ...slide.content, ...editingContent };
  const layoutType = slide.layout?.type || slide.type || "content";
  const layoutInfo = getLayoutInfo(layoutType);

  const renderPreview = () => {
    const title = content.title || "无标题";
    const text = content.text || "";

    switch (layoutType) {
      case "title":
        return (
          <div className="h-full flex flex-col items-center justify-center p-2 text-center">
            <p className="text-[8px] font-bold text-white/90 line-clamp-2">{title}</p>
            {content.subtitle && (
              <p className="text-[6px] text-white/60 mt-1 line-clamp-1">{content.subtitle}</p>
            )}
          </div>
        );

      case "section":
        return (
          <div className="h-full flex flex-col items-center justify-center p-2 text-center bg-white/10">
            <p className="text-[8px] font-bold text-white/90 line-clamp-2">{title}</p>
            {content.description && (
              <p className="text-[5px] text-white/50 mt-1 line-clamp-1">{content.description}</p>
            )}
          </div>
        );

      case "two-column":
        return (
          <div className="h-full flex flex-col p-2">
            <p className="text-[8px] font-bold text-white/90 mb-1 line-clamp-1">{title}</p>
            <div className="flex-1 flex gap-1">
              <div className="flex-1 bg-white/5 rounded p-1">
                <p className="text-[5px] text-white/50 line-clamp-2">{content.left?.title || "左栏"}</p>
              </div>
              <div className="flex-1 bg-white/5 rounded p-1">
                <p className="text-[5px] text-white/50 line-clamp-2">{content.right?.title || "右栏"}</p>
              </div>
            </div>
          </div>
        );

      case "timeline":
        return (
          <div className="h-full flex flex-col p-2">
            <p className="text-[8px] font-bold text-white/90 mb-1">{title}</p>
            <div className="flex-1 flex items-center gap-1">
              {(content.events || []).slice(0, 3).map((_: any, i: number) => (
                <div key={i} className="flex-1 flex flex-col items-center">
                  <div className="w-2 h-2 rounded-full bg-white/30" />
                  <div className="text-[5px] text-white/40 mt-1">{i + 1}</div>
                </div>
              ))}
              {!content.events?.length && (
                <div className="flex-1 h-px bg-white/20" />
              )}
            </div>
          </div>
        );

      case "process":
        return (
          <div className="h-full flex flex-col p-2">
            <p className="text-[8px] font-bold text-white/90 mb-1">{title}</p>
            <div className="flex-1 flex items-center gap-0.5">
              {(content.steps || []).slice(0, 4).map((_: any, i: number) => (
                <div key={i} className="flex items-center">
                  <div className="w-4 h-4 rounded bg-white/20 flex items-center justify-center">
                    <span className="text-[5px] text-white/60">{i + 1}</span>
                  </div>
                  {i < 3 && <div className="w-1 h-px bg-white/20" />}
                </div>
              ))}
              {!content.steps?.length && (
                <div className="flex-1 flex items-center justify-center">
                  <span className="text-[5px] text-white/40">步骤...</span>
                </div>
              )}
            </div>
          </div>
        );

      case "grid":
        return (
          <div className="h-full flex flex-col p-2">
            <p className="text-[8px] font-bold text-white/90 mb-1">{title}</p>
            <div className="flex-1 grid grid-cols-2 gap-1">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="bg-white/5 rounded p-1 flex items-center justify-center">
                  <span className="text-[5px] text-white/40">{i + 1}</span>
                </div>
              ))}
            </div>
          </div>
        );

      case "comparison":
        return (
          <div className="h-full flex flex-col p-2">
            <p className="text-[8px] font-bold text-white/90 mb-1">{title}</p>
            <div className="flex-1 grid grid-cols-3 gap-0.5">
              {[0, 1, 2].map((i) => (
                <div key={i} className="bg-white/5 rounded p-1">
                  <div className="text-[5px] text-white/40 text-center">{i === 0 ? "维度" : `方案${i}`}</div>
                </div>
              ))}
            </div>
          </div>
        );

      case "data":
        return (
          <div className="h-full flex flex-col p-2">
            <p className="text-[8px] font-bold text-white/90 mb-1">{title}</p>
            <div className="flex-1 flex items-center justify-around">
              {(content.stats || []).slice(0, 3).map((stat: any, i: number) => (
                <div key={i} className="text-center">
                  <div className="text-[10px] font-bold text-white/80">{stat?.value || "99%"}</div>
                  <div className="text-[4px] text-white/40">{stat?.label || "指标"}</div>
                </div>
              ))}
              {!content.stats?.length && (
                <div className="text-[8px] font-bold text-white/60">99%</div>
              )}
            </div>
          </div>
        );

      case "quote":
        return (
          <div className="h-full flex flex-col items-center justify-center p-2 text-center">
            <div className="text-[12px] text-white/30 mb-1">"</div>
            <p className="text-[6px] text-white/70 line-clamp-2 italic">{content.quote || "引用内容"}</p>
            {content.author && (
              <p className="text-[5px] text-white/40 mt-1">— {content.author}</p>
            )}
          </div>
        );

      case "image-text":
        return (
          <div className="h-full flex flex-col p-2">
            <p className="text-[8px] font-bold text-white/90 mb-1">{title}</p>
            <div className="flex-1 flex gap-1">
              <div className="flex-1 bg-white/10 rounded flex items-center justify-center">
                <span className="text-[6px] text-white/30">图</span>
              </div>
              <div className="flex-1 bg-white/5 rounded p-1">
                <p className="text-[5px] text-white/50 line-clamp-3">{text || "..."}</p>
              </div>
            </div>
          </div>
        );

      default: // content
        return (
          <div className="h-full flex flex-col p-2">
            <p className="text-[8px] font-bold text-white/90 mb-1 line-clamp-1">{title}</p>
            <div className="flex-1 bg-white/5 rounded p-1">
              <p className="text-[5px] text-white/70 line-clamp-4">{text || "..."}</p>
            </div>
          </div>
        );
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      onClick={onClick}
      className={`relative cursor-pointer rounded-lg overflow-hidden border-2 will-change-transform ${
        isActive
          ? "border-white shadow-lg"
          : "border-white/20 hover:border-white/40"
      }`}
      style={{ transform: "translateZ(0)" }}
    >
      <div className="aspect-video bg-gradient-to-br from-white/10 to-white/5 overflow-hidden relative">
        <div className="absolute top-1 left-1 z-10 flex items-center gap-1">
          <span className="text-[10px] text-white/60">{index + 1}</span>
          <layoutInfo.icon className="w-3 h-3 text-white/40" />
        </div>
        {renderPreview()}
      </div>
    </motion.div>
  );
}
