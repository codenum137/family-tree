import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 加载家谱数据
with open('family_tree.json', 'r', encoding='utf-8') as f:
    family_data = json.load(f)

# 设置节点参数
NODE_WIDTH = 0.8
NODE_HEIGHT = 0.4
HORIZONTAL_SPACING = 1.5
VERTICAL_SPACING = 1.5
MIN_X_SPACING = 0.5  # 节点间最小水平间距

# 构建树结构
class TreeNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children if children else []
        self.x = 0
        self.y = 0
        self.width = 0  # 节点所需宽度
        self.depth = 0  # 节点深度
        self.parent = None

    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self

# 构建树结构
def build_tree(data, parent=None):
    node = TreeNode(data['name'])
    node.parent = parent
    
    if 'children' in data:
        for child in data['children']:
            child_node = build_tree(child, node)
            node.add_child(child_node)
    
    return node

# 计算节点深度
def calculate_depth(node, depth=0):
    node.depth = depth
    for child in node.children:
        calculate_depth(child, depth + 1)

# 自底向上计算节点所需宽度
def calculate_width(node):
    if not node.children:  # 叶子节点
        node.width = NODE_WIDTH
        return node.width
    
    # 先计算所有子节点的宽度
    children_widths = []
    for child in node.children:
        children_widths.append(calculate_width(child))
    
    # 计算子节点总宽度（包括间距）
    total_children_width = sum(children_widths) + (len(node.children) - 1) * HORIZONTAL_SPACING
    
    # 父节点宽度取子节点总宽度和自身宽度的最大值
    node.width = max(total_children_width, NODE_WIDTH)
    return node.width

# 自底向上计算节点位置
def calculate_positions(node, x_offset=0):
    if not node.children:  # 叶子节点
        node.x = x_offset + node.width / 2
        return node.x, node.width
    
    # 先计算所有子节点的位置
    children_positions = []
    current_x = x_offset
    
    for child in node.children:
        child_x, child_width = calculate_positions(child, current_x)
        children_positions.append((child_x, child_width))
        current_x += child_width + HORIZONTAL_SPACING
    
    # 计算子节点位置的平均值作为父节点的x坐标
    node.x = sum(pos[0] for pos in children_positions) / len(children_positions)
    
    # 返回父节点位置和总宽度
    total_width = sum(pos[1] for pos in children_positions) + (len(node.children) - 1) * HORIZONTAL_SPACING
    return node.x, total_width

# 设置y坐标（根据深度）
def set_y_coordinates(node, y_start=0):
    node.y = y_start - node.depth * VERTICAL_SPACING
    for child in node.children:
        set_y_coordinates(child, y_start)

# 绘制家谱图
def draw_family_tree(root):
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # 先绘制所有连接线
    def draw_connections(node):
        for child in node.children:
            # 计算连接点（从父节点底部到子节点顶部）
            x1, y1 = node.x, node.y - NODE_HEIGHT/2
            x2, y2 = child.x, child.y + NODE_HEIGHT/2
            
            # 计算中间点
            mid_y = (y1 + y2) / 2
            
            # 绘制折线：垂直向下 → 水平 → 垂直向下
            ax.plot([x1, x1], [y1, mid_y], 'k-', linewidth=1.5)  # 垂直向下
            ax.plot([x1, x2], [mid_y, mid_y], 'k-', linewidth=1.5)  # 水平
            ax.plot([x2, x2], [mid_y, y2], 'k-', linewidth=1.5)  # 垂直向下
            
            # 添加箭头指示方向
            ax.annotate('', xy=(x2, y2), xytext=(x2, mid_y + 0.1),
                        arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
            
            draw_connections(child)
    
    draw_connections(root)
    
    # 再绘制所有节点（确保节点在连接线上方）
    def draw_nodes(node):
        # 绘制方形节点
        rect = patches.Rectangle(
            (node.x - NODE_WIDTH/2, node.y - NODE_HEIGHT/2),
            NODE_WIDTH, NODE_HEIGHT,
            linewidth=1.5, edgecolor='black', facecolor='white', zorder=3
        )
        ax.add_patch(rect)
        
        # 添加节点文字
        ax.text(node.x, node.y, node.name, 
                ha='center', va='center', fontsize=10, fontweight='bold', zorder=4)
        
        for child in node.children:
            draw_nodes(child)
    
    draw_nodes(root)
    
    # 设置图形范围
    all_nodes = []
    def collect_nodes(node):
        all_nodes.append(node)
        for child in node.children:
            collect_nodes(child)
    
    collect_nodes(root)
    
    min_x = min(node.x - NODE_WIDTH/2 for node in all_nodes) - 1
    max_x = max(node.x + NODE_WIDTH/2 for node in all_nodes) + 1
    min_y = min(node.y - NODE_HEIGHT/2 for node in all_nodes) - 1
    max_y = max(node.y + NODE_HEIGHT/2 for node in all_nodes) + 1
    
    ax.set_xlim(min_x, max_x)
    ax.set_ylim(min_y, max_y)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 添加标题
    plt.title('何氏家谱图', fontsize=16, fontweight='bold', pad=20)
    
    # 保存高分辨率图片
    plt.savefig('familytree.png', dpi=300, bbox_inches='tight')
    plt.show()

# 构建树结构
root = build_tree(family_data)

# 计算节点深度
calculate_depth(root)

# 自底向上计算节点宽度
calculate_width(root)

# 自底向上计算节点位置
calculate_positions(root)

# 设置y坐标
set_y_coordinates(root)

# 绘制家谱图
draw_family_tree(root)
