from django.contrib import admin
from .models import AnalysisRequest, TrendDataPoint


class TrendDataPointInline(admin.TabularInline):
    model = TrendDataPoint
    extra = 0
    readonly_fields = ['date', 'interest_value']


@admin.register(AnalysisRequest)
class AnalysisRequestAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'trend_score', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['keyword']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TrendDataPointInline]


@admin.register(TrendDataPoint)
class TrendDataPointAdmin(admin.ModelAdmin):
    list_display = ['analysis', 'date', 'interest_value']
    list_filter = ['date']