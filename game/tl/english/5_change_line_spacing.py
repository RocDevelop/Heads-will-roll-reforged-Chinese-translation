import os

# 1. 定义要查找和替换的文本
find_text = "{size=-5}"
replace_text = "{size=-7}"
files_modified = 0

# 2. 遍历当前目录（不深入子目录）
for filename in os.listdir("."):
    # 3. 只处理 .rpy 文件
    if filename.endswith(".rpy"):
        file_path = filename
        try:
            # 4. 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 5. 逐行处理，检查是否需要替换
            modified = False
            for i, line in enumerate(lines):
                # 跳过以"old "开头的行
                if line.strip().startswith("old "):
                    continue
                # 替换size=-5为size=-7
                if find_text in line:
                    lines[i] = line.replace(find_text, replace_text)
                    modified = True
            
            # 6. 如果内容有变化，写回文件
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                print(f"已修改: {file_path}")
                files_modified += 1
        except Exception as e:
            print(f"处理文件 {file_path} 出错: {e}")

print(f"\n操作完成，共修改了 {files_modified} 个文件。")