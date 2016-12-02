"""control center"""
#"./test.py --limit 100 --string asfgsaf"
from multiprocessing import Process
import subprocess
import os
import time
import sys
import random
import operator
import math

SURVIVORS = 3
CHILDS = SURVIVORS*2
MUTATIONS = 7
POPULATION = SURVIVORS + CHILDS + MUTATIONS

NUMBER_THREADS = 8
FEATURES = 3 * 5
TOTAL_BIT_GENOTYPE =(9*3+1)*5

SELECTED = 8


def main():
    """main"""

    global POPULATION, NUMBER_THREADS, FEATURES,SURVIVORS, CHILDS, MUTATIONS,TOTAL_BIT_GENOTYPE

    lastgen = int(scanforgenerationsfiles())
    print "Last generation found: #" + str(lastgen)

    # per evitare problemi permetto la riscrittura dell'ultima generazione
    lastgen = lastgen - 1

    if lastgen > 0:
        evolution(lastgen, POPULATION, FEATURES, SURVIVORS, CHILDS, MUTATIONS,TOTAL_BIT_GENOTYPE)
    else:
        createfiles()
        lastgen = 0

    file_stats = open("tmp/stats.csv", "a")

    while True:
        command = 'python ' + os.path.realpath(__file__).replace(
            os.path.basename(__file__), ("test.py --limit 3500 --file tmp/GEN_" + str(lastgen).zfill(3) + "_"), )
        proc = []
        for i in range(0, POPULATION):
            real_command = command + str(i).zfill(3) + " >> /dev/null"
            loc_proc = Process(target=testrun, args=(real_command,))
            proc.append(loc_proc)
            # proc[i].start()

        cycles = 0
        completed = 0
        while completed < POPULATION:
            for i in range(0, NUMBER_THREADS):
                proc[cycles * NUMBER_THREADS + i].start()
            for i in range(0, NUMBER_THREADS):
                proc[cycles * NUMBER_THREADS + i].join()
                completed = completed + 1
            cycles = cycles + 1
            
        lastgen = evolution(lastgen, POPULATION, FEATURES, SURVIVORS, CHILDS, MUTATIONS,TOTAL_BIT_GENOTYPE, file_stats)

        file_stats.write("\n")
        file_stats.flush()

    file_stats.close()


def evolution(generation, individualnumber, features, survivors, childs, mutations, bits, file_stats=None):
    """prende i file e genera i dati per la successiva generazione"""
    # carico tutti i file in una tabella e gli ordina per numero di collisioni
    # crescente

    filename = os.path.realpath(__file__).replace(
        os.path.basename(__file__), ("tmp/GEN_" + str(generation).zfill(3) + "_"))
    #genotype, score, score_sum
    table = [[0 for i in range(3)]for j in range(individualnumber)]
    for i in range(0, individualnumber):
        in_file = open(filename + str(i).zfill(3), "r")
        print in_file.name
        data = in_file.readline()
        score = in_file.readline()
        vettore = str(data).split(";")
        for j in range(0, len(vettore) - 1):
            if math.fmod(j, 3) == 0:
                table[i][0] = str(table[i][0]) + \
                    str("{0:01b}".format(int(vettore[j])))
            else:
                table[i][0] = str(table[i][0]) + str("{0:09b}".format(int(vettore[j])))  # 511 max
        table[i][1] = float(score)

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

    # SURVIVORS
    print "SURVIVORS"
    newtable = [[0 for i in range(1)]for j in range(individualnumber)]
    for i in range(0, survivors):
        selection = random.randint(0, int(score_sum))
        genotype = 0
         #if nothing is selected genotype = 0 give the right choice
        for j in range(1, individualnumber):
            if table[j-1][2] >= selection and table[j][2] <= selection:
                genotype = j
                break
        #meh.......ammette ripetizioni ma che ci vuoi fa'
        newtable[i][0] = table[genotype][0]
    
    # RECOMBINATION
    print "RECOMBINATION"
    for i in range(survivors, survivors+childs-1, 2):
        genotype1 = 0
        genotype2 = 0
        while genotype1 != genotype2:
            selection = random.randint(0, int(score_sum))
            for j in range(1, individualnumber):
                if table[j-1][2] >= selection and table[j][2] <= selection:
                    genotype1 = j
                    break
            selection = random.randint(0, int(score_sum))
            for j in range(1, individualnumber):
                if table[j-1][2] >= selection and table[j][2] <= selection:
                    genotype2 = j
                    break
        midpoint=random.randint(0, bits-2)
        newtable[i][0] = (str(table[genotype1][0]))[0:midpoint]+(str(table[genotype2][0]))[midpoint:bits-1]
        newtable[i+1][0] = (str(table[genotype2][0]))[0:midpoint]+(str(table[genotype1][0]))[midpoint:bits-1]

    #RANDOM FOR NOW (BUT MUST BE DONE THE MUTATIONS IN HERE)
    print "MUTATIONS"
    for i in range(survivors+childs, survivors+childs+mutations):
        stringa = ""
        for j in range(0, bits):
            stringa = str(stringa)+str(controlrandomTrueFalse())
        newtable[i][0] = stringa

    # e' tempo di scrivere i nuovi file da testare per la generazione
    # successiva
    generation = generation + 1
    for i in range(0, individualnumber):
        counter = 0
        out_file = open("tmp/GEN_" + str(generation).zfill(3) +
                        "_" + str(i).zfill(3), "w")
        stringa = newtable[i][0]
        for j in range(0, features):
            if math.fmod(j, 3) == 0:
                out_file.write(str(int(stringa[counter:counter+1], 2)) + ";")
                counter = counter + 1
            else:
                out_file.write(str(int(stringa[counter:counter+9], 2)) + ";")
                counter = counter + 9

        out_file.write("\n")
        out_file.close()

    return generation

""""
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
"""
"""
    # e' tempo di scrivere i nuovi file da testare per la generazione
    # successiva
    generation = generation + 1
    for i in range(0, individualnumber):
        out_file = open("tmp/GEN_" + str(generation).zfill(3) +
                        "_" + str(i).zfill(3), "w")
        stringa=str(table[i][1])
        for j in range(0, features):
            ifmath.fmod(j, 3)==0:
                out_file.write(str(int(stringa[], 2)). + ";")
        out_file.write("\n")
        out_file.close()
    
    return generation
        """


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
    for i in range(0, POPULATION):
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
        line.append(random.randint(0, 511))
        line.append(random.randint(0, 511))
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
