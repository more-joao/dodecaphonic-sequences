

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
