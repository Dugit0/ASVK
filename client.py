import xmlrpc.client
from bs4 import BeautifulSoup
import os

# FILE = "input.xml"
# FILE = "test_out.xml"
tests = "tests"

server = xmlrpc.client.ServerProxy('http://localhost:9000')
for test in os.listdir(tests):
    path_test = os.path.join(tests, test)
    with open(path_test, encoding="utf-8") as f_inp:
        soup = BeautifulSoup(f_inp.read(), "lxml")
    data = soup.data
    proc_limits = [int(tag.text) for tag in data.processors.find_all("limit")]
    prog_cap = [int(tag.text) for tag in data.programs.find_all("capacity")]
    links = [(int(tag.first.text), int(tag.second.text), int(tag.load.text)) for tag in
             data.networks.find_all("netlink")]
    ret = server.solve(proc_limits, prog_cap, links)
    if ret[0] == "success":
        # print(f"{ret[0]}\n{ret[1]}\n{''.join(*ret[2])}\n{ret[3]}")
        print(ret[0])
        print(ret[1])
        print(*ret[2])
        print(ret[3])
    else:
        print(ret[0])
        print(ret[1])

