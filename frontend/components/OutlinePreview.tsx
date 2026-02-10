"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  X, 
  Check, 
  RefreshCw, 
  FileText, 
  Layout,
  ChevronRight,
  AlertCircle
} from "lucide-react";
import { LAYOUT_TYPES, getLayoutInfo } from "./slides/layouts";

interface OutlineSlide {
  type: string;
  title: string;
  subtitle?: string;
  description?: string;
  content?: string;
  bullets?: string[];
  left?: { title: string; points: string[] };
  right?: { title: string; points: string[] };
  events?: { year: string; title: string; description: string }[];
  steps?: string[];
  items?: { title: string; description: string }[];
  stats?: { value: string; label: string; description?: string }[];
  quote?: string;
  author?: string;
  data?: Record<string, any>;
}

interface OutlineData {
  title: string;
  summary?: string;
  theme?: {
    name: string;
    primary_color: string;
    secondary_color: string;
    background_color: string;
    style_description?: string;
  };
  slides: OutlineSlide[];
}

interface OutlinePreviewProps {
  outline: OutlineData | null;
  isLoading: boolean;
  error: string | null;
  onClose: () => void;
  onConfirm: () => void;
  onRegenerate: () => void;
}

export function OutlinePreview({
  outline,
  isLoading,
  error,
  onClose,
  onConfirm,
  onRegenerate,
}: OutlinePreviewProps) {
  const [expandedSlide, setExpandedSlide] = useState<number | null>(0);

  if (isLoading) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass rounded-2xl p-8 max-w-md w-full mx-4 text-center"
        >
          <div className="animate-spin w-12 h-12 border-3 border-white/20 border-t-white rounded-full mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Generating Outline...</h3>
          <p className="text-white/60">AI is analyzing your topic and creating structured content</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass rounded-2xl p-8 max-w-md w-full mx-4"
        >
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2 text-center">Generation Failed</h3>
          <p className="text-white/60 text-center mb-6">{error}</p>
          <div className="flex gap-3">
            <button
              onClick={onRegenerate}
              className="flex-1 flex items-center justify-center gap-2 py-3 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Retry
            </button>
            <button
              onClick={onClose}
              className="flex-1 py-3 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
            >
              Cancel
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  if (!outline) return null;

  const renderSlideContent = (slide: OutlineSlide, index: number) => {
    const layoutInfo = getLayoutInfo(slide.type);
    const Icon = layoutInfo.icon;

    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-3"
      >
        {/* Slide header */}
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
            <Icon className="w-4 h-4 text-white/60" />
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-lg leading-tight">{slide.title}</h4>
            <span className="text-xs text-white/50">{layoutInfo.name}</span>
          </div>
        </div>

        {/* Slide content based on type */}
        <div className="pl-11 space-y-2">
          {slide.subtitle && (
            <p className="text-white/70 text-sm">{slide.subtitle}</p>
          )}
          
          {slide.description && (
            <p className="text-white/60 text-sm">{slide.description}</p>
          )}

          {slide.content && (
            <p className="text-white/70 text-sm line-clamp-3">{slide.content}</p>
          )}

          {slide.bullets && slide.bullets.length > 0 && (
            <ul className="space-y-1">
              {slide.bullets.slice(0, 3).map((bullet, i) => (
                <li key={i} className="text-sm text-white/70 flex items-start gap-2">
                  <span className="text-white/40 mt-1">•</span>
                  <span className="line-clamp-2">{bullet}</span>
                </li>
              ))}
              {slide.bullets.length > 3 && (
                <li className="text-xs text-white/40 pl-4">
                  +{slide.bullets.length - 3} more points
                </li>
              )}
            </ul>
          )}

          {slide.left && slide.right && (
            <div className="grid grid-cols-2 gap-3 text-sm">
              <div className="bg-white/5 rounded-lg p-2">
                <span className="text-white/50 text-xs">{slide.left.title}</span>
                <p className="text-white/70 line-clamp-2">
                  {slide.left.points?.[0] || "..."}
                </p>
              </div>
              <div className="bg-white/5 rounded-lg p-2">
                <span className="text-white/50 text-xs">{slide.right.title}</span>
                <p className="text-white/70 line-clamp-2">
                  {slide.right.points?.[0] || "..."}
                </p>
              </div>
            </div>
          )}

          {slide.events && slide.events.length > 0 && (
            <div className="flex gap-2 overflow-x-auto pb-1">
              {slide.events.slice(0, 3).map((event, i) => (
                <div key={i} className="flex-shrink-0 bg-white/5 rounded-lg p-2 min-w-[100px]">
                  <span className="text-xs text-white/50">{event.year}</span>
                  <p className="text-sm font-medium">{event.title}</p>
                </div>
              ))}
            </div>
          )}

          {slide.stats && slide.stats.length > 0 && (
            <div className="flex gap-4">
              {slide.stats.slice(0, 3).map((stat, i) => (
                <div key={i} className="text-center">
                  <span className="text-xl font-bold text-white">{stat.value}</span>
                  <p className="text-xs text-white/50">{stat.label}</p>
                </div>
              ))}
            </div>
          )}

          {slide.items && slide.items.length > 0 && (
            <div className="grid grid-cols-2 gap-2">
              {slide.items.slice(0, 4).map((item, i) => (
                <div key={i} className="bg-white/5 rounded-lg p-2 text-sm">
                  <span className="font-medium">{item.title}</span>
                </div>
              ))}
            </div>
          )}

          {slide.quote && (
            <blockquote className="border-l-2 border-white/20 pl-3 italic text-white/70">
              "{slide.quote.substring(0, 100)}{slide.quote.length > 100 ? '...' : ''}"
            </blockquote>
          )}
        </div>
      </motion.div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <div>
            <h2 className="text-2xl font-bold">Outline Preview</h2>
            <p className="text-white/60 text-sm mt-1">
              Review the AI-generated structure before creating the full PPT
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex">
          {/* Left: Slide list */}
          <div className="w-1/2 border-r border-white/10 overflow-y-auto p-4 space-y-2">
            {/* Theme info */}
            {outline.theme && (
              <div className="mb-4 p-4 bg-white/5 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <div 
                    className="w-6 h-6 rounded-full border-2 border-white/20"
                    style={{ backgroundColor: outline.theme.primary_color }}
                  />
                  <span className="font-medium">{outline.theme.name}</span>
                </div>
                <p className="text-sm text-white/60">{outline.theme.style_description}</p>
              </div>
            )}

            {/* Summary */}
            {outline.summary && (
              <div className="mb-4 p-4 bg-white/5 rounded-xl">
                <h4 className="text-sm font-medium text-white/70 mb-2">Summary</h4>
                <p className="text-sm text-white/60 line-clamp-4">{outline.summary}</p>
              </div>
            )}

            {/* Slide list */}
            <div className="space-y-2">
              {outline.slides.map((slide, index) => {
                const layoutInfo = getLayoutInfo(slide.type);
                const Icon = layoutInfo.icon;
                const isExpanded = expandedSlide === index;

                return (
                  <motion.button
                    key={index}
                    onClick={() => setExpandedSlide(isExpanded ? null : index)}
                    className={`w-full text-left p-3 rounded-xl transition-colors ${
                      isExpanded 
                        ? 'bg-white/20 border border-white/30' 
                        : 'bg-white/5 hover:bg-white/10 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-white/40 w-6">{index + 1}</span>
                      <Icon className="w-4 h-4 text-white/60" />
                      <span className="flex-1 font-medium truncate">{slide.title}</span>
                      <ChevronRight 
                        className={`w-4 h-4 text-white/40 transition-transform ${
                          isExpanded ? 'rotate-90' : ''
                        }`} 
                      />
                    </div>
                  </motion.button>
                );
              })}
            </div>
          </div>

          {/* Right: Slide detail */}
          <div className="w-1/2 overflow-y-auto p-6">
            <AnimatePresence mode="wait">
              {expandedSlide !== null && outline.slides[expandedSlide] && (
                <motion.div
                  key={expandedSlide}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="bg-white/5 rounded-xl p-6"
                >
                  {renderSlideContent(outline.slides[expandedSlide], expandedSlide)}
                </motion.div>
              )}
            </AnimatePresence>

            {expandedSlide === null && (
              <div className="h-full flex items-center justify-center text-white/40">
                <div className="text-center">
                  <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
                  <p>Select a slide to view details</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-white/10">
          <div className="flex items-center gap-4 text-sm text-white/60">
            <span className="flex items-center gap-2">
              <Layout className="w-4 h-4" />
              {outline.slides.length} slides
            </span>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={onRegenerate}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Regenerate
            </button>
            <button
              onClick={onConfirm}
              className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-white text-purple-600 font-medium hover:opacity-90 transition-opacity"
            >
              <Check className="w-4 h-4" />
              Generate PPT
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
