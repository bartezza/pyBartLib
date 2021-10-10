
import argparse
import logging
import schedule
import time
from typing import Optional
from matplotlib.figure import Figure
from dotenv import load_dotenv
from .telegram import TelegramBot
from .utils import init_logging


class ScheduledService:
    telegram: TelegramBot = None
    tg_prefix: str
    name: str
    # args
    _log: logging.Logger

    def __init__(self, name: str, use_telegram: bool = True):
        init_logging()

        self.name = name

        self._log = logging.getLogger(name)

        parser = argparse.ArgumentParser(description=name)
        parser.add_argument("-e", "--env-file", dest="env_file", action="store",
                            default="../my.env", help="Path to env file")
        parser.add_argument("-t", "--test", dest="test", action="store_true", default=False, help="Run test only")
        parser.add_argument("-notg", "--no-telegram", dest="no_telegram", action="store_true", default=False, help="Disable Telegram")
        self.setup_arg_parser(parser)
        self.args = parser.parse_args()
        
        if self.args.env_file is not None:
            load_dotenv(self.args.env_file)

        if use_telegram and not self.args.no_telegram:
            self.telegram = TelegramBot(welcome_msg=None)
            self.tg_prefix = f"[<b>{self.name}</b>] "
        else:
            self.telegram = None

        self.run()

    def setup_arg_parser(self, parser: argparse.ArgumentParser):
        pass

    def setup_schedule(self):
        pass

    def send_message(self, mex: str, tg_mex: Optional[str] = None):
        self._log.info(mex)
        if self.telegram is not None:
            self.telegram.send_message(self.tg_prefix + (tg_mex or mex))

    def send_photo(self, filename: str, caption: str,
                   delete_afterwards: bool = False):
        if self.telegram is not None:
            self.telegram.send_photo(filename=filename, caption=caption,
                                     delete_afterwards=delete_afterwards)

    def send_figure(self, fig: Figure, caption: str):
        if self.telegram is not None:
            self.telegram.send_figure(fig=fig, caption=caption)

    def run(self):
        if self.telegram is not None:
            self.telegram.run()

        if not self.args.test:
            try:
                if self.telegram is not None:
                    self.telegram.send_message(self.tg_prefix + "Started")
                
                self.setup_schedule()

                self._log.debug("Num jobs = {}, next one = {}".format(len(schedule.jobs), schedule.next_run()))

                while 1:
                    schedule.run_pending()
                    time.sleep(1)
            finally:
                if self.telegram is not None:
                    self.telegram.send_message(self.tg_prefix + "Stopped")
                    self.telegram.stop()

        else:  # just a test
            try:
                self.run_test()
            finally:
                if self.telegram is not None:
                    self.telegram.send_message(self.tg_prefix + "Stopped")
                    self.telegram.stop()

    def run_test(self):
        pass
