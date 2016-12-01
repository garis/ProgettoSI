"""control center"""
#"./test.py --limit 100 --string asfgsaf"
from multiprocessing import Process
import subprocess
import os
import time
import sys
import random
import operator

TOTAL_POPULATION = 32
NUMBER_THREADS = 16
FEATURES = 4 * 5

SELECTED = 8


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

    file_stats = open("tmp/stats.csv", "a")

    while True:
        command = 'python ' + os.path.realpath(__file__).replace(
            os.path.basename(__file__), ("test.py --limit 3500 --file tmp/GEN_" + str(lastgen).zfill(3) + "_"), )
        proc = []
        for i in range(0, TOTAL_POPULATION):
            real_command = command + str(i).zfill(3) + " >> /dev/null"
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
        lastgen = evolution(lastgen, TOTAL_POPULATION, FEATURES, file_stats)

        file_stats.write("\n")
        file_stats.flush()

    file_stats.close()


def evolution(generation, individualnumber, features, file_stats=None):
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
        vettore = str(data).split(";")
        for j in range(0, len(vettore) - 1):
            table[i][j] = int(vettore[j])
        table[i][features] = int(score)

    table = sorted(table, key=operator.itemgetter(features))

    # write statistics on file (only the score)
    if file_stats is not None:
        file_stats.write(str(generation) + ";")
        for i in range(0, individualnumber):
            file_stats.write(str(table[i][features]) + ";")

    # ora avviene la riproduzione in cui solo i primi SELECTED membri vengono
    # usati per RICOMBINARE nuovi membri
    # preservando il migliore (per quello si parte da uno)
    global SELECTED

    # salvo i migliori 2
    for i in range(0, 2):
        for j in range(0, FEATURES):
            table[TOTAL_POPULATION - i - 1][j] = table[i][j]

    #accoppio i SELECTED con un altro SELECTED mischiando al 50% i dati di ognuno
    for i in range(2, SELECTED+2):
        target = random.randint(0, SELECTED)
        while target != i-2:
            target = random.randint(0, SELECTED)

        for j in range(0, FEATURES):
            if controlrandomTrueFalse() == 1:
                temp = table[i][j]
                table[i][j] = table[target][j]
                table[target][j] = temp

    # nuovi individui random
    for i in range(SELECTED+2, TOTAL_POPULATION - 2):
        data = random_spaceship()
        for j in range(0, FEATURES):
            table[i][j] = data[j]

    # ora avvengono le MUTAZIONI....ma ora non ho voglia.....

    # e' tempo di scrivere i nuovi file da testare per la generazione
    # successiva
    generation = generation + 1
    for i in range(0, individualnumber):
        out_file = open("tmp/GEN_" + str(generation).zfill(3) +
                        "_" + str(i).zfill(3), "w")
        for j in range(0, features):
            out_file.write(str(table[i][j]) + ";")
        out_file.write("\n")
        out_file.close()
    return generation


def scanforgenerationsfiles():
    """search for the last generation"""
    try:
        files = []
        for file in os.listdir(os.path.realpath(__file__).replace(os.path.basename(__file__), ("/tmp"),)):
            files.append(file)
        files.sort()
        lastgen = str(files[len(files) - 2]).split("_")
        return lastgen[1]
    except IndexError:
        return 1


def createfiles():
    """generate 30 random spaceships"""
    for i in range(0, TOTAL_POPULATION):
        out_file = open("tmp/GEN_" + str(0).zfill(3) +
                        "_" + str(i).zfill(3), "w")
        line = random_spaceship()
        for j in range(0, len(line)):
            out_file.write(str(line[j]))
            out_file.write(";")
        out_file.write("\n")
        out_file.close()


def random_spaceship():
    """generate a random spaceship"""
    line = []
    for j in range(0, 5):
        line.append(controlrandomTrueFalse(80))
        line.append(random.randint(0, 512))
        line.append(random.randint(0, 512))
        line.append(random.randint(0, 512))
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
