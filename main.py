import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import numpy as np
import os
from markdown_parser import parse_markdown_family_tree

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 文达祖后藤图
TITLE = "正才祖后藤图"

# 加载家谱数据 - 支持markdown和json格式
def load_family_data(title):
    # 首先尝试加载markdown格式
    markdown_path = f'.\\markdown_file\\{title}.md'
    json_path = f'.\\json_file\\{title}.json'
    
    if os.path.exists(markdown_path):
        print(f"加载markdown格式文件: {markdown_path}")
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        result = parse_markdown_family_tree(markdown_content)
        return result['data']
    elif os.path.exists(json_path):
        print(f"加载JSON格式文件: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"找不到文件: {markdown_path} 或 {json_path}")

family_data = load_family_data(TITLE)

# 从JSON中读取字辈信息（如果没有则设为空列表）
GENERATIONS = family_data.get('generations', [])

# 设置节点参数

NODE_WIDTH_HORIZONTAL = 2 # 横向文字的节点宽度
NODE_HEIGHT_HORIZONTAL = 1  # 横向文字的节点高度
NODE_WIDTH_VERTICAL = 0.8 # 纵向文字的节点宽度（明显减小宽度）
NODE_HEIGHT_VERTICAL = 2   # 纵向文字的节点高度（明显增加高度）
PADDING_HORIZONTAL = 0.3   # 横向文字的填充距离
PADDING_VERTICAL = 0.5     # 纵向文字的填充距离（增加填充）
LEVEL_SPACING = 3         # 层级间距

# 定义节点类
class Node:
    def __init__(self, data, parent=None):
        self.data = data
        self.parent = parent
        self.children = []
        self.depth = 0
        self.width = NODE_WIDTH_HORIZONTAL  # 默认为横向宽度
        self.x = 0
        self.y = 0
        self.height = NODE_HEIGHT_HORIZONTAL  # 默认高度
        
    def add_child(self, child):
        self.children.append(child)
        child.parent = self
        child.depth = self.depth + 1
        
        # 根据深度设置节点大小
        if child.depth >= 2:  # 第三代及以后（纵向矩形）
            child.width = NODE_WIDTH_VERTICAL
            child.height = NODE_HEIGHT_VERTICAL
        else:  # 前两代（横向矩形）
            child.width = NODE_WIDTH_HORIZONTAL
            child.height = NODE_HEIGHT_HORIZONTAL

# 构建树结构
def build_tree(data, parent=None):
    node = Node(data, parent)
    
    if 'children' in data:
        for child_data in data['children']:
            child_node = build_tree(child_data, node)
            node.add_child(child_node)
    
    return node

# 计算节点深度
def calculate_depth(node):
    if node.parent:
        node.depth = node.parent.depth + 1
    
    # 根据深度设置节点大小（包括根节点）
    if node.depth >= 2:  # 第三代及以后（纵向矩形）
        node.width = NODE_WIDTH_VERTICAL
        node.height = NODE_HEIGHT_VERTICAL
    else:  # 前两代（横向矩形）
        node.width = NODE_WIDTH_HORIZONTAL
        node.height = NODE_HEIGHT_HORIZONTAL
    
    for child in node.children:
        calculate_depth(child)

# 自底向上计算节点布局宽度（用于位置计算）
def calculate_width(node):
    if not node.children:
        # 叶子节点返回1个单位作为布局宽度
        return 1
    
    total_width = 0
    for child in node.children:
        total_width += calculate_width(child)
    
    # 返回所有子节点的布局宽度总和
    return max(total_width, 1)

# 自底向上计算节点位置
def calculate_positions(node, x=0):
    # 获取布局宽度用于位置计算，考虑节点实际宽度
    layout_width = calculate_width(node)
    # 计算布局间距，对不同深度使用不同的间距系数
    if hasattr(node, 'depth') and node.depth < 2:  # 前两代使用较小的间距
        spacing_factor = 1.2
    else:  # 第三代以后使用基于宽度的间距
        spacing_factor = max(node.width, 1.0) if hasattr(node, 'width') else 1.0
    
    node.x = x + layout_width * spacing_factor / 2
    
    if not node.children:
        return
    
    child_x = x
    for child in node.children:
        child_layout_width = calculate_width(child)
        # 为子节点设置合适的间距
        if hasattr(child, 'depth') and child.depth < 2:  # 前两代
            child_spacing = 1.2
        else:  # 第三代以后
            child_spacing = max(child.width, 1.0) if hasattr(child, 'width') else 1.0
        calculate_positions(child, child_x)
        child_x += child_layout_width * child_spacing

# 设置y坐标
def set_y_coordinates(node, y=0):
    node.y = y
    
    # 根据节点深度设置y坐标间隔
    if node.depth >= 2:  # 第三代及以后
        y_spacing = max(NODE_HEIGHT_VERTICAL + PADDING_VERTICAL * 1.5, 3)  # 基于节点高度设置合理间距
    else:
        y_spacing = LEVEL_SPACING
    
    for child in node.children:
        set_y_coordinates(child, y - y_spacing)

# 绘制家谱图
def draw_family_tree(node):
    # 绘制节点
    for child in node.children:
        draw_family_tree(child)
    
    # 绘制连接线（折线）
    for child in node.children:
        # 计算连接点（从父节点底部到子节点顶部）
        x1, y1 = node.x, node.y - node.height/2
        x2, y2 = child.x, child.y + child.height/2
        
        # 计算中间点
        mid_y = (y1 + y2) / 2
        
        # 绘制折线：垂直向下 → 水平 → 垂直向下
        plt.plot([x1, x1], [y1, mid_y], 'k-', linewidth=1.5)  # 垂直向下
        plt.plot([x1, x2], [mid_y, mid_y], 'k-', linewidth=1.5)  # 水平
        plt.plot([x2, x2], [mid_y, y2], 'k-', linewidth=1.5)  # 垂直向下
    
    # 绘制节点矩形
    rect = patches.Rectangle(
        (node.x - node.width/2, node.y - node.height/2),
        node.width, node.height,
        linewidth=1, edgecolor='black', facecolor='white'
    )
    ax.add_patch(rect)
    
    # 绘制节点文字
    if node.depth < 2:  # 第一代和第二代 - 横向排列
        plt.text(
            node.x, node.y, node.data['name'],
            ha='center', va='center',
            fontsize=10
        )
    else:  # 第三代及以后 - 纵向排列
        # 将名字拆分为单个字符并用换行符连接
        vertical_name = '\n'.join(list(node.data['name']))
        plt.text(
            node.x, node.y, vertical_name,
            ha='center', va='center',
            fontsize=10, linespacing=1.2  # 增加字体大小，调整行间距
        )

# 创建图形
fig, ax = plt.subplots(figsize=(20, 15))
ax.set_aspect('equal')

# 构建树结构
root = build_tree(family_data)

# 计算节点深度
calculate_depth(root)

# 自底向上计算节点位置
calculate_positions(root)

# 设置y坐标
set_y_coordinates(root)

# 绘制家谱图
draw_family_tree(root)

# 设置图形范围
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
    # 获取所有存在的深度
    depths = sorted(set(node.depth for node in all_nodes))
    
    # 绘制字辈标签（仅在GENERATIONS非空时）
    if GENERATIONS:  # 添加判断条件
        # 为每个深度添加字辈标签
        for depth in depths:
            if depth < len(GENERATIONS):
                # 获取该深度的y坐标（取该深度任意节点的y坐标）
                y_coord = next(node.y for node in all_nodes if node.depth == depth)
                
                # 根据节点深度确定标签高度
                if depth >= 2:
                    label_height = NODE_HEIGHT_VERTICAL
                else:
                    label_height = NODE_HEIGHT_HORIZONTAL
                
                # 添加字辈标签背景
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
                
                # 添加字辈文字
                ax.text(min_x - 2.25, y_coord, GENERATIONS[depth], 
                        ha='center', va='center', fontsize=10, 
                        fontweight='bold', color='#333333', zorder=3)
    
    # 设置图形范围
    ax.set_xlim(min_x - 5, max_x)  # 扩展左侧边界以容纳字辈标签
    plt.ylim(min_y, max_y)

# 隐藏坐标轴
plt.axis('off')

# 添加标题
plt.title(TITLE, fontsize=16, pad=20)

# 保存图形
plt.savefig(f'.\\瓜藤图\\{TITLE}.png', dpi=300, bbox_inches='tight')
plt.show()
