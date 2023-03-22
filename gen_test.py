from bs4 import BeautifulSoup
import random

possible_limits = [50, 70, 90, 100]
possible_cap = [5, 10, 15, 20]
possible_load = [10, 50, 70, 100]


def gen_rand():
    global proc_num, prog_num, links_num
    global proc_limits, prog_cap, links
    global possible_limits, possible_cap, possible_load

    proc_num = 8
    prog_num = proc_num * 8

    cur_sum_lim = 0
    cur_sum_cap = 1
    while cur_sum_lim <= cur_sum_cap:
        proc_limits = [random.choice(possible_limits) for i in range(proc_num)]
        prog_cap = [random.choice(possible_cap) for i in range(prog_num)]
        cur_sum_lim = sum(proc_limits)
        cur_sum_cap = sum(prog_cap)

    matr_links = [[0] * prog_num for i in range(prog_num)]
    for i in range(prog_num):
        while True:
            ind1 = random.randint(0, prog_num - 1)
            ind2 = random.randint(0, prog_num - 1)
            if ind1 != i and ind2 != i and ind1 != ind2:
                break
        load1 = random.choice(possible_load)
        load2 = random.choice(possible_load)
        matr_links[i][ind1] = load1
        matr_links[ind1][i] = load1
        matr_links[i][ind2] = load2
        matr_links[ind2][i] = load2

    links = []

    for i in range(prog_num):
        for j in range(i + 1, prog_num):
            if matr_links[i][j] != 0:
                links.append((i, j, matr_links[i][j]))
    links_num = len(links)

    return proc_limits, prog_cap, links


def check_all_param(real, possible):
    ans = True
    check_list = {i: False for i in possible}
    for i in real:
        check_list[i] = True
    for key in possible:
        ans = ans and check_list[key]
    return ans


def check():
    global proc_num, prog_num, links_num
    global proc_limits, prog_cap, links
    global possible_limits, possible_cap, possible_load

    cond1 = ((prog_num / proc_num) >= 8)
    cond2 = ((sum(prog_cap) / proc_num) >= 50)

    set_links = set()
    for link in links:
        set_links.add((link[0], link[1]))
    assert len(set_links) == len(links)

    cond3 = True
    check_links = [0] * prog_num
    for link in links:
        check_links[link[0]] += 1
        check_links[link[1]] += 1
    for prog in range(prog_num):
        if check_links[prog] < 2:
            cond3 = False

    cond4 = check_all_param(proc_limits, possible_limits)
    cond5 = check_all_param(prog_cap, possible_cap)
    cond6 = check_all_param([link[2] for link in links], possible_load)
    return cond1 and cond2 and cond3 and cond4 and cond5 and cond6


try_count = 0
while True:
    gen_rand()
    try_count += 1
    if check():
        break

print(f"-------- {try_count} tries --------")
print("-------- proc --------")
print(proc_num)
print(proc_limits)
print(f"sum limit = {sum(proc_limits)}")

print("-------- prog --------")
print(len(prog_cap))
print(prog_cap)
print(f"sum cap = {sum(prog_cap)}")

print("-------- links --------")
print(len(links))
for link in links:
    print(link)
