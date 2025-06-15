import os
import re
import time
from pathlib import Path
from tqdm import tqdm
from typing import List, Dict, Tuple
import requests

class RenPyBatchTranslator:
    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: str = "https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        # 优化后的命令匹配正则，覆盖更多Ren'Py语法
        self.command_pattern = re.compile(r'(\{[\w=#\.+\-/]+\}|\[.*?\])')
        self.last_error = None
        self.rate_limit_delay = 1  # 基础延迟(秒)

    def _protect_commands(self, text: str) -> Tuple[str, Dict[str, str]]:
        """保护所有Ren'Py命令和格式标记"""
        commands = {}
        protected_text = text
        index = 0
        
        for match in self.command_pattern.finditer(text):
            cmd = match.group(1)
            placeholder = f"__RP{index}__"
            commands[placeholder] = cmd
            protected_text = protected_text.replace(cmd, placeholder, 1)
            index += 1
            
        return protected_text, commands

    def _restore_commands(self, text: str, command_map: Dict[str, str]) -> str:
        """将保护后的文本恢复原始Ren'Py命令"""
        restored_text = text
        for placeholder, cmd in command_map.items():
            restored_text = restored_text.replace(placeholder, cmd)
        return restored_text

    def _create_batch_prompt(self, batch: List[str]) -> str:
        """为批量翻译创建专业提示词"""
        protected_batch = []
        command_maps = []
        
        for line in batch:
            protected, cmd_map = self._protect_commands(line)
            protected_batch.append(protected)
            command_maps.append(cmd_map)
        
        batch_text = "\n".join([f"[LINE {i}] {line}" for i, line in enumerate(protected_batch)])
        
        return """你是一个专业的Ren'Py游戏本地化引擎。请将以下英文文本块精确翻译成中文，所有文本都来自一款中世纪题材的RPG游戏，因此对于其中的一些术语你应该清楚并且保持多次翻译结果能一致。严格遵守规则：
# 翻译规则
1. 保留所有Ren'Py命令(如{{color=#FFF}}、{{size=+2}})和格式标记，位置/内容必须完全不变
2. 命令若分割单词(如"{font=yahei.ttf}{color=#8B0000}{size=+70}H{/size}{/color}{/font}eater Shield")，则先找出完整的单词即Heater Shield，然后将其进行翻译，这个例子里翻译为熨斗盾，之后保留命令和单词开头，最终组合为{font=yahei.ttf}{color=#8B0000}{size=+70}H{/size}{/color}{/font}熨斗盾)
3. 严格保持行对行翻译 - [LINE X]必须对应输出[LINE X]
4. 不要翻译任何技术标记(如[variable]、[image])，只翻译人类可读文本
5. 保留所有原始标点、换行和缩进
6. 确保结果可直接在Ren'Py中运行

除了你了解的RPG术语之外，我这里还有一些先验知识，你必须知道
AGI=敏捷
END=耐力
CRD=协调
STR=力量
Civil Talent=生活天赋

# 重要示例
输入: [LINE 1] {{color=#A9A9A9}}Travel to Avignon
输出: [LINE 1] {{color=#A9A9A9}}前往阿维尼翁

输入: [LINE 2] {{vspace=5}}*Endurance: +3
输出: [LINE 2] {{vspace=5}}*耐力: +3

输入: [LINE 3] {color=#8B0000}{size=+70}M{/size}{/color}{/font}iseriecorde
输出: [LINE 3] {color=#8B0000}{size=+70}慈悲{/size}{/color}{/font}
我给你解释为什么这么翻译：这里需要先找出完整的单词即miseriecorde，然后将其进行翻译，这个例子里翻译为慈悲，之后保留命令和单词开头，最终组合为{color=#8B0000}{size=+70}{/size}慈悲{/color}{/font}

输入: [LINE 4] {font=GoudyInitialen.ttf}{color=#8B0000}{size=+70}H{/size}{/color}{/font}eater Shield"
输出: [LINE 4] {font=GoudyInitialen.ttf}{color=#8B0000}{size=+70}H{/size}{/color}{/font}熨斗盾
我给你解释为什么这么翻译：这里需要先找出完整的单词即Heater Shield，然后将其进行翻译，这个例子里翻译为熨斗盾，之后保留命令和单词开头，最终组合为{font=GoudyInitialen.ttf}{color=#8B0000}{size=+70}H{/size}{/color}{/font}熨斗盾。这是因为GoudyInitialen字体专门用来美化开头字母，所以需要保留。这条规则非常重要必须严格执行！！！！！

输入: [LINE 5] {size=-5}Exhausted! {color=#8B0000}{font=DejaVuSans.ttf}{b}V{/b}{/font}{/color}{vspace=3}{size=-2}{color=#A9A9A9}    Fatigue builds up with every action a character{vspace=3}    takes. As it reaches higher levels the character{vspace=3}    becomes increasingly less combat effective.
输出: [LINE 5] {size=-5}精疲力尽! {color=#8B0000}{font=DejaVuSans.ttf}{b}V{/b}{/font}{/color}{vspace=3}{size=-2}{color=#A9A9A9}    角色每次行动都会积累疲劳值。{vspace=3}    当达到更高等级时，角色的战斗效率会{vspace=3}    逐渐降低。
我给你解释为什么这么翻译：这里的特点在于使用了DejaVuSans字体，这个字体是用来特殊化等级的，因此这里的V保持不动。其他部分按照之前的规则翻译即可
""" + f"""

 待翻译文本(共{len(batch)}行):
{batch_text}
# 输出要求
严格按以下格式返回，包含所有[LINE X]标记:
[LINE 0] 翻译行0
[LINE 1] 翻译行1
...
[LINE N] 翻译行N"""

    def _parse_batch_response(self, response: str, command_maps: List[Dict[str, str]]) -> List[str]:
        """解析批量翻译结果并恢复命令"""
        lines = []
        for line in response.split('\n'):
            if not line.strip():
                continue
                
            # 提取行号和内容
            match = re.match(r'^\[LINE (\d+)\]\s*(.*)', line)
            if not match:
                continue
                
            line_num = int(match.group(1))
            content = match.group(2)
            
            if line_num < len(command_maps):
                # 恢复该行的命令标记
                restored = self._restore_commands(content, command_maps[line_num])
                lines.append(restored + '\n')  # 保留原换行符
        
        return lines

    def translate_batch(self, batch: List[str]) -> List[str]:
        """翻译一个文本批次(100行)"""
        if not batch:
            return []
            
        # 准备批量数据
        protected_batch = []
        command_maps = []
        for line in batch:
            protected, cmd_map = self._protect_commands(line)
            protected_batch.append(protected)
            command_maps.append(cmd_map)
        
        prompt = self._create_batch_prompt(batch)
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 1.3,
            "max_tokens": 4000,  # 增加token限额
            "top_p": 0.9
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60  # 延长超时
            )
            
            if response.status_code != 200:
                self.last_error = f"API错误 {response.status_code}: {response.text}"
                print(f"\n错误: {self.last_error}")
                return batch  # 失败时返回原文
                
            translated = response.json()["choices"][0]["message"]["content"]
            return self._parse_batch_response(translated, command_maps)
            
        except Exception as e:
            self.last_error = f"请求异常: {str(e)}"
            print(f"\n错误: {self.last_error}")
            return batch

    def process_file(self, input_file: str, batch_size: int = 100, test_mode: bool = False):
        """处理整个文件，支持从中断处恢复"""
        input_path = Path(input_file)
        if not input_path.exists():
            print(f"错误: 文件不存在 {input_file}")
            return
            
        output_dir = input_path.parent 
        output_dir.mkdir(exist_ok=True)
        output_name = input_path.name.replace("_dictA.txt", "_dictB.txt")
        output_file = output_dir / output_name
        temp_file = output_file.with_suffix('.tmp')

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return
        
        lines_to_process = source_lines
        if test_mode:
            lines_to_process = source_lines[:300]
            print(f"测试模式：只处理前{len(lines_to_process)}行")
        
        total_lines = len(lines_to_process)
        translated_lines = []
        start_from_line = 0

        if temp_file.exists():
            print(f"检测到临时文件 {temp_file}，尝试从中恢复...")
            try:
                with open(temp_file, 'r', encoding='utf-8') as f:
                    translated_lines = f.readlines()
                start_from_line = len(translated_lines)
                
                if start_from_line > total_lines:
                    print("临时文件行数大于源文件，将从头开始翻译。")
                    start_from_line = 0
                    translated_lines = []
                else:
                    print(f"成功恢复 {start_from_line} 行，将从该行继续。")

            except Exception as e:
                print(f"读取临时文件失败: {str(e)}，将从头开始。")
                translated_lines = []
                start_from_line = 0
        
        with tqdm(total=total_lines, desc="翻译进度", initial=start_from_line) as pbar:
            batches_processed_count = 0
            for i in range(start_from_line, total_lines, batch_size):
                batch = lines_to_process[i:i + batch_size]
                
                if not any(line.strip() for line in batch):
                    translated_lines.extend(batch)
                    pbar.update(len(batch))
                    continue
                
                translated_batch = self.translate_batch(batch)
                
                if len(translated_batch) != len(batch):
                    print(f"\n警告: 批处理返回行数({len(translated_batch)})与发送行数({len(batch)})不匹配。为保证文件完整性，该批次使用原文。")
                    translated_batch = batch

                translated_lines.extend(translated_batch)
                pbar.update(len(batch))
                
                if self.last_error and "rate limit" in self.last_error.lower():
                    delay = min(self.rate_limit_delay * 2, 60)
                    print(f"\n速率限制，等待{delay}秒...")
                    time.sleep(delay)
                else:
                    time.sleep(self.rate_limit_delay)
                
                batches_processed_count += 1
                if batches_processed_count > 0 and batches_processed_count % 10 == 0:
                    self._save_temp_result(output_file, translated_lines)
        
        self._save_final_result(output_file, translated_lines)
        print("\n处理完成！统计信息:")
        print(f"输入文件: {input_file}")
        print(f"输出文件: {output_file}")
        print(f"总行数: {total_lines} | 成功: {len(translated_lines)}")
        
    def _save_temp_result(self, output_file: Path, lines: List[str]):
        """保存临时结果"""
        temp_file = output_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception as e:
            print(f"临时保存失败: {str(e)}")

    def _save_final_result(self, output_file: Path, lines: List[str]):
        """保存最终结果并删除临时文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"结果已保存到: {output_file}")
        except Exception as e:
            print(f"写入最终文件失败: {str(e)}")
            return

        temp_file = output_file.with_suffix('.tmp')
        if temp_file.exists():
            try:
                os.remove(temp_file)
            except OSError as e:
                print(f"警告: 无法删除临时文件 {temp_file}: {e}")


import argparse
args = argparse.ArgumentParser()
args.add_argument("--target_file", type=str, default=None)
args = args.parse_args()

if __name__ == "__main__":

    with open('0 deepseek key.txt', encoding='utf-8') as f:
        key = f.read().strip()  

    API_KEY = key  # 替换为实际API密钥
    
    # 配置参数
    BATCH_SIZE = 10  # 每批处理行数(可调整)
    
    # if args.target_file:
    #     if args.target_file.endswith('.rpy'):
    #         args.target_file = args.target_file[:-4]
    #     INPUT_FILE = f'./deals/{args.target_file}_source.rpy1'
    # else:
    #     INPUT_FILE = "./deals/script_source.rpy1"
    
    translator = RenPyBatchTranslator(api_key=API_KEY)
    
    # 先测试300行
    # print("=== 测试模式 ===")
    # r = translator.translate_batch([
    #     "{font=yahei.ttf}{color=#8B0000}{size=+70}W{/size}{/color}{/font}ooden shield",
    #     "{font=MedievalAlphabet.ttf}{color=#8B0000}{size=+70}P{/size}{/color}{/font}oor Man's Shield"
    # ])
    # print(r)

    
    # 完整运行(确认测试OK后取消注释)
    # print("\n=== 完整模式 ===")

    INPUT_FILE = "./deals/0_dictA.txt"
    translator.process_file(INPUT_FILE, batch_size=BATCH_SIZE, test_mode=False)