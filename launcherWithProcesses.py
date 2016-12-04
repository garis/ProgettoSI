"""control center"""
#"./test.py --limit 100 --string asfgsaf"
from multiprocessing import Process
import os
import time
import sys
import random
import operator
import math
import test

###BUG###
#tmp/stats.csv da ricontrollare
#SPEED!!!!!

SURVIVORS = 5
CHILDS = SURVIVORS*3
MUTATIONS = 44
POPULATION = SURVIVORS + CHILDS + MUTATIONS

NUMBER_THREADS = 16
FEATURES = 2 * 5
TOTAL_BIT_GENOTYPE = (9*2)*5

MUTATION_PROBABILITY = 2  #%

LIMIT = 5000


def main():
    """main"""

    global POPULATION, NUMBER_THREADS, FEATURES,SURVIVORS, CHILDS
    global MUTATIONS, TOTAL_BIT_GENOTYPE, MUTATION_PROBABILITY

    lastgen = int(scanforgenerationsfiles())
    print "Last generation found: #" + str(lastgen)

    # per evitare problemi permetto la riscrittura dell'ultima generazione
    lastgen = lastgen - 1

    if lastgen > 0:
        evolution(lastgen, POPULATION, FEATURES, SURVIVORS, CHILDS, MUTATIONS, TOTAL_BIT_GENOTYPE, MUTATION_PROBABILITY)
    else:
        createfiles(FEATURES)
        lastgen = 0

    file_stats = open("tmp/stats.csv", "a")

    while True:
        #command = 'python ' + os.path.realpath(__file__).replace(
        #    os.path.basename(__file__), ("test.py --limit 3500 --file tmp/GEN_" + str(lastgen).zfill(3) + "_"), )
        path = "tmp/GEN_" + str(lastgen).zfill(3) + "_"
        proc = []
        for i in range(0, POPULATION):
            loc_proc = Process(target=testrun, args=(path + str(i).zfill(3), LIMIT,))
            proc.append(loc_proc)

        cycles = 0
        completed = 0
        while completed < POPULATION:
            for i in range(0, NUMBER_THREADS):
                proc[cycles * NUMBER_THREADS + i].start()
            for i in range(0, NUMBER_THREADS):
                proc[cycles * NUMBER_THREADS + i].join()
                completed = completed + 1
            cycles = cycles + 1

        lastgen = evolution(lastgen, POPULATION, FEATURES, SURVIVORS, CHILDS, MUTATIONS, TOTAL_BIT_GENOTYPE, MUTATION_PROBABILITY, file_stats)

        print "GEN #", lastgen

        file_stats.write("\n")
        file_stats.flush()

    file_stats.close()


def evolution(generation, individualnumber, features, survivors, childs, mutations, bits, mutations_prob, file_stats=None):
    """prende i file e genera i dati per la successiva generazione"""
    # carico tutti i file in una tabella e gli ordina per numero di collisioni
    # crescente

    filename = os.path.realpath(__file__).replace(
        os.path.basename(__file__), ("tmp/GEN_" + str(generation).zfill(3) + "_"))
    #genotype, score, score_sum
    table = [[0 for i in range(3)]for j in range(individualnumber)]
    for i in range(0, individualnumber):
        in_file = open(filename + str(i).zfill(3), "r")
        data = in_file.readline()
        score = in_file.readline()
        vettore = str(data).split(";")
        table[i][0] = ""
        for j in range(0, len(vettore) - 1):
            table[i][0] = str(table[i][0]) + str("{0:09b}".format(int(vettore[j])))  # 511 max
        table[i][1] = float(score)

    #for i in range(0, individualnumber):
    #    print i,"  ",table[i][0]

    # worst to best (increasing values)
    table = sorted(table, key=operator.itemgetter(1))

    # write statistics on file (only the score)
    if file_stats is not None:
        file_stats.write(str(generation) + ";")
        for i in range(0, individualnumber):
            file_stats.write(str(table[i][1]) + ";")

    # CREATION OF SELECTION ROULETTE
    score_sum = 0
    for i in range(0, individualnumber):
        score_sum = score_sum + table[i][1]
        table[i][2] = score_sum
        #print table[i][0], table[i][2]


    # SURVIVORS
    print "SURVIVORS"
    inserted = []
    newtable = [[0 for i in range(1)]for j in range(individualnumber)]
    for i in range(0, survivors):
        selection = random.randint(0, int(score_sum))
        genotype = individualnumber-1
        #print "SEL", selection
        for j in range(0, individualnumber):
            if table[j][2] >= selection and j not in inserted:
                genotype = j
                break
        #print "GENI", genotype, table[genotype][2]
        inserted.append(genotype)
        newtable[i][0] = table[genotype][0]

    #for i in range(0, survivors):
    #    print newtable[i][0]
    #print ""

    # RECOMBINATION
    print "RECOMBINATION"
    for i in range(survivors, survivors+childs, 2):
        genotype1 = 0
        genotype2 = 0
        while genotype1 == genotype2:
            selection = random.randint(0, int(score_sum))
            for j in range(1, individualnumber):
                if table[j][2] >= selection:
                    genotype1 = j
                    break
            selection = random.randint(0, int(score_sum))
            for j in range(1, individualnumber):
                if table[j][2] >= selection:
                    genotype2 = j
                    break
        midpoint = random.randint(1, bits)
        #print "GENI", genotype1, genotype2
        newtable[i][0] = (str(table[genotype1][0]))[0:midpoint]+(str(table[genotype2][0]))[midpoint:bits+1]
        newtable[i+1][0] = (str(table[genotype2][0]))[0:midpoint]+(str(table[genotype1][0]))[midpoint:bits+1]

    #for i in range(survivors, survivors+childs):
    #    print newtable[i][0]
    #print ""

    #MUTATIONS
    print "MUTATIONS"
    for i in range(survivors+childs, survivors+childs+mutations):
        #seleziona un esemplare a caso
        genotype = 0
        selection = random.randint(0, int(score_sum))
        for j in range(1, individualnumber):
            if table[j][2] >= selection:
                genotype = j
                break

        #lo inserisce nella nuova lista mutado a caso
        stringa = ""
        for j in range(0, bits):
            singlebit = bool(int((str(table[genotype][0]))[j:j+1]))
            if controlrandomTrueFalse(mutations_prob):
                singlebit = not singlebit
            stringa = str(stringa)+str(int(singlebit))
        newtable[i][0] = stringa

    #for i in range(survivors+childs, survivors+childs+mutations):
    #    print newtable[i][0]

    # e' tempo di scrivere i nuovi file da testare per la generazione
    # successiva
    generation = generation + 1
    print "Generation", generation, "is born!"
    for i in range(0, individualnumber):
        out_file = open("tmp/GEN_" + str(generation).zfill(3) +
                        "_" + str(i).zfill(3), "w")
        stringa = newtable[i][0]
        for j in range(0, features):
            out_file.write(str(int(stringa[j*9:j*9+9], 2)) + ";")

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


def createfiles(features):
    """generate 30 random spaceships"""
    for i in range(0, POPULATION):
        out_file = open("tmp/GEN_" + str(0).zfill(3) +
                        "_" + str(i).zfill(3), "w")
        line = random_spaceship(features)
        for j in range(0, len(line)):
            out_file.write(str(line[j]))
            out_file.write(";")
        out_file.write("\n")
        out_file.close()


def random_spaceship(features):
    """generate a random spaceship"""
    line = []
    for j in range(0, features):
        line.append(random.randint(0, 511))
    return line


def controlrandomTrueFalse(percent=50):
    return int(random.randrange(100) < percent)


def testrun(path, limit):
    """launch simulation"""
    test.start(path, limit)
    return None

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
