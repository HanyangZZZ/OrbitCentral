from django.db import models


class Item(models.Model):
	name = models.CharField(max_length=120)
	rating = models.FloatField()
	category = models.CharField(max_length=80)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"{self.name} ({self.category})"

# Create your models here.
