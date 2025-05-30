# Модификация проекта: Добавление напоминаний и админ-панели мастера

##  Описание модификации

В рамках модификации проекта был реализован функционал **автоматических уведомлений** клиентам, которые записались на процедуру. Теперь бот **за 24 часа до времени приёма отправляет напоминание** пользователю.

Кроме того, добавлена **внутренняя панель управления для мастера**, через которую можно:
- Просматривать список всех записей
- Отменять любую запись вручную
- Изменять расписание приёма

Эта модификация **повышает удобство работы** с ботом и обеспечивает **дополнительную автоматизацию** бизнес-процесса мастера.

---

##  Техническая реализация

Модификация выполнена на Python с использованием библиотеки `aiogram==2.25.2`. Основное внимание уделено следующим частям проекта:

### 1. Хранение записей

Расширена структура хранения: теперь каждая запись сохраняется с указанием `user_id`, даты и времени, а также типа услуги.

```python
appointments = []
````

---

### 2. Фоновая задача для напоминаний

Создано фоновое задание, которое каждую минуту проверяет, кому из пользователей нужно отправить уведомление.

```python
import asyncio
from datetime import datetime, timedelta

async def notify_upcoming_appointments():
    while True:
        now = datetime.now()
        for appointment in appointments:
            time_diff = appointment['time'] - now
            if timedelta(hours=23, minutes=59) < time_diff < timedelta(days=1, minutes=1):
                await bot.send_message(
                    appointment['user_id'], 
                    f"Напоминаем: у вас завтра запись на {appointment['service']} в {appointment['time'].strftime('%H:%M')}"
                )
        await asyncio.sleep(60)
```

Запускается при старте бота:

```python
loop = asyncio.get_event_loop()
loop.create_task(notify_upcoming_appointments())
```

---

### 3. Админ-панель мастера

Мастер определяется по ID. При вводе команды `/admin` бот отправляет список текущих записей с возможностью их удалить или перенести.

```python
ADMIN_ID = 123456789

@dp.message_handler(commands=['admin'])
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет доступа к админ-панели.")
        return

    if not appointments:
        await message.answer("Записей нет.")
        return

    text = "Текущие записи:\n"
    for i, a in enumerate(appointments):
        text += f"{i+1}. {a['user_name']} — {a['service']} — {a['time'].strftime('%d.%m %H:%M')}\n"
    await message.answer(text)
