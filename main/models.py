from django.db import models
from django.contrib.auth.models import User


#list for a user
class ToDoList(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "todolist", null = True)  # <--- added
	name = models.CharField(max_length = 200)

	def __str__(self):
		return self.name

#items to insert into a list
class Item(models.Model):
	todolist = models.ForeignKey(ToDoList, on_delete = models.CASCADE)
	text = models.CharField(max_length = 300)
	complete = models.BooleanField()
	video = models.BooleanField()
	website = models.BooleanField(default = False)
	siteLink = models.CharField(max_length = 1000)

	def __str__(self):
		return self.text

#model for a simple check box
class CheckBox(models.Model):
	checked = models.BooleanField(False)

	def __str__(self):
		return self.checked
