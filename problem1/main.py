from bs4 import BeautifulSoup
import random

# FILE = "input.xml"
FILE = "test_out.xml"
MAX_STEPS = 5000


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


with open(FILE, encoding="utf-8") as f_inp:
    soup = BeautifulSoup(f_inp.read(), "lxml")

data = soup.data
# proc_num = int(data.processors_num.text)
proc_limits = [int(tag.text) for tag in data.processors.find_all("limit")]
proc_num = len(proc_limits)
# prog_num = int(data.programs_num.text)
prog_cap = [int(tag.text) for tag in data.programs.find_all("capacity")]
prog_num = len(prog_cap)
links = [(int(tag.first.text), int(tag.second.text), int(tag.load.text)) for tag in data.networks.find_all("netlink")]
# links.sort()

print("proc_limits :", proc_limits)
print("prog_cap :", prog_cap)
# print("links :", links)

best_load = sum(map(lambda a: a[2], links))
best_solution = [-1] * prog_num
# print(f"best_load = {best_load}")

global_count_steps = 0
count_steps = 0
flag_success = False
while True:
    count_steps += 1
    global_count_steps += 1
    new_solution = [random.randint(0, proc_num - 1) for i in range(prog_num)]
    new_load = find_load(new_solution, links)
    if new_load < best_load and cheсk(new_solution, proc_limits, prog_cap):
        flag_success = True
        best_load = new_load
        best_solution = new_solution.copy()
        count_steps = 0
    if best_load == 0 or count_steps >= MAX_STEPS:
        break

# print("cont_steps =", count_steps)

if flag_success:
    print("success")
    print(global_count_steps)
    print(*best_solution)
    print(best_load)
else:
    print("failure")
    print(global_count_steps)
