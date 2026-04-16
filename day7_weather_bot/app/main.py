from fastapi import FastAPI
from pydantic import BaseModel
# 1. 导入 CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

from .llm_service import get_ai_advice,extract_temperature_value
from .data_service import get_real_weather_data

app = FastAPI(title="AI Weather Service")

# 2. 在这里添加 CORS 中间件配置
# 这允许前端（HTML/JS）跨域访问你的 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发阶段用 * 最方便，生产环境建议指定具体域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（GET, POST, OPTIONS 等）
    allow_headers=["*"],  # 允许所有请求头
)

class CityRequest(BaseModel):
    city_name: str

class WeatherResponse(BaseModel):
    city: str
    temperature: str
    condition: str
    ai_advice: str

@app.post("/get_weather", response_model=WeatherResponse)
async def get_weather(request: CityRequest):
    city = request.city_name

    # 1. 调用数据服务获取真实天气
    weather_data = get_real_weather_data(city)

    if not weather_data:
        # 即使没有数据，也调用 AI，但传入特定标记
        ai_advice = get_ai_advice(city, "Unknown", "Unknown")
        return {
            "city": city,
            "temperature": "Unknown",
            "condition": "Unknown",
            "ai_advice": ai_advice
        }

    # 2. 如果有数据，正常处理
    temp = weather_data['temperature']
    condition = weather_data['condition']

    # 提取纯数字温度用于逻辑判断（如果需要）
    temp_value = extract_temperature_value(temp)

    ai_advice = get_ai_advice(city, temp, condition, temp_value)

    return {
        "city": city,
        "temperature": temp,
        "condition": condition,
        "ai_advice": ai_advice
    }