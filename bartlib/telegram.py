
import json
import logging
import traceback
import os
from queue import Queue, Empty
from telegram import ParseMode
from telegram.ext import Updater, Dispatcher, CommandHandler
from threading import Thread
import time
from datetime import datetime
from matplotlib.figure import Figure
import tempfile


def dump_exception():
    traceback.print_exc()


class TelegramBotThread(Thread):
    # tg
    queue: Queue
    stopping: bool
    # last_sent
    aggregate: bool
    agg_mex: str
    agg_chat_id: str

    def __init__(self, tg):
        super().__init__()
        self.tg = tg
        self.queue = Queue()
        self.stopping = False
        self.last_sent = datetime.now()
        self.aggregate = True  # NOTE: this works ONLY with one single chat_id
        self.agg_mex = None
        self.agg_chat_id = None
    
    def append(self, data):
        self.queue.put(data, timeout=1)
    
    def run(self):
        while not self.stopping:
            do_send = False
            try:
                data = self.queue.get(block=True, timeout=1)
                if data["type"] == "send_message":
                    now = datetime.now()
                    
                    if not self.aggregate:
                        while (now - self.last_sent).total_seconds() < 0.5:
                            time.sleep(0.5)
                            now = datetime.now()
                        self.tg.updater.bot.send_message(**data["params"])
                        self.last_sent = datetime.now()
                    else:
                        # NOTE: this works ONLY if the chat_id are the same!
                        # add to aggregate mex
                        if self.agg_mex is not None:
                            self.agg_mex += "\n" + data["params"]["text"]
                        else:
                            self.agg_mex = data["params"]["text"]
                            self.agg_chat_id = data["params"]["chat_id"]
                        
                        # print("Agg = '{}'".format(self.agg_mex))

                        if (now - self.last_sent).total_seconds() >= 0.7:
                            try:
                                self.tg.updater.bot.send_message(data["params"]["chat_id"], self.agg_mex, data["params"]["parse_mode"])
                            except:
                                dump_exception()

                            self.agg_mex = None
                            self.last_sent = datetime.now()

                        #     print("SENT")
                        # else:
                        #     print("NOT SENT")

                elif data["type"] == "send_photo":
                    now = datetime.now()
                    while (now - self.last_sent).total_seconds() < 0.5:
                        time.sleep(0.5)
                        now = datetime.now()
                    params = data["params"].copy()
                    filename = params.pop("filename")
                    delete_afterwards = params.pop("delete_afterwards")
                    print(f"Sending {filename}...")
                    self.tg.updater.bot.send_photo(photo=open(filename, "rb"),
                                                   **params)
                    if delete_afterwards:
                        os.unlink(filename)
                    self.last_sent = datetime.now()

            except (TimeoutError, Empty) as exc:
                do_send = True

            except Exception:
                dump_exception()

            # even if we have nothing in the queue, check if we have some
            # aggregated message to send
            if do_send and self.agg_mex is not None:
                now = datetime.now()
                if (now - self.last_sent).total_seconds() >= 0.7:
                    try:
                        self.tg.updater.bot.send_message(self.agg_chat_id, self.agg_mex, parse_mode=ParseMode.HTML)
                    except:
                        dump_exception()
                    self.agg_mex = None
                    self.last_sent = datetime.now()

                    # print("SENT")

    def stop(self):
        self.stopping = True


class TelegramBot:  # (Thread):
    updater: Updater
    dispatcher: Dispatcher
    group_id: str
    cmd_thread: TelegramBotThread

    def __init__(self, welcome_msg="Hello from <b>IBTest</b>",
                 config_file="../telegram.json"):
        # Thread.__init__(self)
      
        logging.getLogger("telegram").setLevel(logging.INFO)
        logging.getLogger("JobQueue").setLevel(logging.INFO)

        with open(config_file, "r") as fp:
            tg_config = json.load(fp)
        
        self.group_id = tg_config["group_id"]

        self.updater = Updater(token=tg_config["token"], use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.add_command("start", self.start)

        self.cmd_thread = TelegramBotThread(tg=self)
        self.cmd_thread.start()

        if welcome_msg is not None:
            self.send_message(welcome_msg)

        # self.updater.bot.send_message(self.group_id, "Hello from <b>IBTest</b>", parse_mode=ParseMode.HTML)

    def run(self):
        self.updater.start_polling()
    
    def stop(self):
        time.sleep(0.01)  # to give time eventually for the thread to start, if not started already
        self.cmd_thread.stop()
        self.updater.stop()
    
    def join(self):
        self.updater.idle()
    
    def add_command(self, name, func):
        self.dispatcher.add_handler(CommandHandler(name, func))
    
    @staticmethod
    def start(update, context):  # command
        print(f"START chat_id = {update.effective_chat.id}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="This is a start!")

    def send_message(self, text, chat_id=None):
        if chat_id is None:
            chat_id = self.group_id
              
        # def send_message_cb(context):
        #     self.updater.bot.send_message(chat_id, text, parse_mode=ParseMode.HTML)
        # self.updater.job_queue.run_once(send_message_cb, 0)

        data = {
            "type": "send_message",
            "params": {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": ParseMode.HTML
            }
        }
        self.cmd_thread.append(data)

    def send_photo(self, filename: str, caption: str = None,
                   chat_id: str = None, delete_afterwards: bool = False):
        if chat_id is None:
            chat_id = self.group_id

        data = {
            "type": "send_photo",
            "params": {
                "chat_id": chat_id,
                "filename": filename,
                "caption": caption,
                "delete_afterwards": delete_afterwards
            }
        }
        self.cmd_thread.append(data)

    def send_figure(self, fig: Figure, caption: str = None,
                    chat_id: str = None):
        filename = os.path.join(tempfile.gettempdir(),
                                next(tempfile._get_candidate_names()) + ".png")
        fig.savefig(filename)
        self.send_photo(filename, caption, delete_afterwards=True)
