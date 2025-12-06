class PuzzleState:
    """تمثيل حالة اللغز"""
    
    def __init__(self, bottles, capacity=4):
        self.bottles = bottles  # قائمة من القوائم
        self.capacity = capacity
        self.num_bottles = len(bottles)
    
    def __str__(self):
        result = []
        for i, bottle in enumerate(self.bottles):
            bottle_str = ' | '.join([color if color else '⬜' for color in bottle])
            result.append(f"الزجاجة {i+1}: [{bottle_str}]")
        return '\n'.join(result)
    
    def copy(self):
        """إنشاء نسخة من الحالة"""
        copied_bottles = [bottle.copy() for bottle in self.bottles]
        return PuzzleState(copied_bottles, self.capacity)
    
    def is_sorted(self):
        """التحقق إذا كانت جميع الزجاجات مفروزة"""
        for bottle in self.bottles:
            if not self._is_bottle_sorted(bottle):
                return False
        return True
    
    def _is_bottle_sorted(self, bottle):
        """التحقق إذا كانت زجاجة مفروزة"""
        # زجاجة فارغة تعتبر مفروزة
        if all(color == 'EMPTY' or color is None for color in bottle):
            return True
        
        # جمع الألوان غير الفارغة
        colors = [color for color in bottle if color and color != 'EMPTY']
        if not colors:
            return True
        
        # جميع الألوان يجب أن تكون متشابهة
        first_color = colors[0]
        return all(color == first_color for color in colors)
    
    def get_top_color(self, bottle_idx):
        """الحصول على اللون العلوي في زجاجة"""
        bottle = self.bottles[bottle_idx]
        for color in bottle:
            if color and color != 'EMPTY':
                return color
        return None
    
    def can_pour(self, from_idx, to_idx):
        """التحقق إذا كان الصب ممكناً"""
        if from_idx == to_idx:
            return False
        
        from_bottle = self.bottles[from_idx]
        to_bottle = self.bottles[to_idx]
        
        # التحقق من الزجاجة المصدر
        source_color = None
        source_count = 0
        for color in from_bottle:
            if color and color != 'EMPTY':
                if source_color is None:
                    source_color = color
                if color == source_color:
                    source_count += 1
                else:
                    break
        
        if source_color is None:  # زجاجة مصدر فارغة
            return False
        
        # التحقق من الزجاجة الهدف
        target_empty_count = sum(1 for color in to_bottle if not color or color == 'EMPTY')
        if target_empty_count == 0:  # زجاجة هدف ممتلئة
            return False
        
        target_top_color = self.get_top_color(to_idx)
        if target_top_color is None:  # زجاجة هدف فارغة
            return True
        
        # يمكن الصب فقط إذا كان نفس اللون
        return target_top_color == source_color
    
    def pour(self, from_idx, to_idx):
        """تنفيذ عملية الصب"""
        if not self.can_pour(from_idx, to_idx):
            return False
        
        from_bottle = self.bottles[from_idx]
        to_bottle = self.bottles[to_idx]
        color = self.get_top_color(from_idx)
        
        # حساب كمية الصب
        pour_amount = 0
        for i in range(len(from_bottle)):
            if from_bottle[i] and from_bottle[i] != 'EMPTY' and from_bottle[i] == color:
                pour_amount += 1
            else:
                break
        
        # حساب السعة المتاحة في الهدف
        available_space = 0
        for i in range(len(to_bottle)):
            if not to_bottle[i] or to_bottle[i] == 'EMPTY':
                available_space += 1
        
        pour_amount = min(pour_amount, available_space)
        
        # تنفيذ الصب
        for _ in range(pour_amount):
            # إزالة من المصدر
            for i in range(len(from_bottle)):
                if from_bottle[i] and from_bottle[i] != 'EMPTY':
                    from_bottle[i] = 'EMPTY'
                    break
            
            # إضافة إلى الهدف
            for i in range(len(to_bottle)-1, -1, -1):
                if not to_bottle[i] or to_bottle[i] == 'EMPTY':
                    to_bottle[i] = color
                    break
        
        return True
    
    def to_tuple(self):
        """تحويل الحالة إلى tuple للتخزين في set"""
        return tuple(tuple(bottle) for bottle in self.bottles)
