class BroadcastApiError(Exception):

    def __init__(self, message):
        super().__init__("Broadcast api error")

