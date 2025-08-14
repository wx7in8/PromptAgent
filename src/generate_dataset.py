import pandas as pd
import json

excel_filepath = "datasets/train_data_2.xlsx"
sheet_name=0
json_filepath = "datasets/train_data.json"

output_data = {
    "name": "custom_task_from_excel",
    "description": "Custom task generated from Excel data, mapping conversation context to a label.",
    "keywords": [
        "text-classification",
        "custom-data"
    ],
    "preferred_score": "exact_str_match",
    "metrics": [
        "exact_str_match",
        "multiple_choice_grade"
    ],
    "examples": []
}


df = pd.read_excel(excel_filepath, sheet_name=sheet_name, header=0, dtype=str)

# 3. 确定输入和输出列的名称
# B列是第2列 (索引为1), C列是第3列 (索引为2), F列是第6列 (索引为5)
input_col_b = df.columns[1]
input_col_c = df.columns[2]
output_col_f = df.columns[3]

# 4. 用空字符串替换NaN值，防止拼接时出错
df.fillna('', inplace=True)

# (可选但推荐) 获取所有唯一的标签，用于生成 target_scores
# 这会让生成的JSON格式与您提供的示例完全一致
all_unique_labels = df[output_col_f].unique().tolist()

LABEL_TO_Q_MAP = {
    "买家拉线下": "Q0",
    "询盘后即刻拉线下": "Q1",
    "商品信息沟通阶段拉线下": "Q2",
    "交易拉线下": "Q3",
    "买家激活拉线下": "Q4",
    "订单信息沟通拉线下": "Q5",       # 兼容两种写法
    "物流信息沟通拉线下": "Q6",       # 兼容两种写法
    "订单发起后拉线下": "Q7"
    # 如果有其他标签，请在这里添加
}


for index, row in df.iterrows():
    # 组合B列和C列作为输入，并去除首尾多余的空格
    input_text = f"#### 沟通内容\n{row[input_col_b]} \n\n#### 订单时间\n{row[input_col_c]}\n\n### 输出".strip()
    # 获取F列作为输出
    label_text = row[output_col_f].strip()
    # 如果输入或输出为空，则跳过该行
    if not input_text or not label_text:
        continue
    # 创建 target_scores 字典
    # 逻辑：正确的标签得分为1，其他所有唯一标签得分为0
    # target_scores = {label: (1 if label == target_text else 0) for label in all_unique_labels}
    # 按照格式创建每条记录
    target_dict = {f"Q{i}": False for i in range(8)}
    q_identifier = LABEL_TO_Q_MAP.get(label_text)
    if q_identifier in target_dict:
        target_dict[q_identifier] = True
    example = {
        "input": input_text,
        # "target_scores": target_scores, # 如果不需要此字段，可以注释掉这行
        "target": json.dumps(target_dict)
    }
    # 将记录添加到 'examples' 列表
    output_data["examples"].append(example)


with open(json_filepath, 'w', encoding='utf-8') as f:
    # ensure_ascii=False 保证中文字符正常显示
    # indent=4         使JSON文件格式优美，易于阅读
    json.dump(output_data, f, ensure_ascii=False, indent=4)