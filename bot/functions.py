# считывает данные из файла passwords.txt, возвращает словарь: {'Пароль': 'Имя Фамилия'}
def get_accounts():
    passwords = open('passwords.txt', 'r', encoding='utf8')
    accounts = {}
    for x in passwords.readlines():
        first_name, last_name, code = x.split()
        accounts[code] = first_name + ' ' + last_name
    passwords.close()
    return accounts


def get_free_names(predmet, queue, accounts):
    res = []
    for x in accounts.values():
        if x not in queue:
            res.append(x)
    text = '<b>Люди вне очереди: </b>\n\n' + ''.join([str(i + 1) + '. ' + res[i] + '\n' for i in range(len(res))])
    return res, text

def what_predmet(callback):
    if 'oti' in callback:
        return 'oti'
    elif 'inf' in callback:
        return 'inf'
    else:
        return '*******'


# меняет пароль человека name с old_code на new_code
def change_password(name, old_code, new_code):
    passwords = open('passwords.txt', 'rt', encoding='utf8')
    text = passwords.read()
    text = text.replace(name + ' ' + old_code, name + ' ' + new_code)
    passwords.close()
    passwords = open('passwords.txt', 'wt', encoding='utf8')
    passwords.write(text)
    passwords.close()


def get_queue(predmet):
    if predmet == 'oti':
        res = [x for x in open('oti.txt', encoding='utf8').readlines()]
    elif predmet == 'inf':
        res = [x for x in open('inf.txt', encoding='utf8').readlines()]
    res = [x.replace('\n', '') for x in res]
    return res

def get_updated_queues(all_queues):
    for x in all_queues.keys():
        all_queues[x] = get_queue(x)
    return all_queues


def update_queue_file(predmet, queue):
    text = ''
    for x in queue:
        text += x + '\n'
    if predmet == 'oti':
        tf = open('oti.txt', 'wt', encoding='utf8')
        tf.write(text)
        tf.close()
    elif predmet == 'inf':
        tf = open('inf.txt', 'wt', encoding='utf8')
        tf.write(text)
        tf.close()


def queue_text(predmet, queue, name):
    if predmet == 'inf':
        text = '<b>Учебная практика:</b>\n\n' \
               + ''.join([str(i + 1) + '. '
                          + queue[i] + '\n' for i in range(len(queue))])
    elif predmet == 'oti':
        text = '<b>Основы программирования:</b>\n\n' \
               + ''.join([str(i + 1) + '. '
                          + queue[i] + '\n' for i in range(len(queue))])
    if name in queue:
        text = text.replace(name, '<b>' + name + '</b>')
    return text[:-1]


def add_or_del(cmd, predmet, queue, name):
    if cmd == 'add':
        if name in queue:
            queue.remove(name)
        queue.append(name)
    elif cmd == 'del':
        if name in queue:
            queue.remove(name)
    update_queue_file(predmet, queue)


def swap(cmd, predmet, queue, first, second):
    if first in queue and second in queue:
        queue[queue.index(first)], queue[queue.index(second)] = queue[queue.index(second)], queue[queue.index(first)]
    update_queue_file(predmet, queue)

# def get_name(code):
#     accounts = get_accounts()
#     try:
#         name = accounts[code]
#     except KeyError:
