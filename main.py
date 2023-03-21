from bs4 import BeautifulSoup

with open("input.xml") as f_inp:
    soup = BeautifulSoup(f_inp.read(), "lxml")

data = soup.data
# proc_num = int(data.processors_num.text)
proc_limits = [int(tag.text) for tag in data.processors.find_all("limit")]
# prog_num = int(data.programs_num.text)
prog_cap = [int(tag.text) for tag in data.programs.find_all("capacity")]
links = [(int(tag.first.text), int(tag.second.text), int(tag.load.text)) for tag in data.networks.find_all("netlink")]


print(proc_limits)
print(prog_cap)
print(links)










