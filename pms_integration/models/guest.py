from django.db import models


class Guest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)

    class Meta:
        unique_together = ("name", "email")

    def __str__(self):
        return f"{self.name} ({self.email or 'No Email'})"
