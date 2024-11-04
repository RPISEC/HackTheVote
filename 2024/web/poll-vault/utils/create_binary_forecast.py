import struct
import random

# Function to create binary forecast data
def create_binary_forecast(num_candidates, candidates, total_votes, num_states, states):
    binary_data = struct.pack('LLL', num_candidates, num_states, total_votes)
    
    for candidate in candidates:
        candidate_id, name, party, polling_percentage, polling_error_margin = candidate
        name = name.encode('utf-8').ljust(20, b'\x00')  # Pad to 20 bytes
        party = party.encode('utf-8').ljust(20, b'\x00')  # Pad to 20 bytes
        binary_data += struct.pack('I20s20sff', candidate_id, name, party, polling_percentage, polling_error_margin)
    
    for state in states:
        state_id, electoral_votes, population, votes_per_candidate = state
        binary_data += struct.pack('III', state_id, electoral_votes, population)
        for votes in votes_per_candidate:
            binary_data += struct.pack('I', votes)
    
    return binary_data

# Example usage
num_candidates = 2
candidates = [
    (1, "Alice", "Party A", 52.3, 3.5),
    (2, "Bob", "Party B", 47.7, 3.5)
]
total_votes = 5000000
num_states = 2
states = [
    (1, 10, 2000000, [1000000, 900000]),
    (2, 20, 3000000, [2500000, 500000])
]

# Step 1: Create and save binary forecast data
binary_forecast = create_binary_forecast(num_candidates, candidates, total_votes, num_states, states)

with open('app/election_data/latest_forecast.bin', 'wb') as f:
    f.write(binary_forecast)