from django import forms

from api.models import Game
from api.services import create_board, create_result


class GameAdminForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = '__all__'

    def clean(self):
        if not self.cleaned_data['board'] and not self.cleaned_data['result']:
            board = create_board(self.cleaned_data['uuid'], {})
            result = create_result({})
            self.cleaned_data['board'] = board
            self.cleaned_data['result'] = result
        return self.cleaned_data
