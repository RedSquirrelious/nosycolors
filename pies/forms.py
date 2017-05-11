import re
import django.core.validators

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MaxLengthValidator

alpha_numeric = RegexValidator(r'^[0-9_@a-zA-Z]*$', 'Only alphanumeric characters and underscores are allowed.')

name_max_length = MaxLengthValidator(15)

class HandleForm(forms.Form):

  screen_name = forms.CharField(label='screen_name', max_length=15, required=True, validators=[alpha_numeric, name_max_length])
  number_of_tweets = forms.IntegerField(label='number_of_tweets', min_value=1, max_value=100)


  def clean_screen_name(self):
    
    screen_name = self.cleaned_data['screen_name']

    if screen_name[0] == '@':
      screen_name = screen_name[1:]

    if '@' in screen_name:
      screen_name = ''

    return screen_name


  # def pick_search_type(self):
  #   screen_name = self.cleaned_data['screen_name']
  #   hashtag = self.cleaned_data['hashtag']

  #   if screen_name and not hashtag:
  #     somethingsometing
  #   elif hashtag and not screen_name:
  #     somethingelse
  #   elif not screen_name and not hashtag:
  #     make them fill it in again
  #   else:
  #     search screen_name for hashtag
