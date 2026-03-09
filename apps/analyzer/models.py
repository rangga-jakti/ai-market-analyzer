from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class AnalysisRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    keyword = models.CharField(max_length=255)
    user = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='analyses'
)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    trend_score = models.FloatField(null=True, blank=True)
    ai_insight = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analysis Request'
        verbose_name_plural = 'Analysis Requests'

    def __str__(self):
        return f"{self.keyword} | Score: {self.trend_score} | {self.status}"
    
class TrendDataPoint(models.Model):

    analysis = models.ForeignKey(
        AnalysisRequest,
        on_delete=models.CASCADE,
        related_name='trend_data_points'
    )
    date = models.DateField()
    interest_value = models.IntegerField()

    class Meta:
        ordering = ['date']
        verbose_name = 'Trend Data Point'
        verbose_name_plural = 'Trend Data Points'

    def __str__(self):
        return f"{self.analysis.keyword} | {self.date} | {self.interest_value}"
    
    