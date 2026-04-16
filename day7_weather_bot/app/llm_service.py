from openai import OpenAI
import os
from dotenv import load_dotenv, find_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
import re # 引入正则

# 加载环境变量
# 1. 获取当前文件 (llm_service.py) 所在的文件夹路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 拼接 .env 的完整路径 (因为 .env 就在当前目录下，所以直接拼文件名)
dotenv_path = os.path.join(current_dir, '.env')

# 3. 强制加载该路径下的文件
load_dotenv(dotenv_path)

# 调试打印：确认 Key 是否加载成功
# 运行后请观察控制台，如果看到 "✅ 成功加载..." 说明路径对了
key_status = os.getenv("DASHSCOPE_API_KEY")
if key_status:
    print("✅ 成功加载 API Key!")
else:
    print(f"❌ 失败！在路径 {dotenv_path} 没找到 Key,请检查文件内容。")

# 4. 初始化客户端
client = OpenAI(
    api_key=key_status, # 直接使用变量，如果为空会报错，正好符合预期
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 初始化 ChromaDB 客户端
# 注意：路径要指向你刚才生成的 chroma_db 文件夹
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

# 这里我们不需要 embedding_function，因为查询时会自动处理
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_collection(name="beijing_knowledge")

def get_rag_context(city: str)-> str:
    """
    从 ChromaDB 中检索与城市相关的知识片段
    """
    try:
        # 简单的关键词检索，实际生产中可以用更复杂的混合检索
        results = collection.query(
            query_texts=[city],
            n_results=2  # 只取最相关的 2 条知识
        )
        # results['documents'] 是一个二维数组，取第一个元素的列表
        documents = results['documents'][0]
        # 把所有片段拼成一段长文本
        return "\n".join(documents)
    except Exception as e:
        print(f"❌ 检索失败: {e}")
        return ""
    
def extract_temperature_value(temp_str: str) -> float:
    """
    工具函数：从 '19.94°C' 这样的字符串中提取数字 19.94
    """
    try:
        # 使用正则提取数字
        match = re.search(r"[-+]?\d*\.\d+|\d+", temp_str)
        if match:
            return float(match.group())
        return 0.0
    except:
        return 0.0

def determine_weather_strategy(temp_val: float, condition: str) -> str:
    """
    智能体核心：根据数值决定策略
    """
    # 策略 1: 极端天气预警
    if "rain" in condition.lower() or "snow" in condition.lower() or temp_val < 0:
        return "Alert Mode" # 预警模式
    
    # 策略 2: 高温预警
    if temp_val > 30:
        return "Heat Warning Mode" # 高温模式

    # 策略 3: 舒适天气 (你的截图展示的情况)
    if 10 <= temp_val <= 25:
        return "Comfortable Mode" # 舒适模式

    # 默认策略
    return "Normal Mode"
    


def get_ai_advice(city: str, temperature: str, condition: str, temp_value: float = None)-> str:
    """
    生成天气建议的核心函数。
    
    修改说明：
    1. 增加了第4个参数 temp_value (可选)，用于接收 main.py 提前计算好的数值。
    2. 增加了对 "Unknown" 的判断逻辑。
    """
    
    # 1. 判断是否为未知数据
    if temperature == "Unknown":
        # 构建一个特殊的 Prompt，告诉 AI 没有实时数据
        system_prompt = "你是一个博学的旅行顾问。"
        user_prompt = f"""
        ⚠️ 注意：系统暂时无法获取 {city} 的实时天气数据。

        请根据你通用的地理和气候知识，结合以下参考资料（如果有），给出一段通用的旅行或生活建议。
        请在回答开头诚实地告诉用户：“抱歉，我暂时没查到实时数据，但根据经验……”

        【参考资料】：
        {get_rag_context(city)}
        """
        
        try:
            completion = client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt}
                ],
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"AI 生成失败: {e}"
    
    # =================================================================================
    # 2. 如果有数据，执行原来的 Agentic Workflow 逻辑
    # =================================================================================
    # 如果 main.py 没传 temp_value，我们自己算一次
    if temp_value is None:
        temp_value = extract_temperature_value(temperature)
    
    # 决定策略
    strategy = determine_weather_strategy(temp_value, condition)
    
    # 检索知识库
    rag_context = get_rag_context(city)

    # 动态构建 System Prompt
    if strategy == "Alert Mode":
        system_role = "你是一个严肃的气象预警员。语气要急切、强调安全。"
    elif strategy == "Comfortable Mode":
        system_role = "你是一个热情的本地导游和贴心朋友。语气要轻松、活泼，多用 Emoji。"
    else:
        system_role = "你是一个专业的天气助手。语气客观、中立。"

    user_prompt = f"""
    当前策略：{strategy}
    当前城市：{city}
    当前温度：{temperature}
    天气状况：{condition}

    【参考资料】：
    {rag_context}

    请根据【当前策略】的要求，结合天气数据和参考资料，生成建议。
    """

    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {'role': 'system', 'content': system_role},
                {'role': 'user', 'content': user_prompt}
            ],
            temperature=0.7
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI 生成失败: {e}"