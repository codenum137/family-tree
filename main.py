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
VERTICAL_SPACING = 1.2

# 递归计算节点位置
def calculate_positions(node, x=0, y=0, level=0, positions=None):
    if positions is None:
        positions = {}
    
    positions[node['name']] = (x, y)
    
    if 'children' in node and node['children']:
        num_children = len(node['children'])
        start_x = x - (num_children - 1) * HORIZONTAL_SPACING / 2
        
        for i, child in enumerate(node['children']):
            child_x = start_x + i * HORIZONTAL_SPACING
            child_y = y - VERTICAL_SPACING
            calculate_positions(child, child_x, child_y, level + 1, positions)
    
    return positions

# 计算所有节点位置
positions = calculate_positions(family_data)

# 创建图形
fig, ax = plt.subplots(figsize=(20, 15))
ax.set_aspect('equal')

# 绘制连接线（折线）
def draw_connections(node, positions):
    if 'children' in node and node['children']:
        parent_pos = positions[node['name']]
        parent_x, parent_y = parent_pos
        
        # 父节点底部中心坐标
        parent_bottom_x = parent_x
        parent_bottom_y = parent_y - NODE_HEIGHT/2
        
        for child in node['children']:
            child_pos = positions[child['name']]
            child_x, child_y = child_pos
            
            # 子节点顶部中心坐标
            child_top_x = child_x
            child_top_y = child_y + NODE_HEIGHT/2
            
            # 计算折线点
            mid_y = (parent_bottom_y + child_top_y) / 2
            
            # 绘制折线：父节点底部 → 垂直向下 → 水平移动 → 垂直向下 → 子节点顶部
            ax.plot([parent_bottom_x, parent_bottom_x], [parent_bottom_y, mid_y], 'k-', linewidth=1.5)
            ax.plot([parent_bottom_x, child_top_x], [mid_y, mid_y], 'k-', linewidth=1.5)
            ax.plot([child_top_x, child_top_x], [mid_y, child_top_y], 'k-', linewidth=1.5)
            
            # 递归绘制子节点的连接
            draw_connections(child, positions)

# 绘制所有连接线
draw_connections(family_data, positions)

# 绘制节点（方形边框）
def draw_nodes(node, positions):
    pos = positions[node['name']]
    x, y = pos
    
    # 创建方形节点
    rect = patches.Rectangle(
        (x - NODE_WIDTH/2, y - NODE_HEIGHT/2), 
        NODE_WIDTH, NODE_HEIGHT,
        linewidth=1.5, 
        edgecolor='black', 
        facecolor='lightblue',
        alpha=0.8
    )
    ax.add_patch(rect)
    
    # 添加文字
    ax.text(x, y, node['name'], 
            ha='center', va='center', 
            fontsize=10, fontweight='bold')
    
    # 递归绘制子节点
    if 'children' in node and node['children']:
        for child in node['children']:
            draw_nodes(child, positions)

# 绘制所有节点
draw_nodes(family_data, positions)

# 设置图形范围
all_x = [pos[0] for pos in positions.values()]
all_y = [pos[1] for pos in positions.values()]
min_x, max_x = min(all_x) - 1, max(all_x) + 1
min_y, max_y = min(all_y) - 1, max(all_y) + 1

ax.set_xlim(min_x, max_x)
ax.set_ylim(min_y, max_y)

# 添加标题和图例
plt.title('何氏家谱图', fontsize=16, fontweight='bold', pad=20)

# 创建图例
node_legend = patches.Rectangle((0, 0), 1, 1, linewidth=1.5, edgecolor='black', facecolor='lightblue', alpha=0.8)
line_legend = plt.Line2D([0], [0], color='black', linewidth=1.5)

plt.legend([node_legend, line_legend], ['家族成员', '父子关系'], 
           loc='upper right', fontsize=12)

# 隐藏坐标轴
ax.axis('off')

# 调整布局
plt.tight_layout()

# 保存图像
plt.savefig('familytree_square.png', dpi=300, bbox_inches='tight')
plt.show()
