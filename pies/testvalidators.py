import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

def clean_screen_name(screen_name):
  # screen_name = self.cleaned_data['screen_name']

  if screen_name[0] == '@':
    screen_name = screen_name[1:]

  if not re.match('^[0-9_@a-zA-Z]*$', screen_name):
    raise ValidationError( "That isn't a valid screen name.  Valid Twitter screen names contain only alphanumeric characters and possibly underscores.")

  if len(screen_name) > 15:
    raise ValidationError("That isn't a valid screen name.  It's too long.  Try again!")

  return screen_name


string = 'sassa'
string2 = '@Squirrel42!'
string3 = '@RedSquirrelious'
string4 = '#&sassa'

print(clean_screen_name(string))

print(clean_screen_name(string2))

print(clean_screen_name(string3))

print(clean_screen_name(string4))