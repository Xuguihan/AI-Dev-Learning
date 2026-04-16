import chromadb
import os

# 获取当前文件所在的目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 向量数据库存储路径
DB_PATH = os.path.join(BASE_DIR, "chroma_db")

def init_knowledge_base():
    # 1. 创建 ChromaDB 客户端，数据会持久化保存在本地文件夹
    client = chromadb.PersistentClient(path=DB_PATH)

    # 2. 创建一个集合（Collection），可以理解为一张表
    # 这样可以避免重复运行脚本时数据叠加或更新不生效
    try:
        client.delete_collection(name="beijing_knowledge")
        print("⚠️ 检测到旧知识库，已清除。")
    except ValueError:
        # 如果集合不存在，delete 会报错，忽略即可
        pass

    # 3. 重新创建集合
    collection = client.create_collection(name="beijing_knowledge")

    # 3. 准备一些“知识片段”（在实际项目中，这些可能来自 PDF、网页等）
    documents = [
        "北京烤鸭是全聚德的最出名，建议去前门店吃，环境好。",
        "故宫博物院周一闭馆，去的时候千万别选周一。",
        "北京的秋天最美,香山红叶一般在10月中下旬开始变红。",
        "北京地铁非常发达,但早晚高峰人非常多,尽量避开7-9点和17-19点。",
        "北京的冬天非常干燥，记得带润唇膏和护手霜。",
        "胡同游推荐去南锣鼓巷，但那里商业化较重，想体验老北京生活可以去烟袋斜街。"
    ]

    # 4. 将这些知识存入数据库
    # ids: 每个知识片段的唯一ID
    # documents: 实际的文本内容
    collection.add(
        documents=documents,
        ids=[f"id{i}" for i in range(len(documents))]
    )

    print("✅ 知识库初始化成功！已存入 ChromaDB。")

if __name__ == "__main__":
    init_knowledge_base()