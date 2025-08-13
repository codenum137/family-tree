#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
家谱生成器 - 图形界面版本
为长辈设计的简单易用的家谱生成工具
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
import threading
from pathlib import Path
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from markdown_parser import parse_markdown_family_tree

class FamilyTreeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("家谱生成器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 创建必要的目录
        self.setup_directories()
        
        # 创建界面
        self.create_widgets()
        
        # 刷新文件列表
        self.refresh_file_list()
    
    def setup_directories(self):
        """创建必要的目录结构"""
        # 检测是否在打包环境中运行
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件环境
            self.base_dir = Path(sys.executable).parent
        else:
            # 开发环境
            self.base_dir = Path.cwd()
            
        self.data_dir = self.base_dir / "家谱数据"
        self.output_dir = self.base_dir / "生成图片"
        
        # 创建目录
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # 兼容旧目录结构（仅在开发环境）
        if not getattr(sys, 'frozen', False):
            old_markdown_dir = self.base_dir / "markdown_file"
            old_output_dir = self.base_dir / "瓜藤图"
            
            if old_markdown_dir.exists():
                # 复制旧文件到新目录
                for file in old_markdown_dir.glob("*.md"):
                    if not (self.data_dir / file.name).exists():
                        import shutil
                        shutil.copy2(file, self.data_dir / file.name)
            
            if old_output_dir.exists():
                # 复制旧图片到新目录
                for file in old_output_dir.glob("*.png"):
                    if not (self.output_dir / file.name).exists():
                        import shutil
                        shutil.copy2(file, self.output_dir / file.name)
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = tk.Label(main_frame, text="家谱生成器", 
                              font=("Microsoft YaHei", 20, "bold"), 
                              fg="#2c3e50")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="选择家谱文件", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        tk.Label(file_frame, text="家谱文件：", font=("Microsoft YaHei", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_var = tk.StringVar()
        self.file_combo = ttk.Combobox(file_frame, textvariable=self.file_var, 
                                      font=("Microsoft YaHei", 10), state="readonly")
        self.file_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.file_combo.bind('<<ComboboxSelected>>', self.on_file_select)
        
        ttk.Button(file_frame, text="刷新列表", command=self.refresh_file_list).grid(row=0, column=2)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="文件信息预览", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        
        self.info_text = tk.Text(preview_frame, height=8, font=("Microsoft YaHei", 9), 
                                wrap=tk.WORD, state=tk.DISABLED, bg="#f8f9fa")
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        # 主要操作按钮
        ttk.Button(button_frame, text="生成家谱图", 
                  command=self.generate_tree, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="打开结果文件夹", 
                  command=self.open_output_folder).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="编辑家谱数据", 
                  command=self.edit_file).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="新建家谱文件", 
                  command=self.create_new_file).pack(side=tk.LEFT)
        
        # 状态栏
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(20, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_var = tk.StringVar(value="请选择一个家谱文件")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, 
                                    font=("Microsoft YaHei", 9), fg="#7f8c8d")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 进度条
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 帮助信息
        help_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="10")
        help_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        help_text = """使用步骤：
1. 从下拉菜单选择一个家谱文件，或点击"新建家谱文件"创建新的家谱
2. 查看文件信息预览，确认家谱数据正确
3. 点击"生成家谱图"按钮，程序会自动生成家谱图片
4. 生成完成后，点击"打开结果文件夹"查看生成的图片
5. 如需修改家谱数据，点击"编辑家谱数据"按钮"""
        
        tk.Label(help_frame, text=help_text, font=("Microsoft YaHei", 9), 
                justify=tk.LEFT, fg="#2c3e50").pack(anchor=tk.W)
    
    def refresh_file_list(self):
        """刷新文件列表"""
        try:
            files = []
            
            # 扫描新目录结构
            if self.data_dir.exists():
                for file in self.data_dir.glob("*.md"):
                    files.append(file.stem)
            
            # 兼容旧目录结构（仅在开发环境）
            if not getattr(sys, 'frozen', False):
                old_markdown_dir = self.base_dir / "markdown_file"
                if old_markdown_dir.exists():
                    for file in old_markdown_dir.glob("*.md"):
                        if file.stem not in files:
                            files.append(file.stem)
            
            # 更新下拉菜单
            self.file_combo['values'] = files
            
            if files:
                if not self.file_var.get() or self.file_var.get() not in files:
                    self.file_combo.current(0)
                    self.on_file_select(None)
                self.status_var.set(f"找到 {len(files)} 个家谱文件")
            else:
                self.file_var.set("")
                self.status_var.set("没有找到家谱文件，请点击'新建家谱文件'创建")
                self.update_info_display("")
                
        except Exception as e:
            messagebox.showerror("错误", f"刷新文件列表时出错：{str(e)}")
    
    def on_file_select(self, event):
        """文件选择事件处理"""
        selected_file = self.file_var.get()
        if not selected_file:
            return
            
        try:
            # 查找文件路径
            file_path = self.data_dir / f"{selected_file}.md"
            if not file_path.exists() and not getattr(sys, 'frozen', False):
                # 仅在开发环境查找旧目录
                file_path = self.base_dir / "markdown_file" / f"{selected_file}.md"
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 分析文件内容
                info = self.analyze_file_content(content, selected_file)
                self.update_info_display(info)
                self.status_var.set(f"已选择：{selected_file}")
            else:
                self.update_info_display("文件不存在")
                self.status_var.set("文件不存在")
                
        except Exception as e:
            self.update_info_display(f"读取文件时出错：{str(e)}")
            self.status_var.set("文件读取失败")
    
    def analyze_file_content(self, content, filename):
        """分析文件内容"""
        try:
            result = parse_markdown_family_tree(content)
            data = result.get('data')
            title = result.get('title', filename)
            
            if not data:
                return "文件内容为空或格式不正确"
            
            # 统计信息
            total_people = self.count_people(data)
            generations = data.get('generations', [])
            max_depth = self.get_max_depth(data, 0)
            
            info_lines = [
                f"家谱标题：{title}",
                f"总人数：{total_people} 人",
                f"最大代数：{max_depth} 代",
            ]
            
            if generations:
                info_lines.append(f"字辈设置：{len(generations)} 个字辈")
                info_lines.append(f"字辈列表：{' → '.join(generations[:5])}{'...' if len(generations) > 5 else ''}")
            else:
                info_lines.append("字辈设置：无")
            
            info_lines.extend([
                "",
                "家族结构预览：",
                self.preview_structure(data, 0, "")[:500] + "..." if len(self.preview_structure(data, 0, "")) > 500 else self.preview_structure(data, 0, "")
            ])
            
            return "\n".join(info_lines)
            
        except Exception as e:
            return f"分析文件时出错：{str(e)}"
    
    def count_people(self, node):
        """统计人数"""
        count = 1
        children = node.get('children', [])
        for child in children:
            count += self.count_people(child)
        return count
    
    def get_max_depth(self, node, current_depth):
        """获取最大深度"""
        children = node.get('children', [])
        if not children:
            return current_depth + 1
        
        max_child_depth = 0
        for child in children:
            child_depth = self.get_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def preview_structure(self, node, depth, prefix):
        """预览家族结构"""
        indent = "  " * depth
        name = node.get('name', '未知')
        result = f"{prefix}{indent}- {name}\n"
        
        children = node.get('children', [])
        for i, child in enumerate(children):
            if depth < 3:  # 只显示前4代
                result += self.preview_structure(child, depth + 1, prefix)
            elif i == 0:
                result += f"{prefix}{'  ' * (depth + 1)}... (还有 {len(children)} 个子孙)\n"
                break
        
        return result
    
    def update_info_display(self, info):
        """更新信息显示"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        self.info_text.config(state=tk.DISABLED)
    
    def generate_tree(self):
        """生成家谱图"""
        selected_file = self.file_var.get()
        if not selected_file:
            messagebox.showwarning("警告", "请先选择一个家谱文件")
            return
        
        # 在新线程中执行生成操作
        threading.Thread(target=self._generate_tree_thread, args=(selected_file,), daemon=True).start()
    
    def _generate_tree_thread(self, filename):
        """在线程中生成家谱图"""
        try:
            # 更新UI
            self.root.after(0, lambda: self.status_var.set("正在生成家谱图..."))
            self.root.after(0, lambda: self.progress.start())
            
            # 导入并执行家谱生成逻辑
            from main import (
                NODE_WIDTH_HORIZONTAL, NODE_HEIGHT_HORIZONTAL,
                NODE_WIDTH_VERTICAL, NODE_HEIGHT_VERTICAL,
                PADDING_HORIZONTAL, PADDING_VERTICAL, LEVEL_SPACING,
                Node, build_tree, calculate_depth, calculate_width,
                calculate_positions, set_y_coordinates, draw_family_tree
            )
            
            # 查找并加载文件
            file_path = self.data_dir / f"{filename}.md"
            if not file_path.exists() and not getattr(sys, 'frozen', False):
                file_path = self.base_dir / "markdown_file" / f"{filename}.md"
            
            if not file_path.exists():
                raise FileNotFoundError(f"找不到文件：{filename}.md")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            result = parse_markdown_family_tree(content)
            family_data = result['data']
            title = result.get('title', filename)
            
            if not family_data:
                raise ValueError("家谱数据为空")
            
            # 设置字辈信息
            GENERATIONS = family_data.get('generations', [])
            
            # 创建图形
            plt.ioff()  # 关闭交互模式
            fig, ax = plt.subplots(figsize=(20, 15))
            ax.set_aspect('equal')
            
            # 构建和计算家谱树
            root = build_tree(family_data)
            calculate_depth(root)
            calculate_positions(root)
            set_y_coordinates(root)
            
            # 绘制家谱图
            draw_family_tree(root)
            
            # 收集所有节点用于设置图形范围
            all_nodes = []
            def collect_nodes(node):
                all_nodes.append(node)
                for child in node.children:
                    collect_nodes(child)
            
            collect_nodes(root)
            
            if all_nodes:
                min_x = min(node.x - node.width/2 for node in all_nodes) - 1
                max_x = max(node.x + node.width/2 for node in all_nodes) + 1
                min_y = min(node.y - node.height/2 for node in all_nodes) - 1
                max_y = max(node.y + node.height/2 for node in all_nodes) + 1
                
                # 添加字辈标签
                depths = sorted(set(node.depth for node in all_nodes))
                
                if GENERATIONS:
                    for depth in depths:
                        if depth < len(GENERATIONS):
                            y_coord = next(node.y for node in all_nodes if node.depth == depth)
                            
                            if depth >= 2:
                                label_height = NODE_HEIGHT_VERTICAL
                            else:
                                label_height = NODE_HEIGHT_HORIZONTAL
                            
                            label_bg = patches.FancyBboxPatch(
                                (min_x - 4, y_coord - label_height/2),
                                3.5, label_height,
                                boxstyle="round,pad=0.1",
                                linewidth=1,
                                edgecolor='none',
                                facecolor='#f0f0f0',
                                alpha=0.8,
                                zorder=2
                            )
                            ax.add_patch(label_bg)
                            
                            ax.text(min_x - 2.25, y_coord, GENERATIONS[depth], 
                                   ha='center', va='center', fontsize=10, 
                                   fontweight='bold', color='#333333', zorder=3)
                
                ax.set_xlim(min_x - 5, max_x)
                plt.ylim(min_y, max_y)
            
            # 隐藏坐标轴和添加标题
            plt.axis('off')
            plt.title(title, fontsize=16, pad=20)
            
            # 保存文件
            output_path = self.output_dir / f"{title}.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # 更新UI
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.status_var.set(f"家谱图生成成功：{output_path.name}"))
            self.root.after(0, lambda: messagebox.showinfo("成功", f"家谱图生成成功！\n保存位置：{output_path}"))
            
        except Exception as e:
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.status_var.set("生成失败"))
            self.root.after(0, lambda: messagebox.showerror("错误", f"生成家谱图时出错：{str(e)}"))
    
    def open_output_folder(self):
        """打开结果文件夹"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(self.output_dir))
            else:  # macOS/Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(self.output_dir)])
            self.status_var.set("已打开结果文件夹")
        except Exception as e:
            messagebox.showerror("错误", f"打开文件夹时出错：{str(e)}")
    
    def edit_file(self):
        """编辑家谱文件"""
        selected_file = self.file_var.get()
        if not selected_file:
            messagebox.showwarning("警告", "请先选择一个家谱文件")
            return
        
        try:
            # 查找文件路径
            file_path = self.data_dir / f"{selected_file}.md"
            if not file_path.exists() and not getattr(sys, 'frozen', False):
                file_path = self.base_dir / "markdown_file" / f"{selected_file}.md"
            
            if not file_path.exists():
                messagebox.showerror("错误", f"找不到文件：{selected_file}.md")
                return
            
            # 用默认编辑器打开
            if os.name == 'nt':  # Windows
                os.startfile(str(file_path))
            else:  # macOS/Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', str(file_path)])
            
            self.status_var.set(f"已打开编辑器：{selected_file}.md")
            
        except Exception as e:
            messagebox.showerror("错误", f"打开文件时出错：{str(e)}")
    
    def create_new_file(self):
        """创建新的家谱文件"""
        try:
            # 弹出对话框获取文件名
            filename = tk.simpledialog.askstring("新建家谱文件", "请输入家谱文件名（不需要.md扩展名）：")
            if not filename:
                return
            
            # 清理文件名
            filename = filename.strip().replace('.md', '')
            if not filename:
                messagebox.showwarning("警告", "文件名不能为空")
                return
            
            file_path = self.data_dir / f"{filename}.md"
            
            if file_path.exists():
                if not messagebox.askyesno("文件已存在", f"文件 {filename}.md 已存在，是否覆盖？"):
                    return
            
            # 创建模板内容
            template_content = f"""# {filename}

## 字辈: 第一代,第二代,第三代,第四代

- 祖先姓名
  - 第二代A
    - 第三代A1
      - 第四代A1a
      - 第四代A1b
    - 第三代A2
  - 第二代B
    - 第三代B1
    - 第三代B2

---
# 使用说明：
# 1. 修改上面的"祖先姓名"为实际的祖先姓名
# 2. 字辈行是可选的，如不需要可以删除
# 3. 使用"-"加空格加姓名的格式添加家族成员  
# 4. 使用缩进（2个空格）表示代际关系
# 5. 保存文件后，在主程序中选择此文件即可生成家谱图
"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # 刷新文件列表并选择新文件
            self.refresh_file_list()
            self.file_var.set(filename)
            self.on_file_select(None)
            
            # 询问是否立即编辑
            if messagebox.askyesno("创建成功", f"家谱文件 {filename}.md 创建成功！\n是否立即打开编辑？"):
                self.edit_file()
            
        except Exception as e:
            messagebox.showerror("错误", f"创建文件时出错：{str(e)}")

def main():
    """主函数"""
    # 导入simpledialog
    import tkinter.simpledialog
    tk.simpledialog = tkinter.simpledialog
    
    root = tk.Tk()
    
    # 设置窗口图标（如果有的话）
    try:
        # 这里可以设置图标文件
        pass
    except:
        pass
    
    app = FamilyTreeGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        root.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动主循环
    root.mainloop()

if __name__ == "__main__":
    main()