import sqlite3
from datetime import datetime
from collections import defaultdict

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import BOT_TOKEN

# ================= НАСТРОЙКИ =================
BOT_TOKEN = BOT_TOKEN  # Замените на ваш токен
DB_NAME = "finance.db"

# Словарь для вывода месяцев на русском
MONTHS_RU = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
    5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
    9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}


# =============================================

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()


# Машина состояний (FSM)
class AddState(StatesGroup):
    waiting_for_amount = State()


class EditState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_date = State()


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ================= ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =================
def format_date_for_user(db_date: str) -> str:
    """Преобразует дату из БД (YYYY-MM-DD) в формат для пользователя (DD.MM.YYYY)"""
    y, m, d = db_date.split("-")
    return f"{d}.{m}.{y}"


async def show_edit_list(target):
    """Показывает список записей для редактирования"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, amount, date FROM records ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()

    builder = InlineKeyboardBuilder()
    if rows:
        for row in rows:
            r_id, amount, date = row
            amount_str = f"{amount:g}"
            # ИЗМЕНЕНИЕ: Форматируем дату для кнопки
            user_date = format_date_for_user(date)
            builder.row(InlineKeyboardButton(text=f"{amount_str} ₽ | {user_date}", callback_data=f"edit_rec:{r_id}"))

    builder.row(InlineKeyboardButton(text="« В главное меню", callback_data="back_to_start"))

    text = "Выберите запись для редактирования:" if rows else "📭 Нет записей для редактирования."

    if isinstance(target, Message):
        await target.answer(text, reply_markup=builder.as_markup())
    elif isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=builder.as_markup())
        await target.answer()


# ================= ОБРАБОТЧИКИ =================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Добавить", callback_data="action_add"))
    builder.row(InlineKeyboardButton(text="📊 Просмотр", callback_data="action_view"))
    builder.row(InlineKeyboardButton(text="✏️ Редактировать", callback_data="action_edit"))
    await message.answer("👋 Добро пожаловать! Выберите действие:", reply_markup=builder.as_markup())


@dp.callback_query(F.data == "back_to_start")
async def cb_back_to_start(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Добавить", callback_data="action_add"))
    builder.row(InlineKeyboardButton(text="📊 Просмотр", callback_data="action_view"))
    builder.row(InlineKeyboardButton(text="✏️ Редактировать", callback_data="action_edit"))
    await callback.message.edit_text("Выберите действие:", reply_markup=builder.as_markup())
    await callback.answer()


# --- ДОБАВИТЬ ---
@dp.callback_query(F.data == "action_add")
async def cb_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddState.waiting_for_amount)
    await callback.message.edit_text("💰 Введите сумму для добавления:")
    await callback.answer()


@dp.message(AddState.waiting_for_amount)
async def msg_add_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))

        # Для БД сохраняем YYYY-MM-DD (для сортировки)
        db_date = datetime.now().strftime("%Y-%m-%d")
        # Для сообщения пользователю используем DD.MM.YYYY
        user_date = datetime.now().strftime("%d.%m.%Y")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO records (amount, date) VALUES (?, ?)", (amount, db_date))
        conn.commit()
        conn.close()

        # ИЗМЕНЕНИЕ: Выводим дату в формате ДД.ММ.ГГГГ
        await message.answer(f"✅ Сохранено: **{amount:g} ₽** на {user_date}", parse_mode="Markdown")
        await state.clear()
        await cmd_start(message)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число (например, 1500 или 1500.50).")


# --- ПРОСМОТР ---
@dp.callback_query(F.data == "action_view")
async def cb_view(callback: CallbackQuery):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT amount, date FROM records ORDER BY date ASC")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await callback.message.edit_text("📭 Записей пока нет.")
        await callback.answer()
        return

    months = defaultdict(list)
    grand_total = 0.0

    for amount, date in rows:
        month = date[:7]  # Формат YYYY-MM
        months[month].append((amount, date))
        grand_total += amount

    text = "📊 **Статистика по месяцам:**\n\n"

    for month, records in sorted(months.items()):
        month_total = sum(record[0] for record in records)

        year, month_num = month.split("-")
        month_name = f"{MONTHS_RU[int(month_num)]} {year}"

        text += f"📅 **{month_name}**\n"
        for amt, full_date in records:
            # Преобразуем дату из YYYY-MM-DD в DD.MM.YYYY
            user_date = format_date_for_user(full_date)
            text += f"  • {amt:g} ₽ - {user_date}\n"
        text += f"  _Итого за месяц: {month_total:g} ₽_\n\n"

    text += f"💰 **Общая сумма: {grand_total:g} ₽**"

    if len(text) > 4000:
        text = text[:3900] + "\n\n⚠️ _Список слишком длинный и был обрезан._"

    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()


# --- РЕДАКТИРОВАТЬ (Список) ---
@dp.callback_query(F.data == "action_edit")
async def cb_edit(callback: CallbackQuery):
    await show_edit_list(callback)


# --- РЕДАКТИРОВАТЬ (Выбор конкретной записи) ---
@dp.callback_query(F.data.startswith("edit_rec:"))
async def cb_edit_rec(callback: CallbackQuery):
    record_id = int(callback.data.split(":")[1])
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💰 Изменить сумму", callback_data=f"edit_amt:{record_id}"))
    builder.row(InlineKeyboardButton(text="📅 Изменить дату", callback_data=f"edit_dt:{record_id}"))
    builder.row(InlineKeyboardButton(text="🗑 Удалить запись", callback_data=f"del_rec:{record_id}"))
    builder.row(InlineKeyboardButton(text="« Назад к списку", callback_data="action_edit"))

    await callback.message.edit_text(f"⚙️ Запись #{record_id}. Выберите действие:", reply_markup=builder.as_markup())
    await callback.answer()


# --- Изменение суммы ---
@dp.callback_query(F.data.startswith("edit_amt:"))
async def cb_edit_amt(callback: CallbackQuery, state: FSMContext):
    record_id = int(callback.data.split(":")[1])
    await state.update_data(record_id=record_id)
    await state.set_state(EditState.waiting_for_amount)
    await callback.message.edit_text("💰 Введите новую сумму:")
    await callback.answer()


@dp.message(EditState.waiting_for_amount)
async def msg_edit_amt(message: Message, state: FSMContext):
    try:
        new_amount = float(message.text.replace(',', '.'))
        data = await state.get_data()
        record_id = data.get("record_id")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE records SET amount = ? WHERE id = ?", (new_amount, record_id))
        conn.commit()
        conn.close()

        await message.answer(f"✅ Сумма успешно обновлена на **{new_amount:g} ₽**", parse_mode="Markdown")
        await state.clear()
        await show_edit_list(message)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число.")


# --- Изменение даты (ОБНОВЛЕНО) ---
@dp.callback_query(F.data.startswith("edit_dt:"))
async def cb_edit_dt(callback: CallbackQuery, state: FSMContext):
    record_id = int(callback.data.split(":")[1])
    await state.update_data(record_id=record_id)
    await state.set_state(EditState.waiting_for_date)
    # ИЗМЕНЕНИЕ: Просим формат ДД.ММ.ГГГГ
    await callback.message.edit_text("📅 Введите новую дату в формате **ДД.ММ.ГГГГ** (например, 15.01.2026):",
                                     parse_mode="Markdown")
    await callback.answer()


@dp.message(EditState.waiting_for_date)
async def msg_edit_dt(message: Message, state: FSMContext):
    new_date_input = message.text.strip()
    try:
        # 1. Проверяем, что пользователь ввел дату в формате ДД.ММ.ГГГГ
        parsed_date = datetime.strptime(new_date_input, "%d.%m.%Y")
        # 2. Конвертируем её в формат ГГГГ-ММ-ДД для корректного сохранения и сортировки в БД
        db_date = parsed_date.strftime("%Y-%m-%d")
    except ValueError:
        await message.answer("❌ Неверный формат даты. Используйте строго **ДД.ММ.ГГГГ** (например, 15.01.2026).")
        return

    data = await state.get_data()
    record_id = data.get("record_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Сохраняем в БД в формате ГГГГ-ММ-ДД
    cursor.execute("UPDATE records SET date = ? WHERE id = ?", (db_date, record_id))
    conn.commit()
    conn.close()

    # Пользователю показываем в привычном формате
    await message.answer(f"✅ Дата успешно обновлена на **{new_date_input}**", parse_mode="Markdown")
    await state.clear()
    await show_edit_list(message)


# --- Удаление записи ---
@dp.callback_query(F.data.startswith("del_rec:"))
async def cb_del_rec(callback: CallbackQuery):
    record_id = int(callback.data.split(":")[1])

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

    await callback.answer("✅ Запись удалена")
    await show_edit_list(callback)


# ================= ЗАПУСК =================
async def main():
    init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())