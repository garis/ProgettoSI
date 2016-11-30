"""control center"""
#"./test.py --limit 100 --string asfgsaf"
from multiprocessing import Process
import subprocess
import os
import time
import sys
import random
import operator

TOTAL_POPULATION = 8
NUMBER_THREADS = 8
FEATURES = 4 * 5

SELECTED = int(TOTAL_POPULATION * 0.5)


def main():
    """main"""

    global TOTAL_POPULATION, NUMBER_THREADS, FEATURES

    lastgen = int(scanforgenerationsfiles())
    print "Last generation found: #" + str(lastgen)

    # per evitare problemi permetto la riscrittura dell'ultima generazione
    lastgen = lastgen - 1

    if lastgen > 0:
        evolution(lastgen, TOTAL_POPULATION, FEATURES)
    else:
        createfiles()
        lastgen = 0

    while True:
        command = 'python ' + os.path.realpath(__file__).replace(
            os.path.basename(__file__), ("test.py --limit 2000 --file tmp/GEN_" + str(lastgen).zfill(3) + "_"), )
        proc = []
        for i in range(0, TOTAL_POPULATION):
            real_command = command + str(i).zfill(3)  # + " >> /dev/null"
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

        lastgen = evolution(lastgen, TOTAL_POPULATION, FEATURES)


def evolution(generation, individualnumber, features):
    """prende i file e genera i dati per la successiva generazione"""
    # carico tutti i file in una tabella e gli ordina per numero di collisioni
    # crescente
    filename = os.path.realpath(__file__).replace(
        os.path.basename(__file__), ("tmp/GEN_" + str(generation).zfill(3) + "_"))
    table = [[0 for i in range(features + 1)]for j in range(individualnumber)]
    for i in range(0, individualnumber):
        in_file = open(filename + str(i).zfill(3), "r")
        print in_file.name
        data = in_file.readline()
        score = in_file.readline()
        #lines.append(str(score + "/" + data).replace("\n", ""))
        vettore = str(data).split(";")
        for j in range(0, len(vettore) - 1):
            table[i][j] = int(vettore[j])
        table[i][features] = int(score)

    table = sorted(table, key=operator.itemgetter(features))

    # ora avviene la riproduzione in cui solo i primi SELECTED membri vengono
    # usati per RICOMBINARE nuovi membri
    global SELECTED
    for i in range(0, SELECTED * 10):
        ship1 = random.randint(0, SELECTED)
        ship2 = random.randint(0, SELECTED)
        while ship2 != ship1:
            ship2 = random.randint(0, SELECTED)
        j = random.randint(0, FEATURES)

        temp = table[ship1][j]
        table[ship1][j] = table[ship2][j]
        table[ship2][j] = temp

    # ora avvengono le MUTAZIONI

    # e' tempo di scrivere i nuovi file da testare per la generazione
    # successiva
    generation = generation + 1
    for i in range(0, individualnumber):
        out_file = open("tmp/GEN_" + str(generation).zfill(3) +
                        "_" + str(i).zfill(3), "w")
        for j in range(0, features):
            out_file.write(str(table[i][j]) + ";")
        out_file.write("S\n")
        out_file.close()
    return generation


def scanforgenerationsfiles():
    """search for the last generation"""
    try:
        files = []
        for file in os.listdir(os.path.realpath(__file__).replace(os.path.basename(__file__), ("/tmp"),)):
            files.append(file)
        files.sort()
        lastgen = str(files[len(files) - 1]).split("_")
        return lastgen[1]
    except IndexError:
        return 1


def createfiles():
    """generate 30 random spaceships"""
    for i in range(0, TOTAL_POPULATION):
        out_file = open("tmp/GEN_" + str(0).zfill(3) +
                        "_" + str(i).zfill(3), "w")
        out_file.write(random_spaceship())
        out_file.close()


def random_spaceship():
    """generate a random spaceship"""
    line = ""
    for j in range(0, 5):
        line = line + str(controlrandomTrueFalse(80)) + ";"
        line = line + str(random.randint(0, 255)) + ";"
        line = line + str(random.randint(0, 255)) + ";"
        line = line + str(random.randint(0, 255)) + ";"
    line = line + "S\n"
    return line


def controlrandomTrueFalse(percent=50):
    return int(random.randrange(100) < percent)


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
