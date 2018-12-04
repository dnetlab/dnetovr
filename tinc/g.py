import os

for i in range(65):
    for j in range(1, 256):
        newname = str(i) + '_' + str(j)
        cmd1 = 'cp 0_1 hosts/' + newname
        os.system(cmd1)
