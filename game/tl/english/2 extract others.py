import re
import os
from typing import List

class NewStringExtractor:
    """
    从Ren'Py翻译文件中提取特定字符串的类
    提取规则：
    1. 行首为空的指定关键字后面的字符串
    2. nvl clear下一行的字符串（如果不是空行）
    """
    
    def __init__(self):
        """初始化提取器"""
        self.results = []

    def is_composed_only_of_commands(self, text):
        """
        检查一个字符串是否完全由 {...} 或 [...] 片段组成。
        """
        pattern = r'\{.*?\}|\[.*?\]'
        
        # 使用 re.sub 将所有匹配到的片段替换为空字符串
        remainder = re.sub(pattern, '', text)
        
        # 去掉残余部分可能存在的空格后，检查是否为空。
        # 如果为空，说明原始字符串完全由命令片段组成。
        return not remainder.strip()

    def has_english_in_free_text(self, text):
        """
        检查一个字符串在移除 {...} 和 [...] 片段后，
        剩下的部分是否包含英文字母。
        """
        # 步骤 1: 移除所有被 {...} 或 [...] 包裹的命令片段
        command_pattern = r'\{.*?\}|\[.*?\]'
        free_text = re.sub(command_pattern, '', text)
        
        # 步骤 2: 检查剩下的'自由文本'是否包含任何英文字母
        # re.search() 如果找到匹配项则返回一个对象(True)，否则返回None(False)。
        return re.search(r'[a-zA-Z]', free_text) is not None

        
    def extract_strings(self, text: str) -> List[str]:
        """
        从文本中提取指定位置的字符串
        提取规则：
        1. 行首为空的指定关键字后面的字符串
        2. nvl clear下一行的字符串（如果不是空行）
        
        :param text: 输入文本
        :return: 提取到的字符串列表（包含双引号）
        """
        results = []
        lines = text.split('\n')
        
        # 支持的关键字列表
        # 不再需要预定义关键字列表，因为我们现在匹配任意英文连续字符串
        
        for i, line in enumerate(lines):
            # 规则1: 匹配行首空白 + 任意英文连续字符串 + 空格 + 双引号字符串
            # 使用正则表达式匹配：行首空白 + 任意英文字母组成的单词(长度>=1) + 空白 + 双引号字符串
            if line.strip().startswith('old'):
                continue

            keyword_pattern = r'^\s*([a-zA-Z]+)\s+(".*")\s*$'
            keyword_match = re.match(keyword_pattern, line)
            if keyword_match:
                results.append(keyword_match.group(2))  # 注意这里是group(2)，因为group(1)是关键字
                continue
            
            # 新增规则：匹配行首为双引号的字符串（允许前面有空格）
            if line.strip().startswith('"'):
                results.append(line.strip().strip('"'))
                continue
            
            # 规则2: 匹配nvl clear下一行的字符串
            if line.strip() == 'nvl clear':
                # 检查下一行
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # 如果下一行不是空行，提取双引号字符串
                    if next_line.strip():  # 不是空行
                        # 匹配双引号字符串
                        quote_pattern = r'^\s*(".*")\s*$'
                        quote_match = re.match(quote_pattern, next_line)
                        if quote_match:
                            results.append(quote_match.group(1))
        

        # 检查结果中是否包含中文，如果包含则跳过
        filtered_results = []
        for result in results:
            # 检查是否包含中文字符
            if not any('\u4e00' <= char <= '\u9fff' for char in result):
                filtered_results.append(result)

        # 去掉双引号
        filtered_results = [result.strip('"') for result in filtered_results]

        # 过滤掉以https开头的字符串
        filtered_results = [result for result in filtered_results if not result.strip().startswith('https')]

        # 过滤掉空字符串
        filtered_results = [result for result in filtered_results if not result.strip() == '']
        
        # 过滤掉被方括号包裹的命令字符串
        filtered_results = [result for result in filtered_results if not (result.strip().startswith('[') and result.strip().endswith(']'))]

        # 过滤掉不包含英文字母的句子
        filtered_results = [s for s in filtered_results if self.has_english_in_free_text(s)]

        # 过滤只有命令的句子
        filtered_results = [s for s in filtered_results if not self.is_composed_only_of_commands(s)]

        # 使用有序字典去重但保持原来的顺序
        filtered_results = list(dict.fromkeys(filtered_results))
        results = filtered_results
        return results
    
    def remove_quotes(self, quoted_strings: List[str]) -> List[str]:
        """
        去掉字符串两端的双引号，保留内部的转义字符
        
        :param quoted_strings: 包含双引号的字符串列表
        :return: 去掉双引号的字符串列表
        """
        unquoted_strings = []
        for s in quoted_strings:
            if s.startswith('"') and s.endswith('"') and len(s) >= 2:
                # 去掉首尾的双引号
                unquoted_strings.append(s[1:-1])
            else:
                # 如果格式不对，保持原样
                unquoted_strings.append(s)
        
        return unquoted_strings
    
    def process_file(self, target_filename: str) -> List[str]:
        """
        处理目标文件，提取字符串
        
        :param target_filename: 目标文件名
        :return: 提取到的字符串列表（去掉双引号）
        """
        try:
            # 读取文件
            with open(target_filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取字符串（包含双引号）
            quoted_strings = self.extract_strings(content)
            
            # 去掉双引号
            unquoted_strings = self.remove_quotes(quoted_strings)
            
            print(f"从文件 {target_filename} 中提取到 {len(unquoted_strings)} 个字符串")
            
            return unquoted_strings
            
        except FileNotFoundError:
            print(f"文件未找到: {target_filename}")
            return []
        except Exception as e:
            print(f"处理文件时出错: {e}")
            return []
    
    def process_multiple_files(self, filenames: List[str]) -> List[str]:
        """
        处理多个文件，提取字符串并合并去重
        
        :param filenames: 文件名列表
        :return: 合并去重后的字符串列表
        """
        all_strings = []
        
        for filename in filenames:
            print(f"正在处理文件: {filename}")
            strings = self.process_file(filename)
            all_strings.extend(strings)
        
        # 合并后再次去重，保持顺序
        unique_strings = list(dict.fromkeys(all_strings))
        
        print(f"总共从 {len(filenames)} 个文件中提取到 {len(all_strings)} 个字符串")
        print(f"去重后剩余 {len(unique_strings)} 个字符串")
        
        self.results = unique_strings
        return unique_strings
    
    def save_to_deals_folder(self, strings: List[str] = None, output_filename: str = "0_dictA.txt") -> str:
        """
        将提取的字符串保存到deals文件夹下
        
        :param strings: 要保存的字符串列表，如果为None则使用self.results
        :param output_filename: 输出文件名
        :return: 输出文件路径
        """
        if strings is None:
            strings = self.results
        
        # 确保deals文件夹存在
        deals_folder = "deals"
        if not os.path.exists(deals_folder):
            os.makedirs(deals_folder)
            print(f"创建了文件夹: {deals_folder}")
        
        # 生成输出文件路径
        output_path = os.path.join(deals_folder, output_filename)
        
        try:
            # 保存文件
            with open(output_path, 'w', encoding='utf-8') as f:
                for string in strings:
                    f.write(string + '\n')
            
            print(f"结果已保存到: {output_path}")
            print(f"共保存了 {len(strings)} 个字符串")
            
            return output_path
            
        except Exception as e:
            print(f"保存文件时出错: {e}")
            return ""
    
    def run(self) -> str:
        """
        完整的处理流程：读取多个文件 -> 提取字符串 -> 合并去重 -> 保存到deals文件夹
        
        :return: 输出文件路径
        """
        # 定义要处理的文件列表
        filenames = ['script.rpy', 'script_dlc.rpy', 'script_dlc_1.rpy', 'script_dlc_2.rpy', 'script_dlc_3.rpy', 'script_downfall.rpy', 'screens.rpy']
        
        print(f"开始处理 {len(filenames)} 个文件")
        
        # 处理多个文件
        extracted_strings = self.process_multiple_files(filenames)
        
        if extracted_strings:
            # 保存到deals文件夹
            output_path = self.save_to_deals_folder(extracted_strings)
            return output_path
        else:
            print("没有提取到任何字符串")
            return ""
    
    def preview_results(self, limit: int = 10):
        """
        预览提取结果
        
        :param limit: 显示的最大条数
        """
        if not self.results:
            print("没有提取到任何结果")
            return
        
        print(f"=== 提取结果预览 (前{min(limit, len(self.results))}条) ===")
        for i, string in enumerate(self.results[:limit], 1):
            print(f"{i}. {repr(string)}")  # 使用repr显示转义字符
        
        if len(self.results) > limit:
            print(f"... 还有 {len(self.results) - limit} 条")

# 测试代码
if __name__ == "__main__":
    # 创建提取器实例
    extractor = NewStringExtractor()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--filename', type=str, help='文件名', default='')
args = parser.parse_args()

# 使用示例：
extractor = NewStringExtractor()
output_file = extractor.run()