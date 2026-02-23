import json
import re
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None  # 初始化用户ID属性
    
    def _get_receiver_room(self, room_name, sender_id):
        """
        从聊天房间名中提取接收者的用户ID，并返回其个人房间名
        例如：room_1_2 -> 如果sender_id是1，则返回user_2；如果是2，则返回user_1
        """
        try:
            # 解析房间名格式 room_user1_user2
            match = re.match(r'room_(\d+)_(\d+)', room_name)
            if not match:
                print(f"房间名格式不正确: {room_name}")
                return None
            
            user1_id = int(match.group(1))
            user2_id = int(match.group(2))
            
            # 确定接收者ID（不是发送者的那个用户）
            receiver_id = user2_id if sender_id == user1_id else user1_id
            
            receiver_room = f"user_{receiver_id}"
            print(f"从房间 {room_name} 中确定接收者: {receiver_id}, 个人房间: {receiver_room}")
            return receiver_room
            
        except Exception as e:
            print(f"解析接收者房间失败: {str(e)}")
            return None
    
    def _parse_receiver_id_from_room(self, room_name, sender_id):
        """
        从聊天房间名中提取接收者的用户ID
        例如：room_1_2 -> 如果sender_id是1，则返回2；如果是2，则返回1
        """
        try:
            # 解析房间名格式 room_user1_user2
            match = re.match(r'room_(\d+)_(\d+)', room_name)
            if not match:
                print(f"房间名格式不正确: {room_name}")
                return None
            
            user1_id = int(match.group(1))
            user2_id = int(match.group(2))
            
            # 确定接收者ID（不是发送者的那个用户）
            receiver_id = user2_id if sender_id == user1_id else user1_id
            print(f"从房间 {room_name} 中解析出接收者ID: {receiver_id}")
            return receiver_id
            
        except Exception as e:
            print(f"解析接收者ID失败: {str(e)}")
            return None
    
    def websocket_connect(self, message):
        print("WebSocket连接请求")

        group = self.scope['url_route']['kwargs'].get("group")
        if not group:
            print("错误：未获取到房间组名")
            return

        print(f"连接到房间: {group}")

        # 允许创建连接
        self.accept()

        # 加入到指定房间
        async_to_sync(self.channel_layer.group_add)(group, self.channel_name)
        print(f"用户已加入房间: {group}")
        
        # 从URL查询参数中获取用户ID
        query_string = self.scope.get('query_string', b'').decode()
        print(f"原始查询字符串: {query_string}")
        
        from urllib.parse import parse_qs
        query_params = parse_qs(query_string)
        print(f"解析后的参数: {query_params}")
        
        user_ids = query_params.get('user_id', [])
        self.user_id = user_ids[0] if user_ids else None
        print(f"当前用户ID: {self.user_id}")

    def websocket_receive(self, message):
        print("接收到原始消息：", message)

        try:
            # 解析客户端发送的JSON数据
            data = json.loads(message['text'])
            print("解析后的数据：", data)

            # 验证必要字段
            required_fields = ['type', 'content']
            if not all(key in data for key in required_fields):
                print("消息格式不完整，缺少必要字段")
                self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "消息格式错误：缺少必要字段"
                }))
                return

            # 验证senderId（如果是聊天消息）
            if data.get('type') == 'message' and not data.get('senderId'):
                print("聊天消息缺少senderId")
                self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "聊天消息必须包含发送者ID"
                }))
                return

            # 根据senderId查询用户昵称
            if data.get('type') == 'message' and data.get('senderId'):
                from trade.models import User
                try:
                    sender_id = int(data['senderId'])
                    user = User.objects.get(id=sender_id)
                    data['senderName'] = user.nickname
                    data['senderId'] = sender_id  # 确保senderId是数字
                    print(f"获取到发送者昵称: {user.nickname}")
                except User.DoesNotExist:
                    print(f"用户ID {data['senderId']} 不存在")
                    self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "发送者用户不存在"
                    }))
                    return
                except Exception as e:
                    print(f"查询用户信息失败: {str(e)}")
                    self.send(text_data=json.dumps({
                        "type": "error",
                        "message": "获取发送者信息失败"
                    }))
                    return

            group = self.scope['url_route']['kwargs'].get("group")
            if not group:
                print("错误：无法获取房间组名")
                return

            # 保存消息到数据库
            try:
                from .models import ChatMessage
                # 从房间名中解析接收者ID
                receiver_id = self._parse_receiver_id_from_room(group, data['senderId'])
                if receiver_id:
                    # 确定消息类型
                    message_type = data.get('type', 'text')
                    if message_type not in ['text', 'image', 'file']:
                        message_type = 'text'
                    
                    # 创建聊天消息记录
                    chat_message = ChatMessage.objects.create(
                        room_name=group,
                        sender_id=data['senderId'],
                        receiver_id=receiver_id,
                        content=data.get('content', ''),
                        message_type=message_type
                    )
                    print(f"消息已保存到数据库，ID: {chat_message.id}")
                else:
                    print("警告：无法解析接收者ID，消息未保存到数据库")
            except Exception as e:
                print(f"保存消息到数据库失败: {str(e)}")
                # 即使数据库保存失败，也要继续处理消息广播

            # 广播消息给房间内的所有用户（包含发送者昵称）
            print(f"广播消息到房间 {group}，发送者: {data.get('senderName', '未知')}")
            
            # 同时广播到接收者的个人消息房间（用于Message.vue同步）
            receiver_personal_room = self._get_receiver_room(group, data['senderId'])
            if receiver_personal_room:
                print(f"同时广播到接收者个人房间: {receiver_personal_room}")
            
            # 发送到聊天房间
            async_to_sync(self.channel_layer.group_send)(
                group,
                {
                    "type": "chat_message",
                    "message": data,
                    "target_room": group
                }
            )
            
            # 发送到接收者个人房间
            if receiver_personal_room:
                async_to_sync(self.channel_layer.group_send)(
                    receiver_personal_room,
                    {
                        "type": "personal_message",
                        "message": data,
                        "target_room": group
                    }
                )

        except json.JSONDecodeError as e:
            print("JSON解析错误：", str(e))
            self.send(text_data=json.dumps({
                "type": "error",
                "message": "JSON格式错误"
            }))
        except Exception as e:
            print("处理消息时出错：", str(e))
            self.send(text_data=json.dumps({
                "type": "error",
                "message": "服务器内部错误"
            }))

    def chat_message(self, event):
        # 发送消息给客户端
        message = event['message']
        target_room = event.get('target_room', '')
        print(f"向客户端发送聊天消息：{message}, 目标房间: {target_room}")

        # 避免发送者收到自己的消息（防止回声）
        try:
            # 获取当前连接的用户ID（需要在连接时存储）
            current_user_id = getattr(self, 'user_id', None)
            sender_id = message.get('senderId')
            
            # 如果是发送者自己，不发送消息
            if current_user_id and str(current_user_id) == str(sender_id):
                print(f"阻止发送者收到自己的消息: {current_user_id}")
                return
            
            # 添加房间信息
            message['room'] = target_room
            
            # 发送给其他房间成员
            self.send(text_data=json.dumps(message, ensure_ascii=False))
            print("聊天消息发送成功")
        except Exception as e:
            print("发送聊天消息失败：", str(e))
    
    def personal_message(self, event):
        # 处理个人消息（用于Message.vue同步）
        message = event['message']
        target_room = event.get('target_room', '')
        print(f"向客户端发送个人消息：{message}, 目标房间: {target_room}")
        
        try:
            # 个人消息直接发送，不需要过滤
            message['room'] = target_room
            message['isPersonal'] = True  # 标记为个人消息
            
            self.send(text_data=json.dumps(message, ensure_ascii=False))
            print("个人消息发送成功")
        except Exception as e:
            print("发送个人消息失败：", str(e))

    def websocket_disconnect(self, message):
        group = self.scope['url_route']['kwargs'].get("group")
        if group:
            print(f"用户离开房间: {group}")
            async_to_sync(self.channel_layer.group_discard)(group, self.channel_name)
        else:
            print("用户断开连接（未加入房间）")

        # 断开连接时自动触发
        raise StopConsumer
