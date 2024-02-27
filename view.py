import pickle
import evaluator

# Adjust the path to where your file is located
filename = 'results/gpt-3.5-turbo-run0.p'

# Load and print the contents of the pickle file
with open(filename, 'rb') as file:
    data = pickle.load(file)

print(data)
