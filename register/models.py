from django.db import models

# Create user object in database
class User(models.Model):
	username = models.CharField(max_length = 100)
	email = models.EmailField(max_length = 100)

	def __str__(self):
		return self.username

# Create list object in database
class VideoList(models.Model):
	name = models.CharField(max_length = 100)

	def __str__(self):
		return self.name

# Create video object in database
class Video(models.Model):
	videolist = models.ForeignKey(VideoList, on_delete = models.CASCADE)
	url = models.URLField()
	text = models.CharField(max_length = 200)

	def __str__(self):
		return self.text
