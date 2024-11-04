#!/usr/bin/env python3
import grp
import os
import pwd
import random
import struct
import sys

def parse_forecast(binary_data):
    '''
    Parse a forecast file
    '''
    def _handle_parse_error(result, error):
        print(f"PARSED DATA {result} prior to error")

    result = {}
    header_format = 'LLL'
    try:
        header_size = struct.calcsize(header_format)

        num_candidates, num_states, total_votes = struct.unpack_from(header_format, binary_data)
        result['num_candidates'] = num_candidates
        result['num_states'] = num_states
        result['total_votes'] = total_votes
        
        offset = header_size
        candidate_format = 'I20s20sff'
        candidate_size = struct.calcsize(candidate_format)
        
        candidates = []
        for _ in range(num_candidates):
            candidate_id, name, party, polling_percentage, polling_error_margin = struct.unpack_from(candidate_format, binary_data, offset)
            name = name.decode('utf-8').strip('\x00')
            party = party.decode('utf-8').strip('\x00')
            candidates.append((candidate_id, name, party, polling_percentage, polling_error_margin))
            offset += candidate_size
        result['candidates'] = candidates
        
        states = []
        state_format = 'III'
        state_size = struct.calcsize(state_format)
        
        for _ in range(num_states):
            state_id, electoral_votes, population = struct.unpack_from(state_format, binary_data, offset)
            offset += state_size
            votes_per_candidate = []
            for _ in range(num_candidates):
                votes = struct.unpack_from('I', binary_data, offset)[0]
                votes_per_candidate.append(votes)
                offset += 4
            states.append((state_id, electoral_votes, population, votes_per_candidate))
        result['states'] = states
        
        return result

    except Exception as e:
        # If we fail to parse our input, log what we have for debugging
        _handle_parse_error(result, e)

def run_forecast_simulation(parsed_data, num_simulations=1000):
    '''
    Run a forecast with the given data up to num_simulations times
    '''
    candidates = parsed_data['candidates']
    states = parsed_data['states']
    
    electoral_college_threshold = 270
    candidate_wins = {candidate[1]: 0 for candidate in candidates}  # Track wins per candidate
    
    for _ in range(num_simulations):
        electoral_votes = {candidate[1]: 0 for candidate in candidates}
        
        for state in states:
            state_id, electoral_votes_state, population, votes_per_candidate = state
            
            candidate_results = []
            for i, candidate in enumerate(candidates):
                candidate_id, name, party, polling_percentage, polling_error_margin = candidate
                adjusted_polling_percentage = random.gauss(polling_percentage, polling_error_margin)
                adjusted_polling_percentage = max(0, min(100, adjusted_polling_percentage))
                
                candidate_results.append((name, adjusted_polling_percentage))
            
            winner = max(candidate_results, key=lambda x: x[1])[0]
            electoral_votes[winner] += electoral_votes_state
        
        winner = max(electoral_votes, key=electoral_votes.get)
        candidate_wins[winner] += 1
    
    forecast_results = {candidate: (wins / num_simulations) * 100 for candidate, wins in candidate_wins.items()}
    likely_winner = max(forecast_results, key=forecast_results.get)
    
    return {
        'candidate_win_probabilities': forecast_results,
        'likely_winner': likely_winner
    }

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    '''
    Security best practice: drop privileges as soon as possible
    '''
    try:
        # Get the uid/gid from the name using the pwd and grp modules
        target_uid = pwd.getpwnam(uid_name).pw_uid
        target_gid = grp.getgrnam(gid_name).gr_gid

        # Set the new group
        os.setgid(target_gid)

        # Remove group privileges
        os.setgroups([])

        # Set the new user
        os.setuid(target_uid)

        # Verify we can no longer escalate back to root
        os.seteuid(target_uid)
    except Exception as e:
        print(f"Failed to drop privileges: {str(e)}")
        sys.exit(1)

def do_forecast():
    from sys import argv
    with open(argv[1], 'rb') as f:
        parsed_forecast = parse_forecast(f.read())

    if parsed_forecast is not None:
        # Run the forecast
        forecast_result = run_forecast_simulation(parsed_forecast, num_simulations=1000)

        # Display forecast results
        print("Forecast Results:")
        print(f"Candidate Win Probabilities: {forecast_result['candidate_win_probabilities']}")
        print(f"Likely Winner: {forecast_result['likely_winner']}")

if __name__ == "__main__":
    drop_privileges()
    do_forecast()