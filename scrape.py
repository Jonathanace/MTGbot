import threading

def test():
    threading.Timer(10.0, test).start()
    print("test called")

test()