
import time
from beatrade.utils.telegram import TelegramBot
import schedule


if __name__ == "__main__":
    telegram = TelegramBot()
    telegram.run()

    if 1:
        for i in range(10):
            print("Sending {}".format(i))
            telegram.send_message("Test {}".format(i))
            time.sleep(0.2)

    def job():
        print("Message from job")
        telegram.send_message("Message from job")

    if 1:
        schedule.every().minute.at(":00").do(job)
        schedule.every().minute.at(":30").do(job)
        print("Num jobs: {}".format(len(schedule.jobs)))

    if 1:
        try:
            while True:
                # print("Asd")
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    print("Stopping...")
    telegram.stop()

    print("Stopped")
