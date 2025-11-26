"""   
def mutation(self, schedule, mutation_rate=0.1):
    
    mutated_schedule = copy.deepcopy(schedule)
        
    for i in range(len(mutated_schedule)):

        if random.random() < mutation_rate:
        
            mutation_type = random.choice(['resource', 'time', 'both'])
            if mutation_type == 'resource' or mutation_type == 'both':
                # changing resources
                mutated_schedule[i][0] = random.randint(1, self.num_resources)
                
            if mutation_type == 'time' or mutation_type == 'both':
                # change start time
                mutated_schedule[i][1] = random.randint(0, 50)
        
    return mutated_schedule
    
    
def influence_evolution(self, schedule, belief_space, mutation_rate=0.1, influence_strength=0.5):
       
    # copy 3ashan man3emelsh taghyir fe original
    influenced_schedule = copy.deepcopy(schedule)
        
    for job_id in range(len(influenced_schedule)):
            
        if random.random() < influence_strength:
                
            #(Normative Knowledge) 
            current_resource, current_time = influenced_schedule[job_id]
            resource_range = belief_space.normative[job_id]['resource_range']  # مثال: (1, 3)
            time_range = belief_space.normative[job_id]['time_range']          # مثال: (5, 20)
            best_resource = belief_space.normative[job_id]['best_resource']    # مثال: 2
            best_time = belief_space.normative[job_id]['best_time']            # مثال: 12
           
     #resources 3dt el range?
        if current_resource < resource_range[0] or current_resource > resource_range[1]:
            #han3ml check lw el resources wehsha 3ashan neshoof el best
                if best_resource:
                    influenced_schedule[job_id][0] = best_resource
                else:
                    influenced_schedule[job_id][0] = random.randint(
                        resource_range[0], 
                        resource_range[1]
                    )
                
                if current_time < time_range[0] or current_time > time_range[1]:
                  
                    if best_time:
                        influenced_schedule[job_id][1] = best_time
                    else:
                        influenced_schedule[job_id][1] = random.randint(
                            int(time_range[0]), 
                            int(time_range[1])
                        )
                
                # (Domain Knowledge) 
                # critical ya3ni fe many jobs depend on it
                if job_id in belief_space.domain_knowledge['critical_jobs']:
                    
                # critical jobs != bottleneck resource  ya3ni msh betrooh lel  resource el zahma                   
                    bottlenecks = belief_space.domain_knowledge['bottleneck_resources']
                    
                    if influenced_schedule[job_id][0] in bottlenecks:
                        available = [r for r in range(1, self.num_resources + 1) 
                                   if r not in bottlenecks]
                        
                    if available:
                        influenced_schedule[job_id][0] = random.choice(available)
                #(Situational Knowledge) 
                
                if belief_space.best_solution and random.random() < 0.3:
                   influenced_schedule[job_id] = copy.deepcopy(
                        belief_space.best_solution[job_id]
                    )
    
    return influenced_schedule
    """

"""from collections import Counter
import random
import copy

def selection(population, fitness_scores):

    idx1 = random.randint(0, len(population) - 1)
    idx2 = random.randint(0, len(population) - 1)
    
    if fitness_scores[idx1] < fitness_scores[idx2]:
        return population[idx1]
    else:
        return population[idx2]


def crossover(parent1_chromosome, parent2_chromosome):
    
    p1 = copy.deepcopy(parent1_chromosome)
    p2 = copy.deepcopy(parent2_chromosome)
    size = len(p1)

    #Pick two random cut-off points
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size

    # 3.Copy the "chunk" from parent 1 directly to the child
    chunk = p1[start:end]
    child[start:end] = chunk
    
    # 4. Count the items in the chunk
    chunk_item_counts = Counter(chunk)
    
    # 5. Get the list of items to add from Parent 2
    p2_items_to_add = []

    for item in p2:

        # Check if this item is "available" in the chunk
        if item in chunk_item_counts and chunk_item_counts[item] > 0:
            chunk_item_counts[item] -= 1

        else:
            p2_items_to_add.append(item)

    # 6. Fill in the 'None' gaps in the child, using the items from parent 2
    child_pointer = 0
    p2_pointer = 0
    
    while p2_pointer < len(p2_items_to_add):

        if child_pointer == start:
            # We've reached the middle chunk, jump to the end
            child_pointer = end
        
        # If this slot is empty, fill it
        if child[child_pointer] is None:
            child[child_pointer] = p2_items_to_add[p2_pointer]
            p2_pointer += 1
            
        child_pointer += 1
        
    return child


def mutation(chromosome, belief_space, mutation_rate=0.1):
    
    new_chromosome = copy.deepcopy(chromosome)
    
    # --- 1. CULTURAL INFLUENCE (30% Chance) ---
    # This replaces your friend's 'influence_evolution' function.
    if random.random() < 0.3: 
        
        # A. SITUATIONAL KNOWLEDGE (Copying the Leader)
        # Logic: "If Job A is before Job B in the Best Schedule, I should do that too."
        best_ever = belief_space['best_schedule_so_far']
        
        if best_ever: # Only if we have a history
            # Pick two random spots in our child
            idx1, idx2 = sorted(random.sample(range(len(new_chromosome)), 2))
            job_a = new_chromosome[idx1]
            job_b = new_chromosome[idx2]
            
            # Check: Where are they in the Best Schedule?
            try:
                pos_a_in_best = best_ever.index(job_a)
                pos_b_in_best = best_ever.index(job_b)
                
                # If the Best Schedule has B before A...
                if pos_b_in_best < pos_a_in_best:
                    # ...but WE have A before B (since idx1 < idx2)...
                    # SWAP THEM to match the leader!
                    new_chromosome[idx1], new_chromosome[idx2] = job_b, job_a
                    return new_chromosome 
            except ValueError:
                pass 

        # B. DOMAIN KNOWLEDGE (Critical Jobs)
        # Logic: "Long/Critical jobs should be done FIRST."
        # (We assume even-numbered jobs are 'critical' for this example)
        idx = random.randint(1, len(new_chromosome) - 1)
        job_id = new_chromosome[idx]
        
        # Your friend's check: "if job_id in belief_space...critical_jobs"
        # For now, let's pretend Job 0 is always critical:
        is_critical = (job_id == 0) 
        
        if is_critical:
            # It's critical! Move it earlier in the priority list (swap left)
            # This translates "Don't put on busy machine" to "Schedule it earlier"
            new_chromosome[idx], new_chromosome[idx-1] = new_chromosome[idx-1], new_chromosome[idx]
            return new_chromosome


    # --- 2. STANDARD MUTATION (10% Chance) ---
    # If we didn't use culture, we check for a normal random mutation.
    elif random.random() < mutation_rate:
        if len(new_chromosome) >= 2:
            idx1, idx2 = random.sample(range(len(new_chromosome)), 2)
            # Simple random swap
            new_chromosome[idx1], new_chromosome[idx2] = new_chromosome[idx2], new_chromosome[idx1]

    return new_chromosome"""





from collections import Counter
import random
import copy


def selection(population, fitness_scores):
    idx1 = random.randint(0, len(population) - 1)
    idx2 = random.randint(0, len(population) - 1)

    if fitness_scores[idx1] < fitness_scores[idx2]:
        return population[idx1]
    else:
        return population[idx2]


def crossover(parent1_chromosome, parent2_chromosome):
    p1 = copy.deepcopy(parent1_chromosome)
    p2 = copy.deepcopy(parent2_chromosome)
    size = len(p1)

    # Pick two random cut-off points
    start, end = sorted(random.sample(range(size), 2))
    child = [None] * size

    # 3. Copy the "chunk" from parent 1 directly to the child
    chunk = p1[start:end]
    child[start:end] = chunk

    # 4. Count the items in the chunk
    chunk_item_counts = Counter(chunk)

    # 5. Get the list of items to add from Parent 2
    p2_items_to_add = []
    for item in p2:
        # Check if this item is "available" in the chunk
        if item in chunk_item_counts and chunk_item_counts[item] > 0:
            chunk_item_counts[item] -= 1
        else:
            p2_items_to_add.append(item)

    # 6. Fill in the 'None' gaps in the child, using the items from parent 2
    child_pointer = 0
    p2_pointer = 0

    while p2_pointer < len(p2_items_to_add):
        if child_pointer == start:
            # We've reached the middle chunk, jump to the end
            child_pointer = end

        # If this slot is empty, fill it
        if child[child_pointer] is None:
            child[child_pointer] = p2_items_to_add[p2_pointer]
            p2_pointer += 1

        child_pointer += 1

    return child

def mutation(chromosome, belief_space, mutation_rate=0.1):
    
    new_chromosome = copy.deepcopy(chromosome)
    
    # --- 1. CULTURAL INFLUENCE (30% Chance) ---
    # This replaces your friend's 'influence_evolution' function.
    if random.random() < 0.3: 
        
        # A. SITUATIONAL KNOWLEDGE (Copying the Leader)
        # Logic: "If Job A is before Job B in the Best Schedule, I should do that too."
        best_ever = belief_space['best_schedule_so_far']
        
        if best_ever: # Only if we have a history
            # Pick two random spots in our child
            idx1, idx2 = sorted(random.sample(range(len(new_chromosome)), 2))
            job_a = new_chromosome[idx1]
            job_b = new_chromosome[idx2]
            
            # Check: Where are they in the Best Schedule?
            try:
                pos_a_in_best = best_ever.index(job_a)
                pos_b_in_best = best_ever.index(job_b)
                
                # If the Best Schedule has B before A...
                if pos_b_in_best < pos_a_in_best:
                    # ...but WE have A before B (since idx1 < idx2)...
                    # SWAP THEM to match the leader!
                    new_chromosome[idx1], new_chromosome[idx2] = job_b, job_a
                    return new_chromosome 
            except ValueError:
                pass 

        # B. DOMAIN KNOWLEDGE (Critical Jobs)
        # Logic: "Long/Critical jobs should be done FIRST."
        # (We assume even-numbered jobs are 'critical' for this example)
        idx = random.randint(1, len(new_chromosome) - 1)
        job_id = new_chromosome[idx]
        
        # CHECK THE BELIEF SPACE!
        # (This is the real influence)
        is_critical = (job_id in belief_space['critical_jobs'])
        
        if is_critical:
            # It IS a big job! Move it earlier.
            new_chromosome[idx], new_chromosome[idx-1] = new_chromosome[idx-1], new_chromosome[idx]
            return new_chromosome


    # --- 2. STANDARD MUTATION (10% Chance) ---
    # If we didn't use culture, we check for a normal random mutation.
    elif random.random() < mutation_rate:
        if len(new_chromosome) >= 2:
            idx1, idx2 = random.sample(range(len(new_chromosome)), 2)
            # Simple random swap
            new_chromosome[idx1], new_chromosome[idx2] = new_chromosome[idx2], new_chromosome[idx1]















'''def mutation(chromosome, belief_space, mutation_rate=0.1):
    new_chromosome = copy.deepcopy(chromosome)

    if random.random() < mutation_rate:
        idx1, idx2 = random.sample(range(len(new_chromosome)), 2)
        new_chromosome[idx1], new_chromosome[idx2] = new_chromosome[idx2], new_chromosome[idx1]

    return new_chromosome


def influence_evolution(chromosome, belief_space, influence_strength=0.5):
    influenced_chromosome = copy.deepcopy(chromosome)

    if not hasattr(belief_space, 'normative') or not belief_space.normative:
        return influenced_chromosome

    if isinstance(influenced_chromosome[0], (int, float)):
        for position in range(len(influenced_chromosome)):
            if random.random() < influence_strength:

                job_id = influenced_chromosome[position]

                if position in belief_space.normative:
                    norm = belief_space.normative[position]

                    if 'lower_bound' in norm and 'upper_bound' in norm:
                        L_j = norm['lower_bound']
                        U_j = norm['upper_bound']

                        r = random.uniform(0, 1)

                        new_job_id = L_j + r * (U_j - L_j)
                        new_job_id = int(round(new_job_id))

                        if new_job_id in influenced_chromosome:
                            current_pos = position
                            new_pos = influenced_chromosome.index(new_job_id)

                            influenced_chromosome[current_pos], influenced_chromosome[new_pos] = \
                                influenced_chromosome[new_pos], influenced_chromosome[current_pos]



    elif isinstance(influenced_chromosome[0], list) and len(influenced_chromosome[0]) == 2:

        for job_id in range(len(influenced_chromosome)):

            if random.random() < influence_strength:

                if job_id in belief_space.normative:
                    norm = belief_space.normative[job_id]

                    current_resource, current_time = influenced_chromosome[job_id]

                    if 'resource_lower' in norm and 'resource_upper' in norm:
                        L_resource = norm['resource_lower']
                        U_resource = norm['resource_upper']

                        #  x_ij = L_j(t) + r * (U_j(t) - L_j(t))
                        r = random.uniform(0, 1)
                        new_resource = L_resource + r * (U_resource - L_resource)
                        new_resource = int(round(new_resource))

                        if hasattr(belief_space, 'num_resources'):
                            new_resource = max(1, min(new_resource, belief_space.num_resources))

                        influenced_chromosome[job_id][0] = new_resource

                    if 'time_lower' in norm and 'time_upper' in norm:
                        L_time = norm['time_lower']
                        U_time = norm['time_upper']

                        r = random.uniform(0, 1)
                        new_time = L_time + r * (U_time - L_time)
                        new_time = int(round(new_time))

                        new_time = max(0, new_time)

                        influenced_chromosome[job_id][1] = new_time

    return influenced_chromosome'''