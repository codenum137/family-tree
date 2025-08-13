#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
家谱生成器打包脚本
使用PyInstaller将GUI程序打包成Windows可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_requirements():
    """检查打包环境"""
    print("检查打包环境...")
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False
    
    # 检查必要模块
    required_modules = ['tkinter', 'matplotlib', 'numpy']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} 已安装")
        except ImportError:
            print(f"✗ {module} 未安装")
            return False
    
    return True

def create_spec_file():
    """创建PyInstaller spec文件"""
    print("创建spec文件...")
    
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import matplotlib

block_cipher = None

# 获取matplotlib数据文件路径
mpl_data_dir = Path(matplotlib.get_data_path())

# 添加数据文件
a = Analysis(
    ['family_tree_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('markdown_parser.py', '.'),
        ('main.py', '.'),
        ('家谱数据', '家谱数据'),
        (str(mpl_data_dir), 'matplotlib/mpl-data'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        'matplotlib.backends.backend_tkagg',
        'numpy',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='家谱生成器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
)
'''
    
    with open('family_tree.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content.strip())
    
    print("✓ spec文件创建完成")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    try:
        # 运行PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'family_tree.spec']
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        
        print("✓ 构建成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_distribution():
    """创建发布包"""
    print("创建发布包...")
    
    # 创建发布目录
    dist_dir = Path("家谱工具发布包")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # 复制可执行文件
    exe_file = Path("dist/家谱生成器.exe")
    if exe_file.exists():
        shutil.copy2(exe_file, dist_dir / "家谱生成器.exe")
        print("✓ 可执行文件已复制")
    else:
        print("✗ 找不到可执行文件")
        return False
    
    # 复制家谱数据目录
    src_data_dir = Path("家谱数据")
    dst_data_dir = dist_dir / "家谱数据"
    if src_data_dir.exists():
        shutil.copytree(src_data_dir, dst_data_dir)
        print("✓ 家谱数据目录已复制")
    
    # 创建生成图片目录
    output_dir = dist_dir / "生成图片"
    output_dir.mkdir()
    print("✓ 生成图片目录已创建")
    
    # 复制瓜藤图中的图片（如果有）
    old_output_dir = Path("瓜藤图")
    if old_output_dir.exists():
        for png_file in old_output_dir.glob("*.png"):
            shutil.copy2(png_file, output_dir / png_file.name)
        print(f"✓ 已复制现有图片文件")
    
    return True

def clean_build():
    """清理构建文件"""
    print("清理构建文件...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['family_tree.spec']
    
    for dir_name in dirs_to_remove:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"✓ 已删除 {dir_name}")
    
    for file_name in files_to_remove:
        if Path(file_name).exists():
            os.remove(file_name)
            print(f"✓ 已删除 {file_name}")

def main():
    """主函数"""
    print("=" * 50)
    print("家谱生成器 - 打包脚本")
    print("=" * 50)
    
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 检查环境
    if not check_requirements():
        print("\n请先安装必要的依赖包")
        return False
    
    try:
        # 创建spec文件
        create_spec_file()
        
        # 构建可执行文件
        if not build_executable():
            return False
        
        # 创建发布包
        if not create_distribution():
            return False
        
        print("\n" + "=" * 50)
        print("打包完成！")
        print("=" * 50)
        print("发布包位置: 家谱工具发布包/")
        print("可执行文件: 家谱工具发布包/家谱生成器.exe")
        print("\n使用说明:")
        print("1. 将整个'家谱工具发布包'文件夹复制到目标电脑")
        print("2. 双击'家谱生成器.exe'即可运行")
        print("3. 家谱数据文件放在'家谱数据'文件夹中")
        print("4. 生成的图片保存在'生成图片'文件夹中")
        
        # 询问是否清理构建文件
        try:
            choice = input("\n是否清理构建文件? (y/n): ")
            if choice.lower() in ['y', 'yes']:
                clean_build()
        except KeyboardInterrupt:
            pass
        
        return True
        
    except Exception as e:
        print(f"\n✗ 打包过程中出现错误: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\n按回车键退出...")
        sys.exit(1)
    else:
        input("\n按回车键退出...")