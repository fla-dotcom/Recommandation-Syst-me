from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="userprofile"
    )

    interests = models.JSONField(blank=True, null=True)
    skill_level = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    difficulty = models.CharField(max_length=50)
    tags = models.TextField(blank=True)

    rating_avg = models.FloatField(default=0)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    def __str__(self):
        return self.title

class Interaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    watch_percentage = models.FloatField(default=0)
    rating = models.FloatField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "course")

class Recommendation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recommendations"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="recommended_to"
    )

    score = models.FloatField()

    algorithm_type = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reco {self.user.username} → {self.course.title}"

#test :
class Item(models.Model):
    item_id = models.IntegerField(primary_key=True)

    name = models.TextField()
    description = models.TextField()

    theme = models.TextField()
    difficulty = models.TextField()
    software = models.TextField()
    type = models.TextField()

    def __str__(self):
        return self.name