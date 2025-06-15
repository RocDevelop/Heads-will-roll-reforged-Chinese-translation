import sys
import os
import shutil

# --- 配置 ---
GUI_FILE_PATH = '../../gui.rpy'
BACKUP_DIR = './backup'

# 定义我们要进行的替换操作
# 格式为：{ "要查找的行开头": "完整的新行内容" }
REPLACEMENTS = {
    "define gui.text_font":         'define gui.text_font = "SourceHanSansSC-Regular.otf"',
    "define gui.name_text_font":    'define gui.name_text_font = "SourceHanSansSC-Bold.otf"',
    "define gui.interface_text_font":'define gui.interface_text_font = "SourceHanSansSC-Medium.otf"'
}

def main():
    """主程序"""
    print(f"开始处理文件: {GUI_FILE_PATH}")

    # --- 第一步: 备份原始文件 ---
    try:
        # 1. 确保备份目录存在，如果不存在则创建
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # 2. 获取源文件名，并构建备份文件的完整路径
        base_filename = os.path.basename(GUI_FILE_PATH)
        backup_file_path = os.path.join(BACKUP_DIR, base_filename + '.bk')
        
        # 3. 执行复制备份
        shutil.copy2(GUI_FILE_PATH, backup_file_path)
        print(f"-> 成功备份原始文件到: {os.path.abspath(backup_file_path)}")
        
    except FileNotFoundError:
        print(f"!! 错误：找不到源文件 '{GUI_FILE_PATH}'，无法进行备份和修改。")
        sys.exit(1)
    except Exception as e:
        print(f"!! 错误：备份文件时失败: {e}")
        sys.exit(1)


    # --- 第二步: 逐行读取和修改文件内容 ---
    try:
        with open(GUI_FILE_PATH, 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
    except Exception as e:
        print(f"!! 错误：读取文件时失败: {e}")
        sys.exit(1)

    new_lines = []
    lines_changed_count = 0

    for line in original_lines:
        stripped_line = line.strip()
        found_match = False
        
        for line_start, new_line_content in REPLACEMENTS.items():
            if stripped_line.startswith(line_start):
                indentation = line[:len(line) - len(line.lstrip())]
                new_line_with_indent = indentation + new_line_content + '\n'
                
                if new_line_with_indent != line:
                    new_lines.append(new_line_with_indent)
                    print(f"  -> 准备修改: {line_start}")
                    lines_changed_count += 1
                else:
                    new_lines.append(line)
                
                found_match = True
                break
        
        if not found_match:
            new_lines.append(line)

    # --- 第三步: 检查并写回文件 ---
    if lines_changed_count == 0:
        print("\n-> 文件检查完成。所有字体定义已是最新，无需修改。")
        sys.exit(0)

    try:
        with open(GUI_FILE_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"\n-> 操作完成！成功修改了 {lines_changed_count} 行字体定义。")
        print("下一步：请重启Ren'Py启动器，并 '删除持久性数据' 以确保界面完全更新。")
    except Exception as e:
        print(f"!! 错误：写入新文件时失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # 确保脚本从其所在的目录运行，这样 './backup' 路径才是正确的
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()