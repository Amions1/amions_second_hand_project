"""
知识库模块 - 使用Chroma存储平台规则和帮助文档
"""
import os
from langchain_community.document_loaders import TextLoader
from langchain_classic.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 知识库配置
KB_COLLECTION_NAME = "kb_common"
KB_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
SYS_TXT_PATH = os.path.join(os.path.dirname(__file__), "load", "sys.txt")

# 全局变量存储向量数据库实例
_vector_store = None


def get_embeddings():
    """获取OpenAI嵌入模型"""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        openai_api_base=os.getenv('OPENAI_API_BASE')
    )

#初始化知识库：加载sys.txt，语义切分，存入Chroma
def init_knowledge_base():
    global _vector_store
    # 检查Chroma持久化目录是否存在
    chroma_db_path = os.path.join(KB_PERSIST_DIR, KB_COLLECTION_NAME)
    #向量化模型
    embeddings = get_embeddings()
    print(f"加载chroma: {chroma_db_path}")
    _vector_store = Chroma(
        collection_name=KB_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=chroma_db_path
    )
    
    return _vector_store


def _create_knowledge_base(embeddings, persist_path):
    """
    创建新的知识库：加载文件、切分文档、存入Chroma
    """
    # 1. 使用TextLoader加载sys.txt
    print(f"[知识库] 加载文件: {SYS_TXT_PATH}")
    loader = TextLoader(SYS_TXT_PATH, encoding='utf-8')
    documents = loader.load()
    print(f"[知识库] 成功加载文档，共 {len(documents)} 个文档")
    
    # 2. 根据语义进行切分
    # 使用RecursiveCharacterTextSplitter，按语义层次切分
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,        # 每个块的最大字符数
        chunk_overlap=100,     # 块之间的重叠字符数，保持上下文连贯
        separators=["\n\n", "\n", "。", "；", " ", ""],  # 按语义层次切分
        length_function=len,
        is_separator_regex=False
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"[知识库] 文档切分完成，共 {len(chunks)} 个文本块")
    
    # 3. 存入Chroma向量数据库
    print(f"[知识库] 开始向量化并存储到Chroma...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=KB_COLLECTION_NAME,
        persist_directory=persist_path
    )
    
    print(f"[知识库] 知识库创建完成，存储路径: {persist_path}")
    return vector_store


def search_knowledge_base(query: str, top_k: int = 3) -> str:

    global _vector_store
    
    if _vector_store is None:
        print("[知识库] 知识库未初始化，正在初始化...")
        init_knowledge_base()
    
    print(f"[知识库] 查询: {query}")
    
    # 执行相似度搜索
    results = _vector_store.similarity_search(query, k=top_k)
    
    if not results:
        return "未找到相关知识库内容"
    
    # 组合查询结果
    knowledge_content = "\n\n".join([
        f"[相关文档 {i+1}]\n{doc.page_content}"
        for i, doc in enumerate(results)
    ])
    
    print(f"[知识库] 找到 {len(results)} 条相关内容")
    return knowledge_content


def refresh_knowledge_base():
    """
    刷新知识库：删除旧知识库，重新加载sys.txt
    用于sys.txt内容更新后重新构建知识库
    """
    global _vector_store
    
    # 删除旧的持久化目录
    import shutil
    if os.path.exists(KB_PERSIST_DIR):
        shutil.rmtree(KB_PERSIST_DIR)
        print(f"[知识库] 已删除旧知识库: {KB_PERSIST_DIR}")
    
    # 重置全局变量
    _vector_store = None
    
    # 重新初始化
    return init_knowledge_base()
