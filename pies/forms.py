from django import forms

class HandleForm(forms.Form):
    screen_name = forms.CharField(label='screen_name', max_length=15)
    number_of_tweets = forms.IntegerField(label='number_of_tweets')