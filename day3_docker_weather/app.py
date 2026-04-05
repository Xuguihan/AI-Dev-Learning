import requests

def get_weather(city_name, api_key):
    """
    获取天气信息，并返回格式化的字符串（如果成功）
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"

    try:
        # 1. 发送请求
        response = requests.get(url, timeout=10)  # 增加超时限制，防止卡死

        # 2. 检查 HTTP 状态码
        if response.status_code == 200:
            data = response.json()

            # 3. 提取数据
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            humidity = data['main']['humidity']

            # 4. 返回格式化好的数据（而不是直接在这里打印，这样更灵活）
            return f"城市：{city_name}\n当前温度：{temp}°C\n天气状况：{desc}\n湿度：{humidity}%"

        else:
            # 如果状态码不是 200，返回错误信息
            return f"❌ 获取 {city_name} 失败。错误代码：{response.status_code}"

    except Exception as e:
        # 如果发生网络错误或其他异常，返回错误信息
        return f"❌ 获取 {city_name} 时发生网络错误：{e}"

# --- 主程序入口 ---
if __name__ == "__main__":
    # ⚠️ 请务必在这里填入你自己的 API Key
    my_api_key = "4dcbd3c79b89fe3e4d08df16ed13aa92"

    cities = ["London", "Beijing"]

    for city in cities:
        # 调用函数并接收返回值
        result = get_weather(city, my_api_key)

        # 打印返回值
        print(result)
        print("-" * 30)  # 打印分隔线