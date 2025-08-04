import json
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.font_manager import FontProperties

# 设置中文字体
font = FontProperties(fname=r"C:\Windows\Fonts\simhei.ttf", size=10)

# 加载家谱JSON数据
with open('family_tree.json', 'r', encoding='utf-8') as f:
    family_data = json.load(f)

# 创建有向图
G = nx.DiGraph()

# 添加节点和边的递归函数
def add_nodes_edges(node, parent=None, level=0, pos_dict=None, level_nodes=None):
    if pos_dict is None:
        pos_dict = {}
    if level_nodes is None:
        level_nodes = {}
    
    # 添加当前节点
    G.add_node(node['name'])
    
    # 记录节点层级
    if level not in level_nodes:
        level_nodes[level] = []
    level_nodes[level].append(node['name'])
    
    # 添加父子关系边
    if parent is not None:
        G.add_edge(parent, node['name'])
    
    # 递归处理子节点
    if 'children' in node:
        for child in node['children']:
            add_nodes_edges(child, node['name'], level+1, pos_dict, level_nodes)
    
    return pos_dict, level_nodes

# 构建图结构
pos_dict, level_nodes = add_nodes_edges(family_data)

# 计算节点位置 - 改进布局算法
def calculate_positions(level_nodes):
    pos = {}
    max_level = max(level_nodes.keys())
    
    for level, nodes in level_nodes.items():
        # 计算当前层级的节点数
        num_nodes = len(nodes)
        # 计算水平间距
        x_spacing = 10.0 / (num_nodes + 1)
        # 计算垂直位置（根节点在顶部）
        y_pos = -level * 1.5  # 增加垂直间距
        
        # 为当前层级的每个节点分配位置
        for i, node in enumerate(nodes):
            x_pos = (i + 1) * x_spacing
            pos[node] = (x_pos, y_pos)
    
    return pos

# 计算节点位置
pos = calculate_positions(level_nodes)

# 绘制图形
plt.figure(figsize=(16, 12))  # 增大图形尺寸
nx.draw(G, pos, with_labels=True, node_size=2000, node_color='skyblue', 
        font_size=9, font_weight='bold', arrows=True, 
        arrowstyle='-|>', arrowsize=12, 
        font_family=font.get_name(),
        edge_color='gray', width=1.5)

# 添加标题
plt.title("何氏家谱图", fontsize=16, fontproperties=font)

# 隐藏坐标轴
plt.axis('off')

# 调整布局防止重叠
plt.tight_layout(pad=2.0)  # 增加内边距

# 保存图片
plt.savefig('familytree_improved.png', dpi=300, bbox_inches='tight')
plt.show()
