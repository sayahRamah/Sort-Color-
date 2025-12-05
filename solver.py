# =================================================================
# solver.py (مُحدث: لا تغييرات في المنطق)
# =================================================================
import copy
from collections import deque

MAX_CAPACITY = 4 

def is_solved(state):
    """التحقق من أن كل زجاجة تحتوي على لون واحد أو فارغة."""
    for bottle in state:
        if not bottle: continue
        if len(set(bottle)) > 1: return False
    return True

def get_valid_moves(state):
    """إيجاد جميع حركات الصب الصالحة الممكنة."""
    valid_moves = []
    num_bottles = len(state)
    
    for i in range(num_bottles): # الزجاجة المصدر
        if not state[i]: continue

        source_top_shape = state[i][-1]
        
        units_to_pour = 0
        for shape in reversed(state[i]):
            if shape == source_top_shape: units_to_pour += 1
            else: break
        
        if source_top_shape == 99 and units_to_pour < len(state[i]):
            continue

        for j in range(num_bottles): # الزجاجة الهدف
            if i == j: continue

            target_space = MAX_CAPACITY - len(state[j])
            
            if not state[j] or source_top_shape == state[j][-1]:
                
                if target_space >= units_to_pour:
                    
                    if state[j] and state[j][-1] == 99:
                        continue
                        
                    valid_moves.append((i, j, units_to_pour))
                    
    return valid_moves

def apply_move(state, move):
    """تطبيق الحركة (i, j, units) على الحالة الحالية."""
    i, j, units = move
    new_state = copy.deepcopy(state)
    poured_shapes = new_state[i][-units:]
    new_state[i] = new_state[i][:-units]
    new_state[j].extend(poured_shapes)
    return new_state

def state_to_tuple(state):
    """تحويل الحالة إلى tuple لاستخدامها في مجموعة visited."""
    return tuple(tuple(bottle) for bottle in state)

def solve_puzzle(initial_state):
    """خوارزمية BFS لإيجاد أقصر مسار للحل."""
    
    initial_state_tuple = state_to_tuple(initial_state)
    queue = deque([([(None, initial_state_tuple)], initial_state_tuple)])
    visited = {initial_state_tuple}

    while queue:
        path, current_state_tuple = queue.popleft()
        current_state = [list(bottle) for bottle in current_state_tuple]

        if is_solved(current_state):
            return path[1:] 

        for i, j, units in get_valid_moves(current_state):
            move_info = (i, j)
            next_state = apply_move(current_state, (i, j, units))
            next_state_tuple = state_to_tuple(next_state)

            if next_state_tuple not in visited:
                visited.add(next_state_tuple)
                new_path = path + [(move_info, next_state_tuple)]
                queue.append((new_path, next_state_tuple))
    
    return None
