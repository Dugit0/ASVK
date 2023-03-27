import multiprocessing as mulproc
from bs4 import BeautifulSoup
import random
import sys

FILE = "../problem1/test_16proc_1.xml"  # Путь до файла с входными данными
MAX_STEPS = 5000  # Максимальное число итераций алгоритма для каждого процесса
PROCESS_NUM = 4  # Число процессов


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


def gen_random_solution(proc_limits, prog_cap):
    # Функция для генерации случайного решения
    # proc_limits - список с предельными нагрузками на процессоры
    # prog_cap - список с нагрузками на процессор для каждой программы

    proc_num = len(proc_limits)
    prog_num = len(prog_cap)
    programs = list(range(prog_num))
    random.shuffle(programs)
    solution = [0] * prog_num
    proc_ind = 0
    prog_ind = 0
    while proc_ind < proc_num:
        cur_lim = 0
        while prog_ind < prog_num:
            cur_lim += prog_cap[programs[prog_ind]]
            if cur_lim > proc_limits[proc_ind]:
                cur_lim -= prog_cap[programs[prog_ind]]
                break
            else:
                solution[programs[prog_ind]] = proc_ind
                prog_ind += 1
        proc_ind += 1
    return solution


def solve_problem(proc_limits, prog_cap, links):
    global FILE, MAX_STEPS
    global mul_best_load, mul_best_solution

    proc_num = len(proc_limits)
    prog_num = len(prog_cap)

    global_count_steps = 0  # Глобальный счетчик итераций
    count_steps = 0  # Счетчик для подсчета итеграций между двумя найденными решениями
    flag_success = False  # Флаг нахождения решения
    with mul_best_load.get_lock():
        best_load = mul_best_load.value
    while True:
        count_steps += 1
        global_count_steps += 1
        # Генерируем решение
        # Вариант 1: абсолютно случайная генерация процессора для каждой программы
        # new_solution = [random.randint(0, proc_num - 1) for i in range(prog_num)]
        # Вариант 2: случайная генерация программ для процессора с учетом предела нагрузки процессора
        new_solution = gen_random_solution(proc_limits, prog_cap)
        # Считаем нагрузку
        new_load = find_load(new_solution, links)
        # Проверяем что найденное решение лучше известного
        # Блокировка для синхронизации и сравнение текущего решения с лучшим
        with mul_best_load.get_lock(), mul_best_solution.get_lock():
            flag_best_choice = new_load < mul_best_load.value
        # Проверка корректности
        if flag_best_choice and cheсk(new_solution, proc_limits, prog_cap):
            flag_success = True
            with mul_best_load.get_lock(), mul_best_solution.get_lock():
                # Проверка на случай, если за время проверки на корректность решение было улучшено
                if new_load < mul_best_load.value:
                    mul_best_load.value = new_load
                    for i in range(prog_num):
                        mul_best_solution[i] = new_solution[i]
            count_steps = 0
        # Условие выхода
        if mul_best_load.value == 0 or count_steps >= MAX_STEPS:
            break
    # Запись результата
    with mul_flag_success.get_lock(), mul_global_count_steps.get_lock():
        mul_flag_success.value = int(bool(mul_flag_success.value) or flag_success)
        mul_global_count_steps.value += global_count_steps


if __name__ == "__main__":

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
    mul_best_load = mulproc.Value('i', sum(map(lambda a: a[2], links)) + 1)
    # Инициализация общих для всех процессов переменных
    mul_best_solution = mulproc.Array('i', [-1] * prog_num)  # Лучшее решение
    mul_flag_success = mulproc.Value('i', 0)  # Флаг нахождения решения
    mul_global_count_steps = mulproc.Value('i', 0)  # Глобальный счетчик итераций

    all_process = []
    # Создание и запуск потоков
    for i in range(PROCESS_NUM):
        new_proc = mulproc.Process(target=solve_problem, args=(proc_limits, prog_cap, links))
        all_process.append(new_proc)
        new_proc.start()
    # Ожидание потоков
    for i in range(PROCESS_NUM):
        all_process[i].join()
    # Вывод результатов
    if mul_flag_success.value:
        print("success")
        print(mul_global_count_steps.value)
        print(list(mul_best_solution.get_obj()))
        print(mul_best_load.value)
    else:
        print("failure")
        print(mul_global_count_steps.value)
