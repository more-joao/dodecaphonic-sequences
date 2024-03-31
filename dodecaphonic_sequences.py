from primeform_reduction import get_prime_form
from itertools import permutations, combinations
from math import factorial
import time
import numpy as np

print('running...')

def calculate_distance(a, b):
    terms = [a,b]
    distance = (terms[1]-terms[0])
    while distance < 0 or distance > 11:
        if distance > 11:
            distance -= 12
        elif distance < 0:
            distance += 12
    return distance


def break_ties(intervals): # symmetrical sets are also handled!
    counter = 1
    while True:
        distances = [x[1] for x in intervals]
        distances.sort()
        intervals = [x for x in intervals if x[1] == min(distances)]
        if len(intervals) == 1:
            break
        else:
            # print('Tie found. Breaking...')
            # print('Possible intervals: ', intervals)
            counter += 1
            try:
                for interval in intervals:
                    # print(interval)    
                    distance = calculate_distance(interval[0][0], interval[0][len(interval[0])-counter])
                    intervals.remove(interval)
                    intervals.insert(0, (interval[0], distance))
            except: # in the case of unbreakable ties (symmetrical intervals), a list index error will rise; in this instance, any interval is acceptable, thus we can break
                # print(f'Symmetrical intervals: {intervals}')
                break
    return intervals
            

def get_possible_arrangements(set):
    arrangements = []
    for x in set:
        arrangement = [e for e in set if e != x]
        arrangement.sort()
        arrangement.insert(0, x)
        for i in arrangement[1::]:
            if i < arrangement[0]:
                arrangement.remove(i)
                arrangement.insert(len(arrangement), i)
        arrangements.append(arrangement)
    return arrangements


def get_normal_order(pc_set):
    pc_set = list(set(pc_set))
    pc_set.sort()

    for i in range(0, len(pc_set)):
        while pc_set[i] >= 12:
            if pc_set[i]-12 not in pc_set:
                pc_set[i] = pc_set[i]-12
            else:
                pc_set[i] = None
                break

    pc_set = [e for e in pc_set if e != None]
    # reduces pitch classes outside of (0-11) w/o changing the original ascending order.
    
    intervals = [] # follows the form (arrangement, distance)
    for a in get_possible_arrangements(pc_set):
        distance = calculate_distance(a[0], a[len(a)-1])
        intervals.append((a, distance))
    
    intervals = break_ties(intervals)
    # print(f'Normal ordered set: {intervals[0][0]}')
    return intervals[0][0]


def transpose_set(pc_set, tn=0):
    transposed_set = pc_set.copy()
    for x in pc_set:
        transposed_set[pc_set.index(x)] -= tn
        if transposed_set[pc_set.index(x)] < 0:
            transposed_set[pc_set.index(x)] += 12
    # print(f'Tn{calculate_distance(pc_set[0], transposed_set[0])} transposed set: {transposed_set}')
    return transposed_set


def invert_set(pc_set):
    inverted_set = pc_set.copy()
    for x in pc_set:
        inverted_set[pc_set.index(x)] = 12 - inverted_set[pc_set.index(x)]
        if inverted_set[pc_set.index(x)] < 0:
            inverted_set[pc_set.index(x)] += 12
        elif inverted_set[pc_set.index(x)] >= 12:
            inverted_set[pc_set.index(x)] -= 12

    # print(f'Inverted set: {inverted_set}')
    return inverted_set


def get_prime_form(pc_set):
    possible_prime_forms = []

    pc_set = get_normal_order(pc_set)
    if pc_set[0] != 0:
        pc_set = transpose_set(pc_set, pc_set[0])
    possible_prime_forms.append(pc_set)

    pc_set = invert_set(pc_set)
    pc_set = get_normal_order(pc_set)
    pc_set = transpose_set(pc_set, pc_set[0])
    if pc_set not in possible_prime_forms:
        possible_prime_forms.append(pc_set)
    for f in possible_prime_forms:
        distance = calculate_distance(f[0], f[len(f)-1])
        possible_prime_forms.remove(f)
        possible_prime_forms.insert(0, (f, distance))
    # print(f'Possible prime forms and outer interval lengths: {possible_prime_forms}')
    return break_ties(possible_prime_forms)[0][0]


def break_sequence(permutation, chord_len):
    broken_sequence = []
    # print(f'Sequence: {permutation}')
    i = 0
    while len(permutation)%chord_len != 0: # repeats n pitch classes, allowing for an even separation of chords -> mod is the number of exceeding pcs
        permutation.append(permutation[i])
        i += 1
        # print(f'Complemented sequence: {permutation}')

    for i,x in enumerate(range(int(len(permutation)/chord_len)), start=0):
        broken_sequence.append(permutation[i*chord_len:chord_len+(chord_len*i)])
    return list(broken_sequence)


def rotate(sequence): # outputs all the possible rotations for a given sequence
    sequences = []
    this_sequence = sequence.copy()
    sequences.append(this_sequence)

    while True:
        sequence.insert(len(sequence), sequence[0])
        sequence.remove(sequence[0])
        this_sequence = sequence.copy()
        if this_sequence == sequences[0]:
            break
        sequences.append(this_sequence)
    return sequences


def add_chords(pool, sequence, chord_len, initial=True): # recursively builds adequate sequences and tests them once they're lengthy enough (12 notes) 
    # here, the "initial" parameter serves as a bridge for recursion
    generated_sequences = []
    if initial is True:
        sequence_prime_form = get_prime_form(sequence)
        for pp in permutations(pool, chord_len):
            this_prime_form = get_prime_form(list(pp))
            if this_prime_form != sequence_prime_form and len(this_prime_form) == chord_len:
                generated_sequences.append([sequence, list(pp)])
    else:
        generated_sequences = add_chords(pool, sequence, chord_len, True)
        for s in generated_sequences:
            if len(generated_sequences) != 0:
                while len([y for z in generated_sequences[0] for y in z]) <= (12-chord_len):
                    complemented_sequences = []
                    for n,x in enumerate(generated_sequences, start=0):
                        invalid_intervals = []
                        this_pool = pool.copy()
                        prime_forms = [get_prime_form(g) for g in x]

                        for pp in permutations(this_pool, chord_len):
                            this_prime_form = get_prime_form(list(pp))
                            if this_prime_form not in prime_forms and sorted(list(pp)) not in invalid_intervals and x[len(x)-1][chord_len-1] != list(pp)[0]:
                                if len(this_prime_form) == chord_len:
                                    complemented_sequences.append(x+[list(pp)])

                                    if len([y for z in x+[list(pp)] for y in z]) == 12: # tests all rotations for complete sequences
                                        #print(f'testing: {[y for z in x+[list(pp)] for y in z]}')
                                        intervals = []
                                        valid = True
                                        this_seq = rotate([y for z in x+[list(pp)] for y in z])

                                        for l in this_seq[0:int(12/int(12/chord_len))]:
                                            prime_form = []
                                            broken_sequence = (break_sequence(l, chord_len))
                                            for i,b in enumerate(broken_sequence):
                                                broken_sequence[i] = get_prime_form(b)
                                                prime_form.append(broken_sequence[i])
                                                if broken_sequence[i] in intervals or len(broken_sequence[i]) != chord_len:
                                                    valid = False
                                                else:
                                                    intervals.append(broken_sequence[i])
                                            #print(l, broken_sequence, valid)
                                            
                                        if valid == True:
                                            with open('valid_sequences.txt', '+a') as file:
                                                print('found valid sequence')
                                                file.write(f'{this_seq[0]} - scale: {notes}\n')
                            else:
                                if sorted(list(pp)) not in invalid_intervals:
                                    invalid_intervals.append(sorted(list(pp)))

                    if len(complemented_sequences) != 0:
                        generated_sequences = complemented_sequences.copy()
                    else:
                        return []

    return generated_sequences


def get_initial_permutations(note_pool, chord_len): # an initial n-chord is one of the form [0,a,b]
    valid_sequences = []
    for p in permutations(note_pool[1:], chord_len-1):
            this_pool = note_pool.copy()
            this_sequence = list(p)
            this_sequence.insert(0,0)
            valid_sequences.append(this_sequence)
    return valid_sequences


def build_sequence(note_pool, chord_len): # paired with the function immediately above, throws every possible "initial" n-chords to add_chords(); 
    sequences = get_initial_permutations(note_pool, chord_len)
    for x in sequences:
        start = time.time()
        print(f'starting with {x}')
        this_pool = note_pool.copy()
        add_chords(this_pool, x, chord_len, False)
        end = time.time()
        print(f'finished with {x} - time elapsed: {end-start} seconds')
        

def show_representatives(iterable, chord_len): # accessory function that calculates all representatives of all pc set classes for a given scale 
    representatives = []
    for x in permutations(iterable, chord_len):
        this = (sorted(list(x)), get_prime_form(list(x)))
        if this not in representatives:
            representatives.append(this)
    classes = [x[1] for x in representatives]
    unique = []
    for r in sorted(representatives):
        print(r)
    for x in classes:
        if x not in unique:
            unique.append(x)
    unique = sorted(unique)
    print(f'{unique} - {len(unique)} total classes.')
    lengths = []
    for x in unique:
        lengths.append(len([e for e in representatives if e[1] == x]))
    print('number of possible representatives for each class: ', lengths)


def possible_scales(length):
    pool = [0,1,2,3,4,5,6,7,8,9,10,11]
    generated_scales = []
    for x in combinations(pool, length):
        generated_scales.append(x)
    print(len(generated_scales), f'total scales of length {length}')
    return generated_scales


notes = [0,1,3,4,5,7,9] # example scale
chord_block_len = 3 # chord length - in this case, trichords

print(f'scale: {notes}')
build_sequence(notes, chord_block_len)

# show_representatives(notes, 3)
