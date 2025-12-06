import json
import os
from datetime import datetime
import pytz

class Database:
    def __init__(self):
        self.users_file = 'users.json'
        self.sessions_file = 'sessions.json'
        self.load_data()
    
    def load_data(self):
        """تحميل البيانات من الملفات"""
        self.users = self._load_file(self.users_file, {})
        self.sessions = self._load_file(self.sessions_file, {})
    
    def _load_file(self, filename, default):
        """تحميل ملف JSON"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def _save_file(self, filename, data):
        """حفظ بيانات إلى ملف"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
    
    def save_users(self):
        """حفظ بيانات المستخدمين"""
        return self._save_file(self.users_file, self.users)
    
    def save_sessions(self):
        """حفظ الجلسات"""
        return self._save_file(self.sessions_file, self.sessions)
    
    def get_user(self, user_id):
        """الحصول على بيانات مستخدم"""
        return self.users.get(str(user_id))
    
    def save_user(self, user_id, user_data):
        """حفظ بيانات مستخدم"""
        self.users[str(user_id)] = user_data
        self.save_users()
    
    def get_session(self, chat_id):
        """الحصول على جلسة"""
        return self.sessions.get(str(chat_id))
    
    def save_session(self, chat_id, session_data):
        """حفظ جلسة"""
        self.sessions[str(chat_id)] = session_data
        self.save_sessions()
    
    def delete_session(self, chat_id):
        """حذف جلسة"""
        if str(chat_id) in self.sessions:
            del self.sessions[str(chat_id)]
            self.save_sessions()
    
    def track_user_start(self, user_id, username, first_name, language='ar'):
        """تتبع بدء مستخدم جديد"""
        now = datetime.now(pytz.UTC).isoformat()
        user_key = str(user_id)
        
        if user_key not in self.users:
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'first_seen': now,
                'last_seen': now,
                'language': language,
                'start_count': 1,
                'games_played': 0,
                'solutions_found': 0
            }
        else:
            user_data = self.users[user_key]
            user_data['last_seen'] = now
            user_data['start_count'] = user_data.get('start_count', 0) + 1
            user_data['language'] = language
        
        self.save_user(user_id, user_data)
        return user_data
    
    def get_daily_stats(self):
        """الحصول على إحصائيات اليوم"""
        now = datetime.now(pytz.UTC)
        today = now.date()
        
        stats = {
            'total_users': len(self.users),
            'active_today': 0,
            'new_today': 0,
            'languages': {},
            'recent_users': []
        }
        
        for user_id, user in self.users.items():
            last_seen = datetime.fromisoformat(user['last_seen'].replace('Z', '+00:00'))
            if last_seen.date() == today:
                stats['active_today'] += 1
            
            first_seen = datetime.fromisoformat(user['first_seen'].replace('Z', '+00:00'))
            if first_seen.date() == today:
                stats['new_today'] += 1
            
            lang = user.get('language', 'ar')
            stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
        
        # آخر 10 مستخدمين
        sorted_users = sorted(self.users.values(), 
                            key=lambda x: x['last_seen'], 
                            reverse=True)[:10]
        stats['recent_users'] = sorted_users
        
        return stats

# إنشاء كائن قاعدة بيانات عالمي
db = Database()
