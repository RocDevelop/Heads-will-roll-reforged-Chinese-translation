import re
import os
from typing import List

class NewStringExtractor:
    """
    从Ren'Py翻译文件中提取new字符串的类
    """
    
    def __init__(self):
        """初始化提取器"""
        self.results = []
        
    def extract_new_strings(self, text: str) -> List[str]:
        """
        从文本中提取行首为空的new后面的字符串
        保留双引号和转义字符，完全一模一样
        
        :param text: 输入文本
        :return: 提取到的字符串列表（包含双引号）
        """
        # 正则表达式：匹配行首空白 + new + 空白 + 引号内容
        pattern = r'^\s*old\s+(".*")\s*$'
        
        results = []
        
        # 按行处理
        for line in text.split('\n'):
            match = re.match(pattern, line)
            if match:
                # 提取完整的引号字符串，保持原样
                results.append(match.group(1))
                # 检查结果中是否包含中文，如果包含则跳过

                
        filtered_results = []
        for result in results:
            # 检查是否包含中文字符
            if not any('\u4e00' <= char <= '\u9fff' for char in result):
                filtered_results.append(result)

        # 过滤掉以https开头的字符串
        filtered_results = [result for result in filtered_results if not result.strip().startswith('"https')]
        
        # 使用集合去重
        filtered_results = list(set(filtered_results))

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
        处理目标文件，提取new字符串
        
        :param target_filename: 目标文件名
        :return: 提取到的字符串列表（去掉双引号）
        """
        try:
            # 读取文件
            with open(target_filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取new字符串（包含双引号）
            quoted_strings = self.extract_new_strings(content)
            
            # 去掉双引号
            unquoted_strings = self.remove_quotes(quoted_strings)
            
            # 保存结果
            self.results = unquoted_strings
            
            print(f"从文件 {target_filename} 中提取到 {len(unquoted_strings)} 个字符串")
            
            return unquoted_strings
            
        except FileNotFoundError:
            print(f"文件未找到: {target_filename}")
            return []
        except Exception as e:
            print(f"处理文件时出错: {e}")
            return []
    
    def save_to_deals_folder(self, target_filename: str, strings: List[str] = None) -> str:
        """
        将提取的字符串保存到deals文件夹下
        
        :param target_filename: 原文件名
        :param strings: 要保存的字符串列表，如果为None则使用self.results
        :return: 输出文件路径
        """
        if strings is None:
            strings = self.results
        
        # 确保deals文件夹存在
        deals_folder = "deals"
        if not os.path.exists(deals_folder):
            os.makedirs(deals_folder)
            print(f"创建了文件夹: {deals_folder}")
        
        # 生成输出文件名
        base_name = os.path.splitext(os.path.basename(target_filename))[0]
        output_filename = f"8_{base_name}_dictA.rpy"
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
    
    def run(self, target_filename: str) -> str:
        """
        完整的处理流程：读取文件 -> 提取字符串 -> 保存到deals文件夹
        
        :param target_filename: 目标文件名
        :return: 输出文件路径
        """
        print(f"开始处理文件: {target_filename}")
        
        # 处理文件
        extracted_strings = self.process_file(target_filename)
        
        if extracted_strings:
            # 保存到deals文件夹
            output_path = self.save_to_deals_folder(target_filename, extracted_strings)
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
    # 处理文件（完整流程）
    output_file = extractor.run("common.rpy")
    # 预览结果
    extractor.preview_results()    