COLOR_SYSTEM = {
    # 30 لون مختلف
    'R1': {'hex': '#FF0000', 'emoji': '🔴', 'name': 'Red Light'},
    'R2': {'hex': '#CC0000', 'emoji': '🟥', 'name': 'Red Medium'},
    'R3': {'hex': '#990000', 'emoji': '🟤', 'name': 'Red Dark'},
    'R4': {'hex': '#FF6666', 'emoji': '❤️', 'name': 'Red Pink'},
    'R5': {'hex': '#FF3333', 'emoji': '💖', 'name': 'Red Bright'},
    
    'B1': {'hex': '#0000FF', 'emoji': '🔵', 'name': 'Blue Light'},
    'B2': {'hex': '#0000CC', 'emoji': '🟦', 'name': 'Blue Medium'},
    'B3': {'hex': '#000099', 'emoji': '💙', 'name': 'Blue Dark'},
    'B4': {'hex': '#6666FF', 'emoji': '💠', 'name': 'Blue Light2'},
    'B5': {'hex': '#3333FF', 'emoji': '🌀', 'name': 'Blue Bright'},
    
    'G1': {'hex': '#00FF00', 'emoji': '🟢', 'name': 'Green Light'},
    'G2': {'hex': '#00CC00', 'emoji': '💚', 'name': 'Green Medium'},
    'G3': {'hex': '#009900', 'emoji': '🌲', 'name': 'Green Dark'},
    'G4': {'hex': '#66FF66', 'emoji': '🍀', 'name': 'Green Light2'},
    'G5': {'hex': '#33FF33', 'emoji': '🌿', 'name': 'Green Bright'},
    
    'Y1': {'hex': '#FFFF00', 'emoji': '🟡', 'name': 'Yellow Light'},
    'Y2': {'hex': '#CCCC00', 'emoji': '🌟', 'name': 'Yellow Medium'},
    'Y3': {'hex': '#999900', 'emoji': '🌕', 'name': 'Yellow Dark'},
    'Y4': {'hex': '#FFFF66', 'emoji': '⭐', 'name': 'Yellow Light2'},
    'Y5': {'hex': '#FFFF33', 'emoji': '☀️', 'name': 'Yellow Bright'},
    
    'P1': {'hex': '#8800FF', 'emoji': '🟣', 'name': 'Purple Light'},
    'P2': {'hex': '#6600CC', 'emoji': '🍇', 'name': 'Purple Medium'},
    'P3': {'hex': '#440099', 'emoji': '👾', 'name': 'Purple Dark'},
    'P4': {'hex': '#CC66FF', 'emoji': '🦄', 'name': 'Purple Light2'},
    'P5': {'hex': '#9933FF', 'emoji': '🔮', 'name': 'Purple Bright'},
    
    'O1': {'hex': '#FF8800', 'emoji': '🟠', 'name': 'Orange Light'},
    'O2': {'hex': '#FF6600', 'emoji': '🍊', 'name': 'Orange Medium'},
    'O3': {'hex': '#FF4400', 'emoji': '🎃', 'name': 'Orange Dark'},
    'O4': {'hex': '#FFAA00', 'emoji': '🌅', 'name': 'Orange Light2'},
    'O5': {'hex': '#FF7700', 'emoji': '🔥', 'name': 'Orange Bright'},
    
    # ألوان خاصة
    'EMPTY': {'hex': '#E0E0E0', 'emoji': '⬜', 'name': 'Empty'},
    'UNKNOWN': {'hex': '#C0C0C0', 'emoji': '❓', 'name': 'Unknown'}
}

# ألوان سريعة للعرض
QUICK_COLORS = [
    '🔴', '🔵', '🟢', '🟡',
    '🟣', '🟠', '⚫', '⚪',
    '❤️', '💙', '💚', '💛',
    '💜', '🧡', '🖤', '❓'
]

def get_color_emoji(color_id):
    """الحصول على إيموجي اللون"""
    return COLOR_SYSTEM.get(color_id, COLOR_SYSTEM['UNKNOWN'])['emoji']

def get_color_name(color_id, language='ar'):
    """الحصول على اسم اللون"""
    color_data = COLOR_SYSTEM.get(color_id)
    if color_data:
        return color_data['name']
    return 'Unknown'
