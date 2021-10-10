
if __name__ == "__main__":
    if 0:
        from win10toast import ToastNotifier

        toaster = ToastNotifier()
        # toaster.show_toast("Sample Notification", "Testing toast tester toast toast")


    if 0:
        from pygame import mixer # Load the required library

        mixer.init()
        mixer.music.load("alarm.mp3")
        mixer.music.play()


    if 0:
        from playsound import playsound

        playsound("alarm.mp3")


    from bartlib.notification import Notifier

    notifier = Notifier()
    notifier.notify("test", "test")
