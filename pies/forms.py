import re
from django.utils.translation import ugettext as _
from django import forms
from django.core.validators import RegexValidator, MaxLengthValidator, MaxValueValidator, MinValueValidator

alpha_numeric = RegexValidator(r'^[0-9_@a-zA-Z]*$', 'Only alphanumeric characters and underscores are allowed.')
name_max_length = MaxLengthValidator(16, 'Screen name must be 15 characters or less.  16 characters if you include the @ symbol')


class MyMaxValidator(MaxValueValidator):
    message = _("You want too many tweets.  Enter a number between 1 and 100.")


class MyMinValidator(MinValueValidator):
    message = _("At least ask for 1 tweet.")

class HandleForm(forms.Form):
    screen_name = forms.CharField(label='screen_name', required=True,
                                  error_messages={'required': 'Did you forget to enter a screen name?'})
    number_of_tweets = forms.IntegerField(label='number_of_tweets',
                                          validators=[MyMaxValidator(100), MyMinValidator(1)],
                                          error_messages={'required': 'Enter a number between 1 and 100'})



    def clean_screen_name(self):
        screen_name = self.cleaned_data['screen_name']
        if screen_name[0] == '@':
            screen_name = screen_name[1:]

        if len(screen_name) > 15:
            raise forms.ValidationError(_("Too long.  Enter 15 characters or less."), code="TooLong")

        if not re.match(r'^[0-9_a-zA-Z]*$', screen_name):
            raise forms.ValidationError(_("Enter numbers, letters, or underscores for the screen name."), code="WrongChar")

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
