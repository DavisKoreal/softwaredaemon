import numpy as np
import matplotlib.pyplot as plt

# Generate random data for 5 graphs
x = np.linspace(0, 10, 100)
data = [np.random.rand(100) for _ in range(5)]

# Save data to a file or use directly in GUI
print("Random data generated:", data)