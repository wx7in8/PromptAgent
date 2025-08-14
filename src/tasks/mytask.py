# define task prompts for various datasets
from .base_task import BaseDataset, BaseTask
import re
import string
import json

class CustomTask(BaseTask):
    def __init__(self, 
                 train_size, 
                 eval_size,
                 test_size=None,  
                 
                 task_name = "mytask",
                 task_description = "task from my datasets",
                 data_dir='',  
                 seed=None, 
                 
                 post_instruction=True, 
                 TaskDataset=BaseDataset,
                 option_num=5, 
                 **kwargs):
        self.options = {}
        super().__init__(
                        task_name = task_name,  
                        task_description = task_description, 
                        data_dir=data_dir,
                        seed = seed,
                        train_size = train_size,
                        eval_size=eval_size,
                        test_size = test_size,
                        post_instruction = post_instruction,
                        TaskDataset=TaskDataset,
                        option_num=option_num,
                        )
        
    def load_task_dataset(self, data_dir):
        '''
            <task specific>
        '''
        json_data = self._load_json_file(data_dir)
        self.task_description = json_data['description']
        # max_example = max(json_data['examples'], key=lambda x: len(x['target_scores']))
        # self.option_num = len(max_example['target_scores'])
        return json_data
    
    def transform_format(self, data):
        original_examples = data['examples']

        examples = []
        # Extracting input and target scores
        for example in original_examples:
            question = example['input']
            if 'task_prefix' in data.keys():
                task_prefix = data['task_prefix'].strip()
                question = task_prefix+"\n"+question
            
            target = example['target']
            
            # Generating options and answer
            # options = list(target_scores.keys())
            # answer = [chr(65 + i) for i, option in enumerate(options) if target_scores[option] == 1][0]
            answer = target
            # for i, option in enumerate(options):
            #     self.options[option.lower()] = f'{chr(65 + i)}'
            # options = [f'({chr(65 + i)}) {option}' for i, option in enumerate(options)]
            # options_str = 'Options:\n'+'\n'.join(options)
            question_str = question
            
            # Formatting the output
            formatted_example = {
                'question': question_str,
                'answer': answer
            }
            examples.append(formatted_example)
        
        return examples
    
    def clean_response(self, response):
        # 1. 使用正则表达式查找所有JSON对象。
        # re.DOTALL 使得 '.' 可以匹配包括换行符在内的任意字符。
        # '\{.*?\S\}' 确保匹配到非空的、有内容的JSON
        matches = re.findall(r'\{.*?\}', response, re.DOTALL)
        # 2. 如果没有找到匹配项，返回一个无效的默认值
        if not matches:
            return "{}"
        # 3. 选择最后一个匹配项，这通常是模型的最终答案
        last_match = matches[-1]
        try:
            # 4. 将提取的字符串解析为Python字典
            parsed_json = json.loads(last_match)
            # 确保解析出来的是一个字典类型
            if not isinstance(parsed_json, dict):
                return "{}"
            # 5. 将字典重新序列化为规范的JSON字符串
            # sort_keys=True 确保键的顺序总是固定的 (Q0, Q1, Q2, ...)，
            # 这对于字符串比较至关重要。
            # separators=(',', ':') 创建最紧凑的格式，移除所有不必要的空格。
            # labels的格式是 '{"Q0": false, ...}'，有空格，所以我们不使用separators
            canonical_string = json.dumps(parsed_json, sort_keys=True)
            return canonical_string
        except json.JSONDecodeError:
            # 6. 如果解析失败，说明它不是一个有效的JSON，返回无效的默认值
            return "{}"
        
    # def clean_response(self, response):
    #     letters = string.ascii_uppercase[:self.option_num] + string.ascii_lowercase[:self.option_num]
    #     clean_pattern = r"<answer>([\s\S]*?)<\/answer>"
    #     match = re.findall(clean_pattern, response.lower())
    #     if len(match) == 0 or not match[-1].strip():
    #         pattern_str = '|'.join([re.escape(option) for option in self.options])
    #         backup_match = re.findall(pattern_str, response, re.IGNORECASE)

    #         if backup_match:
    #             return self.options[backup_match[-1].lower()]
    #         else:
    #             return 'N/A: Format error'

    #     answer = re.search(r"\([" + letters + r"]\)", match[-1])
    #     if answer is not None:
    #         return answer.group(0)[1].upper()
    #     answer = re.search(r"[" + letters + r"]", match[-1])
    #     if answer is None:
    #         return 'N/A: Format error'
    #     return answer[0].upper()
