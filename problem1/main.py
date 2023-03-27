from bs4 import BeautifulSoup
import random
import sys

FILE = "input.xml" # Путь до файла с входными данными
MAX_STEPS = 5000   # Максимальное число итераций алгоритма


def find_load(solution, links):
    # Функция для поиска суммарной нагрузки на сеть для решения
    # solution - найденное решение
    # links - список программ, которые обмениваются данными

    ans = 0
    for link in links:
        first_prog = link[0]
        second_prog = link[1]
        if solution[first_prog] != solution[second_prog]:
            ans += link[2]
    return ans


def cheсk(solution, proc_limits, prog_cap):
    # Функция для проверки корректности найденного решения
    # solution - найденное решение
    # proc_limits - список с предельными нагрузками на процессоры
    # prog_cap - список с нагрузками на процессор для каждой программы
    
    proc_num = len(proc_limits)
    prog_num = len(prog_cap)
    cur_proc_limits = [0] * proc_num
    for prog in range(prog_num):
        cur_proc_limits[solution[prog]] += prog_cap[prog]
    for proc in range(proc_num):
        if cur_proc_limits[proc] > proc_limits[proc]:
            return False
    return True


# Открытие и считывание файла
with open(FILE, encoding="utf-8") as f_inp:
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

# Расчет теоретически максимальной нагрузки
best_load = sum(map(lambda a: a[2], links)) + 1
best_solution = [-1] * prog_num

global_count_steps = 0   # Глобальный счетчик итераций
count_steps = 0          # Счетчик для подсчета итеграций между двумя найденными решениями
flag_success = False     # Флаг нахождения решения
while True:
    count_steps += 1
    global_count_steps += 1
    # Генерируем решение
    new_solution = [random.randint(0, proc_num - 1) for i in range(prog_num)]
    # Считаем нагрузку
    new_load = find_load(new_solution, links)
    # Проверяем что найденное решение лучше известного
    if new_load < best_load and cheсk(new_solution, proc_limits, prog_cap):
        flag_success = True
        best_load = new_load
        best_solution = new_solution.copy()
        count_steps = 0
    # Условие выхода из цикла
    if best_load == 0 or count_steps >= MAX_STEPS:
        break

# Вывод результата
if flag_success:
    print("success")
    print(global_count_steps)
    print(*best_solution)
    print(best_load)
else:
    print("failure")
    print(global_count_steps)
