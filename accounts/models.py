from django.db import models

# Create your models here.
class User(models.Model):
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=200)
    name = models.CharField(max_length=20)
    access_token = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'