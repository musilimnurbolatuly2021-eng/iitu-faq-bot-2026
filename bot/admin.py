from django.contrib import admin
from .models import FAQ, ChatHistory

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'keywords')
    search_fields = ('question', 'keywords')

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('username', 'user_message', 'language', 'created_at')
    list_filter = ('language', 'created_at')
    search_fields = ('username', 'user_message')
    readonly_fields = ('created_at',)