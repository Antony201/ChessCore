import uuid

import chess
from annoying.fields import AutoOneToOneField
from core.tournament.models import TimeControlType
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

User = get_user_model()


class Elo(models.Model):
    """
    https://en.wikipedia.org/wiki/Elo_rating_system#Mathematical_details
    """

    rating = models.IntegerField(default=1200)
    previous_rating = models.IntegerField(default=1200)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4)

    player = AutoOneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="elo"
    )

    def update_rating(self, new_rating):
        self.previous_rating = self.rating
        self.rating = new_rating

        self.save()


class Result(models.Model):
    """
    Holds result and termination data following the PGN spec
    result: declares the winner
    termination: gives additional data about the result
    http://www.saremba.de/chessgml/standards/pgn/pgn-complete.htm#c9.8.1
    """

    # RESULT
    WHITE_WINS = "White wins"
    BLACK_WINS = "Black wins"
    DRAW = "Draw"
    IN_PROGRESS = "In progress"
    SCHEDULED = 'Scheduled'

    # TERMINATION
    ABANDONED = "Abandoned"
    ADJUDICATION = "Adjudication"
    DEATH = "Death"
    EMERGENCY = "Emergency"
    NORMAL = "Normal"
    RULES_INFRACTION = "Rules infraction"
    TIME_FORFEIT = "Time forfeit"
    CAPITULATION = "Capitulation"
    UNTERMINATED = "Unterminated"

    RESULT_CHOICES = [
        (WHITE_WINS, "White wins"),
        (BLACK_WINS, "Black wins"),
        (DRAW, "Drawn game"),
        (
            IN_PROGRESS,
            "Game still in progress, game abandoned, or result otherwise unknown",
        ),
        (
            SCHEDULED,
            'Game scheduled'
        )
    ]

    TERMINATION_CHOICES = [
        (ABANDONED, "Abandoned game."),
        (ADJUDICATION, "Result due to third party adjudication process."),
        (DEATH, "One or both players died during the course of this game."),
        (EMERGENCY, "Game concluded due to unforeseen circumstances."),
        (NORMAL, "Game terminated in a normal fashion."),
        (
            RULES_INFRACTION,
            "Administrative forfeit due to losing player's failure to observe either the Laws of Chess or the event regulations.",
        ),
        (
            TIME_FORFEIT,
            "Loss due to losing player's failure to meet time control requirements.",
        ),
        (CAPITULATION, "Player capitulated."),
        (UNTERMINATED, "Game not terminated."),
    ]

    result = models.TextField(choices=RESULT_CHOICES, default=SCHEDULED,)
    termination = models.TextField(choices=TERMINATION_CHOICES, default=UNTERMINATED,)

    def __str__(self):
        return self.result

    @property
    def finished(self):
        """
        Игра окончена
        """
        return self.result in (self.WHITE_WINS, self.BLACK_WINS, self.DRAW)


class Board(models.Model):
    """
    python-chess Board data
    """
    BLACK_PIECES = ["q", "k", "b", "n", "r", "p"]
    WHITE_PIECES = [p.upper() for p in BLACK_PIECES]

    fen = models.TextField(default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    board_fen = models.TextField(default="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    board_fen_flipped = models.TextField(default="RNBKQBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbkqbnr")
    ep_square = models.IntegerField(null=True)
    castling_xfen = models.TextField(null=True)
    castling_rights = models.TextField(null=True)
    turn = models.BooleanField(default=True)
    fullmove_number = models.IntegerField(default=1)
    halfmove_clock = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    game_uuid = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return f'{self.game}: {self.fen}'

    def update(self, chess_board, *args, **kwargs):
        """
        Updates all the information needed to recover a Board (except for the move stack)
        """
        attributes = [
            "ep_square",
            "turn",
            "fullmove_number",
            "halfmove_clock",
        ]

        for i in attributes:
            setattr(self, i, getattr(chess_board, i))

        chess_board_flip_vert = chess_board.transform(chess.flip_vertical)
        chess_board_rotated = chess_board_flip_vert.transform(chess.flip_horizontal)

        self.castling_rights = str(chess_board.castling_rights)
        self.fen = chess_board.fen()
        self.board_fen = chess_board.board_fen()
        self.board_fen_flipped = chess_board_rotated.board_fen()
        self.castling_xfen = chess_board.castling_xfen()

        self.save()

    @property
    def move_stack(self):
        if self.move_set:
            moves = self.move_set.all()
            move_ucis = [m.uci() for m in moves]
            return move_ucis
        return []

    @classmethod
    def from_fen(cls, fen):
        """
        A FEN string contains the position part board_fen(), the turn, the castling part (castling_rights),
        the en passant square (ep_square), the halfmove_clock and the fullmove_number.
        """

        board = chess.Board(fen)

        board_data = {
            "fen": fen,
            "turn": board.turn,
            "castling_xfen": board.castling_xfen(),
            "castling_rights": board.castling_rights,
            "ep_square": board.ep_square,
            "fullmove_number": board.fullmove_number,
            "halfmove_clock": board.halfmove_clock,
        }

        return cls(**board_data)

    def __str__(self):
        return self.fen


class Piece(models.Model):
    BLACK_PAWN_SYMBOL = "P"
    BLACK_KNIGHT_SYMBOL = "N"
    BLACK_BISHOP_SYMBOL = "B"
    BLACK_ROOK_SYMBOL = "R"
    BLACK_QUEEN_SYMBOL = "Q"
    BLACK_KING_SYMBOL = "K"
    WHITE_PAWN_SYMBOL = "p"
    WHITE_KNIGHT_SYMBOL = "n"
    WHITE_BISHOP_SYMBOL = "b"
    WHITE_ROOK_SYMBOL = "r"
    WHITE_QUEEN_SYMBOL = "q"
    WHITE_KING_SYMBOL = "k"

    PIECE_CHOICES = [
        (BLACK_PAWN_SYMBOL, "Black pawn"),
        (BLACK_KNIGHT_SYMBOL, "Black knight"),
        (BLACK_BISHOP_SYMBOL, "Black bishop"),
        (BLACK_ROOK_SYMBOL, "Black rook"),
        (BLACK_QUEEN_SYMBOL, "Black queen"),
        (BLACK_KING_SYMBOL, "Black king"),
        (WHITE_PAWN_SYMBOL, "White pawn"),
        (WHITE_KNIGHT_SYMBOL, "White knight"),
        (WHITE_BISHOP_SYMBOL, "White bishop"),
        (WHITE_ROOK_SYMBOL, "White rook"),
        (WHITE_QUEEN_SYMBOL, "White queen"),
        (WHITE_KING_SYMBOL, "White king"),
    ]

    SQUARE_CHOICES = [
        (getattr(chess, i.upper()), i.upper(),) for i in chess.SQUARE_NAMES
    ]

    piece_type = models.CharField(max_length=1, choices=PIECE_CHOICES,)

    square = models.CharField(max_length=2, choices=SQUARE_CHOICES, null=True,)

    captured = models.BooleanField(default=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE,)

    def __str__(self):
        return self.piece_type


class Game(models.Model):
    NONE = "none"
    CAM = "cam"
    BOARD = "board"
    BOTH = "both"
    BROADCAST_TYPE_CHOICES = [
        (NONE, "No stream"),
        (CAM, "Camera"),
        (BOARD, "Board"),
        (BOTH, "Camera and desktop"),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    white_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="white_player",
        null=True,
    )
    black_player = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="black_player",
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    result = models.OneToOneField(Result, on_delete=models.CASCADE, null=True, blank=True)
    board = models.OneToOneField(Board, on_delete=models.CASCADE, null=True, blank=True)
    white_player_points = models.FloatField(null=True, blank=True)
    black_player_points = models.FloatField(null=True, blank=True)
    black_player_broadcast_board = models.CharField(max_length=300, null=True, blank=True)
    white_player_broadcast_board = models.CharField(max_length=300, null=True, blank=True)
    black_player_broadcast = models.CharField(max_length=300, null=True, blank=True)
    white_player_broadcast = models.CharField(max_length=300, null=True, blank=True)
    black_player_can_claim_draw = models.BooleanField(default=True)
    white_player_can_claim_draw = models.BooleanField(default=True)
    time_control_type = models.ForeignKey(TimeControlType, on_delete=models.CASCADE, null=True)
    white_player_time_spent = models.SmallIntegerField(null=True, blank=True, default=0)
    black_player_time_spent = models.SmallIntegerField(null=True, blank=True, default=0)
    broadcast_type = models.CharField(max_length=100, choices=BROADCAST_TYPE_CHOICES)

    def check_white_or_black(self, user_id: int) -> str:
        if self.white_player and self.white_player.id == user_id:
            return 'white'
        elif self.black_player and self.black_player.id == user_id:
            return 'black'

    def set_cam_broadcast(self, color: str, value):
        if self.broadcast_type in ('cam', 'both'):
            setattr(self, f'{color}_player_broadcast', value)
            self.save()
        else:
            pass

    def set_board_broadcast(self, color: str, value):
        if self.broadcast_type in ('board', 'both'):
            setattr(self, f'{color}_player_broadcast_board', value)
            self.save()
        else:
            pass

    def set_claim_draw(self, color: str, value: bool):
        setattr(self, f'{color}_player_can_claim_draw', value)
        self.save()

    def _calc_times(self):
        timestamps = {0: self.started_at}
        for n, timestamp in enumerate(Move.objects.filter(board=self.board).values_list('created_at', flat=True)):
            timestamps[n + 1] = timestamp

        move_times = {0: 0}
        for n, timestamp in enumerate(timestamps):
            if n > 0:
                delta = (timestamps[timestamp] - timestamps.get(n - 1)).total_seconds()
                move_times[n] = delta
        return move_times

    def move_amount(self, user: User):
        """
        Общее количество ходов определенного игрока
        """
        return Move.objects.filter(board=self.board, user=user).count()

    @property
    def white_player_time_remaining(self):
        move_times = self._calc_times()

        white_player_time_spent = 0
        for delta in move_times:
            if delta % 2 != 0:
                white_player_time_spent += int(move_times[delta])

        tct_time = self.time_control_type.time
        if tct_time is not None:
            white_player_time_remaining = tct_time - white_player_time_spent
        else:
            white_player_time_remaining = 0

        # учет доп времени
        tct_addition_time = self.time_control_type.additional_time
        move_amount = self.move_amount(self.white_player)
        if tct_addition_time:
            white_player_time_remaining += move_amount * tct_addition_time
        return white_player_time_remaining

    @property
    def black_player_time_remaining(self):
        move_times = self._calc_times()

        black_player_time_spent = 0
        for delta in move_times:
            if delta % 2 == 0:
                black_player_time_spent += int(move_times[delta])

        tct_time = self.time_control_type.time
        if tct_time is not None:
            black_player_time_remaining = tct_time - black_player_time_spent
        else:
            black_player_time_remaining = 0

        # учет доп времени
        tct_addition_time = self.time_control_type.additional_time
        move_amount = self.move_amount(self.black_player)
        if tct_addition_time:
            black_player_time_remaining += move_amount * tct_addition_time
        return black_player_time_remaining


class Move(models.Model):
    """
    Each individual move that composes a board's move stack
    """
    created_at = models.DateTimeField(auto_now_add=True)
    from_square = models.CharField(max_length=2)
    to_square = models.TextField(max_length=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.from_square}-{self.to_square} by {self.user}"

    def uci(self):
        return chess.Move.from_uci(f"{self.from_square}{self.to_square}")


class Position(models.Model):
    piece_file = models.CharField(max_length=1)
    piece_rank = models.CharField(max_length=1)
    timestamp = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4)
    piece = models.ForeignKey(Piece, on_delete=models.CASCADE,)

    def __str__(self):
        return f"{self.piece_file}{self.piece_rank}"


class Claim(models.Model):
    THREEFOLD_REPETITION = "tr"
    FIFTY_MOVES = "ft"
    DRAW = "d"

    CLAIM_CHOICES = [
        (THREEFOLD_REPETITION, "Threefold repetition"),
        (FIFTY_MOVES, "Fifty moves"),
        (DRAW, "Draw"),
    ]

    claim_type = models.CharField(max_length=2, choices=CLAIM_CHOICES,)

    def __str__(self):
        return self.claim_type


class ClaimItem(models.Model):
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    timestamp = models.DateTimeField(auto_now_add=True)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE,)
