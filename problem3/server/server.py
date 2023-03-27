from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random

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


def solve(proc_limits, prog_cap, links):
    global MAX_STEPS

    proc_num = len(proc_limits)
    prog_num = len(prog_cap)

    best_load = sum(map(lambda a: a[2], links))
    best_solution = [-1] * prog_num

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

    if flag_success:
        return "success", global_count_steps, best_solution, best_load
    else:
        return "failure", global_count_steps, [-1] * prog_num, -1


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)


with SimpleXMLRPCServer(('0.0.0.0', 9000),
                        requestHandler=RequestHandler) as server:
    server.register_function(solve)
    server.serve_forever()
