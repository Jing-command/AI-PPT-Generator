"use client";

import { useState, useEffect } from "react";
import { getLayoutInfo, LAYOUT_TYPES } from "./layouts";

interface SlideEditorProps {
  slide: any;
  onUpdate: (id: string, data: any) => Promise<any>;
}

export function SlideEditor({ slide, onUpdate }: SlideEditorProps) {
  const layoutType = slide.layout?.type || slide.type || "content";
  const layoutInfo = getLayoutInfo(layoutType);
  const content = slide.content || {};

  // 本地状态
  const [localContent, setLocalContent] = useState(content);

  useEffect(() => {
    setLocalContent(content);
  }, [slide.id]);

  const handleUpdate = async (updates: any) => {
    const newContent = { ...localContent, ...updates };
    setLocalContent(newContent);
    await onUpdate(slide.id, { content: newContent });
  };

  // 标题页
  if (layoutType === "title") {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center">
        <input
          type="text"
          value={localContent.title || ""}
          onChange={(e) => handleUpdate({ title: e.target.value })}
          placeholder="输入主标题"
          className="text-4xl font-bold bg-transparent border-b-2 border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors text-center w-full"
        />
        <input
          type="text"
          value={localContent.subtitle || ""}
          onChange={(e) => handleUpdate({ subtitle: e.target.value })}
          placeholder="输入副标题"
          className="text-xl text-white/70 bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-1 transition-colors text-center w-3/4"
        />
      </div>
    );
  }

  // 章节页
  if (layoutType === "section") {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center">
        <input
          type="text"
          value={localContent.title || ""}
          onChange={(e) => handleUpdate({ title: e.target.value })}
          placeholder="章节标题"
          className="text-4xl font-bold bg-transparent border-b-2 border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors text-center w-full"
        />
        <input
          type="text"
          value={localContent.description || ""}
          onChange={(e) => handleUpdate({ description: e.target.value })}
          placeholder="章节描述"
          className="text-lg text-white/70 bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-1 transition-colors text-center w-2/3"
        />
      </div>
    );
  }

  // 双栏对比
  if (layoutType === "two-column") {
    const left = localContent.left || { title: "", points: [] };
    const right = localContent.right || { title: "", points: [] };

    return (
      <div className="h-full flex flex-col">
        <input
          type="text"
          value={localContent.title || ""}
          onChange={(e) => handleUpdate({ title: e.target.value })}
          placeholder="页面标题"
          className="text-2xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
        />
        <div className="flex-1 grid grid-cols-2 gap-6">
          {/* 左栏 */}
          <div className="bg-white/5 rounded-lg p-4">
            <input
              type="text"
              value={left.title}
              onChange={(e) => handleUpdate({ left: { ...left, title: e.target.value } })}
              placeholder="左栏标题"
              className="w-full text-lg font-semibold bg-transparent border-b border-white/20 focus:border-white/40 focus:outline-none pb-1 mb-3"
            />
            <textarea
              value={left.points?.join("\n") || ""}
              onChange={(e) => handleUpdate({ left: { ...left, points: e.target.value.split("\n") } })}
              placeholder="要点（每行一个）..."
              className="w-full flex-1 bg-transparent resize-none focus:outline-none text-sm leading-relaxed min-h-[150px]"
            />
          </div>
          {/* 右栏 */}
          <div className="bg-white/5 rounded-lg p-4">
            <input
              type="text"
              value={right.title}
              onChange={(e) => handleUpdate({ right: { ...right, title: e.target.value } })}
              placeholder="右栏标题"
              className="w-full text-lg font-semibold bg-transparent border-b border-white/20 focus:border-white/40 focus:outline-none pb-1 mb-3"
            />
            <textarea
              value={right.points?.join("\n") || ""}
              onChange={(e) => handleUpdate({ right: { ...right, points: e.target.value.split("\n") } })}
              placeholder="要点（每行一个）..."
              className="w-full flex-1 bg-transparent resize-none focus:outline-none text-sm leading-relaxed min-h-[150px]"
            />
          </div>
        </div>
      </div>
    );
  }

  // 时间轴
  if (layoutType === "timeline") {
    const events = localContent.events || [];

    const updateEvent = (index: number, field: string, value: string) => {
      const newEvents = [...events];
      newEvents[index] = { ...newEvents[index], [field]: value };
      handleUpdate({ events: newEvents });
    };

    const addEvent = () => {
      handleUpdate({ events: [...events, { year: "", title: "", description: "" }] });
    };

    const removeEvent = (index: number) => {
      const newEvents = events.filter((_: any, i: number) => i !== index);
      handleUpdate({ events: newEvents });
    };

    return (
      <div className="h-full flex flex-col">
        <input
          type="text"
          value={localContent.title || ""}
          onChange={(e) => handleUpdate({ title: e.target.value })}
          placeholder="时间轴标题"
          className="text-2xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
        />
        <div className="flex-1 overflow-y-auto">
          <div className="relative pl-8">
            {/* 时间线 */}
            <div className="absolute left-3 top-0 bottom-0 w-px bg-white/20" />
            
            {events.map((event: any, index: number) => (
              <div key={index} className="relative mb-4">
                {/* 时间点 */}
                <div className="absolute left-[-22px] w-4 h-4 rounded-full bg-white/30 border-2 border-white/50" />
                
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <input
                      type="text"
                      value={event.year || ""}
                      onChange={(e) => updateEvent(index, "year", e.target.value)}
                      placeholder="年份"
                      className="w-20 text-sm font-semibold bg-transparent border-b border-white/20 focus:border-white/40 focus:outline-none"
                    />
                    <input
                      type="text"
                      value={event.title || ""}
                      onChange={(e) => updateEvent(index, "title", e.target.value)}
                      placeholder="事件标题"
                      className="flex-1 text-sm font-semibold bg-transparent border-b border-white/20 focus:border-white/40 focus:outline-none"
                    />
                    <button
                      onClick={() => removeEvent(index)}
                      className="text-white/40 hover:text-red-400 text-xs"
                    >
                      删除
                    </button>
                  </div>
                  <input
                    type="text"
                    value={event.description || ""}
                    onChange={(e) => updateEvent(index, "description", e.target.value)}
                    placeholder="事件描述"
                    className="w-full text-sm text-white/70 bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none"
                  />
                </div>
              </div>
            ))}
          </div>
          
          <button
            onClick={addEvent}
            className="mt-4 w-full py-2 rounded-lg border border-dashed border-white/30 text-white/50 hover:border-white/50 hover:text-white/70 transition-colors"
          >
            + 添加时间节点
          </button>
        </div>
      </div>
    );
  }

  // 流程图
  if (layoutType === "process") {
    const steps = localContent.steps || [];

    return (
      <div className="h-full flex flex-col">
        <input
          type="text"
          value={localContent.title || ""}
          onChange={(e) => handleUpdate({ title: e.target.value })}
          placeholder="流程标题"
          className="text-2xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
        />
        <div className="flex-1 flex items-center justify-center">
          <div className="flex flex-wrap items-center justify-center gap-2">
            {steps.map((step: string, index: number) => (
              <div key={index} className="flex items-center">
                <div className="flex flex-col items-center">
                  <div className="w-24 h-16 rounded-lg bg-white/10 flex items-center justify-center px-2">
                    <input
                      type="text"
                      value={step}
                      onChange={(e) => {
                        const newSteps = [...steps];
                        newSteps[index] = e.target.value;
                        handleUpdate({ steps: newSteps });
                      }}
                      className="w-full text-center text-sm bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none"
                    />
                  </div>
                  <span className="text-xs text-white/40 mt-1">步骤 {index + 1}</span>
                </div>
                {index < steps.length - 1 && (
                  <div className="mx-2 text-white/30">→</div>
                )}
              </div>
            ))}
          </div>
        </div>
        <div className="flex justify-center gap-2 mt-4">
          <button
            onClick={() => handleUpdate({ steps: [...steps, ""] })}
            className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm transition-colors"
          >
            + 添加步骤
          </button>
          {steps.length > 0 && (
            <button
              onClick={() => handleUpdate({ steps: steps.slice(0, -1) })}
              className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-sm text-red-300 transition-colors"
            >
              删除最后一步
            </button>
          )}
        </div>
      </div>
    );
  }

  // 网格展示
  if (layoutType === "grid") {
    const items = localContent.items || [];

    return (
      <div className="h-full flex flex-col">
        <input
          type="text"
          value={localContent.title || ""}
          onChange={(e) => handleUpdate({ title: e.target.value })}
          placeholder="网格标题"
          className="text-2xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
        />
        <div className="flex-1 grid grid-cols-2 gap-4 overflow-y-auto">
          {items.map((item: any, index: number) => (
            <div key={index} className="bg-white/5 rounded-lg p-4">
              <input
                type="text"
                value={item.title || ""}
                onChange={(e) => {
                  const newItems = [...items];
                  newItems[index] = { ...item, title: e.target.value };
                  handleUpdate({ items: newItems });
                }}
                placeholder={`项目 ${index + 1}`}
                className="w-full font-semibold bg-transparent border-b border-white/20 focus:border-white/40 focus:outline-none pb-1 mb-2"
              />
              <textarea
                value={item.description || ""}
                onChange={(e) => {
                  const newItems = [...items];
                  newItems[index] = { ...item, description: e.target.value };
                  handleUpdate({ items: newItems });
                }}
                placeholder="描述..."
                className="w-full bg-transparent resize-none focus:outline-none text-sm text-white/70"
                rows={3}
              />
            </div>
          ))}
        </div>
        <div className="flex justify-center gap-2 mt-4">
          <button
            onClick={() => handleUpdate({ items: [...items, { title: "", description: "" }] })}
            className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm transition-colors"
          >
            + 添加项目
          </button>
          {items.length > 0 && (
            <button
              onClick={() => handleUpdate({ items: items.slice(0, -1) })}
              className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-sm text-red-300 transition-colors"
            >
              删除最后一项
            </button>
          )}
        </div>
      </div>
    );
  }

  // 数据展示
  if (layoutType === "data") {
    const stats = localContent.stats || [];

    return (
      <div className="h-full flex flex-col">
        <input
          type="text"
          value={localContent.title || ""}
          onChange={(e) => handleUpdate({ title: e.target.value })}
          placeholder="数据标题"
          className="text-2xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
        />
        <div className="flex-1 flex items-center justify-around">
          {stats.map((stat: any, index: number) => (
            <div key={index} className="text-center">
              <input
                type="text"
                value={stat.value || ""}
                onChange={(e) => {
                  const newStats = [...stats];
                  newStats[index] = { ...stat, value: e.target.value };
                  handleUpdate({ stats: newStats });
                }}
                placeholder="数值"
                className="text-5xl font-bold text-center bg-transparent border-b-2 border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none w-32"
              />
              <input
                type="text"
                value={stat.label || ""}
                onChange={(e) => {
                  const newStats = [...stats];
                  newStats[index] = { ...stat, label: e.target.value };
                  handleUpdate({ stats: newStats });
                }}
                placeholder="指标名称"
                className="block mt-2 text-sm text-white/60 text-center bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none w-full"
              />
            </div>
          ))}
        </div>
        <div className="flex justify-center gap-2 mt-4">
          <button
            onClick={() => handleUpdate({ stats: [...stats, { value: "", label: "" }] })}
            className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm transition-colors"
          >
            + 添加数据
          </button>
          {stats.length > 0 && (
            <button
              onClick={() => handleUpdate({ stats: stats.slice(0, -1) })}
              className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-sm text-red-300 transition-colors"
            >
              删除最后一项
            </button>
          )}
        </div>
      </div>
    );
  }

  // 引用页
  if (layoutType === "quote") {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center px-8">
        <div className="text-6xl text-white/20 mb-4">"</div>
        <textarea
          value={localContent.quote || ""}
          onChange={(e) => handleUpdate({ quote: e.target.value })}
          placeholder="输入引用内容..."
          className="w-full text-2xl text-center bg-transparent resize-none focus:outline-none leading-relaxed mb-6"
          rows={4}
        />
        <div className="flex items-center gap-4">
          <div className="w-12 h-px bg-white/30" />
          <div className="flex flex-col">
            <input
              type="text"
              value={localContent.author || ""}
              onChange={(e) => handleUpdate({ author: e.target.value })}
              placeholder="作者名称"
              className="text-center bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none font-semibold"
            />
            <input
              type="text"
              value={localContent.title || ""}
              onChange={(e) => handleUpdate({ title: e.target.value })}
              placeholder="作者头衔"
              className="text-center text-sm text-white/60 bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none mt-1"
            />
          </div>
          <div className="w-12 h-px bg-white/30" />
        </div>
      </div>
    );
  }

  // 图文混排
  if (layoutType === "image-text") {
    return (
      <div className="h-full flex flex-col">
        <input
          type="text"
          value={localContent.title || ""}
          onChange={(e) => handleUpdate({ title: e.target.value })}
          placeholder="标题"
          className="text-2xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
        />
        <div className="flex-1 grid grid-cols-2 gap-6">
          <div className="bg-white/5 rounded-lg flex flex-col">
            <div className="flex-1 flex items-center justify-center text-white/30">
              <div className="text-center">
                <div className="text-4xl mb-2">🖼️</div>
                <span className="text-sm">图片区域</span>
              </div>
            </div>
            <input
              type="text"
              value={localContent.image_url || ""}
              onChange={(e) => handleUpdate({ image_url: e.target.value })}
              placeholder="图片 URL"
              className="px-3 py-2 bg-white/10 text-sm focus:outline-none border-t border-white/10"
            />
          </div>
          <textarea
            value={localContent.text || ""}
            onChange={(e) => handleUpdate({ text: e.target.value })}
            placeholder="文字内容..."
            className="bg-white/5 rounded-lg p-4 resize-none focus:outline-none focus:ring-2 focus:ring-white/20"
          />
        </div>
      </div>
    );
  }

  // 对比表
  if (layoutType === "comparison") {
    const items = localContent.items || [];

    return (
      <div className="h-full flex flex-col">
        <input
          type="text"
          value={localContent.title || ""}
          onChange={(e) => handleUpdate({ title: e.target.value })}
          placeholder="对比标题"
          className="text-2xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
        />
        <div className="flex-1 overflow-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-white/20">
                <th className="text-left p-2 text-sm text-white/60">对比项</th>
                <th className="text-left p-2 text-sm text-white/60">方案 A</th>
                <th className="text-left p-2 text-sm text-white/60">方案 B</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item: any, index: number) => (
                <tr key={index} className="border-b border-white/10">
                  <td className="p-2">
                    <input
                      type="text"
                      value={item.name || ""}
                      onChange={(e) => {
                        const newItems = [...items];
                        newItems[index] = { ...item, name: e.target.value };
                        handleUpdate({ items: newItems });
                      }}
                      className="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none"
                    />
                  </td>
                  <td className="p-2">
                    <input
                      type="text"
                      value={item.valueA || ""}
                      onChange={(e) => {
                        const newItems = [...items];
                        newItems[index] = { ...item, valueA: e.target.value };
                        handleUpdate({ items: newItems });
                      }}
                      className="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none"
                    />
                  </td>
                  <td className="p-2">
                    <input
                      type="text"
                      value={item.valueB || ""}
                      onChange={(e) => {
                        const newItems = [...items];
                        newItems[index] = { ...item, valueB: e.target.value };
                        handleUpdate({ items: newItems });
                      }}
                      className="w-full bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex justify-center gap-2 mt-4">
          <button
            onClick={() => handleUpdate({ items: [...items, { name: "", valueA: "", valueB: "" }] })}
            className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm transition-colors"
          >
            + 添加对比项
          </button>
          {items.length > 0 && (
            <button
              onClick={() => handleUpdate({ items: items.slice(0, -1) })}
              className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-sm text-red-300 transition-colors"
            >
              删除最后一项
            </button>
          )}
        </div>
      </div>
    );
  }

  // 默认内容页
  return (
    <div className="h-full flex flex-col">
      <input
        type="text"
        value={localContent.title || ""}
        onChange={(e) => handleUpdate({ title: e.target.value })}
        placeholder="幻灯片标题"
        className="text-3xl font-bold bg-transparent border-b border-transparent hover:border-white/20 focus:border-white/40 focus:outline-none pb-2 mb-4 transition-colors"
      />
      <textarea
        value={localContent.text || ""}
        onChange={(e) => handleUpdate({ text: e.target.value })}
        placeholder="在此输入内容..."
        className="flex-1 bg-transparent resize-none focus:outline-none text-lg leading-relaxed"
      />
      {localContent.bullets?.length > 0 && (
        <div className="mt-4 space-y-1">
          {localContent.bullets.map((bullet: string, i: number) => (
            <div key={i} className="flex items-center gap-2 text-white/70">
              <span>•</span>
              <span>{bullet}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
