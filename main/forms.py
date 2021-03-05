from django import forms

class CreateListForm(forms.Form):
	name = forms.CharField(label="Name ", max_length=300)

# class TextForm(forms.Form):
# 	search = forms.CharField(label = "Search ", max_length = 100)

