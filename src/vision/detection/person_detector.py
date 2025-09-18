#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物检测模块
专门检测人物上半身(5x5cm, 距离50cm+)并用绿色框标记
"""

from maix import nn, image
import math

class PersonDetector:
    """
    真实人物上半身检测器类
    专门用于检测5x5cm人物照片(距离50cm+)
    """
    
    def __init__(self, camera_width=512, camera_height=320):
        """
        初始化人物检测器
        
        Args:
            camera_width: 摄像头宽度(像素)
            camera_height: 摄像头高度(像素)
        """
        print("初始化真实人物上半身检测器...")
        
        # 摄像头参数
        self.camera_width = camera_width
        self.camera_height = camera_height
        
        # 初始化人脸检测器（专门用于真实人物）
        try:
            self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
            self.has_face_detector = True
            print("✓ 人脸检测器初始化成功")
        except Exception as e:
            print(f"× 人脸检测器初始化失败: {e}")
            self.has_face_detector = False
        
        # 物理尺寸和距离参数
        self.photo_size_cm = 5.0           # 照片尺寸 5x5cm
        self.min_distance_cm = 50.0        # 最小距离 50cm
        self.typical_distance_cm = 60.0    # 典型距离 60cm
        
        # 根据物理尺寸计算像素范围
        self._calculate_pixel_ranges()
        
        # 检测参数 - 针对真实人脸优化
        self.face_confidence_threshold = 0.75  # 提高置信度要求
        self.max_detections = 3                # 最多检测3个人物
        
        # 上半身检测参数
        self.torso_ratio_min = 1.2  # 上半身最小长宽比(高/宽)
        self.torso_ratio_max = 2.5  # 上半身最大长宽比
        
        print(f"检测参数: 照片{self.photo_size_cm}x{self.photo_size_cm}cm, 距离>{self.min_distance_cm}cm")
        print(f"像素范围: {self.min_pixel_size}-{self.max_pixel_size}px")
        
    def _calculate_pixel_ranges(self):
        """
        根据物理尺寸和距离计算像素大小范围
        """
        # 假设摄像头视野角度约60度(典型值)
        fov_degree = 60.0
        fov_radian = math.radians(fov_degree)
        
        # 在最小距离(50cm)时的像素大小(最大)
        view_width_at_min_dist = 2 * self.min_distance_cm * math.tan(fov_radian / 2)
        pixels_per_cm_max = self.camera_width / view_width_at_min_dist
        self.max_pixel_size = int(self.photo_size_cm * pixels_per_cm_max)
        
        # 在较远距离(100cm)时的像素大小(最小) 
        max_distance_cm = 100.0
        view_width_at_max_dist = 2 * max_distance_cm * math.tan(fov_radian / 2)
        pixels_per_cm_min = self.camera_width / view_width_at_max_dist
        self.min_pixel_size = int(self.photo_size_cm * pixels_per_cm_min)
        
        # 确保合理的范围
        self.min_pixel_size = max(self.min_pixel_size, 25)  # 最小25像素
        self.max_pixel_size = min(self.max_pixel_size, 150) # 最大150像素
        
    def detect_faces(self, img):
        """
        检测真实人物人脸并扩展为上半身区域
        
        Args:
            img: 输入图像
            
        Returns:
            list: 检测到的上半身区域列表
        """
        if not self.has_face_detector:
            return []
        
        try:
            faces = self.face_detector.detect(img, conf_th=self.face_confidence_threshold)
            
            valid_torsos = []
            for face in faces:
                face_x, face_y, face_w, face_h = face.x, face.y, face.w, face.h
                
                # 检查人脸尺寸是否在合理范围内
                if not self._is_valid_face_size(face_w, face_h):
                    continue
                
                # 从人脸推算上半身区域
                torso_bbox = self._face_to_torso(face_x, face_y, face_w, face_h, img)
                
                if torso_bbox:
                    x, y, w, h = torso_bbox
                    
                    # 验证上半身比例
                    if self._is_valid_torso_ratio(w, h):
                        valid_torsos.append({
                            'type': 'upper_body',
                            'bbox': (x, y, w, h),
                            'confidence': face.score,
                            'face_bbox': (face_x, face_y, face_w, face_h),
                            'landmarks': getattr(face, 'landmarks', None)
                        })
            
            return valid_torsos[:self.max_detections]
            
        except Exception as e:
            print(f"人脸检测错误: {e}")
            return []
    
    def _is_valid_face_size(self, face_w, face_h):
        """
        检查人脸尺寸是否在预期的物理范围内
        
        Args:
            face_w, face_h: 人脸宽度和高度
            
        Returns:
            bool: 是否为有效尺寸
        """
        # 人脸通常占整个5x5cm照片的约1/3到1/2
        expected_face_min = self.min_pixel_size // 3
        expected_face_max = self.max_pixel_size // 2
        
        avg_face_size = (face_w + face_h) / 2
        
        return expected_face_min <= avg_face_size <= expected_face_max
    
    def _face_to_torso(self, face_x, face_y, face_w, face_h, img):
        """
        从人脸区域推算上半身区域
        
        Args:
            face_x, face_y, face_w, face_h: 人脸边界框
            img: 图像对象
            
        Returns:
            tuple: 上半身边界框 (x, y, w, h) 或 None
        """
        # 上半身通常是人脸的2-3倍高，1.5倍宽
        torso_w = int(face_w * 1.5)
        torso_h = int(face_h * 2.5)
        
        # 上半身中心应该在人脸下方
        torso_center_x = face_x + face_w // 2
        torso_center_y = face_y + face_h + torso_h // 3
        
        # 计算上半身左上角
        torso_x = max(0, torso_center_x - torso_w // 2)
        torso_y = max(0, face_y)  # 从人脸顶部开始
        
        # 确保不超出图像边界
        torso_w = min(torso_w, img.width - torso_x)
        torso_h = min(torso_h, img.height - torso_y)
        
        # 验证最终尺寸
        if torso_w < self.min_pixel_size or torso_h < self.min_pixel_size:
            return None
            
        return (torso_x, torso_y, torso_w, torso_h)
    
    def _is_valid_torso_ratio(self, w, h):
        """
        检查上半身长宽比是否合理
        
        Args:
            w, h: 宽度和高度
            
        Returns:
            bool: 比例是否合理
        """
        if w == 0:
            return False
            
        ratio = h / w
        return self.torso_ratio_min <= ratio <= self.torso_ratio_max
    
    def detect_persons(self, image):
        """
        检测图像中的真实人物上半身
        
        Args:
            image: 输入图像
            
        Returns:
            list: 检测到的人物上半身区域列表
        """
        # 只使用人脸检测器来检测真实人物
        detections = self.detect_faces(image)
        
        # 如果检测到多个，按置信度排序并过滤重叠
        if len(detections) > 1:
            detections = self.filter_overlapping_detections(detections)
        
        return detections[:self.max_detections]
    
    def filter_overlapping_detections(self, detections, overlap_threshold=0.5):
        """
        过滤重叠的检测结果
        
        Args:
            detections: 检测结果列表
            overlap_threshold: 重叠阈值
            
        Returns:
            list: 过滤后的检测结果
        """
        if len(detections) <= 1:
            return detections
        
        # 按置信度排序
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        filtered = []
        for detection in detections:
            bbox1 = detection['bbox']
            
            # 检查与已选择的检测是否重叠
            overlapped = False
            for selected in filtered:
                bbox2 = selected['bbox']
                if self.calculate_iou(bbox1, bbox2) > overlap_threshold:
                    overlapped = True
                    break
            
            if not overlapped:
                filtered.append(detection)
        
        return filtered
    
    def calculate_iou(self, bbox1, bbox2):
        """
        计算两个边界框的IoU（交并比）
        
        Args:
            bbox1, bbox2: (x, y, w, h) 格式的边界框
            
        Returns:
            float: IoU值
        """
        x1, y1, w1, h1 = bbox1
        x2, y2, w2, h2 = bbox2
        
        # 计算交集
        x_left = max(x1, x2)
        y_top = max(y1, y2)
        x_right = min(x1 + w1, x2 + w2)
        y_bottom = min(y1 + h1, y2 + h2)
        
        if x_right <= x_left or y_bottom <= y_top:
            return 0.0
        
        intersection = (x_right - x_left) * (y_bottom - y_top)
        union = w1 * h1 + w2 * h2 - intersection
        
        return intersection / union if union > 0 else 0.0
    
    def draw_green_boxes(self, img, detections):
        """
        在检测到的人物上半身周围绘制绿色框
        
        Args:
            img: 输入图像
            detections: 检测结果
            
        Returns:
            image: 标记后的图像
        """
        for i, detection in enumerate(detections):
            x, y, w, h = detection['bbox']
            detection_type = detection['type']
            confidence = detection['confidence']
            
            # 绘制绿色边界框 - 上半身区域
            green_color = image.Color.from_rgb(0, 255, 0)  # 绿色
            try:
                img.draw_rect(x, y, w, h, color=green_color, thickness=2)
            except AttributeError:
                try:
                    img.draw_rectangle(x, y, x+w, y+h, color=green_color, thickness=2)
                except AttributeError:
                    try:
                        img.draw_rect(x, y, x+w, y+h, green_color)
                    except:
                        print(f"绘制上半身框: ({x}, {y}, {w}, {h})")
            
            # 绘制人脸框(如果有)
            if 'face_bbox' in detection:
                fx, fy, fw, fh = detection['face_bbox']
                face_color = image.Color.from_rgb(0, 255, 255)  # 青色
                try:
                    img.draw_rect(fx, fy, fw, fh, color=face_color, thickness=1)
                except:
                    print(f"绘制人脸框: ({fx}, {fy}, {fw}, {fh})")
            
            # 绘制标签
            label = f"人物{i+1}: {confidence:.2f}"
            try:
                img.draw_string(x, max(y-25, 0), label, color=green_color)
            except AttributeError:
                try:
                    img.draw_text(x, max(y-25, 0), label, color=green_color)
                except AttributeError:
                    print(f"检测标签: {label} at ({x}, {y})")
            
            # 绘制尺寸信息
            size_label = f"{w}x{h}px"
            try:
                img.draw_string(x, max(y-10, 0), size_label, color=green_color)
            except:
                print(f"尺寸标签: {size_label}")
            
            # 绘制人脸关键点(如果有)
            if detection.get('landmarks'):
                landmarks = detection['landmarks']
                for point in landmarks:
                    try:
                        img.draw_circle(point[0], point[1], 2, color=green_color, thickness=-1)
                    except:
                        print(f"人脸关键点: ({point[0]}, {point[1]})")
        
        return img
    
    def get_detection_info(self, detections):
        """
        获取检测信息摘要
        
        Args:
            detections: 检测结果列表
            
        Returns:
            dict: 检测信息摘要
        """
        if not detections:
            return {
                'count': 0,
                'types': [],
                'confidence_avg': 0.0,
                'upper_body_bboxes': [],
                'face_bboxes': []
            }
        
        types = [det['type'] for det in detections]
        confidences = [det['confidence'] for det in detections]
        upper_body_bboxes = [det['bbox'] for det in detections]
        face_bboxes = [det.get('face_bbox', None) for det in detections]
        
        return {
            'count': len(detections),
            'types': types,
            'confidence_avg': sum(confidences) / len(confidences),
            'upper_body_bboxes': upper_body_bboxes,
            'face_bboxes': [bbox for bbox in face_bboxes if bbox is not None],
            'pixel_size_range': f"{self.min_pixel_size}-{self.max_pixel_size}px",
            'photo_size_cm': self.photo_size_cm,
            'min_distance_cm': self.min_distance_cm
        }
    
    def get_debug_info(self):
        """
        获取调试信息
        
        Returns:
            dict: 调试参数信息
        """
        return {
            'camera_size': f"{self.camera_width}x{self.camera_height}",
            'photo_size_cm': self.photo_size_cm,
            'min_distance_cm': self.min_distance_cm,
            'pixel_range': f"{self.min_pixel_size}-{self.max_pixel_size}px",
            'confidence_threshold': self.face_confidence_threshold,
            'torso_ratio_range': f"{self.torso_ratio_min}-{self.torso_ratio_max}",
            'max_detections': self.max_detections,
            'has_face_detector': self.has_face_detector
        }
