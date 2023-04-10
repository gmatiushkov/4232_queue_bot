from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton


def start_menu_ikb(is_update):
    ikb = InlineKeyboardMarkup()
    ikb1 = InlineKeyboardButton(text='ОП', callback_data='show oti')
    ikb1_upd = InlineKeyboardButton(text='🔄', callback_data='show oti')
    ikb2 = InlineKeyboardButton(text='УП', callback_data='show inf')
    ikb2_upd = InlineKeyboardButton(text='🔄', callback_data='show inf')
    ikb3 = InlineKeyboardButton(text='👤 Войти', callback_data='log in')
    if is_update == 'oti':
        ikb.add(ikb1_upd, ikb2).add(ikb3)
    elif is_update == 'inf':
        ikb.add(ikb1, ikb2_upd).add(ikb3)
    else:
        ikb.add(ikb1, ikb2).add(ikb3)
    return ikb


def user_menu_ikb():
    ikb = InlineKeyboardMarkup()
    ikb1 = InlineKeyboardButton(text='ОП', callback_data='edit oti')
    ikb2 = InlineKeyboardButton(text='УП', callback_data='edit inf')
    ikb3 = InlineKeyboardButton(text='Изменить код', callback_data='change code')
    ikb.add(ikb1, ikb2).add(ikb3)
    return ikb


def back_ikb():
    ikb = InlineKeyboardMarkup()
    ikb1 = InlineKeyboardButton(text='⬅️ Отмена', callback_data='back')
    ikb.add(ikb1)
    return ikb


def next_ikb():
    ikb = InlineKeyboardMarkup()
    ikb1 = InlineKeyboardButton(text='Далее ➡️', callback_data='next')
    ikb.add(ikb1)
    return ikb


def edit_queue_ikb(queue, name, is_admin, predmet, is_open):
    ikb = InlineKeyboardMarkup()
    ikb1 = InlineKeyboardButton(text='✏  Записаться в конец очереди', callback_data='add {}'.format(predmet))
    ikb2 = InlineKeyboardButton(text='✏  Перезаписаться в конец очереди', callback_data='readd down {}'.format(predmet))
    ikb3 = InlineKeyboardButton(text='❌  Удалить себя из очереди', callback_data='del {}'.format(predmet))
    ikb4 = InlineKeyboardButton(text='⬅️ Назад', callback_data='back')
    ikb5 = InlineKeyboardButton(text='admin', callback_data='admin {}'.format(predmet))
    ikb6 = InlineKeyboardButton(text='🔄', callback_data='upd {}'.format(predmet))

    if name not in queue and is_open:
        ikb.add(ikb1)
    elif name in queue:
        if queue[-1] != name and is_open:
            ikb.add(ikb2)
        ikb.add(ikb3)
    ikb.add(ikb4).insert(ikb6)

    if is_admin:
        ikb.insert(ikb5)

    return ikb


def admin_ikb(queue, predmet, is_open):
    ikb = InlineKeyboardMarkup()
    ikb1 = InlineKeyboardButton(text='✏️  Вписать кого-то', callback_data='insert {}'.format(predmet))
    ikb2 = InlineKeyboardButton(text='❌ Удалить кого-то', callback_data='delete {}'.format(predmet))
    ikb3 = InlineKeyboardButton(text='🌀️ Поменять местами', callback_data='swap {}'.format(predmet))
    ikb4 = InlineKeyboardButton(text='⬅️ Отмена', callback_data='back to edit {}'.format(predmet))
    ikb5 = InlineKeyboardButton(text='🔑 Открыть очередь', callback_data='open {}'.format(predmet))
    ikb6 = InlineKeyboardButton(text='🔒 Закрыть очередь', callback_data='close {}'.format(predmet))
    ikb7 = InlineKeyboardButton(text='🗑 Очистить очередь', callback_data='clear {}'.format(predmet))
    ikb8 = InlineKeyboardButton(text='🔄', callback_data='upd {}'.format(predmet))

    l = len(queue)
    if l <= 30:
        ikb.add(ikb1)
    if l > 0:
        ikb.add(ikb2)
    if l >= 2:
        ikb.add(ikb3)

    if is_open:
        ikb.add(ikb6)
    else:
        ikb.add(ikb5)

    if l > 0:
        ikb.add(ikb7)
    ikb.add(ikb4).insert(ikb8)
    return ikb


def back_to_admin_ikb(predmet):
    ikb = InlineKeyboardMarkup()
    ikb4 = InlineKeyboardButton(text='⬅️ Отмена', callback_data='back to admin {}'.format(predmet))
    ikb.add(ikb4)
    return ikb


def next_to_admin_ikb(predmet):
    ikb = InlineKeyboardMarkup()
    ikb4 = InlineKeyboardButton(text='Готово ➡️', callback_data='back to admin {}'.format(predmet))
    ikb.add(ikb4)
    return ikb


def are_you_sure_ikb(op, predmet):
    ikb = InlineKeyboardMarkup()
    ikb1 = InlineKeyboardButton(text='Да', callback_data='yes {} {}'.format(op, predmet))
    ikb2 = InlineKeyboardButton(text='Нет', callback_data='no {} {}'.format(op, predmet))
    ikb.add(ikb2).insert(ikb1)
    return ikb
