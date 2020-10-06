from bitlist import bitlist

def attestation_performance(cursor, slot):
    
    # returns a dict showing the attestation performance of each validator active in this slot
    # as the minimum inclusion distance (or -1 if attestation was missed)
    
    cursor.execute(f"SELECT f_committee FROM t_beacon_committees WHERE f_slot = {slot} ORDER BY f_index")
    result = cursor.fetchall()
    # committee_lookup is a list of committees (themselves lists of validator indices) for this slot
    committee_lookup = [result[committee_index][0] for committee_index in range(len(result))]
    query = f"""SELECT f_committee_index, f_inclusion_slot, f_aggregation_bits, f_beacon_block_root
                FROM t_attestations
                WHERE f_slot = {slot}
                ORDER BY f_inclusion_slot"""
    cursor.execute(query)
    attestations = cursor.fetchall()
    # committee_performance = minimum inclusion distance for each committee/validator this slot (or -1 if missed)
    committee_performance = [[-1] * len(committee_lookup[committee_index])
                             for committee_index in range(len(committee_lookup))]
    for attestation in attestations:
        beacon_root = attestation[3].hex()
        cursor.execute(f"SELECT f_canonical FROM t_blocks WHERE f_root = '\\x{beacon_root}'")
        if not cursor.fetchone():
    	    continue
        committee_index = attestation[0]
        committee_size = len(committee_lookup[committee_index])
        inclusion_slot = attestation[1]
        inclusion_distance = inclusion_slot - slot - 1
        # to get the aggregation bits in correct order, reverse order of the bytes and then reverse whole bitlist
        # also exclude any bits that were added as padding by the .tobytes() method
        aggregation_bits = bitlist(attestation[2].tobytes()[::-1])[:-(committee_size+1):-1]
        
        # record the shortest inclusion_distance for each member
        for committee_position, bit in enumerate(aggregation_bits):
            if bit and (committee_performance[committee_index][committee_position] == -1):
                committee_performance[committee_index][committee_position] = inclusion_distance
    
    # flatten lookup tables
    validators  = [validator for committee in committee_lookup for validator in committee]
    performance = [inclusion_distance for committee in committee_performance for inclusion_distance in committee]
    
    return dict(zip(validators, performance))
    
# function for calculating the distribution of outages - not required as no outages after block 5000
def outage_distribution(participation_rate_history, min_participation=2/3):
    run_length = 0
    distribution = {}
    for participation_rate in participation_rate_history:
        if participation_rate > min_participation and run_length > 0:
            if run_length in distribution:
                distribution[run_length] += 1
            else:
                dsitribution[run_length] = 1
            run_length = 0
        else:
            run_length += 1
            longest_run = run_length if run_length > longest_run else longest_run
    
    return distribution
