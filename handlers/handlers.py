import json
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

main_router = Router()


class Notes(StatesGroup):
    title_note = State()
    description_note = State()
    get_notes = State()
    delete_note = State()


@main_router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        'Приветствую в телеграм боте для сохранения заметок.\n'
        'Для ознакомления с командами пропиши /help'
    )


@main_router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        '<b><i>Доступные команды:</i></b>\n'
        '<b>/help</b> - Информация о командах.\n'
        '<b>/add_note</b> - Добавить заметку.\n'
        '<b>/notes</b> - Просмотреть заметки.\n'
        '<b>/delete_note</b> - Удалить заметку.\n'
        '<b>/cancel</b> - Отменить действие.'
    )


@main_router.message(Command('cancel'), StateFilter('*'))
async def cmd_cancel(message: Message, state: FSMContext):
    await message.answer(
        text='Действие было отменено.', reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@main_router.message(Command('add_note'))
async def cmd_add_note(message: Message, state: FSMContext):
    await message.answer('Введите название заметки')
    await state.set_state(Notes.title_note)


@main_router.message(StateFilter(Notes.title_note))
async def add_title(message: Message, state: FSMContext):
    title = message.text
    user_id = str(message.from_user.id)

    with open('json/notes.json') as file:
        notes = json.load(file)

    if user_id in notes and title in notes[user_id]:
        await message.answer(
            'Заметка с таким названием уже есть.'
            'Пожалуйста, введите другое.'
        )
        return await state.set_state(Notes.title_note)

    await state.update_data(title=title)
    await message.answer('Теперь введите описание заметки.')
    await state.set_state(Notes.description_note)


@main_router.message(StateFilter(Notes.description_note))
async def add_description(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = str(message.from_user.id)
    title = data['title']
    description = message.text

    with open('json/notes.json', 'r') as file:
        notes = json.load(file)

    if user_id not in notes:
        user_notes = {title: description}
        notes[user_id] = user_notes
    else:
        notes[user_id][title] = description

    with open('json/notes.json', 'w') as file:
        json.dump(notes, file, indent=4)

    await message.answer(
        'Отлично, была создана новая заметка.\n'
        f'Название: {title}\n'
        f'Описание: {description}'
    )
    await state.clear()


@main_router.message(Command('delete_note', 'notes'))
async def cmd_get_notes(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)

    with open('json/notes.json', 'r') as file:
        notes = json.load(file)

    if user_id not in notes or not notes[user_id]:
        await message.answer('У вас нет заметок.')
        return

    titles = [title for title in notes[user_id].keys()]

    if len(titles) <= 5:
        row = [KeyboardButton(text=title) for title in titles]

        await message.answer(
            text='Выберите заметку',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[row], resize_keyboard=True
                ),
        )
    else:
        titles_1 = titles[:5]
        titles_2 = titles[6:]
        row_1 = [KeyboardButton(text=title) for title in titles_1]
        row_2 = [KeyboardButton(text=title) for title in titles_2]

        await message.answer(
            text='Выберите заметку',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[row_1, row_2], resize_keyboard=True
            ),
        )
    await state.update_data(titles=titles)

    if message.text == '/delete_note':
        await state.set_state(Notes.delete_note)
    else:
        await state.set_state(Notes.get_notes)


@main_router.message(StateFilter(Notes.delete_note))
@main_router.message(StateFilter(Notes.get_notes))
async def get_and_delete_notes(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    title = message.text
    data = await state.get_data()
    titles = data['titles']

    if title not in titles:
        await message.answer('Введите существующую заметку')
        await state.clear()
        return await cmd_get_notes(message, state)

    with open('json/notes.json', 'r') as file:
        notes = json.load(file)

    if await state.get_state() == 'Notes:get_notes':
        description = notes[user_id][title]

        await message.answer(
            text=f'<b>{title}</b>\n' f'{description}',
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
    else:
        notes[user_id].pop(title)

        with open('json/notes.json', 'w') as file:
            json.dump(notes, file, indent=4)

        await message.answer(
            text='Заметка была успешно удалена.',
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
