import requests
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei'] # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False # 用来正常显示负号

# 1. 定义获取天气的函数
def get_weather_data(city_name, api_key):
    """
    获取未来几天的天气预报数据，解析 JSON 并存入列表
    """
    # 使用 forecast 接口获取未来预测数据
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units=metric&cnt=40"

    print(f"正在从 API 获取 {city_name} 的原始数据...")

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            data_list = []

            # 解析 JSON 列表
            # 注意：API 返回的是每3小时一个时间点的数据
            for item in data['list']:
                # 提取日期时间字符串，例如 '2026-04-08 12:00:00'
                dt_text = item['dt_txt']
                # 只截取日期部分，例如 '2026-04-08'，用于后续分组
                date = dt_text.split(' ')[0]

                # 提取该时间点的预测温度
                temp = item['main']['temp']
                # 提取天气描述
                desc = item['weather'][0]['description']

                # 将数据存入字典
                row = {
                    '城市': city_name,
                    '日期': date,          # 只保留日期
                    '时间点': dt_text,     # 保留完整时间用于参考（可选）
                    '预测气温': temp,      # 这是该时间点的具体温度
                    '天气描述': desc
                }
                data_list.append(row)

            return data_list

        else:
            print(f"❌ 获取 {city_name} 失败。错误代码：{response.status_code}")
            return []

    except Exception as e:
        print(f"❌ 获取 {city_name} 时发生网络错误：{e}")
        return []

# --- 主程序入口 ---
if __name__ == "__main__":
    # ⚠️ 请务必在这里填入你自己的 API Key
    my_api_key = "4dcbd3c79b89fe3e4d08df16ed13aa92"
    target_city = "Beijing"

    # 1. 获取原始数据列表
    raw_data = get_weather_data(target_city, my_api_key)

    if raw_data:
        # 2. 数据分析与处理
        df_raw = pd.DataFrame(raw_data)

        # 核心修正步骤：按“日期”分组，计算每天的 max 和 min
        # 这会自动把同一天的所有时间点（如 00:00, 03:00...）合并
        df_grouped = df_raw.groupby('日期').agg(
            城市=('城市', 'first'),          # 取城市名（每天都是一样的）
            最高温=('预测气温', 'max'),      # 取当天所有预测气温的最大值
            最低温=('预测气温', 'min'),      # 取当天所有预测气温的最小值
            天气描述=('天气描述', lambda x: x.mode()[0] if not x.mode().empty else 'Unknown') # 取出现频率最高的天气描述
        ).reset_index()

        # 3. 计算温差
        df_grouped['温差'] = df_grouped['最高温'] - df_grouped['最低温']

        # 4. 调整列的顺序，使其更美观
        final_df = df_grouped[['城市', '日期', '最高温', '最低温', '温差', '天气描述']]

        # 5. 输出结果
        # 导出到 Excel
        output_file = "weather_forecast_result.xlsx"
        final_df.to_excel(output_file, index=False)
        print(f"数据已成功导出到 {output_file}")

        # 打印最热的天
        # 找出温差最大或者最高温最高的那一天
        hottest_row = final_df.loc[final_df['最高温'].idxmax()]
        print(f"分析结果：未来几天最热的是 {hottest_row['日期']}，最高温达到 {hottest_row['最高温']:.2f}°C")

        # 打印前几行看看效果
        print("\n表格预览：")
        print(final_df.head())

        # ==========================================
        # --- 第二部分：读取 Excel 并绘图 (新增代码) ---
        # ==========================================

        excel_file = output_file

        print(f"📊 正在读取 {excel_file} 并绘制图表...")
        
        # 1. 读取 Excel 文件
        # 确保安装了 openpyxl 库: pip install openpyxl
        df_plot = pd.read_excel(excel_file)

        # 2. 设置画布大小 (宽12英寸，高6英寸) 和 分辨率
        plt.figure(figsize=(12, 6), dpi=100)

        # 3. 绘制两条折线
        # 绘制最高温：红色线条，带圆圈标记
        plt.plot(df_plot['日期'], df_plot['最高温'], 
                 marker='o', linestyle='-', color='#FF6347', 
                 label='最高温', linewidth=2, markersize=8)

        # 绘制最低温：蓝色线条，带三角标记
        plt.plot(df_plot['日期'], df_plot['最低温'], 
                 marker='^', linestyle='-', color='#1E90FF', 
                 label='最低温', linewidth=2, markersize=8)

        # 4. 添加标题和标签 (设置中文字体以防乱码，这里使用通用设置)
        # 注意：如果你的系统没有 SimHei 字体，中文可能会显示为方块。
        # 如果乱码，可以将标题改为英文，或配置 matplotlib 字体。
        plt.title(f"{target_city} 未来5天气温趋势", fontsize=16, pad=20)
        plt.xlabel("日期", fontsize=12)
        plt.ylabel("温度 (°C)", fontsize=12)

        # 5. 添加网格线
        plt.grid(True, linestyle='--', alpha=0.7)

        # 6. 添加图例
        plt.legend(fontsize=12, loc='upper left')

        # 7. 优化布局 (防止标签被遮挡)
        plt.tight_layout()

        # 8. 保存图片到本地
        image_filename = "weather_trend.png"
        plt.savefig(image_filename, dpi=300) # dpi=300 保存高清图片
        print(f"✅ 图表已保存为 {image_filename}")

        # 显示图表 (在脚本运行结束时弹出窗口)
        plt.show()
