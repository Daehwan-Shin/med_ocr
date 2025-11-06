import cv2
from paddleocr import PaddleOCR
from .preprocess import preprocess_both

class OCREngine:
    def __init__(self):
        self.ocr = PaddleOCR(lang="korean", det=True, rec=True, use_angle_cls=True, show_log=False)

    def ocr_lines(self, bgr):
        variants = preprocess_both(bgr)
        best_lines = []
        for v in variants:
            result = self.ocr.ocr(v, cls=True)
            lines = []
            for page in result:
                for box, (txt, conf) in page:
                    if conf is None: conf = 0
                    if conf < 0.45:
                        continue
                    lines.append(txt)
            if len(lines) > len(best_lines):
                best_lines = lines
        return best_lines
