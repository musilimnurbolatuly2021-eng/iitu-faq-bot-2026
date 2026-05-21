from django.db import models

class FAQ(models.Model):
    question = models.CharField(max_length=300, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    keywords = models.CharField(max_length=300, verbose_name="Ключевые слова")

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ сұрақтары"


class ChatHistory(models.Model):
    user_id = models.BigIntegerField(verbose_name="Пользователь ID")
    username = models.CharField(max_length=100, blank=True, verbose_name="Username")
    user_message = models.TextField(verbose_name="Сообщение")
    bot_answer = models.TextField(verbose_name="Ответ бота")
    language = models.CharField(max_length=5, default='ru', verbose_name="Язык")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    def __str__(self):
        return f"{self.username} — {self.created_at.strftime('%d.%m.%Y %H:%M')}"

    class Meta:
        verbose_name = "История чата"
        verbose_name_plural = "История чата"
        ordering = ['-created_at']