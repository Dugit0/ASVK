import xmlrpc.client
from bs4 import BeautifulSoup
import os
import sys

tests = "tests"  # Путь до директории с тестами

# Создание соединения с сервером
server = xmlrpc.client.ServerProxy('http://myserver:9000')

# Проход по всем тестам
for test in os.listdir(tests):
    path_test = os.path.join(tests, test)

    # Открытие и считывание файла
    with open(path_test, encoding="utf-8") as f_inp:
        try:
            soup = BeautifulSoup(f_inp.read(), "lxml")
        except:
            print("Неверный формат .xml файла", file=sys.stderr)
            sys.exit(1)

    # Парсинг файла с входными данными с проверкой на корректность формата файла
    data = soup.data
    if data == None:
        print("Не найден тег data", file=sys.stderr)
        sys.exit(1)

    if data.processors == None:
        print("Не найден тег processors", file=sys.stderr)
        sys.exit(1)
    # Список с предельными нагрузками на процессоры
    proc_limits = [int(tag.text) for tag in data.processors.find_all("limit")]

    # Число процессоров
    proc_num = len(proc_limits)
    if proc_num == 0:
        print("Недопустимое число процессоров (0 процессоров)", file=sys.stderr)
        sys.exit(1)

    if data.programs == None:
        print("Не найден тег programs", file=sys.stderr)
        sys.exit(1)
    # Список с нагрузками на процессор для каждой программы
    prog_cap = [int(tag.text) for tag in data.programs.find_all("capacity")]

    # Число программ
    prog_num = len(prog_cap)
    if prog_num == 0:
        print("Недопустимое число программ (0 программ)", file=sys.stderr)
        sys.exit(1)

    try:
        # unsorted_links - список программ, которые обмениваются данными в формате:
        # (первая_программа, вторая_программа, нагрузка_на_сеть)
        unsorted_links = [(int(tag.first.text), int(tag.second.text), int(tag.load.text)) for tag in
                          data.networks.find_all("netlink")]
    except:
        print("Неверный формат тега netlink", file=sys.stderr)
        sys.exit(1)

    # links - отсортированный список программ, которые обмениваются данными в формате:
    links = []
    for link in unsorted_links:
        min_prog = min(link[0], link[1])
        max_prog = max(link[0], link[1])
        links.append((min_prog, max_prog, link[2]))
    links.sort(key=lambda a: a[0])
    
    # Обращение к серверу
    ret = server.solve(proc_limits, prog_cap, links)
    # Вывод результатов
    if ret[0] == "success":
        print(ret[0])
        print(ret[1])
        print(*ret[2])
        print(ret[3])
    else:
        print(ret[0])
        print(ret[1])

