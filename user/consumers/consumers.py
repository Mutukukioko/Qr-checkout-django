from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from user.models import Message

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.shop_id = self.scope['url_route']['kwargs']['shop_id']
        self.shop_group_name = 'shop_%s' % self.shop_id

        # Join room group
        await self.channel_layer.group_add(
            self.shop_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.shop_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Save message to database
        await self.save_message(message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.shop_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @sync_to_async
    def save_message(self, message):
        Message.objects.create(
            sender=self.scope['user'],
            receiver_id=self.shop_id,
            message=message
        )
