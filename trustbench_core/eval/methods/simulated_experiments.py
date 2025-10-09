# eval/methods/simulated_experiments.py
import random, time

def jitter_delay(base=0.05, jitter=0.05):
    time.sleep(base + random.random()*jitter)

def malformed_input_cases():
    return ["", "{}", "[not json", "\u0000", "DROP TABLE users;"]
