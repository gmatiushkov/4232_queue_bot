from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import MessageNotModified

from config import TOKEN_API
from messages import *
from functions import *
from keybords import *

bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=MemoryStorage())

accounts = get_accounts()
all_queues = {'oti': get_queue('oti'), 'inf': get_queue('inf')}
admins = [x.replace('\n', '') for x in open('admins.txt', encoding='utf8').readlines()]
queue_is_open = {'oti': True, 'inf': False}


class UserStates(StatesGroup):
    log_out = State()
    waiting_for_code = State()
    log_in = State()
    changing_the_code_1 = State()
    changing_the_code_2 = State()
    edit = State()
    admin = State()
    waiting_num = State()
    waiting_num2 = State()


async def on_startup(_):
    print('Бот живой!')


@dp.message_handler(commands=['start'], state='*')
async def start_command(message: types.Message, state: FSMContext):
    data = await state.get_data()

    try:
        last_message = data['lastmessage']
        await bot.delete_message(chat_id=message.chat.id, message_id=last_message)
    except Exception:
        pass
    msg = await message.answer(text=WELCOME,
                               parse_mode='html',
                               reply_markup=start_menu_ikb('default'))
    await message.delete()
    await UserStates.log_out.set()
    await state.update_data(lastmessage=msg['message_id'])


@dp.callback_query_handler(text='log in', state=UserStates.log_out)
async def log_in(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(ENTER_CODE, parse_mode='html', reply_markup=back_ikb())
    await state.update_data(lastmessage=callback.message.message_id)  # сохранение ID последнего сообщения бота
    await state.update_data(lasttext=callback.message.text)  # сохранение текста последнего сообщения бота
    await UserStates.waiting_for_code.set()
    await callback.answer()


@dp.callback_query_handler(state=UserStates.log_out)
async def show(callback: types.CallbackQuery, state: FSMContext):
    global all_queues
    all_queues = get_updated_queues(all_queues)
    predmet = what_predmet(callback.data)
    text = queue_text(predmet, all_queues[predmet], 'noname')
    try:
        await callback.message.edit_text(text, parse_mode='html', reply_markup=start_menu_ikb(predmet))
    except MessageNotModified:
        await callback.answer('Обновлено')
    else:
        await callback.answer()


@dp.callback_query_handler(text='back', state=UserStates.waiting_for_code)
async def back_to_start_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(text=WELCOME, parse_mode='html', reply_markup=start_menu_ikb('default'))
    await UserStates.log_out.set()
    await callback.answer()


@dp.callback_query_handler(text='next', state=UserStates.log_in)
async def next_to_user_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(text=USER_MENU, parse_mode='html', reply_markup=user_menu_ikb())
    await callback.answer()


@dp.callback_query_handler(text='change code', state=UserStates.log_in)
async def change_code(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(text=ENTER_OLD_CODE, parse_mode='html', reply_markup=back_ikb())
    await UserStates.changing_the_code_1.set()
    await callback.answer()


@dp.callback_query_handler(text='back',
                           state=[UserStates.changing_the_code_1, UserStates.changing_the_code_2, UserStates.edit,
                                  UserStates.edit])
async def cancel_changing_the_code(callback: types.CallbackQuery):
    await callback.message.edit_text(text=USER_MENU, parse_mode='html', reply_markup=user_menu_ikb())
    await UserStates.log_in.set()
    await callback.answer()


@dp.callback_query_handler(state=UserStates.log_in)
async def edit(callback: types.CallbackQuery, state: FSMContext):
    global all_queues
    all_queues = get_updated_queues(all_queues)
    predmet = what_predmet(callback.data)
    await state.update_data(queue=predmet)
    data = await state.get_data()
    code = data['code']
    name = accounts[code]
    await callback.message.edit_text(text=queue_text(predmet, all_queues[predmet], name), parse_mode='html',
                                     reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'], predmet,
                                                                 queue_is_open[predmet]))
    await UserStates.edit.set()
    await callback.answer()


@dp.callback_query_handler(state=UserStates.edit)
async def edit_me(callback: types.CallbackQuery, state: FSMContext):
    global all_queues
    all_queues = get_updated_queues(all_queues)
    predmet = what_predmet(callback.data)
    data = await state.get_data()
    code = data['code']
    name = accounts[code]

    if 'no del' in callback.data:
        await callback.message.edit_text(text=queue_text(predmet, all_queues[predmet], name), parse_mode='html',
                                         reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                     predmet, queue_is_open[predmet]))
        await callback.answer()

    elif 'no add' in callback.data:
        await callback.message.edit_text(text=queue_text(predmet, all_queues[predmet], name), parse_mode='html',
                                         reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                     predmet, queue_is_open[predmet]))
        await callback.answer()

    elif 'no readd down' in callback.data:
        await callback.message.edit_text(text=queue_text(predmet, all_queues[predmet], name), parse_mode='html',
                                         reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                     predmet, queue_is_open[predmet]))
        await callback.answer()

    elif 'yes readd down' in callback.data:
        if queue_is_open[predmet]:
            if name not in all_queues[predmet]:
                text = queue_text(predmet, all_queues[predmet], name)
                await callback.message.edit_text(text=text, parse_mode='html',
                                                 reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                             predmet, queue_is_open[predmet]))
                await callback.answer(YOU_NOT_IN_QUEUE_NOW)
            else:
                all_queues[predmet].remove(name)
                all_queues[predmet].append(name)
                update_queue_file(predmet, all_queues[predmet])
                text = queue_text(predmet, all_queues[predmet], name)
                await callback.message.edit_text(text=text, parse_mode='html',
                                                 reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                             predmet, queue_is_open[predmet]))
        await callback.answer()


    elif 'yes del' in callback.data:
        if name not in all_queues[predmet]:
            text = queue_text(predmet, all_queues[predmet], name)
            await callback.message.edit_text(text=text, parse_mode='html',
                                             reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                         predmet, queue_is_open[predmet]))
            await callback.answer(YOU_NOT_IN_QUEUE_NOW)
        else:
            all_queues[predmet].remove(name)
            update_queue_file(predmet, all_queues[predmet])
            text = queue_text(predmet, all_queues[predmet], name)
            await callback.message.edit_text(text=text, parse_mode='html',
                                             reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                         predmet, queue_is_open[predmet]))
        await callback.answer()

    elif 'readd down' in callback.data:
        await callback.message.edit_text(text=ARE_YOU_SURE_ADD, parse_mode='html',
                                         reply_markup=are_you_sure_ikb('readd down', predmet))
        await callback.answer()

    elif 'add' in callback.data:
        if queue_is_open[predmet]:
            if name in all_queues[predmet]:
                await callback.answer(YOU_ALREADY_IN_QUEUE)
            else:
                all_queues[predmet].append(name)
                update_queue_file(predmet, all_queues[predmet])
                text = queue_text(predmet, all_queues[predmet], name)
                await callback.message.edit_text(text=text, parse_mode='html',
                                                 reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                             predmet, queue_is_open[predmet]))
        else:
            await callback.answer(QUEUE_IS_CLOSED)
            await callback.message.edit_text(text=queue_text(predmet, all_queues[predmet], name), parse_mode='html',
                                             reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                         predmet, queue_is_open[predmet]))
        await callback.answer()

    elif 'del' in callback.data:
        await callback.message.edit_text(text=ARE_YOU_SURE_DEL, parse_mode='html',
                                         reply_markup=are_you_sure_ikb('del', predmet))
        await callback.answer()


    elif 'admin' in callback.data:
        text = queue_text(predmet, all_queues[predmet], 'noname')
        await callback.message.edit_text(text=text, parse_mode='html',
                                         reply_markup=admin_ikb(all_queues[predmet], predmet, queue_is_open[predmet]))
        await UserStates.admin.set()
        await callback.answer()

    elif 'upd' in callback.data:
        all_queues = get_updated_queues(all_queues)
        data = await state.get_data()
        code = data['code']
        name = accounts[code]
        try:
            await callback.message.edit_text(text=queue_text(predmet, all_queues[predmet], name), parse_mode='html',
                                             reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                         predmet, queue_is_open[predmet]))
        except MessageNotModified:
            pass
        await callback.answer('Обновлено')


@dp.callback_query_handler(state=UserStates.admin)
async def admin(callback: types.CallbackQuery, state: FSMContext):
    global all_queues
    all_queues = get_updated_queues(all_queues)
    predmet = what_predmet(callback.data)
    data = await state.get_data()
    code = data['code']
    name = accounts[code]

    if 'insert' in callback.data:
        text = get_free_names(predmet, all_queues[predmet], accounts)[1]
        await callback.message.edit_text(text=text + INSERT_WHO, parse_mode='html',
                                         reply_markup=back_to_admin_ikb(predmet))
        await UserStates.waiting_num.set()
        await state.update_data(operation='insert')
        await callback.answer()

    elif 'delete' in callback.data:
        text = queue_text(predmet, all_queues[predmet], 'noname')
        await callback.message.edit_text(text=text + DELETE_WHO, parse_mode='html',
                                         reply_markup=back_to_admin_ikb(predmet))
        await UserStates.waiting_num.set()
        await state.update_data(operation='delete')
        await callback.answer()

    elif 'swap' in callback.data:
        text = queue_text(predmet, all_queues[predmet], 'noname')
        await callback.message.edit_text(text=text + SWAP_WHO, parse_mode='html',
                                         reply_markup=back_to_admin_ikb(predmet))
        await UserStates.waiting_num.set()
        await state.update_data(operation='swap')
        await callback.answer()

    elif 'back to edit' in callback.data:
        await callback.message.edit_text(text=queue_text(predmet, all_queues[predmet], name), parse_mode='html',
                                         reply_markup=edit_queue_ikb(all_queues[predmet], name, data['isadmin'],
                                                                     predmet, queue_is_open[predmet]))
        await UserStates.edit.set()
        await callback.answer()

    elif 'open' in callback.data:
        queue_is_open[predmet] = True
        text = queue_text(predmet, all_queues[predmet], 'noname')
        await callback.message.edit_text(text=text, parse_mode='html',
                                         reply_markup=admin_ikb(all_queues[predmet], predmet, queue_is_open[predmet]))
        await callback.answer()

    elif 'close' in callback.data:
        queue_is_open[predmet] = False
        text = queue_text(predmet, all_queues[predmet], 'noname')
        await callback.message.edit_text(text=text, parse_mode='html',
                                         reply_markup=admin_ikb(all_queues[predmet], predmet, queue_is_open[predmet]))
        await callback.answer()

    elif 'no' in callback.data:
        text = queue_text(predmet, all_queues[predmet], 'noname')
        await callback.message.edit_text(text=text, parse_mode='html',
                                         reply_markup=admin_ikb(all_queues[predmet], predmet, queue_is_open[predmet]))
        await callback.answer()

    elif 'yes clear' in callback.data:
        all_queues[predmet] = []
        update_queue_file(predmet, all_queues[predmet])
        text = queue_text(predmet, all_queues[predmet], 'noname')
        await callback.message.edit_text(text=text, parse_mode='html',
                                         reply_markup=admin_ikb(all_queues[predmet], predmet, queue_is_open[predmet]))
        await callback.answer()

    elif 'clear' in callback.data:
        await callback.message.edit_text(text=ARE_YOU_SURE_CLEAR, parse_mode='html',
                                         reply_markup=are_you_sure_ikb('clear', predmet))
        await callback.answer()

    elif 'upd' in callback.data:
        text = queue_text(predmet, all_queues[predmet], 'noname')
        try:
            await callback.message.edit_text(text=text, parse_mode='html',
                                             reply_markup=admin_ikb(all_queues[predmet], predmet,
                                                                    queue_is_open[predmet]))
        except MessageNotModified:
            pass
        await callback.answer('Обновлено')


@dp.callback_query_handler(state=[UserStates.waiting_num, UserStates.waiting_num2])
async def back_to_admin(callback: types.CallbackQuery, state: FSMContext):
    global all_queues
    all_queues = get_updated_queues(all_queues)
    predmet = what_predmet(callback.data)
    data = await state.get_data()
    code = data['code']
    name = accounts[code]
    text = queue_text(predmet, all_queues[predmet], name)
    if 'back to admin' in callback.data:
        await callback.message.edit_text(text=text, parse_mode='html',
                                         reply_markup=admin_ikb(all_queues[predmet], predmet, queue_is_open[predmet]))
        await UserStates.admin.set()
        await callback.answer()


@dp.message_handler(content_types=types.ContentType.TEXT, state=UserStates.waiting_num)
async def num_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_message, last_text, predmet, oper = data['lastmessage'], data['lasttext'], data['queue'], data['operation']
    people = get_free_names(predmet, all_queues[predmet], accounts)[0]
    text = queue_text(predmet, all_queues[predmet], 'noname')
    if oper == 'insert':
        if message.text.isdigit() and len(people) >= int(message.text) > 0:
            num = int(message.text)
            await bot.edit_message_text(
                text=text + INSERT_WHERE.format(people[num - 1]), chat_id=message.chat.id, message_id=last_message,
                parse_mode='html',
                reply_markup=back_to_admin_ikb(predmet))
            await state.update_data(nameoper=people[num - 1])
            await message.delete()
            await UserStates.waiting_num2.set()
        else:
            try:
                await bot.edit_message_text(
                    text=get_free_names(predmet, all_queues[predmet], accounts)[1] + WRONG_NUM + INSERT_WHO,
                    chat_id=message.chat.id,
                    message_id=last_message, parse_mode='html',
                    reply_markup=back_to_admin_ikb(predmet))
            except MessageNotModified:
                pass
            finally:
                await message.delete()
    elif oper == 'delete':
        if message.text.isdigit() and len(all_queues[predmet]) >= int(message.text) > 0:
            num = int(message.text)
            name = all_queues[predmet][num - 1]
            all_queues[predmet].remove(all_queues[predmet][num - 1])
            update_queue_file(predmet, all_queues[predmet])
            text = queue_text(predmet, all_queues[predmet], 'noname')
            await bot.edit_message_text(text=text + DELETE_DONE.format(name), chat_id=message.chat.id,
                                        message_id=last_message, parse_mode='html',
                                        reply_markup=next_to_admin_ikb(predmet))
            await message.delete()
        else:
            try:
                await bot.edit_message_text(
                    text=text + WRONG_NUM + DELETE_WHO, chat_id=message.chat.id,
                    message_id=last_message, parse_mode='html',
                    reply_markup=back_to_admin_ikb(predmet))
            except MessageNotModified:
                pass
            finally:
                await message.delete()

    elif oper == 'swap':
        if message.text.isdigit() and len(all_queues[predmet]) >= int(message.text) > 0:
            num = int(message.text)
            name = all_queues[predmet][num - 1]
            await state.update_data(swapnum=num)
            await bot.edit_message_text(
                text=text + SWAP_WITH_WHO.format(name), chat_id=message.chat.id, message_id=last_message,
                parse_mode='html',
                reply_markup=back_to_admin_ikb(predmet))
            await message.delete()
            await UserStates.waiting_num2.set()
        else:
            try:
                await bot.edit_message_text(
                    text=text + WRONG_NUM + SWAP_WHO, chat_id=message.chat.id,
                    message_id=last_message, parse_mode='html',
                    reply_markup=back_to_admin_ikb(predmet))
            except MessageNotModified:
                pass
            finally:
                await message.delete()


@dp.message_handler(content_types=types.ContentType.TEXT, state=UserStates.waiting_num2)
async def num2_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    last_message, last_text, predmet, oper = data['lastmessage'], data['lasttext'], data['queue'], data['operation']
    try:
        name = data['nameoper']
    except KeyError:
        pass
    text = queue_text(predmet, all_queues[predmet], 'noname')
    if oper == 'insert':
        if message.text.isdigit() and len(all_queues[predmet]) + 1 >= int(message.text) > 0:
            num = int(message.text)
            all_queues[predmet].insert(int(message.text) - 1, name)
            update_queue_file(predmet, all_queues[predmet])
            text = queue_text(predmet, all_queues[predmet], 'noname')
            await bot.edit_message_text(text=text + INSERT_DONE.format(name), chat_id=message.chat.id,
                                        message_id=last_message,
                                        parse_mode='html',
                                        reply_markup=next_to_admin_ikb(predmet))
            await message.delete()
        else:
            try:
                await bot.edit_message_text(
                    text=text + WRONG_NUM + INSERT_WHERE.format(data['nameoper']), chat_id=message.chat.id,
                    message_id=last_message, parse_mode='html',
                    reply_markup=back_to_admin_ikb(predmet))
            except MessageNotModified:
                pass
            finally:
                await message.delete()
    elif oper == 'swap':
        if message.text.isdigit() and len(all_queues[predmet]) >= int(message.text) > 0:
            num = int(message.text)
            queue = all_queues[predmet]
            swapindex1 = data['swapnum'] - 1
            swapindex2 = num - 1
            swapname1 = queue[swapindex1]
            swapname2 = queue[swapindex2]
            queue = all_queues[predmet]
            x = queue[swapindex1]
            queue[swapindex1] = queue[swapindex2]
            queue[swapindex2] = x
            all_queues[predmet] = queue
            update_queue_file(predmet, all_queues[predmet])
            text = queue_text(predmet, all_queues[predmet], 'noname')
            await bot.edit_message_text(text=text + SWAP_DONE.format(swapname1, swapname2), chat_id=message.chat.id,
                                        message_id=last_message,
                                        parse_mode='html',
                                        reply_markup=next_to_admin_ikb(predmet))
            await message.delete()
        else:
            try:
                await bot.edit_message_text(
                    text=text + WRONG_NUM + SWAP_WITH_WHO, chat_id=message.chat.id,
                    message_id=last_message, parse_mode='html',
                    reply_markup=back_to_admin_ikb(predmet))
            except MessageNotModified:
                pass
            finally:
                await message.delete()


@dp.message_handler(content_types=types.ContentType.TEXT, state=UserStates.waiting_for_code)
async def code_entered(message: types.Message, state: FSMContext):
    global accounts
    accounts = get_accounts()
    global admins
    data = await state.get_data()
    last_message, last_text = data['lastmessage'], data['lasttext']
    if message.text in accounts.keys():
        name = accounts[message.text]
        await bot.edit_message_text(
            text=HELLO.format(name),
            chat_id=message.chat.id, message_id=last_message,
            parse_mode='html', reply_markup=next_ikb())
        await message.delete()
        await UserStates.log_in.set()
        await state.update_data(name=name)
        await state.update_data(code=message.text)
        admins = [x.replace('\n', '') for x in open('admins.txt', encoding='utf8').readlines()]
        await state.update_data(isadmin=name in admins)
    else:
        try:
            await bot.edit_message_text(text=WRONG_CODE, chat_id=message.chat.id, message_id=last_message,
                                        parse_mode='html', reply_markup=back_ikb())
        except MessageNotModified:
            pass
        finally:
            await message.delete()


@dp.message_handler(content_types=types.ContentType.TEXT, state=UserStates.changing_the_code_1)
async def old_code_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    old_code, last_message = data['code'], data['lastmessage']
    if message.text == old_code:
        await bot.edit_message_text(text=ENTER_NEW_CODE, chat_id=message.chat.id, message_id=last_message,
                                    parse_mode='html', reply_markup=back_ikb())
        await UserStates.changing_the_code_2.set()
        await message.delete()
    else:
        try:
            await bot.edit_message_text(text=WRONG_CODE, chat_id=message.chat.id, message_id=last_message,
                                        parse_mode='html', reply_markup=back_ikb())
        except MessageNotModified:
            pass
        finally:
            await message.delete()


@dp.message_handler(content_types=types.ContentType.TEXT, state=UserStates.changing_the_code_2)
async def new_code_entered(message: types.Message, state: FSMContext):
    data = await state.get_data()
    old_code, last_message = data['code'], data['lastmessage']
    if old_code == message.text:
        try:
            await bot.edit_message_text(text=CODES_ARE_EQUAL, chat_id=message.chat.id, message_id=last_message,
                                        parse_mode='html', reply_markup=back_ikb())
        except MessageNotModified:
            pass
        finally:
            return await message.delete()
    if len(message.text) > 20:
        try:
            await bot.edit_message_text(text=TO_LONG_CODE, chat_id=message.chat.id, message_id=last_message,
                                        parse_mode='html', reply_markup=back_ikb())
        except MessageNotModified:
            pass
        finally:
            return await message.delete()
    if len(message.text) < 4:
        try:
            await bot.edit_message_text(text=TO_SHORT_CODE, chat_id=message.chat.id, message_id=last_message,
                                        parse_mode='html', reply_markup=back_ikb())
        except MessageNotModified:
            pass
        finally:
            return await message.delete()
    if any(x not in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for x in message.text):
        try:
            await bot.edit_message_text(text=BAD_SYMBOLS, chat_id=message.chat.id, message_id=last_message,
                                        parse_mode='html', reply_markup=back_ikb())
        except MessageNotModified:
            pass
        finally:
            return await message.delete()
    global accounts
    if message.text in accounts.keys():
        try:
            await bot.edit_message_text(text=NOT_ORIGINAL_CODE, chat_id=message.chat.id, message_id=last_message,
                                        parse_mode='html', reply_markup=back_ikb())
        except MessageNotModified:
            pass
        finally:
            return await message.delete()
    change_password(accounts[old_code], old_code, message.text)
    accounts = get_accounts()
    await state.update_data(code=message.text)
    await UserStates.log_in.set()
    await message.delete()
    await bot.edit_message_text(text=CODE_CHANGED + message.text, chat_id=message.chat.id, message_id=last_message,
                                parse_mode='html', reply_markup=next_ikb())


@dp.message_handler(content_types=types.ContentType.ANY, state='*')
async def shit_filter(message: types.Message):
    await message.delete()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
