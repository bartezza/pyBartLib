
import argparse
import logging
import schedule
import time
import traceback
import html
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
        init_logging(dont_reinit=True)

        self.name = name

        self._log = logging.getLogger(name)

        parser = argparse.ArgumentParser(description=name)
        parser.add_argument("-t", "--test", dest="test", action="store_true", default=False, help="Run test only")
        parser.add_argument("-notg", "--no-telegram", dest="no_telegram", action="store_true", default=False, help="Disable Telegram")
        self.setup_arg_parser(parser)
        self.args = parser.parse_args()
        
        self.parse_arguments()

        if use_telegram and not self.args.no_telegram:
            self.telegram = TelegramBot(welcome_msg=None)
            self.tg_prefix = f"[<b>{self.name}</b>] "
        else:
            self.telegram = None

    def setup_arg_parser(self, parser: argparse.ArgumentParser):
        pass
    
    def parse_arguments(self):
        pass

    def setup_schedule(self):
        pass
    
    def _tg_cmd(self, update, context, func, simple: bool):
        try:
            if simple:
                func()
            else:
                func(update=update, context=context)
        except:
            mex = traceback.format_exc()
            self.send_message(mex, tg_mex="Exception: {}".format(html.escape(mex)))
    
    def add_command(self, cmd: str, func, simple: bool = True):
        if self.telegram is not None:
            self.telegram.add_command(cmd, lambda update, context: self._tg_cmd(update, context, func, simple))

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
