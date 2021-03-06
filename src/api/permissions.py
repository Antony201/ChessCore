"""
API permissions for checks such as piece ownership
"""

import chess
from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class GamePermission(permissions.BasePermission):
    message = "That move is not valid or allowed"

    def has_object_permission(self, request, view, obj):
        """
        Allow players to see each other's pieces
        Only allow the owner of a piece to move it (i.e. if you play as White you can only move white pieces)

        python-chess Piece.color is True for white pieces, False for black ones
        obj: Game instance
        """

        if request.method in permissions.SAFE_METHODS:
            return True

        if view.action == "move":
            from_square = request.data.get("from_square")
            square = getattr(chess, from_square.upper())
            board = chess.Board(obj.board.fen)
            user = User.objects.get(username=request.user)

            if user in (obj.white_player, obj.black_player):
                if obj.white_player == obj.black_player:
                    return True

                player_color = "white" if user == obj.white_player else "black"

            else:
                return False

            piece_color = "white" if board.color_at(square) else "black"

            return player_color == piece_color
        elif view.action == "capitulate":
            if request.user not in (obj.white_player, obj.black_player):
                return False
        elif view.action == "claim_draw":
            if request.user not in (obj.white_player, obj.black_player):
                return False
        elif view.action == 'repeat_game':
            if request.user not in (obj.white_player, obj.black_player):
                return False
            if not obj.result.finished:
                return False
        return True
