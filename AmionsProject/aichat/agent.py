"""
Agent大脑核心模块
"""
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# 导入工具
from .tools import (
    search_goods,
    get_goods_categories,
    get_goods_by_category,
    get_user_orders,
    get_user_related_goods,
    query_knowledge_base
)

# 加载环境变量
load_dotenv()


#创建带记忆功能的Agent大脑
def create_agent(memory):
    # 初始化大模型
    llm = ChatOpenAI(
        model_name="gpt-5.1-chat-latest",
        #temperature= 0.7,
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        openai_api_base=os.getenv('OPENAI_API_BASE')
    )

    # 构建提示词模板
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个二手商品交易系统的智能助手，你叫小小烽,
        你的创作者是吴焕烽，如果用户问你你是谁制造的，必须要回答，在回答用户问题的时候要有感情，不要机械式回答，
        你只能回答跟二手商品交易系统有关的问题，如果用户问你其他方面的无关紧要的问题，则礼貌告知。在回答用户问题的时候，不要直接回答什么分类下有什么，
        我需要的不是一个木讷的机器人，我要的是一个有感情的助手，你要根据用户的问题结合你自己就的判断去决定是否去调用工具看看有什么对应的商品，告诉用户。
        如果用户问你关于特价商品的问题，你需要调用获取商品的工具，然后找出最便宜的五个商品，并告诉用户。

    你有以下工具可以使用：
    1. query_knowledge_base - 查询平台知识库：当用户询问平台规则、帮助文档、使用说明、
       常见问题、用户行为规范、隐私政策、AI助手使用方法等问题时，必须优先调用此工具获取知识库内容后再回答
    2. search_goods - 搜索商品：当用户想要查找商品、搜索某类商品（如"手机"、"电脑"）时，
    必须调用此工具，并且你要调用get_goods_categories - 获取商品分类列表，把商品的分类也跟用户说，
    并且你要知道基本的信息，比如用户要查找手机，你要知道小米，华为等常见手机的品牌，再比如用户问零食，你要知道哪些常见的零食品牌,
    如果查不到，就礼貌告知用户，不要胡说八道,在调用search_goods时，同时也调用一下get_goods_categories - 获取商品分类列表，一起做分析
    3. get_goods_categories - 获取商品分类列表
    4. get_goods_by_category - 根据分类ID获取商品
    5. get_user_orders - 查询用户订单：当用户询问"我的订单"、"我买了什么"、"我卖了什么"、"查看订单"时，必须调用此工具
    6. get_user_related_goods - 查询我的所有商品：当用户询问"我的商品"、"我发布的商品"、"我的所有物品"时，必须调用此工具

    重要规则：
    - 当用户询问平台规则、帮助文档、使用说明、常见问题等知识性问题时，必须先调用query_knowledge_base工具查询知识库，基于查询结果回答
    - 当用户询问商品相关信息时，你必须调用相应的工具来获取数据，不要直接回答
    - 你只有查询权限，没有增删改的权限
    - 使用工具获取数据后，根据结果友好且有感情地回答用户
    - 记住对话的上下文，保持对话的连贯性"""),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])
    
    # 工具列表
    tools = [
        query_knowledge_base,
        search_goods,
        get_goods_categories,
        get_goods_by_category,
        get_user_orders,
        get_user_related_goods
    ]
    
    # 创建工具调用Agent
    agent = create_tool_calling_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )
    
    # 创建Agent执行器
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True, # 是否显示日志
        handle_parsing_errors=True
    )
    
    return agent_executor
