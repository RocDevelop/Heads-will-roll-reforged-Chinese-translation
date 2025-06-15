import os
import shutil
import sys

class Replacer:
    """
    一个用于根据源文件和目标文件替换文本内容的类。
    """

    def process_file(self, filename_base: str):
        """
        处理单个文件集。

        :param filename_base: 文件名的基础部分 (例如, 'chapter1')
        """
        # 构建文件路径
        source_file_path = os.path.join('deals', f'9_dictA.txt')
        target_file_path = os.path.join('deals', f'9_dictB.txt')
        original_file_path = f'{filename_base}.rpy'
        backup_file_path = os.path.join('backup', f'{filename_base}.rpy.bk')

        try:
            print(f"开始处理: {original_file_path}")

            # 1. 读取源和目标文件来创建翻译映射
            translation_map = self._create_translation_map(source_file_path, target_file_path)
            if not translation_map:
                print("翻译映射为空，已跳过。")
                return

            # 2. 创建backup文件夹（如果不存在）
            backup_dir = 'backup'
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # 3. 备份原始文件，避免同名冲突
            backup_file_path = self._get_unique_backup_path(backup_file_path)
            print(f"备份原始文件到: {backup_file_path}")
            shutil.copyfile(original_file_path, backup_file_path)

            # 4. 读取原始文件并进行替换
            with open(original_file_path, 'r', encoding='utf-8') as f:
                original_lines = f.readlines()
            
            new_lines = self._replace_content(original_lines, translation_map)

            # 5. 将修改后的内容写回原始文件
            with open(original_file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"文件 {original_file_path} 已成功处理。")

        except FileNotFoundError as e:
            print(f"错误: 文件未找到 - {e}. 请确保以下文件存在:")
            print(f"  - {original_file_path}")
            print(f"  - {source_file_path}")
            print(f"  - {target_file_path}")
        except Exception as e:
            print(f"处理过程中发生未知错误: {e}")

    def _get_unique_backup_path(self, backup_file_path: str) -> str:
        """获取唯一的备份文件路径，避免同名冲突。"""
        if not os.path.exists(backup_file_path):
            return backup_file_path
        
        # 如果文件存在，依次添加数字后缀
        base_path, ext = os.path.splitext(backup_file_path)
        counter = 1
        while True:
            new_backup_path = f"{base_path}_{counter}{ext}"
            if not os.path.exists(new_backup_path):
                return new_backup_path
            counter += 1

    def _create_translation_map(self, source_path: str, target_path: str) -> dict:
        """从源文件和目标文件创建翻译映射。"""
        translation_map = {}
        with open(source_path, 'r', encoding='utf-8') as f_source, \
             open(target_path, 'r', encoding='utf-8') as f_target:
            
            source_lines = f_source.readlines()
            target_lines = f_target.readlines()

            if len(source_lines) != len(target_lines):
                print("警告: 源文件和目标文件的行数不匹配。将使用最短的长度。")

            for src, trg in zip(source_lines, target_lines):
                source_text = src.strip()
                target_text = trg.strip().replace('"', "'")
                if source_text:  # 确保源文本不为空
                    # 根据要求，源和目标字符串在匹配和替换时需要加上双引号
                    quoted_source = f'"{source_text}"'
                    quoted_target = f'"{target_text}"'
                    translation_map[quoted_source] = quoted_target
        return translation_map

    def _replace_content(self, lines: list, translation_map: dict) -> list:
        """根据翻译映射替换内容。"""
        # 按键（源字符串）长度降序排序，以优先匹配更长的字符串
        # 例如，确保 "a big dog" 在 "dog" 之前被匹配和替换
        sorted_translations = sorted(
            translation_map.items(), 
            key=lambda item: len(item[0]), 
            reverse=True
        )

        new_lines = []
        from tqdm import tqdm
        for line in tqdm(lines):
            processed_line = line
            if not processed_line.strip().startswith('old'):
                for source, target in sorted_translations:
                    if source in processed_line:
                        processed_line = processed_line.replace(source, target)
            new_lines.append(processed_line)
        return new_lines



import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='替换文本内容')
    parser.add_argument('--filename', type=str, help='文件名', default='')
    args = parser.parse_args()
    
    # if args.filename == '':
    #     args.filename = 'script_dlc'
    # filename_base = args.filename
    for filename_base in ['script', 'script_dlc', 'script_dlc_1', 'script_dlc_2', 'script_dlc_3', 'script_downfall', 'screens']:
    # for filename_base in ['script_downfall']:
        if filename_base.endswith('.rpy'):
            filename_base = filename_base[:-4]
            
        replacer = Replacer()
        replacer.process_file(filename_base)
