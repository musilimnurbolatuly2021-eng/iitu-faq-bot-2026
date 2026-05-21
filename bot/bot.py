import os
import sys

# ===== DJANGO БАПТАУЫ =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

import django
django.setup()

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)
from bot.models import ChatHistory

load_dotenv(os.path.join(BASE_DIR, '.env'))
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ===== IITU FAQ СӨЗДІГІ =====
FAQ = {
    "расписание": {
        "ru": "📅 *Расписание IITU*\n\n"
              "• Личный кабинет: https://cabinet.iitu.kz\n"
              "• Осенний семестр: сентябрь – декабрь\n"
              "• Весенний семестр: февраль – май\n"
              "• Пары: 8:30 / 10:10 / 11:50 / 13:30 / 15:10 / 16:50\n"
              "• Длительность пары: 80 минут",
        "kz": "📅 *IITU кестесі*\n\n"
              "• Жеке кабинет: https://cabinet.iitu.kz\n"
              "• Күзгі семестр: қыркүйек – желтоқсан\n"
              "• Көктемгі семестр: ақпан – мамыр\n"
              "• Сабақтар: 8:30 / 10:10 / 11:50 / 13:30 / 15:10 / 16:50\n"
              "• Сабақ ұзақтығы: 80 минут"
    },
    "кесте": {
        "ru": "📅 *Расписание IITU*\n\n• cabinet.iitu.kz → Расписание\n• Пары: 8:30 / 10:10 / 11:50 / 13:30",
        "kz": "📅 *IITU кестесі*\n\n• cabinet.iitu.kz → Кесте\n• Сабақтар: 8:30 / 10:10 / 11:50 / 13:30"
    },
    "сессия": {
        "ru": "📝 *Сессия в IITU*\n\n"
              "• Зимняя сессия: январь (1–3 неделя)\n"
              "• Летняя сессия: май–июнь\n"
              "• Расписание: cabinet.iitu.kz\n"
              "• Допуск: посещаемость не менее 70%\n"
              "• Пересдача: в течение 2 недель после сессии\n\n"
              "⚠️ При 3+ долгах — отчисление!",
        "kz": "📝 *IITU сессиясы*\n\n"
              "• Қысқы сессия: қаңтар (1–3 апта)\n"
              "• Жазғы сессия: мамыр–маусым\n"
              "• Кесте: cabinet.iitu.kz\n"
              "• Жіберу: қатысу 70%-дан кем болмауы керек\n\n"
              "⚠️ 3+ қарыз болса — шығарылу!"
    },
    "экзамен": {
        "ru": "📝 *Экзамены IITU*\n\n"
              "• Итоговый экзамен — 40% от оценки\n"
              "• РК1 и РК2 — по 30% каждый\n"
              "• Минимальный балл: 50 из 100\n"
              "• Расписание: cabinet.iitu.kz",
        "kz": "📝 *IITU емтихандары*\n\n"
              "• Қорытынды емтихан — 40%\n"
              "• РБ1 және РБ2 — әрқайсысы 30%\n"
              "• Минималды балл: 50/100\n"
              "• Кесте: cabinet.iitu.kz"
    },
    "стипендия": {
        "ru": "💰 *Стипендия в IITU*\n\n"
              "• Академическая: ~36 000 тг/мес\n"
              "• Социальная: ~50 000 тг/мес\n"
              "• Повышенная (GPA 3.5+): ~54 000 тг/мес\n\n"
              "📌 Условия:\n"
              "• GPA не ниже 2.67\n"
              "• Нет академических долгов\n\n"
              "💳 Выплата: 10–15 числа каждого месяца",
        "kz": "💰 *IITU стипендиясы*\n\n"
              "• Академиялық: ~36 000 тг/ай\n"
              "• Әлеуметтік: ~50 000 тг/ай\n"
              "• Жоғарылатылған (GPA 3.5+): ~54 000 тг/ай\n\n"
              "📌 Шарттар:\n"
              "• GPA 2.67-ден кем болмауы\n"
              "• Академиялық қарыз болмауы\n\n"
              "💳 Төлем: әр айдың 10–15-інде"
    },
    "грант": {
        "ru": "🎓 *Гранты IITU*\n\n"
              "• Государственный образовательный грант\n"
              "• Грант акимата г. Алматы\n"
              "• Внутренние гранты IITU\n"
              "• Международные: Erasmus+, Болашак\n\n"
              "📧 dekanat@iitu.kz",
        "kz": "🎓 *IITU гранттары*\n\n"
              "• Мемлекеттік білім беру гранты\n"
              "• Алматы қалалық әкімдігінің гранты\n"
              "• IITU ішкі гранттары\n"
              "• Халықаралық: Erasmus+, Болашақ\n\n"
              "📧 dekanat@iitu.kz"
    },
    "деканат": {
        "ru": "🏢 *Деканат IITU*\n\n"
              "📍 ул. Манаса 34/1, Алматы\n"
              "🕐 Пн–Пт: 9:00–18:00\n"
              "☕ Обед: 13:00–14:00\n\n"
              "📞 +7 (727) 330-09-11\n"
              "📧 info@iitu.kz\n"
              "🌐 https://iitu.kz",
        "kz": "🏢 *IITU деканаты*\n\n"
              "📍 Манас көш. 34/1, Алматы\n"
              "🕐 Дс–Жм: 9:00–18:00\n"
              "☕ Түскі ас: 13:00–14:00\n\n"
              "📞 +7 (727) 330-09-11\n"
              "📧 info@iitu.kz\n"
              "🌐 https://iitu.kz"
    },
    "кабинет": {
        "ru": "💻 *Личный кабинет IITU*\n\n"
              "🔗 https://cabinet.iitu.kz\n\n"
              "✅ Расписание\n"
              "✅ Оценки и GPA\n"
              "✅ Задания\n"
              "✅ Оплата обучения\n"
              "✅ Запись на пересдачу\n\n"
              "❓ Проблемы: it-support@iitu.kz",
        "kz": "💻 *IITU жеке кабинеті*\n\n"
              "🔗 https://cabinet.iitu.kz\n\n"
              "✅ Кесте\n"
              "✅ Бағалар мен GPA\n"
              "✅ Тапсырмалар\n"
              "✅ Оқу төлемі\n"
              "✅ Қайта тапсыруға жазылу\n\n"
              "❓ Мәселе: it-support@iitu.kz"
    },
    "библиотека": {
        "ru": "📚 *Библиотека IITU*\n\n"
              "📍 1 этаж главного корпуса\n"
              "🕐 Пн–Пт: 9:00–20:00\n"
              "🕐 Сб: 10:00–17:00\n\n"
              "🔗 https://lib.iitu.kz\n"
              "• Доступ к Springer, IEEE, Scopus",
        "kz": "📚 *IITU кітапханасы*\n\n"
              "📍 Бас корпустың 1 қабаты\n"
              "🕐 Дс–Жм: 9:00–20:00\n"
              "🕐 Сб: 10:00–17:00\n\n"
              "🔗 https://lib.iitu.kz\n"
              "• Springer, IEEE, Scopus базалары"
    },
    "справка": {
        "ru": "📄 *Справки в IITU*\n\n"
              "1️⃣ cabinet.iitu.kz → Заявления → Справка\n"
              "2️⃣ Или лично: деканат, каб. 101\n\n"
              "• Справка студента: 1 рабочий день\n"
              "• Транскрипт: 3 рабочих дня\n"
              "• Академическая справка: 5 дней\n\n"
              "🕐 Деканат: Пн–Пт 9:00–17:00",
        "kz": "📄 *IITU анықтамалары*\n\n"
              "1️⃣ cabinet.iitu.kz → Өтініштер → Анықтама\n"
              "2️⃣ Немесе деканат: 101 каб.\n\n"
              "• Студент анықтамасы: 1 жұмыс күні\n"
              "• Транскрипт: 3 жұмыс күні\n"
              "• Академиялық анықтама: 5 күн\n\n"
              "🕐 Деканат: Дс–Жм 9:00–17:00"
    },
    "куратор": {
        "ru": "👨‍🏫 *Куратор в IITU*\n\n"
              "• Контакт: cabinet.iitu.kz → Профиль\n"
              "• По вопросам: деканат каб. 101\n\n"
              "Куратор помогает:\n"
              "✅ Академические вопросы\n"
              "✅ Перевод и восстановление\n"
              "✅ Документы и справки",
        "kz": "👨‍🏫 *IITU кураторы*\n\n"
              "• Байланыс: cabinet.iitu.kz → Профиль\n"
              "• Сұрақтар: деканат 101 каб.\n\n"
              "Куратор көмектеседі:\n"
              "✅ Академиялық сұрақтар\n"
              "✅ Ауыстыру және қалпына келтіру\n"
              "✅ Құжаттар мен анықтамалар"
    },
    "общежитие": {
        "ru": "🏠 *Общежитие IITU*\n\n"
              "• Стоимость: от 15 000 тг/мес\n"
              "• Заявление: cabinet.iitu.kz\n"
              "• Приоритет: иногородние, льготники\n\n"
              "📞 Комендант: +7 (727) 330-09-11 (доб. 3)",
        "kz": "🏠 *IITU жатақханасы*\n\n"
              "• Құны: айына 15 000 тг-дан\n"
              "• Өтініш: cabinet.iitu.kz\n"
              "• Басымдық: қалааралық студенттер\n\n"
              "📞 Комендант: +7 (727) 330-09-11 (қос. 3)"
    },
    "wifi": {
        "ru": "📶 *Wi-Fi в IITU*\n\n"
              "• Сеть: IITU_Students\n"
              "• Логин: ваш Student ID\n"
              "• Пароль: дата рождения DDMMYYYY\n\n"
              "❓ Проблемы: it-support@iitu.kz",
        "kz": "📶 *IITU Wi-Fi*\n\n"
              "• Желі: IITU_Students\n"
              "• Логин: Student ID\n"
              "• Пароль: туған күн ККААЯЯЯЯ\n\n"
              "❓ Мәселе: it-support@iitu.kz"
    },
}

# ===== КНОПКИ =====
MAIN_KEYBOARD = [
    ["📅 Расписание / Кесте", "📝 Сессия / Сессия"],
    ["💰 Стипендия / Стипендия", "🏢 Деканат / Деканат"],
    ["📚 Библиотека / Кітапхана", "💻 Кабинет / Кабинет"],
    ["📋 Все вопросы / Барлық сұрақтар"]
]

# ===== ТІЛДІ АНЫҚТАУ =====
def detect_lang(text: str) -> str:
    kz_chars = set("әіңғүұқөһ")
    text_lower = text.lower()
    if any(c in text_lower for c in kz_chars):
        return "kz"
    kz_words = ["кесте", "сессия", "деканат", "кітапхана", "стипендия",
                "анықтама", "сұрақ", "барлық", "қандай", "қалай", "жатақхана"]
    if any(w in text_lower for w in kz_words):
        return "kz"
    return "ru"

# ===== ТАРИХТЫ САҚТАУ =====
import asyncio
from asgiref.sync import sync_to_async

async def save_history(user_id: int, username: str, user_msg: str, bot_msg: str, lang: str):
    try:
        await sync_to_async(ChatHistory.objects.create)(
            user_id=user_id,
            username=username or "anonymous",
            user_message=user_msg[:500],
            bot_answer=bot_msg[:500],
            language=lang
        )
    except Exception as e:
        print(f"⚠️ Тарих сақталмады: {e}")

# ===== ЖАУАП ІЗДЕУ =====
def get_answer(text: str, lang: str) -> str:
    text_lower = text.lower()

    keyword_map = {
        "расписание": "расписание", "кесте": "кесте",
        "сессия": "сессия", "экзамен": "экзамен", "емтихан": "экзамен",
        "стипендия": "стипендия", "грант": "грант",
        "деканат": "деканат",
        "кабинет": "кабинет", "cabinet": "кабинет",
        "библиотека": "библиотека", "кітапхана": "библиотека",
        "справка": "справка", "анықтама": "справка",
        "куратор": "куратор",
        "общежитие": "общежитие", "жатақхана": "общежитие",
        "wifi": "wifi", "вайфай": "wifi", "интернет": "wifi",
    }

    for keyword, faq_key in keyword_map.items():
        if keyword in text_lower and faq_key in FAQ:
            return FAQ[faq_key].get(lang, FAQ[faq_key].get("ru", ""))

    if lang == "kz":
        return (
            "🤔 Сұрақты түсінбедім.\n\n"
            "Мына тақырыптарды жаз:\n"
            "• кесте • сессия • стипендия\n"
            "• деканат • кітапхана • кабинет\n"
            "• справка • куратор • wifi\n\n"
            "/help — барлық тақырыптар"
        )
    return (
        "🤔 Не понял вопрос.\n\n"
        "Попробуй написать:\n"
        "• расписание • сессия • стипендия\n"
        "• деканат • библиотека • кабинет\n"
        "• справка • куратор • wifi\n\n"
        "/help — все темы"
    )

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
    text = (
        "👋 *Привет! Сәлем!*\n\n"
        "Я — IITU FAQ бот 🎓\n"
        "Мен — IITU FAQ боты 🎓\n\n"
        "Отвечаю по темам / Жауап беремін:\n"
        "📅 Расписание / Кесте\n"
        "📝 Сессия / Экзамены\n"
        "💰 Стипендия / Грант\n"
        "🏢 Деканат / Контакты\n"
        "📚 Библиотека / Кітапхана\n"
        "💻 Кабинет / Cabinet\n\n"
        "Напиши вопрос или нажми кнопку 👇\n"
        "Сұрақ жаз немесе батырманы бас 👇"
    )
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=keyboard)

    await save_history(
        update.message.from_user.id,
        update.message.from_user.username or "",
        "/start",
        "Бот запущен",
        "ru"
    )

# ===== /help =====
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 *IITU FAQ Bot — Барлық тақырыптар*\n\n"
        "🇷🇺 *На русском:*\n"
        "расписание • сессия • экзамен\n"
        "стипендия • грант • деканат\n"
        "библиотека • кабинет • справка\n"
        "куратор • общежитие • wifi\n\n"
        "🇰🇿 *Қазақша:*\n"
        "кесте • сессия • емтихан\n"
        "стипендия • грант • деканат\n"
        "кітапхана • кабинет • анықтама\n"
        "куратор • жатақхана\n\n"
        "🌐 https://iitu.kz\n"
        "💻 https://cabinet.iitu.kz"
    )
    await update.message.reply_text(text, parse_mode='Markdown')

# ===== ХАБАРЛАМА ӨҢДЕУ =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Пустой ввод проверки
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "anonymous"

    # Пустая строка
    if len(text) == 0:
        await update.message.reply_text(
            "⚠️ Бос хабарлама!\nПожалуйста, напишите вопрос."
        )
        return

    # Слишком длинный текст
    if len(text) > 500:
        await update.message.reply_text(
            "⚠️ Хабарлама тым ұзын. Қысқаша жазыңыз.\n"
            "Сообщение слишком длинное. Напишите короче."
        )
        return

    lang = detect_lang(text)
    text_lower = text.lower()

    # Все вопросы батырмасы
    if "барлық" in text_lower or "все вопросы" in text_lower:
        await help_cmd(update, context)
        return

    # Батырма арқылы іздеу
    button_map = {
        "расписание": "расписание", "кесте": "кесте",
        "сессия": "сессия", "стипендия": "стипендия",
        "деканат": "деканат", "библиотека": "библиотека",
        "кітапхана": "библиотека", "кабинет": "кабинет",
    }

    answer = None
    for btn_key, faq_key in button_map.items():
        if btn_key in text_lower and faq_key in FAQ:
            answer = FAQ[faq_key].get(lang, FAQ[faq_key].get("ru", ""))
            break

    # Еркін мәтін
    if not answer:
        answer = get_answer(text, lang)

    # Жауап жіберу
    try:
        await update.message.reply_text(answer, parse_mode='Markdown')
    except Exception:
        clean_answer = answer.replace('*', '').replace('_', '')
        await update.message.reply_text(clean_answer)

    # Тарихты сақтау
    await save_history(user_id, username, text, answer, lang)

# ===== MAIN =====
async def main():
    if not TOKEN:
        print("❌ TELEGRAM_TOKEN табылмады! .env файлын тексер!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ IITU FAQ Bot іске қосылды!")
    print("📌 Тақырыптар: расписание, сессия, стипендия, деканат, библиотека, кабинет")
    print("🔗 Django Admin: http://127.0.0.1:8000/admin")
    app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())