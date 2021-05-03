from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

# Create register page view here.
def register(response):
	if response.method == "POST":
		#create a new log in form
		form = UserCreationForm(response.POST)
		# if the user is valid, send to home
		if form.is_valid():
			form.save()
			return redirect("/home")
	else:
		form = UserCreationForm()
		
	return render(response, "register/register.html", {"form":form})