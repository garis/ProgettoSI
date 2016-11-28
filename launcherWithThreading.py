"""control center"""
#"./test.py --limit 100 --string asfgsaf"
import subprocess
import os
import threading
import time
import sys


def main():
    """main"""
    command = 'python ' + os.path.realpath(__file__).replace(
        os.path.basename(__file__), "test.py --limit 2000 --string asfgsaf")

    try:
        for i in range(0, 8):
            thread = LaunchTest(command)
            thread.start()
    except:
        print "Error: unable to start thread"
    while (int)(threading.activeCount()) > 1:
        time.sleep(1)


class LaunchTest(threading.Thread):
    """thread simulation"""

    def __init__(self, command):
        super(LaunchTest, self).__init__()
        self.command = command

    def run(self):
        """launch simulation"""
        print self.command
        subprocess.call(self.command, shell=True)


if __name__ == '__main__':
    START_TIME = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - START_TIME))
    sys.exit(0)
