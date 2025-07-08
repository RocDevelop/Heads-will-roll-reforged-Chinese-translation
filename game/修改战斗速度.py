import os
import time

# --- 核心配置 (这些值将由用户的选择动态决定) ---

# 1. 定义不同速度对应的字符串常量，方便管理和调用
# 注意：严格按照原始代码中的文本进行匹配
SPEED_ORIGINAL = "renpy.pause (0.8"  # 原版速度 (最慢)
SPEED_2X = "renpy.pause (0.41"       # 2倍速 (较快)
SPEED_4X = "renpy.pause (0.21"       # 4倍速 (最快)

# 2. 脚本将在当前目录(.)及所有子目录中搜索
ROOT_DIRECTORY = "."

# 3. 要处理的文件扩展名
FILE_EXTENSION = ".rpy"


def process_files(strings_to_find, replacement_string, description):
    """
    主函数，用于遍历文件并根据传入的参数执行替换。

    Args:
        strings_to_find (list): 需要查找的字符串列表。
        replacement_string (str): 用来替换的新字符串。
        description (str): 对当前操作的描述，用于打印信息。
    """
    print(f"\n--- 正在执行: {description} ---")
    print(f"目标文件类型: *{FILE_EXTENSION}")
    print(f"查找内容: {strings_to_find}")
    print(f"替换为:   {replacement_string}\n")
    
    # 等待一秒，让用户看清信息
    time.sleep(1)

    files_modified_count = 0
    files_scanned_count = 0
    
    # os.walk 会递归遍历所有子目录
    for root, dirs, files in os.walk(ROOT_DIRECTORY):
        for filename in files:
            if filename.endswith(FILE_EXTENSION):
                files_scanned_count += 1
                file_path = os.path.join(root, filename)
                
                try:
                    # 使用 with 语句确保文件被正确关闭
                    # 指定 encoding='utf-8' 对处理 .rpy 文件至关重要
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    new_content = original_content
                    
                    # 依次执行替换
                    for string_to_find in strings_to_find:
                        new_content = new_content.replace(string_to_find, replacement_string)
                    
                    # 只有在文件内容确实发生改变时，才执行写操作
                    if new_content != original_content:
                        print(f"[已修改] -> {file_path}")
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        files_modified_count += 1
                    
                except Exception as e:
                    print(f"[错误] 处理文件 {file_path} 时出错: {e}")

    print("\n--- 操作执行完毕 ---")
    print(f"总共扫描了 {files_scanned_count} 个 {FILE_EXTENSION} 文件。")
    print(f"总共修改了 {files_modified_count} 个文件。")


def main_menu():
    """
    显示主菜单并处理用户输入。
    """
    while True:
        # 清屏 (可选，但在终端中体验更好)
        # os.system('cls' if os.name == 'nt' else 'clear') 
        
        # --- 打印对小白友好的菜单界面 ---
        print("==========================================================")
        print("==                                                      ==")
        print("==              Ren'Py 游戏战斗速度修改器               ==")
        print("==                                                      ==")
        print("==========================================================")
        print("\n本工具可以批量修改 .rpy 文件中的战斗等待时间，以调整速度。")
        print("请将本程序放置在游戏的 game 文件夹里运行（默认应该就是了，千万别移动它）。\n")
        print("-------------------- 请选择要应用的速度 --------------------")
        print("  [1] 恢复原版战斗速度 (最慢，游戏默认值，适合新手)")
        print("  [2] 设置为 2 倍战斗速度 (应该大家都适合)")
        print("  [3] 设置为 4 倍战斗速度 (极快，非老手战斗词条可能跳的太快，你不习惯)")
        print("----------------------------------------------------------")
        print("  [q] 退出程序")
        print("----------------------------------------------------------\n")
        
        choice = input("请输入您的选择 (1/2/3/q) 然后按回车键（也就是键盘上的Enter键）: ").strip().lower()

        if choice == '1':
            # 逻辑: 查找所有加速版本，替换为原版
            process_files(
                strings_to_find=[SPEED_2X, SPEED_4X],
                replacement_string=SPEED_ORIGINAL,
                description="恢复原版战斗速度"
            )
            break  # 完成操作后退出循环
        
        elif choice == '2':
            # 逻辑: 查找原版和4倍速版本，替换为2倍速
            process_files(
                strings_to_find=[SPEED_ORIGINAL, SPEED_4X],
                replacement_string=SPEED_2X,
                description="设置为 2 倍战斗速度"
            )
            break
            
        elif choice == '3':
            # 逻辑: 查找原版和2倍速版本，替换为4倍速
            process_files(
                strings_to_find=[SPEED_ORIGINAL, SPEED_2X],
                replacement_string=SPEED_4X,
                description="设置为 4 倍战斗速度"
            )
            break
            
        elif choice == 'q':
            print("\n已选择退出程序。")
            break
            
        else:
            print("\n[输入无效!] 您输入的不是 1, 2, 3 或 q，请重新输入。")
            time.sleep(2) # 暂停2秒，让用户看清错误提示
            print("\n" * 2) # 打印空行以分隔

# 当该脚本被直接运行时，才执行 main_menu 函数
if __name__ == "__main__":
    main_menu()
    # 防止窗口在执行后立即关闭
    input("\n按回车键退出程序...")