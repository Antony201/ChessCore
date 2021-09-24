from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from api.models import Game
from api.serializers import GameSerializer


@database_sync_to_async
def get_serialized_game(uuid):
    game = Game.objects.get(uuid=uuid)
    return GameSerializer(game).data


async def send_game_data_to_group(game_uuid, game_data: dict):
    """
    Отправка в websocket room обновленных данных о партии
    """
    layer = get_channel_layer()
    await layer.group_send(f'game_{game_uuid}', {'type': 'game_data', 'game': game_data})
