f = open("a.txt", "r")
for line in f.readlines():
    linestr = line.strip()
    linestrlist = tuple(map(int, linestr.split()))
    print(linestrlist)