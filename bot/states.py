from enum import Enum

class UserState(Enum):
    """حالات المستخدم في المحادثة"""
    START = 0
    WAITING_FOR_IMAGE = 1
    IMAGE_RECEIVED = 2
    CONFIRMING_PUZZLE = 3
    SOLVING = 4
    SHOWING_SOLUTION = 5
    MANUAL_INPUT = 6
    CORRECTING = 7

class UserSession:
    """جلسة مستخدم"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.state = UserState.START
        self.puzzle_state = None
        self.puzzle_image_path = None
        self.processed_state = None
        self.solution = None
        self.current_step = 0
        self.last_message_id = None
    
    def reset(self):
        """إعادة تعيين الجلسة"""
        self.state = UserState.START
        self.puzzle_state = None
        self.puzzle_image_path = None
        self.processed_state = None
        self.solution = None
        self.current_step = 0
    
    def to_dict(self):
        """تحويل الجلسة إلى قاموس للتخزين"""
        return {
            'user_id': self.user_id,
            'state': self.state.value,
            'current_step': self.current_step
        }
    
    @classmethod
    def from_dict(cls, data):
        """إنشاء جلسة من قاموس"""
        session = cls(data['user_id'])
        session.state = UserState(data['state'])
        session.current_step = data.get('current_step', 0)
        return session
