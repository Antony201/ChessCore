import requests
from requests import Response
from django.conf import settings

from api.broadcast.exceptions import BroadcastApiError


class AbstractCreateBroadcast:
    _url = settings.VIDEO_BROADCAST

    @property
    def url(self):
        return self._url

    def get_data(self):
        pass

    def get_result_from_res(self, res: Response):
        return res.json()['data']['id']

    def do_request(self):
        res = requests.post(self.url, json=self.get_data())
        if res.status_code != 200:
            raise BroadcastApiError
        return self.get_result_from_res(res)


class CreateSession(AbstractCreateBroadcast):

    def get_data(self):
        return dict(
            janus='create',
            transaction='XFWaWrh10g2y'
        )


class CreateData(AbstractCreateBroadcast):

    def __init__(self, session_id: int):
        self.session_id = session_id

    @property
    def url(self):
        return f'{self._url}/{self.session_id}'

    def get_data(self):
        return dict(
            janus='attach',
            plugin='janus.plugin.videoroom',
            opaque_id='screensharingtest-pFwIMR65Dzcd',
            transaction='XFWaWrh10g2y'
        )


class CreateRoom(AbstractCreateBroadcast):

    def __init__(
        self, session_id: int, data_id: int, full_name, field_name
    ):
        self.session_id = session_id
        self.data_id = data_id
        self.full_name = full_name
        self.field_name = field_name

    @property
    def url(self):
        return f'{self._url}/{self.session_id}/{self.data_id}'

    def get_data(self):
        return dict(
            janus='message',
            body=dict(
                request='create',
                description=f'{self.full_name} {self.field_name}',
                bitrate=500000,
                publishers=1,
            ),
            transaction='XFWaWrh10g2y'
        )

    def get_result_from_res(self, res: Response):
        return res.json()['plugindata']['data']['room']


def create_session():
    session_id = CreateSession().do_request()
    data_id = CreateData(session_id).do_request()
    return session_id, data_id


def create_rooms_for_user(
    session_id: int, data_id: int, full_name
):
    camera = CreateRoom(
        session_id, data_id,
        full_name, 'камера'
    ).do_request()
    board = CreateRoom(
        session_id, data_id,
        full_name, 'рабочий стол'
    ).do_request()
    return camera, board
