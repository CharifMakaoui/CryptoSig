#!/usr/local/bin/python
"""Main app module
"""

import time
import sys, getopt
import _thread
import threading

import logs
import conf
import structlog

from conf import Configuration
from exchange import ExchangeInterface
from notification import Notifier
from behaviour import Behaviour


def main(argv):
    """Initializes the application
    """
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))

    # Create new threads
    thread1 = StartWork("config", "4h Configuration start")
    thread1.daemon = True
    thread1.start()

    time.sleep(20)

    thread2 = StartWork("config-1d", "1D Configuration start")
    thread2.daemon = True
    thread2.start()



    while True:
        pass


class StartWork(threading.Thread):
    def __init__(self, filename, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.filename = filename

    def run(self):
        print("Starting " + self.threadID)
        run_from_config(self.filename, self.threadID)


def run_from_config(config_ff, threadID):
    # Load settings and create the config object
    config = Configuration(config_ff)
    settings = config.settings

    # Set up logger
    logs.configure_logging(settings['log_level'], settings['log_mode'])
    logger = structlog.get_logger()

    logger.info(" %s", threadID)

    # Configure and run configured behaviour.
    exchange_interface = ExchangeInterface(config.exchanges)
    notifier = Notifier(config.notifiers, config)

    behaviour = Behaviour(
        config,
        exchange_interface,
        notifier
    )

    while True:
        if settings['run_on_start']:
            behaviour.run(settings['market_pairs'], settings['output_mode'])
            logger.info("Sleeping for %s seconds", settings['update_interval'])
            time.sleep(settings['update_interval'])
        else:
            logger.info("Run on start not enabled waiting for %s seconds", settings['wait_and_run'])
            time.sleep(settings['wait_and_run'])


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(0)
