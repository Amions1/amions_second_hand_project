
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import ChatMessage
from trade.models import User

#获取聊天用户列表
@method_decorator(csrf_exempt, name='dispatch')
class ChatUsersView(View):
    def get(self, request):
        try:
            # 从请求中获取当前用户ID
            user_id = request.GET.get('user_id')
            if not user_id:
                return JsonResponse({
                    'status': '400',
                    'msg': '缺少用户ID参数',
                    'data':[]
                })
            
            user_id = int(user_id)
            
            # 查询该用户参与的所有聊天记录
            sent_messages = ChatMessage.objects.filter(sender_id=user_id)
            received_messages = ChatMessage.objects.filter(receiver_id=user_id)
            
            # 获取所有聊天对象的信息
            chat_partners = self._get_chat_partners(user_id, sent_messages, received_messages)
            
            # 获取用户详细信息
            partner_ids = list(chat_partners.keys())
            users_info = self._get_users_info(partner_ids)
            
            # 组装最终数据
            result_data = self._assemble_result_data(chat_partners, users_info)
            
            return JsonResponse({
                'status': '200',
                'msg': '获取聊天用户列表成功',
                'data': result_data,
                'count': len(result_data)
            })
            
        except ValueError:
            return JsonResponse({
                'status': '400',
                'msg': '用户ID格式错误',
                'data':[]
            })
        except Exception as e:
            return JsonResponse({
                'status': '500',
                'msg': f'服务器内部错误: {str(e)}',
                'data': []
            })
    
    def _get_chat_partners(self, user_id, sent_messages, received_messages):
        """获取聊天伙伴信息"""
        chat_partners = {}
        
        # 处理发送的消息
        for msg in sent_messages:
            partner_id = msg.receiver_id
            if partner_id != user_id:
                if partner_id not in chat_partners:
                    chat_partners[partner_id] = {
                        'id': partner_id,
                        'last_message': msg.content,
                        'last_time': msg.created_at,
                        'message_count': 0
                    }
                # 更新为最新的消息
                if msg.created_at > chat_partners[partner_id]['last_time']:
                    chat_partners[partner_id]['last_message'] = msg.content
                    chat_partners[partner_id]['last_time'] = msg.created_at
                chat_partners[partner_id]['message_count'] += 1
        
        # 处理接收的消息
        for msg in received_messages:
            partner_id = msg.sender_id
            if partner_id != user_id:
                if partner_id not in chat_partners:
                    chat_partners[partner_id] = {
                        'id': partner_id,
                        'last_message': msg.content,
                        'last_time': msg.created_at,
                        'message_count': 0
                    }
                # 更新为最新的消息
                if msg.created_at > chat_partners[partner_id]['last_time']:
                    chat_partners[partner_id]['last_message'] = msg.content
                    chat_partners[partner_id]['last_time'] = msg.created_at
                chat_partners[partner_id]['message_count'] += 1
        
        return chat_partners
    
    def _get_users_info(self, user_ids):
        """获取用户详细信息"""
        users_info = {}
        if user_ids:
            users = User.objects.filter(id__in=user_ids)
            for user in users:
                users_info[user.id] = {
                    'id': user.id,
                    'nickname': user.nickname,
                }
        return users_info
    
    def _assemble_result_data(self, chat_partners, users_info):
        """组装最终返回的数据"""
        result_data = []
        for partner_id, partner_data in chat_partners.items():
            if partner_id in users_info:
                user_info = users_info[partner_id]
                result_data.append({
                    'id': user_info['id'],
                    'name': user_info['nickname'],
                    'nickname': user_info['nickname'],
                    'last_message': partner_data['last_message'][:50] + '...' if len(partner_data['last_message']) > 50 else partner_data['last_message'],
                    'last_time': partner_data['last_time'].isoformat(),
                    'unread_count': 0,
                    'message_count': partner_data['message_count']
                })
        
        # 按最后消息时间排序
        result_data.sort(key=lambda x: x['last_time'], reverse=True)
        return result_data

#获取历史聊天记录
@method_decorator(csrf_exempt, name='dispatch')
class ChatHistoryView(View):
    def get(self, request, room_name):
        try:
            # 验证房间名格式
            if not room_name or not room_name.startswith('room_'):
                return JsonResponse({
                    'status': '400',
                    'msg': '房间名格式错误',
                    'data':[]
                })
            
            # 查询该房间的所有聊天记录，按时间升序排列
            messages = ChatMessage.objects.filter(
                room_name=room_name
            ).select_related('sender', 'receiver').order_by('created_at')
            
            # 转换为前端需要的格式
            history_data = []
            for msg in messages:
                history_data.append({
                    'sender_id': msg.sender.id,
                    'receiver_id': msg.receiver.id,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat(),
                    'timestamp': msg.created_at.timestamp(),
                    'message_type': msg.message_type,
                    'is_read': msg.is_read
                })
            
            return JsonResponse({
                'status': '200',
                'msg': '获取聊天历史成功',
                'data': history_data,
                'count': len(history_data)
            })
            
        except Exception as e:
            return JsonResponse({
                'status': '500',
                'msg': f'服务器内部错误: {str(e)}',
                'data': []
            })



