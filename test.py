import random
import time

def printrand():
    while True:
        print(random.randint(1, 100))
        time.sleep(1)

if __name__ == "__main__":
    printrand()