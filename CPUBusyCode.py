# Python script to keep the CPU busy with calculations

import math

def continuous_computation():
    i = 0
    while True:
        # Performing some calculations
        math.sqrt(i)
        math.sin(i)
        math.cos(i)
        math.tan(i)
        # Increment i to change the input for calculation
        i += 1
        if i > 10000:  # Reset i to prevent it from becoming too large
            i = 0

if __name__ == "__main__":
    continuous_computation()
