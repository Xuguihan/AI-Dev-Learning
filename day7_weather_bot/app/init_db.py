import sqlite3
import pandas as pd
import os

# 关键修改：获取当前文件所在的目录 (也就是 app 文件夹)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库路径：app/weather.db
DB_PATH = os.path.join(BASE_DIR, "weather.db")

# Excel 路径：app/weather_forecast_result.xlsx
EXCEL_FILE_PATH = os.path.join(BASE_DIR, "weather_forecast_result.xlsx")

def init_database():
    # 1. 读取 Excel 数据 (为了演示，我们假设你之前的 Excel 还在)
    df = pd.read_excel(EXCEL_FILE_PATH)

    # 2. 连接到 SQLite 数据库 (如果文件不存在，会自动创建)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 3. 创建表 (Table)
    # 如果表已经存在，先删除（演示用，实际开发不要随便删表）
    cursor.execute("DROP TABLE IF EXISTS weather_data")

    # 创建新表
    cursor.execute("""
        CREATE TABLE weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            date TEXT,
            temperature REAL,
            condition TEXT
        )
    """)

    # 4. 把 Excel 的数据插入到数据库
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO weather_data (city, date, temperature, condition)
            VALUES (?, ?, ?, ?)
        """, (row['City'], row['日期'], row['Temperature'], row['Condition']))

    # 5. 提交并关闭
    conn.commit()
    conn.close()
    print(f"✅ 数据库初始化成功！数据已写入 {DB_PATH}")

if __name__ == "__main__":
    init_database()