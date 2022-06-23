import threading

def hello_world():
    threading.Timer(1.0, hello_world).start() # called every second
    print("Hello, World!")

hello_world()