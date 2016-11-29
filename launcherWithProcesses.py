"""control center"""
#"./test.py --limit 100 --string asfgsaf"
from multiprocessing import Process
import subprocess
import os
import time
import sys
import random

TOTAL_POPULATION = 32
NUMBER_THREADS = 8


def main():
    """main"""
    global TOTAL_POPULATION, NUMBER_THREADS
    createfiles()
    command = 'python ' + os.path.realpath(__file__).replace(
        os.path.basename(__file__), "test.py --limit 200 --file tmp/GEN_1_", )
    # try:
    proc = []
    for i in range(0, TOTAL_POPULATION):
        real_command = command + str(i)
        loc_proc = Process(target=testrun, args=(real_command,))
        proc.append(loc_proc)
        # proc[i].start()

    cycles = 0
    completed = 0
    while completed < TOTAL_POPULATION:
        for i in range(0, NUMBER_THREADS):
            proc[cycles * NUMBER_THREADS + i].start()
        for i in range(0, NUMBER_THREADS):
            proc[cycles * NUMBER_THREADS + i].join()
            completed = completed + 1
        cycles = cycles + 1

    # except:
        # print "Error: unable to start thread"


def createfiles():
    """generate 30 random spaceships"""
    for i in range(0, TOTAL_POPULATION):
        out_file = open("tmp/GEN_1_" + str(i), "w")
        out_file.write(random_spaceship())
        out_file.close()


def random_spaceship():
    """generate a random spaceship"""
    line = ""
    line = line + str(random.randint(0, 1))
    for j in range(0, 5):
        line = line + str(random.randint(0, 1)) + ";"
        line = line + str(random.randint(0, 255)) + ";"
        line = line + str(random.randint(0, 255)) + ";"
        line = line + str(random.randint(0, 255)) + ";"
    line = line + "S\n"
    return line


def testrun(str):
    """launch simulation"""
    print str
    subprocess.call(str, shell=True)


if __name__ == '__main__':
    START_TIME = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - START_TIME))
    sys.exit(0)

"""
Nome Gen_#[numero generazione]_#[numero test]
Struttura file per un test:
Riga 0: Stringa che descrive il comportamento
Riga 1: Risultato (sara' scritto al termine del test)
"""
