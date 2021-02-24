import threading

def print1():
    for i in range(0,10):
        print(1)

def print2():
    while True:
        print(2)
        
if __name__ == '__main__':
    thread1 = threading.Thread(target=print1)
    thread2 = threading.Thread(target=print2)
    thread1.start()
    thread1.join()
    thread2.start()
    thread2.join()
    