#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物检测模块
负责检测A4纸上的三个人物并用绿色框标记
支持真实人物和动漫人物检测
"""

from maix import nn, image
import math

class PersonDetector:
    """
    人物检测器类
    支持真实人物和动漫人物检测
    """
    
    def __init__(self):
        """
        初始化人物检测器
        """
        print("初始化人物检测器...")
        
        # 初始化人脸检测器（用于真实人物）
        try:
            self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
            self.has_face_detector = True
            print("✓ 人脸检测器初始化成功")
        except Exception as e:
            print(f"× 人脸检测器初始化失败: {e}")
            self.has_face_detector = False
        
        # 初始化通用物体检测器（用于动漫人物等）
        try:
            self.object_detector = nn.YOLOv5(model="/root/models/yolov5s.mud")
            self.has_object_detector = True
            print("✓ 物体检测器初始化成功")
        except Exception as e:
            print(f"× 物体检测器初始化失败: {e}")
            self.has_object_detector = False
        
        # 检测参数
        self.face_confidence_threshold = 0.7
        self.object_confidence_threshold = 0.5
        self.min_detection_size = 30
        self.max_detections = 3  # 最多检测3个人物
        
    def detect_faces(self, img):
        """
        检测人脸（真实人物）
        
        Args:
            img: 输入图像
            
        Returns:
            list: 检测到的人脸位置列表
        """
        if not self.has_face_detector:
            return []
        
        try:
            faces = self.face_detector.detect(img, conf_th=self.face_confidence_threshold)
            
            valid_faces = []
            for face in faces:
                x, y, w, h = face.x, face.y, face.w, face.h
                if w >= self.min_detection_size and h >= self.min_detection_size:
                    valid_faces.append({
                        'type': 'face',
                        'bbox': (x, y, w, h),
                        'confidence': face.score,
                        'landmarks': getattr(face, 'landmarks', None)
                    })
            
            return valid_faces[:self.max_detections]  # 限制检测数量
            
        except Exception as e:
            print(f"人脸检测错误: {e}")
            return []
    
    def detect_person_objects(self, img):
        """
        检测人物对象（包括动漫人物）
        
        Args:
            img: 输入图像
            
        Returns:
            list: 检测到的人物位置列表
        """
        if not self.has_object_detector:
            return []
        
        try:
            objects = self.object_detector.detect(img, conf_th=self.object_confidence_threshold)
            
            persons = []
            for obj in objects:
                if obj.class_id == 0:  # person class in COCO dataset
                    x, y, w, h = obj.x, obj.y, obj.w, obj.h
                    if w >= self.min_detection_size and h >= self.min_detection_size:
                        persons.append({
                            'type': 'person',
                            'bbox': (x, y, w, h),
                            'confidence': obj.score,
                            'class_name': 'person'
                        })
            
            return persons[:self.max_detections]  # 限制检测数量
            
        except Exception as e:
            print(f"人物检测错误: {e}")
            return []
    
    def detect_persons(self, image):
        """
        检测图像中的人物（综合方法）
        
        Args:
            image: 输入图像
            
        Returns:
            list: 检测到的人物位置列表
        """
        all_detections = []
        
        # 检测真实人脸
        faces = self.detect_faces(image)
        all_detections.extend(faces)
        
        # 检测人物轮廓
        persons = self.detect_person_objects(image)
        all_detections.extend(persons)
        
        # 去重重叠的检测结果
        filtered_detections = self.filter_overlapping_detections(all_detections)
        
        # 确保最多返回3个检测结果
        return filtered_detections[:self.max_detections]
    
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
        在检测到的人物周围绘制绿色框
        
        Args:
            img: 输入图像
            detections: 检测结果
            
        Returns:
            image: 标记后的图像
        """
        for detection in detections:
            x, y, w, h = detection['bbox']
            detection_type = detection['type']
            confidence = detection['confidence']
            
            # 绘制绿色边界框 - 使用MaixPy的正确API
            color = image.Color.from_rgb(0, 255, 0)  # 绿色
            try:
                # 尝试MaixPy的rect绘制方法
                img.draw_rect(x, y, w, h, color=color, thickness=2)
            except AttributeError:
                try:
                    # 尝试其他可能的方法名
                    img.draw_rectangle(x, y, x+w, y+h, color=color, thickness=2)
                except AttributeError:
                    try:
                        # 尝试更简单的绘制方法
                        img.draw_rect(x, y, x+w, y+h, color)
                    except:
                        # 降级处理：只打印信息
                        print(f"绘制绿色框: ({x}, {y}, {w}, {h}) - {detection_type}")
            
            # 绘制标签
            label = f"{detection_type}: {confidence:.2f}"
            try:
                img.draw_string(x, max(y-20, 0), label, color=color)
            except AttributeError:
                try:
                    img.draw_text(x, max(y-20, 0), label, color=color)
                except AttributeError:
                    print(f"检测标签: {label} at ({x}, {y})")
            
            # 如果是人脸检测，绘制关键点
            if detection_type == 'face' and detection.get('landmarks'):
                landmarks = detection['landmarks']
                for point in landmarks:
                    try:
                        img.draw_circle(point[0], point[1], 2, color=color, thickness=-1)
                    except AttributeError:
                        try:
                            img.draw_circle(point[0], point[1], 2, color=color)
                        except AttributeError:
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
                'bboxes': []
            }
        
        types = [det['type'] for det in detections]
        confidences = [det['confidence'] for det in detections]
        bboxes = [det['bbox'] for det in detections]
        
        return {
            'count': len(detections),
            'types': types,
            'confidence_avg': sum(confidences) / len(confidences),
            'bboxes': bboxes
        }
