import pandas as pd

# 1. 读取数据
# 确保 students.xlsx 和 main.py 在同一个文件夹
df = pd.read_excel('students.xlsx')

print("--- 原始数据 ---")
print(df)

# 2. 数据处理：计算平均分
# axis=1 表示按行计算（横向），即 (数学+英语+物理)/3
df['平均分'] = df[['数学', '英语', '物理']].mean(axis=1)

# 3. 数据筛选：找出平均分大于 80 的“学霸”
top_students = df[df['平均分'] > 80]

print("\n--- 平均分大于 80 的学霸 ---")
print(top_students[['姓名', '平均分']])

# 4. 保存结果到新文件
top_students.to_excel('top_students_result.xlsx', index=False)
print("\n结果已保存到 top_students_result.xlsx")