from django.contrib.auth.models import User
from django.db import models
# Create your models here.
class List(models.Model):
  name = models.CharField(max_length=100)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  sort = models.IntegerField()

  def save(self, *args, **kwargs):
    if not self.pk:
      self.sort = self.user.list_set.count()

    super(List, self).save(*args, **kwargs)

  def __str__(self):
    return self.name

class Task(models.Model):
  name = models.CharField(max_length=100)
  description = models.CharField(max_length=10000)
  is_done = models.BooleanField(default=False)
  deadline = models.DateTimeField(blank=True, null=True,)
  sort = models.IntegerField()
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  list = models.ForeignKey(List, on_delete=models.CASCADE, default=None)

  def save(self, *args, **kwargs):
    if not self.pk:
      self.sort = self.list.task_set.count()
    super(Task, self).save(*args, **kwargs)

  def __str__(self):
    return self.name