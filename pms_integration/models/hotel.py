from django.db import models

class PMSConfig(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    config_json = models.JSONField()

    def __str__(self):
        return f"{self.name} v{self.version}"
    
class Hotel(models.Model):
    name = models.CharField(max_length=255)
    pms_config = models.ForeignKey(PMSConfig, on_delete=models.PROTECT, related_name='hotels')

    def __str__(self):
        return self.name