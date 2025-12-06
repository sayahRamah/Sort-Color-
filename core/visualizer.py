from PIL import Image, ImageDraw, ImageFont
import os
from config import COLOR_PALETTE

class PuzzleVisualizer:
    """رسم حالة اللغز كصورة"""
    
    def __init__(self, bottle_width=60, bottle_height=240, margin=20):
        self.bottle_width = bottle_width
        self.bottle_height = bottle_height
        self.margin = margin
        self.layer_height = bottle_height // 4
    
    def create_puzzle_image(self, puzzle_state, title="حالة اللغز"):
        """إنشاء صورة للغز"""
        num_bottles = len(puzzle_state)
        
        # حساب أبعاد الصورة
        cols = min(num_bottles, 5)  # 5 زجاجات في كل صف
        rows = (num_bottles + cols - 1) // cols
        
        img_width = cols * (self.bottle_width + self.margin) + self.margin
        img_height = rows * (self.bottle_height + self.margin) + self.margin + 50
        
        # إنشاء الصورة
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)
        
        # إضافة العنوان
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((img_width//2, 20), title, fill='black', font=font, anchor='mm')
        
        # رسم الزجاجات
        for i, bottle in enumerate(puzzle_state):
            row = i // cols
            col = i % cols
            
            x = col * (self.bottle_width + self.margin) + self.margin
            y = row * (self.bottle_height + self.margin) + 50 + self.margin
            
            # رسم الزجاجة
            self._draw_bottle(draw, x, y, bottle, i+1)
        
        return img
    
    def _draw_bottle(self, draw, x, y, bottle, bottle_num):
        """رسم زجاجة واحدة"""
        # رسم الإطار
        draw.rectangle(
            [x, y, x + self.bottle_width, y + self.bottle_height],
            outline='black',
            width=2
        )
        
        # رسم الطبقات
        for layer in range(4):
            layer_y = y + (3 - layer) * self.layer_height
            
            if layer < len(bottle):
                color_name = bottle[layer]
                if color_name and color_name != 'EMPTY':
                    # الحصول على لون RGB
                    if color_name in COLOR_PALETTE:
                        hex_color = COLOR_PALETTE[color_name][1]
                        emoji = COLOR_PALETTE[color_name][0]
                    else:
                        hex_color = '#808080'
                        emoji = '❓'
                    
                    # تحويل hex إلى RGB
                    hex_color = hex_color.lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    
                    # رسم الطبقة الملونة
                    draw.rectangle(
                        [x + 2, layer_y + 2, x + self.bottle_width - 2, layer_y + self.layer_height - 2],
                        fill=rgb,
                        outline='black',
                        width=1
                    )
                    
                    # إضافة الإيموجي إذا كان هناك مساحة كافية
                    if self.bottle_width > 40:
                        try:
                            font = ImageFont.truetype("arial.ttf", 20)
                            draw.text(
                                (x + self.bottle_width//2, layer_y + self.layer_height//2),
                                emoji,
                                fill='white' if sum(rgb) < 384 else 'black',
                                font=font,
                                anchor='mm'
                            )
                        except:
                            pass
                else:
                    # رسم طبقة فارغة
                    draw.rectangle(
                        [x + 2, layer_y + 2, x + self.bottle_width - 2, layer_y + self.layer_height - 2],
                        fill='white',
                        outline='#CCCCCC',
                        width=1
                    )
        
        # إضافة رقم الزجاجة
        draw.text(
            (x + self.bottle_width//2, y + self.bottle_height + 5),
            f"#{bottle_num}",
            fill='black',
            anchor='mt'
        )
    
    def create_solution_step_image(self, step_info, puzzle_state):
        """إنشاء صورة لخطوة في الحل"""
        img = self.create_puzzle_image(puzzle_state.bottles, f"الخطوة {step_info['step']}")
        draw = ImageDraw.Draw(img)
        
        # إضافة وصف الخطوة
        description = f"صب {step_info['color']} من #{step_info['from']+1} إلى #{step_info['to']+1}"
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        img_width, img_height = img.size
        draw.text(
            (img_width//2, img_height - 20),
            description,
            fill='blue',
            font=font,
            anchor='mm'
        )
        
        return img
