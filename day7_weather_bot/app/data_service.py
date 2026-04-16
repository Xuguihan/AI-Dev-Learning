import sqlite3
import os

# 关键修改：必须和 init_db.py 用同样的逻辑定位数据库
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "weather.db")

def get_real_weather_data(city_name: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. 明确指定只查询我们需要的3个字段（不要 SELECT *）
        # 注意顺序：city, temperature, condition
        cursor.execute("""
            SELECT city, temperature, condition 
            FROM weather_data 
            WHERE city = ?
            ORDER BY id DESC  -- 建议加上这个，获取最新的一条
            LIMIT 1
        """, (city_name,))

        row = cursor.fetchone()
        conn.close()

        if row:
            # 2. 确保索引对应 SQL 查询的顺序
            # row[0] = city, row[1] = temperature, row[2] = condition
            return {
                "city": row[0],
                # 确保温度是字符串，加上单位
                "temperature": f"{row[1]}°C" if row[1] is not None else "Unknown",
                "condition": row[2]
            }
        else:
            return None

    except Exception as e:
        print(f"❌ 数据库错误: {e}")
        return None