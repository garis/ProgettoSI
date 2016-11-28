"""control center"""
#"./test.py --limit 100 --string asfgsaf"
from multiprocessing import Process
import subprocess
import os
import time
import sys


def main():
    """main"""
    command = 'python ' + os.path.realpath(__file__).replace(
        os.path.basename(__file__), "test.py --limit 2000 --string asfgsaf")
    try:
        proc = []
        for i in range(0, 8):
            loc_proc = Process(target=testrun, args=(command,))
            proc.append(loc_proc)
            proc[i].start()
        for i in range(0, 8):
            proc[i].join()
    except:
        print "Error: unable to start thread"


def testrun(str):
    """launch simulation"""
    print str
    subprocess.call(str, shell=True)


if __name__ == '__main__':
    START_TIME = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - START_TIME))
    sys.exit(0)
