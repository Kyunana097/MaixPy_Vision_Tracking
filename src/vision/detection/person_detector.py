#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物检测模块
专门检测人物上半身并用绿色框标记
"""

class PersonDetector:
    """
    人物检测器类
    负责检测图像中的人物并返回边界框信息
    """
    
    def __init__(self, camera_width=512, camera_height=320):
        """
        初始化人物检测器
        
        Args:
            camera_width: 摄像头宽度(像素)
            camera_height: 摄像头高度(像素)
        """
        print("🔍 初始化人物检测器...")
        
        # 摄像头参数
        self.camera_width = camera_width
        self.camera_height = camera_height
        
        # 初始化人脸检测器
        try:
            from maix import nn
            self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
            self.has_face_detector = True
            print("✓ Face detector initialized successfully")
        except Exception as e:
            print(f"✗ Face detector initialization failed: {e}")
            self.face_detector = None
            self.has_face_detector = False
        self.max_detections = 3
        
        print("✓ 人物检测器初始化完成（待集成实际检测模块）")
    
    def detect_persons(self, img):
        """
        检测图像中的人物
        
        Args:
            img: 输入图像
            
        Returns:
            list: 检测结果列表，每个元素包含：
                {
                    'bbox': (x, y, w, h),           # 上半身边界框
                    'face_bbox': (x, y, w, h),      # 人脸边界框（可选）
                    'confidence': float,            # 置信度
                    'type': 'upper_body'            # 检测类型
                }
        """
        
        detections = []
        
        if self.has_face_detector and self.face_detector:
            try:
                # 使用真实的人脸检测
                faces = self.face_detector.detect(img)
                
                for face in faces:
                    # 从人脸推算上半身
                    face_x, face_y, face_w, face_h = face.x, face.y, face.w, face.h
                    
                    # 上半身估算：宽度1.5倍，高度2.5倍
                    body_w = int(face_w * 1.5)
                    body_h = int(face_h * 2.0)
                    body_x = max(0, face_x - (body_w - face_w) // 2)
                    body_y = face_y  # 从人脸顶部开始
                    
                    # 确保不超出图像边界
                    img_width = img.width() if callable(img.width) else img.width
                    img_height = img.height() if callable(img.height) else img.height
                    
                    body_x = min(body_x, img_width - body_w)
                    body_y = min(body_y, img_height - body_h)
                    body_w = min(body_w, img_width - body_x)
                    body_h = min(body_h, img_height - body_y)
                    
                    detection = {
                        'bbox': (body_x, body_y, body_w, body_h),
                        'face_bbox': (face_x, face_y, face_w, face_h),
                        'confidence': 0.9,
                        'type': 'upper_body'
                    }
                    detections.append(detection)
            
            except Exception as e:
                print(f"Face detection error: {e}")
        
        return detections
    
    def draw_detection_boxes(self, img, detections):
        """
        在检测到的人物周围绘制边界框
        
        Args:
            img: 输入图像
            detections: 检测结果列表
            
        Returns:
            image: 标记后的图像
        """
        try:
            from maix import image
        except ImportError:
            return img
        
        for detection in detections:
            bbox = detection['bbox']
            face_bbox = detection.get('face_bbox')
            x, y, w, h = bbox
            
            # 绘制上半身绿色边界框
            try:
                green_color = image.Color.from_rgb(0, 255, 0)
                img.draw_rect(x, y, w, h, color=green_color, thickness=2)
            except:
                pass
            
            # 绘制人脸框
            if face_bbox:
                fx, fy, fw, fh = face_bbox
                try:
                    cyan_color = image.Color.from_rgb(0, 255, 255)
                    img.draw_rect(fx, fy, fw, fh, color=cyan_color, thickness=1)
                except:
                    pass
            
            # 绘制标签
            try:
                confidence = detection.get('confidence', 0.0)
                label = f"Person: {confidence:.2f}"
                white_color = image.Color.from_rgb(255, 255, 255)
                img.draw_string(x, max(y-20, 0), label, color=white_color)
            except:
                pass
        
        return img
    
    def get_detection_info(self, detections):
        """
        获取检测信息摘要
        
        Args:
            detections: 检测结果列表
            
        Returns:
            dict: 检测信息摘要
        """
        return {
            'count': len(detections),
            'types': [det.get('type', 'unknown') for det in detections],
            'confidence_avg': sum(det.get('confidence', 0) for det in detections) / len(detections) if detections else 0.0,
            'upper_body_bboxes': [det.get('bbox') for det in detections],
            'face_bboxes': [det.get('face_bbox') for det in detections if det.get('face_bbox')]
        }
    
    def get_debug_info(self):
        """
        获取调试信息
        
        Returns:
            dict: 调试参数信息
        """
        return {
            'camera_size': f"{self.camera_width}x{self.camera_height}",
            'max_detections': self.max_detections,
            'has_face_detector': self.has_face_detector,
            'module_status': 'initialized_placeholder'
        }

# TODO: 参考standalone_gui.py中的SimplePersonDetector实现
# 需要集成的功能：
# 1. 人脸检测器初始化 (nn.FaceDetector)
# 2. 人脸检测 (detect_persons方法)
# 3. 人脸到上半身的转换 (face_to_torso)
# 4. 检测结果绘制 (draw_detection_boxes)
# 5. 重叠检测过滤 (filter_overlapping_detections)
