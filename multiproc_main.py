import multiprocessing as mulproc
from bs4 import BeautifulSoup
import random

# FILE = "input.xml"
FILE = "test_out.xml"
MAX_STEPS = 5000
PROCESS_NUM = 4

def find_load(solution, links):
    ans = 0
    for link in links:
        first_prog = link[0]
        second_prog = link[1]
        if solution[first_prog] != solution[second_prog]:
            ans += link[2]
    return ans


def cheсk(solution, proc_limits, prog_cap):
    proc_num = len(proc_limits)
    prog_num = len(prog_cap)
    cur_proc_limits = [0] * proc_num
    for prog in range(prog_num):
        cur_proc_limits[solution[prog]] += prog_cap[prog]
    for proc in range(proc_num):
        if cur_proc_limits[proc] > proc_limits[proc]:
            return False
    return True


def solve_problem(proc_limits, prog_cap, links):
    global FILE, MAX_STEPS
    global mul_best_load, mul_best_solution

    proc_num = len(proc_limits)
    prog_num = len(prog_cap)

    # print("proc_limits :", proc_limits)
    # print("prog_cap :", prog_cap)
    # print("links :", links)

    global_count_steps = 0
    count_steps = 0
    flag_success = False
    with mul_best_load.get_lock():
        best_load = mul_best_load.value
    while True:
        count_steps += 1
        global_count_steps += 1
        new_solution = [random.randint(0, proc_num - 1) for i in range(prog_num)]
        new_load = find_load(new_solution, links)
        with mul_best_load.get_lock(), mul_best_solution.get_lock():
            flag_best_choice = new_load < mul_best_load.value
        if flag_best_choice and cheсk(new_solution, proc_limits, prog_cap):
            flag_success = True
            with mul_best_load.get_lock(), mul_best_solution.get_lock():
                if new_load < mul_best_load.value:
                    mul_best_load.value = new_load
                    # mul_best_solution = mulproc.Array('i', new_solution.copy())
                    for i in range(prog_num):
                        mul_best_solution[i] = new_solution[i]
            count_steps = 0
        if mul_best_load.value == 0 or count_steps >= MAX_STEPS:
            break
    with mul_flag_success.get_lock(), mul_global_count_steps.get_lock():
        # print(global_count_steps)
        mul_flag_success.value = int(bool(mul_flag_success.value) or flag_success)
        mul_global_count_steps.value += global_count_steps

if __name__ == "__main__":

    with open(FILE, encoding="utf-8") as f_inp:
        soup = BeautifulSoup(f_inp.read(), "lxml")
    data = soup.data
    proc_limits = [int(tag.text) for tag in data.processors.find_all("limit")]
    proc_num = len(proc_limits)
    prog_cap = [int(tag.text) for tag in data.programs.find_all("capacity")]
    prog_num = len(prog_cap)
    links = [(int(tag.first.text), int(tag.second.text), int(tag.load.text)) for tag in
             data.networks.find_all("netlink")]

    mul_best_load = mulproc.Value('i', sum(map(lambda a: a[2], links)))
    mul_best_solution = mulproc.Array('i', [-1] * prog_num)
    mul_flag_success = mulproc.Value('i', 0)
    mul_global_count_steps = mulproc.Value('i', 0)

    all_process = []
    for i in range(PROCESS_NUM):
        new_proc = mulproc.Process(target=solve_problem, args=(proc_limits, prog_cap, links))
        all_process.append(new_proc)
        new_proc.start()
    for i in range(PROCESS_NUM):
        all_process[i].join()
    if mul_flag_success.value:
        print("success")
        print(mul_global_count_steps.value)
        print(list(mul_best_solution.get_obj()))
        print(mul_best_load.value)
    else:
        print("failure")
        print(mul_global_count_steps.value)
