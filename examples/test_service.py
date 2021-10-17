
import traceback
import html
import argparse
import schedule
from dotenv import load_dotenv
from bartlib.scheduled_service import ScheduledService


class TestService(ScheduledService):
    def __init__(self):
        super().__init__(name="TestService")

    def setup_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("-e", "--env-file", dest="env_file", action="store",
                            default="../my.env", help="Path to env file")
    
    def parse_arguments(self):
        if self.args.env_file is not None:
            load_dotenv(self.args.env_file)

    def setup_schedule(self):
        # for idx in range(0, 60, 10):
        #     what = "{:02}".format(idx)
        #     schedule.every().minute.at(what).do(self.run_job)

        self.telegram.add_command("test", self.cmd_test_tg)

        schedule.every().minutes.at(":00").do(self.cmd_periodic)
        schedule.every().minutes.at(":10").do(self.cmd_periodic)
        schedule.every().minutes.at(":20").do(self.cmd_periodic)
        schedule.every().minutes.at(":30").do(self.cmd_periodic)
        schedule.every().minutes.at(":40").do(self.cmd_periodic)
        schedule.every().minutes.at(":50").do(self.cmd_periodic)

    def cmd_test_tg(self, update, context):
        try:
            self.send_message("Test command")
        except:
            mex = traceback.format_exc()
            self.send_message(mex, tg_mex="Exception: {}".format(html.escape(mex)))

    def cmd_periodic(self, is_test=False):
        try:
            if is_test:
                print("Schedule test!")
            else:
                self.send_message("Schedule")
        except:
            mex = traceback.format_exc()
            self.send_message(mex, tg_mex="Exception: {}".format(html.escape(mex)))

    def run_test(self):
        self.cmd_periodic(is_test=True)


if __name__ == "__main__":
    svc = TestService()
