
import os
import argparse
import logging
import schedule
import time
import traceback
import html
from typing import Optional, List
from matplotlib.figure import Figure
from dotenv import load_dotenv
from pprint import pprint
from .telegram import TelegramBot
from .utils import init_logging


class ScheduledService:
    telegram: TelegramBot = None
    tg_prefix: str
    name: str
    # args
    is_test: bool
    _log: logging.Logger
    commands: dict  # {"cmd", "func", "simple"}
    dev_chat_id: str

    def __init__(self, name: str, use_telegram: bool = True):
        init_logging(dont_reinit=True)

        self.dev_chat_id = os.getenv("TG_DEV_CHAT_ID", "270129568")

        self.name = name
        self._log = logging.getLogger(name)
        self.commands = {}

        parser = argparse.ArgumentParser(description=name)
        parser.add_argument("-t", "--test", dest="test", action="store_true", default=False, help="Run test only")
        parser.add_argument("-notg", "--no-telegram", dest="no_telegram", action="store_true", default=False, help="Disable Telegram")
        self.setup_arg_parser(parser)
        self.args = parser.parse_args()

        self.is_test = self.args.test
        
        self.parse_arguments()

        if use_telegram and not self.args.no_telegram:
            self.telegram = TelegramBot(welcome_msg=None)
            self.tg_prefix = f"[<b>{self.name}</b>] "
        else:
            self.telegram = None

        self.setup_commands()

    def tg_help(self):
        cmds = sorted(list(self.commands.keys()))
        cmds = ["/" + cmd for cmd in cmds]
        mex = "Available commands:\n" + "\n".join(cmds)
        self.send_message(mex)

    def tg_testtg(self, update, context):
        pprint(f"update = {update}, context = {context}")
        chat = update["message"]["chat"]
        chat_name = chat["title"]
        chat_id = chat["id"]
        print(f"chat name = {chat_name}, id = {chat_id}")

    def setup_arg_parser(self, parser: argparse.ArgumentParser):
        pass
    
    def parse_arguments(self):
        pass

    def setup_commands(self):
        self.add_command("help", self.tg_help, simple=True)
        self.add_command("testtg", self.tg_testtg, simple=False)

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
            self.send_message(mex, tg_mex="Exception: {}".format(html.escape(mex)), chat_id=self.dev_chat_id)
    
    def add_command(self, cmd: str, func, simple: bool = True):
        if self.telegram is not None:
            self.telegram.add_command(cmd, lambda update, context: self._tg_cmd(update, context, func, simple))
        self._log.debug(f"Registered command '{cmd}'")
        # add to local list
        self.commands[cmd] = {"cmd": cmd, "func": func, "simple": simple}
    
    def exec_command(self, cmd: str):
        cmd_info = self.commands.get(cmd)
        if cmd_info is not None:
            if cmd_info["simple"]:
                return cmd_info["func"]()
            else:
                return cmd_info["func"](update=None, context=None)
        else:
            self._log.error(f"Unknown command '{cmd}'")

    def send_message(self, mex: str, tg_mex: Optional[str] = None, chat_id: Optional[str] = None):
        self._log.info(mex)
        if self.telegram is not None:
            self.telegram.send_message(self.tg_prefix + (tg_mex or mex), chat_id=chat_id)

    def send_photo(self, filename: str, caption: str,
                   delete_afterwards: bool = False):
        self._log.info(f"Sending photo {filename} ({caption})")
        if self.telegram is not None:
            self.telegram.send_photo(filename=filename, caption=caption,
                                     delete_afterwards=delete_afterwards)

    def send_figure(self, fig: Figure, caption: str):
        self._log.info(f"Sending figure ({caption})")
        if self.telegram is not None:
            self.telegram.send_figure(fig=fig, caption=caption)

    def run(self):
        if self.telegram is not None:
            self.telegram.run()

        if not self.args.test:
            try:
                if self.telegram is not None:
                    self.telegram.send_message(self.tg_prefix + "Started", chat_id=self.dev_chat_id)
                
                self.setup_schedule()

                self._log.debug("Num jobs = {}, next one = {}".format(len(schedule.jobs), schedule.next_run()))

                while 1:
                    schedule.run_pending()
                    time.sleep(1)
            finally:
                if self.telegram is not None:
                    self.telegram.send_message(self.tg_prefix + "Stopped", chat_id=self.dev_chat_id)
                    self.telegram.stop()

        else:  # just a test
            try:
                self.run_test()
            finally:
                if self.telegram is not None:
                    self.telegram.send_message(self.tg_prefix + "Stopped", chat_id=self.dev_chat_id)
                    self.telegram.stop()

    def run_test(self):
        pass
