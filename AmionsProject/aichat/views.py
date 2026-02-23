import json
import logging
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from langchain_classic.memory import ConversationBufferWindowMemory

from .agent import create_agent
from .knowledge_base import init_knowledge_base




# 初始化知识库（服务启动时加载）
init_knowledge_base()


logger = logging.getLogger(__name__)
@method_decorator(csrf_exempt, name='dispatch')
class AIChatView(View):
    # 存储每个用户的记忆 {user_id: ConversationBufferWindowMemory}
    _user_memories = {}
    # 最大记忆轮数
    _max_memory_turns = 10

    def _get_or_create_memory(self, user_id):
        """
        获取或创建用户的记忆对象（通过独立构造器）
        """
        if user_id is None:
            return ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=self._max_memory_turns
            )
        
        if user_id not in self._user_memories:
            logger.info(f"为用户 {user_id} 创建新的对话记忆")
            self._user_memories[user_id] = ConversationBufferWindowMemory(
                memory_key="chat_history",
                return_messages=True,
                k=self._max_memory_turns
            )
        
        return self._user_memories[user_id]

    def post(self, request):
        try:
            # 解析请求体(json格式)
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            user_id = data.get('user_id')

            if not user_message:
                return JsonResponse({
                    'status': '400',
                    'msg': '消息内容不能为空',
                    'data': []
                })

            logger.info(f"AI助手收到用户 {user_id} 的提问: {user_message}")

            # 获取或创建用户的记忆对象（通过独立构造器）
            memory = self._get_or_create_memory(user_id)
            
            # 创建带该用户记忆的agent
            agent = create_agent(memory)

            # 构建输入，可以加入用户上下文
            input_text = user_message
            if user_id:
                input_text = f"当前用户ID是{user_id}。用户问题：{user_message}"

            # 调用Agent获取回答
            response = agent.invoke({"input": input_text})
            ai_response = response.get('output', '抱歉，我暂时无法回答这个问题。')
            logger.info(f"AI助手回答用户 {user_id}: {ai_response}")

            return JsonResponse({
                'status':'200',
                'msg':'success',
                'data': {
                    'response': ai_response,
                    'type': 'ai_message'
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'status':'400',
                'msg':'请求JSON格式错误',
                'data':[]
            })
        except Exception as e:
            logger.error(f"AI助手处理请求时出错: {str(e)}")
            return JsonResponse({
                'status':'500',
                'msg':f'服务器内部错误: {str(e)}',
                'data':[]
            })
