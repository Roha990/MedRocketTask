from datetime import *
import os
import requests

API_USERS = f"https://json.medrocket.ru/users"
API_TODOS = f"https://json.medrocket.ru/todos"


def main() -> None:
    tasks_list = requests.get(API_TODOS)
    user_list = requests.get(API_USERS)
    if not os.path.isdir("tasks"):
        os.mkdir("tasks")
    for user in user_list.json():
        create_task(user, tasks_list)


# Функция для создания задач пользователя с выгрузкой в папку "tasks".
# На вход функции подается пользователь и необработанный массив ВСЕХ задач.
def create_task(user, tasks) -> None:
    user_tasks = [[], []]  # Первый массив - это список завершенных задач. Второй - список актуальных задач.
    for task in tasks.json():
        if "userId" in task:
            if task["userId"] == user["id"]:
                if task["completed"]:
                    user_tasks[0].append(task)
                else:
                    user_tasks[1].append(task)
    if not os.path.isfile(f'tasks/{user["username"]}.txt') or not os.path.exists(f'tasks/{user["username"]}.txt'):
        write_task(user, user_tasks)
    else:
        datatime_create_task = datetime.fromtimestamp(os.stat(f'tasks/{user["username"]}.txt').st_ctime)
        old_name = f'tasks/{user["username"]}'
        new_name = f'tasks/old_{user["username"]}_{datetime.strftime(datatime_create_task, "%Y-%m-%dT%H_%M")}'
        # Если одинаковое имя файла добавляет в конец "_another"
        try:
            os.rename(old_name + ".txt", new_name + ".txt")
            write_task(user, user_tasks)
        except FileExistsError:
            additionally_name = new_name + "_another"
            while os.path.isfile(additionally_name + ".txt"):
                collusia = collusia + "_another"
            os.rename(new_name + ".txt", collusia + ".txt")
            write_task(user, user_tasks)


# Функция записи текста в файл
# На вход функции подается пользователь и обработанный массив задач пользователя
def write_task(user, user_tasks) -> None:
    with open(f'tasks/{user["username"]}.txt', 'w') as report:
        report.write(f'# Отчёт для {user["company"]["name"]}.'
                     f'\n{user["name"]} <{user["email"]}> {datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M")} '
                     f'\nВсего задач:{len(user_tasks[0]) + len(user_tasks[1])}'
                     f'\n\n')
        if len(user_tasks[0] + user_tasks[1]) == 0:
            report.write(f"Для пользователя '{user['name']}'' задач нет")
        else:
            report.write(f'## Актуальные задачи ({len(user_tasks[1])}):')
            write_task_title(user_tasks[1], report)
            report.write(f'\n\n## Завершенные задачи ({len(user_tasks[0])}):')
            write_task_title(user_tasks[0], report)


# Функция записи задач в файл
def write_task_title(tasks, file) -> None:
    for task in tasks:
        if len(task["title"]) > 46:
            file.write(f'\n- {task["title"][0:46]}…')
        else:
            file.write(f'\n- {task["title"]}')
