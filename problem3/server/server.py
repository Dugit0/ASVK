from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random

MAX_STEPS = 5000


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


def solve(proc_limits, prog_cap, links):
    global MAX_STEPS

    proc_num = len(proc_limits)
    prog_num = len(prog_cap)

    # Расчет теоретически максимальной нагрузки
    best_load = sum(map(lambda a: a[2], links)) + 1
    best_solution = [-1] * prog_num

    global_count_steps = 0  # Глобальный счетчик итераций
    count_steps = 0  # Счетчик для подсчета итеграций между двумя найденными решениями
    flag_success = False  # Флаг нахождения решения
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
        if new_load < best_load and cheсk(new_solution, proc_limits, prog_cap):
            flag_success = True
            best_load = new_load
            best_solution = new_solution.copy()
            count_steps = 0
        # Условие выхода из цикла
        if best_load == 0 or count_steps >= MAX_STEPS:
            break

    if flag_success:
        return "success", global_count_steps, best_solution, best_load
    else:
        return "failure", global_count_steps, [-1] * prog_num, -1


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


# Инициализация сервера
with SimpleXMLRPCServer(('0.0.0.0', 9000),
                        requestHandler=RequestHandler) as server:
    # Открытие доступа к функции solve
    server.register_function(solve)
    # Запуск сервера
    server.serve_forever()
