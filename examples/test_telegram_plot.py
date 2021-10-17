
import traceback
import html
import argparse
from dotenv import load_dotenv
from bartlib.scheduled_service import ScheduledService


class TestServicePlot(ScheduledService):
    def __init__(self):
        super().__init__(name="TestServicePlot")

    def setup_arg_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument("-e", "--env-file", dest="env_file", action="store",
                            default="../my.env", help="Path to env file")
    
    def parse_arguments(self):
        if self.args.env_file is not None:
            load_dotenv(self.args.env_file)

    def setup_schedule(self):
        self.telegram.add_command("plot", self.cmd_plot_tg)

    def cmd_plot_tg(self, update, context):
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            # Data for plotting
            t = np.arange(0.0, 2.0, 0.01)
            s = 1 + np.sin(2 * np.pi * t)

            fig, ax = plt.subplots()
            ax.plot(t, s)

            ax.set(xlabel='time (s)', ylabel='voltage (mV)',
                title='About as simple as it gets, folks')
            ax.grid()

            # filename = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()) + ".png")
            # fig.savefig(filename)
            # self.send_photo(filename, "Caption", delete_afterwards=True)
            
            self.send_figure(fig, "Caption")
        except:
            mex = traceback.format_exc()
            self.send_message(mex, tg_mex="Exception: {}".format(html.escape(mex)))


if __name__ == "__main__":
    svc = TestServicePlot()
