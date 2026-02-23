from django.db import models
from trade.models import User


class ChatMessage(models.Model):
    """聊天消息模型"""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('file', '文件'),
    ]
    
    # 消息基本信息
    room_name = models.CharField(max_length=50, verbose_name='房间名，格式：room_小ID_大ID')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='接收者')
    content = models.TextField(verbose_name='消息内容')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='text', verbose_name='消息类型')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'chat_messages'
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        # 优化查询的索引
        indexes = [
            models.Index(fields=['room_name', 'created_at'], name='idx_room_time'),
            models.Index(fields=['receiver', 'is_read', 'created_at'], name='idx_receiver_unread'),
            models.Index(fields=['sender', 'created_at'], name='idx_sender_time'),
        ]
    
    def __str__(self):
        return f'{self.sender.nickname} -> {self.receiver.nickname}: {self.content[:20]}'
    
    @classmethod
    def get_room_name(cls, user1_id, user2_id):
        """生成标准化的房间名：room_小ID_大ID"""
        min_id = min(user1_id, user2_id)
        max_id = max(user1_id, user2_id)
        return f'room_{min_id}_{max_id}'
    
    @property
    def sender_nickname(self):
        """获取发送者昵称"""
        return self.sender.nickname
    
    @property
    def receiver_nickname(self):
        """获取接收者昵称"""
        return self.receiver.nickname
