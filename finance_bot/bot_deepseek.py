import asyncio
import sqlite3
from datetime import datetime
from calendar import monthrange
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import BOT_TOKEN

# Конфигурация
API_TOKEN = BOT_TOKEN  # Замените на ваш токен
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Состояния для FSM
class AddAmountState(StatesGroup):
    waiting_for_amount = State()


class EditAmountState(StatesGroup):
    waiting_for_new_amount = State()


class EditDateState(StatesGroup):
    waiting_for_new_date = State()


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


init_db()


# Вспомогательные функции для работы с БД
def add_expense(user_id, amount, date):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (user_id, amount, date) VALUES (?, ?, ?)',
                   (user_id, amount, date))
    conn.commit()
    conn.close()


def get_user_expenses_for_month(user_id, year, month):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    start_date = f"{year}-{month:02d}-01"
    _, last_day = monthrange(year, month)
    end_date = f"{year}-{month:02d}-{last_day}"

    cursor.execute('''
        SELECT id, amount, date FROM expenses 
        WHERE user_id = ? AND date BETWEEN ? AND ?
        ORDER BY date
    ''', (user_id, start_date, end_date))
    expenses = cursor.fetchall()
    conn.close()
    return expenses


def get_all_user_expenses(user_id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, amount, date FROM expenses WHERE user_id = ? ORDER BY date', (user_id,))
    expenses = cursor.fetchall()
    conn.close()
    return expenses


def update_expense_amount(expense_id, new_amount):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE expenses SET amount = ? WHERE id = ?', (new_amount, expense_id))
    conn.commit()
    conn.close()


def update_expense_date(expense_id, new_date):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE expenses SET date = ? WHERE id = ?', (new_date, expense_id))
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()


# Главное меню
def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить", callback_data="add")],
        [InlineKeyboardButton(text="📊 Просмотр", callback_data="view")],
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit")]
    ])
    return keyboard


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🌟 Добро пожаловать в бот учета расходов!\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu()
    )


# Обработчик кнопки "Добавить"
@dp.callback_query(F.data == "add")
async def add_expense_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("💰 Введите сумму (например: 1500.50):")
    await state.set_state(AddAmountState.waiting_for_amount)
    await callback.answer()


@dp.message(AddAmountState.waiting_for_amount)
async def process_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(',', '.'))
        today = datetime.now().strftime("%Y-%m-%d")
        add_expense(message.from_user.id, amount, today)
        await message.answer(f"✅ Добавлено: {amount} руб. за {today}")
        await message.answer("Выберите действие:", reply_markup=get_main_menu())
        await state.clear()
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректное число (например: 1500.50)")


# Обработчик кнопки "Просмотр"
@dp.callback_query(F.data == "view")
async def view_expenses_callback(callback: CallbackQuery):
    now = datetime.now()
    expenses = get_user_expenses_for_month(callback.from_user.id, now.year, now.month)

    if not expenses:
        await callback.message.answer(f"📭 За {now.strftime('%B %Y')} нет расходов")
    else:
        response = f"📅 Расходы за {now.strftime('%B %Y')}:\n\n"
        total = 0
        for expense_id, amount, date in expenses:
            response += f"📌 {date}: {amount} руб.\n"
            total += amount
        response += f"\n💰 Итого за месяц: {total} руб."

        # Общая сумма всех расходов
        all_expenses = get_all_user_expenses(callback.from_user.id)
        total_all = sum(exp[1] for exp in all_expenses)
        response += f"\n🏦 Общая сумма всех расходов: {total_all} руб."

        await callback.message.answer(response)

    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


# Обработчик кнопки "Редактировать"
@dp.callback_query(F.data == "edit")
async def edit_expenses_callback(callback: CallbackQuery):
    expenses = get_all_user_expenses(callback.from_user.id)

    if not expenses:
        await callback.message.answer("📭 У вас пока нет записей для редактирования")
        await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
        await callback.answer()
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for expense_id, amount, date in expenses:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"📌 {date} - {amount} руб.",
                callback_data=f"edit_{expense_id}"
            )
        ])

    # Добавляем кнопку "Назад"
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_main")
    ])

    await callback.message.answer("✏️ Выберите запись для редактирования:", reply_markup=keyboard)
    await callback.answer()


# Обработчик выбора записи для редактирования
@dp.callback_query(F.data.startswith("edit_") & ~F.data.startswith("edit_amount_") & ~F.data.startswith("edit_date_"))
async def select_expense_for_edit(callback: CallbackQuery):
    expense_id = int(callback.data.split("_")[1])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Изменить сумму", callback_data=f"edit_amount_{expense_id}")],
        [InlineKeyboardButton(text="📅 Изменить дату", callback_data=f"edit_date_{expense_id}")],
        [InlineKeyboardButton(text="🗑️ Удалить запись", callback_data=f"delete_{expense_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="edit")]
    ])

    await callback.message.answer("🔧 Что хотите сделать?", reply_markup=keyboard)
    await callback.answer()


# Обработчик изменения суммы
@dp.callback_query(F.data.startswith("edit_amount_"))
async def edit_amount(callback: CallbackQuery, state: FSMContext):
    expense_id = int(callback.data.split("_")[2])
    await state.update_data(expense_id=expense_id)
    await callback.message.answer("💰 Введите новую сумму (например: 1500.50):")
    await state.set_state(EditAmountState.waiting_for_new_amount)
    await callback.answer()


@dp.message(EditAmountState.waiting_for_new_amount)
async def process_new_amount(message: types.Message, state: FSMContext):
    try:
        new_amount = float(message.text.replace(',', '.'))
        data = await state.get_data()
        expense_id = data.get('expense_id')
        if expense_id:
            update_expense_amount(expense_id, new_amount)
            await message.answer(f"✅ Сумма успешно изменена на {new_amount} руб.")
            await message.answer("Выберите действие:", reply_markup=get_main_menu())
        else:
            await message.answer("❌ Ошибка: не найден ID записи")
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите корректное число (например: 1500.50)")


# Обработчик изменения даты
@dp.callback_query(F.data.startswith("edit_date_"))
async def edit_date(callback: CallbackQuery, state: FSMContext):
    expense_id = int(callback.data.split("_")[2])
    await state.update_data(expense_id=expense_id)
    await callback.message.answer("📅 Введите новую дату (в формате ГГГГ-ММ-ДД, например: 2024-12-25):")
    await state.set_state(EditDateState.waiting_for_new_date)
    await callback.answer()


@dp.message(EditDateState.waiting_for_new_date)
async def process_new_date(message: types.Message, state: FSMContext):
    try:
        new_date = message.text.strip()
        # Проверка формата даты
        datetime.strptime(new_date, "%Y-%m-%d")
        data = await state.get_data()
        expense_id = data.get('expense_id')
        if expense_id:
            update_expense_date(expense_id, new_date)
            await message.answer(f"✅ Дата успешно изменена на {new_date}")
            await message.answer("Выберите действие:", reply_markup=get_main_menu())
        else:
            await message.answer("❌ Ошибка: не найден ID записи")
        await state.clear()
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте ГГГГ-ММ-ДД (например: 2024-12-25)")


# Обработчик удаления записи
@dp.callback_query(F.data.startswith("delete_"))
async def delete_expense_callback(callback: CallbackQuery):
    expense_id = int(callback.data.split("_")[1])
    delete_expense(expense_id)
    await callback.message.answer("✅ Запись успешно удалена")
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


# Обработчик кнопки "Назад в меню"
@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.answer("Выберите действие:", reply_markup=get_main_menu())
    await callback.answer()


# Запуск бота
async def main():
    print("🚀 Бот запущен...")
    print("✅ Бот готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())