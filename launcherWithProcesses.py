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

#NOTA BENE:
#per mia sanità mentale d'ora in poi:
# navicella/astronave/triangolo azzurro = individuo
# geni = bit che rappresentano i comportamento dell'individuo

#quando c'e' da scegliere un individuo si usa la "roulette selection"
#esempio:   individuo1: punteggio =20
#           individuo2: punteggio =30
#           totale=                50
#estraggo un numero da 1 a 50 e così più un individuo è bravo e più probabilità ha di essere scelto

SURVIVORS = 14                              #quanti individui (estratti a random con la roulette) preservo inalterati
CHILDS = SURVIVORS*3                        #quanti individui (estratti a random con la roulette) sono da creare sfruttando la precedente generazione (combinandone i geni)
MUTATIONS = 72                              #quanti individui (estratti a random con la roulette) vengono afflitti da una mutazione
POPULATION = SURVIVORS + CHILDS + MUTATIONS #quanti individui ci sono in tutto

NUMBER_THREADS = 4                          #quante esecuzioni contemporanee sono ammesse
FEATURES = 2 * 5                            #quanti campi servono per descrivere un individuo
TOTAL_BIT_GENOTYPE = (9*2)*5                #quanti bit servono per descrivere un individuo

MUTATION_PROBABILITY = 3  #%                #% quanto e' probabile che avvenga una mutazione

LIMIT = 10000                               #per quante iterazioni far andare la simulazione

def main():
    """main"""

    #cerco l'ultima generazione in tmp/ cosicche' si possa riprendere una esecuzione interrotta...
    lastgen = int(scanforgenerationsfiles())
    print "Last generation found: #" + str(lastgen)

    #... per evitare problemi permetto la riscrittura dell'ultima generazione...
    lastgen = lastgen - 1

    #...se ho trovato qualcosa.....
    if lastgen > 0:
        #...evolvo usando i dati presi dall'ultima generazione trovata...
        evolution(lastgen, POPULATION, FEATURES, SURVIVORS, CHILDS, MUTATIONS, TOTAL_BIT_GENOTYPE, MUTATION_PROBABILITY)
    else:
        #...genero degli individui da zero in maniera casuale
        createfiles(FEATURES)
        lastgen = 0

    #file di statistiche varie
    file_stats = open("tmp/stats.csv", "a")

    while True:
        #creo i processi per simulare l'indiviudo...
        path = "tmp/GEN_" + str(lastgen).zfill(3) + "_"
        proc = []
        for i in range(0, POPULATION):
            loc_proc = Process(target=testrun, args=(path + str(i).zfill(3), LIMIT,))
            proc.append(loc_proc)

        #... li avvio andare le simulazioni in gruppi di NUMBER_THREADS...
        cycles = 0
        completed = 0
        while completed < POPULATION:
            for i in range(0, NUMBER_THREADS):
                proc[cycles * NUMBER_THREADS + i].start()
            for i in range(0, NUMBER_THREADS):
                proc[cycles * NUMBER_THREADS + i].join()
                completed = completed + 1
            cycles = cycles + 1

        #... e una volta finite le simulazioni genero la nuova generazione....
        lastgen = evolution(lastgen, POPULATION, FEATURES, SURVIVORS, CHILDS, MUTATIONS, TOTAL_BIT_GENOTYPE, MUTATION_PROBABILITY, file_stats)

        print "GEN #", lastgen

        file_stats.write("\n")
        file_stats.flush()

    file_stats.close()


def evolution(generation, individualnumber, features, survivors, childs, mutations, bits, mutations_prob, file_stats=None):
    """prende i file e genera i dati per la successiva generazione"""
    # carico tutti i file in una tabella e gli ordino per numero di collisioni crescente....

    filename = os.path.realpath(__file__).replace(
        os.path.basename(__file__), ("tmp/GEN_" + str(generation).zfill(3) + "_"))
    #STRUTTURA table:
    # [genotype, score, score_sum]
    # score_sum serve per la roulette di selezione
    table = [[0 for i in range(3)]for j in range(individualnumber)]
    for i in range(0, individualnumber):
        in_file = open(filename + str(i).zfill(3), "r")
        data = in_file.readline()
        score = in_file.readline()
        vettore = str(data).split(";")
        table[i][0] = ""
        for j in range(0, len(vettore) - 1):
            table[i][0] = str(table[i][0]) + str("{0:09b}".format(int(vettore[j])))  # 511 max
        try:
            table[i][1] = float(score)
        except ValueError:
            table[i][1] = 0

    #for i in range(0, individualnumber):
    #    print i,"  ",table[i][0]

    # ordino dal peggiore al migliore (increasing values)
    table = sorted(table, key=operator.itemgetter(1))

    # scrivo le statistiche sul file stats.csv (solo il punteggio di ogni individuo)
    if file_stats is not None:
        file_stats.write(str(generation) + ";")
        for i in range(0, individualnumber):
            file_stats.write(str(table[i][1]) + ";")

    #ora avvengono le cose interessanti.
    #inizio col creare i dati per la roulette di selezione...
    score_sum = 0
    for i in range(0, individualnumber):
        score_sum = score_sum + table[i][1]
        table[i][2] = score_sum
        #print table[i][0], table[i][2]

    #...ora mi occupo degli individui da tramandare intatti nella nuova generazione
    print "SURVIVORS"
    inserted = []
    newtable = [[0 for i in range(1)]for j in range(individualnumber)]
    for i in range(0, survivors):
        #ne scelgo uno a caso...
        selection = random.randint(0, int(score_sum))
        genotype = individualnumber-1
        #print "SEL", selection
        for j in range(0, individualnumber):
            #...evitando di inserirlo più volte (gli individui non si moltiplicano da soli)
            if table[j][2] >= selection and j not in inserted:
                genotype = j
                break
        #print "GENI", genotype, table[genotype][2]
        inserted.append(genotype)
        #... e inserisco il prescelto nella nuova generazione
        newtable[i][0] = table[genotype][0]

    #for i in range(0, survivors):
    #    print newtable[i][0]
    #print ""

    # ora mi occupo di mischiare tra loro i bit di 2 individui
    print "RECOMBINATION"
    for i in range(survivors, survivors+childs, 2):
        #scelgo due individui distinti...
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
        #...e un punto di mezzo che determina uno spezzamento da usare per mischiare i bit
        midpoint = random.randint(1, bits)
        #print "GENI", genotype1, genotype2
        #ora li mischio creando 2 individui
        #esempio:
        #A = [++++++++++], B =[----------], RANDOM = 6 allora:
        #N1=[++++++----] AND N2 = [------++++]

        newtable[i][0] = (str(table[genotype1][0]))[0:midpoint]+(str(table[genotype2][0]))[midpoint:bits+1]
        newtable[i+1][0] = (str(table[genotype2][0]))[0:midpoint]+(str(table[genotype1][0]))[midpoint:bits+1]

    #for i in range(survivors, survivors+childs):
    #    print newtable[i][0]
    #print ""

    #ora i occupo delle mutazioni
    #non si fa altro che scegliere un individuo e fare il bit flip di un solo bit in base ad una certa probabilità...
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

    #... e ora tempo di scrivere i nuovi file da testare per la generazione successiva.
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
    """generate #POPULATION random spaceships"""
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
