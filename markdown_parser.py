import re
import json

def parse_markdown_family_tree(markdown_content):
    """
    解析markdown格式的家谱数据，转换为JSON格式
    
    格式示例：
    # 标题
    ## 字辈: 第一代,第二代,第三代,第四代
    - 第一代
      - 第二代A
        - 第三代A1
        - 第三代A2
      - 第二代B
    """
    lines = markdown_content.strip().split('\n')
    
    title = ""
    generations = []
    root_data = None
    stack = []  # 用于跟踪层级关系
    
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
            
        # 解析标题
        if line.startswith('# '):
            title = line[2:].strip()
            continue
        
        # 解析字辈信息
        if line.startswith('## 字辈:') or line.startswith('## 字辈：'):
            generations_text = line.split(':', 1)[1].strip() if ':' in line else line.split('：', 1)[1].strip()
            generations = [gen.strip() for gen in generations_text.split(',')]
            continue
            
        # 解析家谱节点
        if line.startswith(' ') or line.startswith('-'):
            # 计算缩进级别
            indent_level = 0
            temp_line = line
            
            # 移除开头的空格和破折号
            while temp_line.startswith(' ') or temp_line.startswith('-'):
                if temp_line.startswith(' '):
                    temp_line = temp_line[1:]
                    if indent_level == 0 or (indent_level > 0 and temp_line.startswith(' ')):
                        indent_level += 1
                elif temp_line.startswith('-'):
                    temp_line = temp_line[1:].strip()
                    break
            
            # 修正缩进计算（每两个空格算一级）
            indent_level = (len(line) - len(line.lstrip(' '))) // 2
            
            name = temp_line.strip()
            if not name:
                continue
                
            # 创建节点数据
            node_data = {"name": name}
            
            # 处理根节点
            if indent_level == 0:
                root_data = node_data
                stack = [root_data]
            else:
                # 调整stack到当前层级
                while len(stack) > indent_level:
                    stack.pop()
                
                # 添加到父节点
                if len(stack) > 0:
                    parent = stack[-1]
                    if 'children' not in parent:
                        parent['children'] = []
                    parent['children'].append(node_data)
                    stack.append(node_data)
    
    # 如果有字辈信息，添加到根数据中
    if generations and root_data:
        root_data["generations"] = generations
    
    return {
        "title": title,
        "data": root_data
    }

def markdown_to_json_file(markdown_file_path, json_file_path):
    """
    将markdown格式的家谱文件转换为JSON格式
    """
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        result = parse_markdown_family_tree(markdown_content)
        
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(result['data'], f, ensure_ascii=False, indent=2)
        
        return result['title']
    except Exception as e:
        print(f"转换失败: {e}")
        return None

# 测试函数
if __name__ == "__main__":
    # 测试示例
    test_markdown = """# 文达祖后藤图
- 文达
  - 明圣
    - 俊盛
      - 永盛
        - 方益
  - 明德
    - 天盛
      - 方程"""
    
    result = parse_markdown_family_tree(test_markdown)
    print("标题:", result['title'])
    print("数据:", json.dumps(result['data'], ensure_ascii=False, indent=2))