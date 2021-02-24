from django.db import models

# Create your models here.
class User(models.Model):
	username = models.CharField(max_length = 100)
	email = models.EmailField(max_length = 100)

	def __str__(self):
		return self.username

class VideoList(models.Model):
	name = models.CharField(max_length = 100)

	def __str__(self):
		return self.name

class Video(models.Model):
	videolist = models.ForeignKey(VideoList, on_delete = models.CASCADE)
	url = models.URLField()
	text = models.CharField(max_length = 200)

	def __str__(self):
		return self.text
