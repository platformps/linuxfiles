import time

def main():
    while True:
        # Perform some CPU-intensive task
        for _ in range(1000000):
            pass

        # Simulate memory usage
        some_list = [0] * 1000000

        # Sleep for a while to control loop speed
        time.sleep(1)

if __name__ == "__main__":
    main()