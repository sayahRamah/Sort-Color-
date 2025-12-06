from collections import deque
from .puzzle import PuzzleState

class PuzzleSolver:
    """حل اللغز باستخدام خوارزمية BFS"""
    
    def __init__(self, initial_state):
        self.initial_state = initial_state
        self.solution = None
    
    def solve(self):
        """إيجاد أقصر حل باستخدام BFS"""
        if self.initial_state.is_sorted():
            return []
        
        # BFS
        queue = deque()
        visited = set()
        parent = {}
        move = {}
        
        start_tuple = self.initial_state.to_tuple()
        queue.append(self.initial_state)
        visited.add(start_tuple)
        
        while queue:
            current_state = queue.popleft()
            current_tuple = current_state.to_tuple()
            
            # إذا وصلنا للحل
            if current_state.is_sorted():
                # إعادة بناء المسار
                self.solution = self._reconstruct_path(parent, move, current_tuple)
                return self.solution
            
            # توليد الحالات التالية
            for from_idx in range(current_state.num_bottles):
                for to_idx in range(current_state.num_bottles):
                    if current_state.can_pour(from_idx, to_idx):
                        new_state = current_state.copy()
                        new_state.pour(from_idx, to_idx)
                        new_tuple = new_state.to_tuple()
                        
                        if new_tuple not in visited:
                            visited.add(new_tuple)
                            queue.append(new_state)
                            parent[new_tuple] = current_tuple
                            move[new_tuple] = (from_idx, to_idx)
        
        return None  # لا يوجد حل
    
    def _reconstruct_path(self, parent, move, goal_state):
        """إعادة بناء مسار الحل"""
        path = []
        current = goal_state
        
        while current in parent:
            prev = parent[current]
            if current in move:
                path.append(move[current])
            current = prev
        
        path.reverse()
        return path
    
    def get_solution_steps(self):
        """الحصول على خطوات الحل مع الوصف"""
        if not self.solution:
            return []
        
        steps = []
        current_state = self.initial_state.copy()
        
        for step_num, (from_idx, to_idx) in enumerate(self.solution, 1):
            color = current_state.get_top_color(from_idx)
            steps.append({
                'step': step_num,
                'from': from_idx,
                'to': to_idx,
                'color': color,
                'state_before': current_state.copy()
            })
            current_state.pour(from_idx, to_idx)
        
        return steps
