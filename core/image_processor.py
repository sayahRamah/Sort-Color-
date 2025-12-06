import cv2
import numpy as np
from PIL import Image
import colorsys
from config import COLOR_CLUSTERS, COLOR_PALETTE

class ImageProcessor:
    """معالجة الصور لاستخراج حالة اللغز"""
    
    def __init__(self):
        self.colors_detected = []
    
    def process_image(self, image_path):
        """معالجة الصورة لاستخراج الزجاجات والألوان"""
        # تحميل الصورة
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("تعذر تحميل الصورة")
        
        # تحويل إلى HSV لتحليل الألوان بشكل أفضل
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # كشف الزجاجات (التقريب المبسط)
        bottles = self._detect_bottles(img)
        
        # استخراج ألوان كل زجاجة
        puzzle_state = []
        for bottle_rect in bottles:
            bottle_colors = self._extract_bottle_colors(img, hsv, bottle_rect)
            puzzle_state.append(bottle_colors)
        
        return puzzle_state
    
    def _detect_bottles(self, image):
        """كشف مواقع الزجاجات في الصورة"""
        # هذه نسخة مبسطة - في الإصدار الحقيقي تحتاج خوارزمية أكثر تطوراً
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # البحث عن الدوائر/المستطيلات
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bottles = []
        height, width = image.shape[:2]
        min_area = (width * height) * 0.001  # 0.1% من مساحة الصورة
        max_area = (width * height) * 0.1    # 10% من مساحة الصورة
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(contour)
                bottles.append((x, y, w, h))
        
        # ترتيب الزجاجات من اليسار لليمين، من الأعلى لأسفل
        bottles.sort(key=lambda rect: (rect[1] // (h * 2), rect[0]))
        
        return bottles[:20]  # الحد الأقصى 20 زجاجة
    
    def _extract_bottle_colors(self, img, hsv, bottle_rect):
        """استخراج ألوان زجاجة واحدة"""
        x, y, w, h = bottle_rect
        
        # تقسيم الزجاجة إلى 4 طبقات
        layer_height = h // 4
        bottle_colors = []
        
        for layer in range(4):
            layer_y = y + (layer * layer_height)
            layer_roi = img[layer_y:layer_y + layer_height, x:x + w]
            hsv_roi = hsv[layer_y:layer_y + layer_height, x:x + w]
            
            if layer_roi.size == 0:
                bottle_colors.append('EMPTY')
                continue
            
            # حساب متوسط اللون
            avg_color = np.mean(layer_roi, axis=(0, 1))
            avg_hsv = np.mean(hsv_roi, axis=(0, 1))
            
            # تحويل إلى لون مسمى
            color_name = self._classify_color(avg_color, avg_hsv)
            bottle_colors.append(color_name)
        
        return bottle_colors
    
    def _classify_color(self, bgr_color, hsv_color):
        """تصنيف اللون إلى أقرب لون معروف"""
        r, g, b = bgr_color[2], bgr_color[1], bgr_color[0]
        h, s, v = hsv_color
        
        # تحويل إلى hex
        hex_color = f"#{int(r):02x}{int(g):02x}{int(b):02x}".upper()
        
        # البحث في تجميعات الألوان
        best_match = 'UNKNOWN'
        min_distance = float('inf')
        
        for cluster_name, cluster_colors in COLOR_CLUSTERS.items():
            for cluster_color in cluster_colors:
                # حساب المسافة بين الألوان
                distance = self._color_distance(hex_color, cluster_color)
                if distance < min_distance:
                    min_distance = distance
                    best_match = cluster_name
        
        # إذا كانت المسافة كبيرة جداً، قد تكون فارغة
        if min_distance > 100:
            return 'EMPTY'
        
        return best_match
    
    def _color_distance(self, hex1, hex2):
        """حساب المسافة بين لونين"""
        # تحويل hex إلى RGB
        r1 = int(hex1[1:3], 16)
        g1 = int(hex1[3:5], 16)
        b1 = int(hex1[5:7], 16)
        
        r2 = int(hex2[1:3], 16)
        g2 = int(hex2[3:5], 16)
        b2 = int(hex2[5:7], 16)
        
        # حساب المسافة الإقليدية
        return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    
    def get_color_emoji(self, color_name):
        """الحصول على إيموجي اللون"""
        if color_name in COLOR_PALETTE:
            return COLOR_PALETTE[color_name][0]
        elif color_name == 'EMPTY':
            return '⬜'
        else:
            return '❓'
