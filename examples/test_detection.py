#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物检测测试示例
用于测试人物检测功能，支持真实人物和动漫人物检测
"""

import sys
import os
from maix import camera, display, app, time, image, nn
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
            # 使用YOLOv5或类似模型检测person类别
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
            # 人脸检测
            faces = self.face_detector.detect(img, conf_th=self.face_confidence_threshold)
            
            # 过滤小尺寸检测
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
            
            return valid_faces
            
        except Exception as e:
            print(f"人脸检测错误: {e}")
            return []
    
    def detect_persons(self, img):
        """
        检测人物（包括动漫人物）
        
        Args:
            img: 输入图像
            
        Returns:
            list: 检测到的人物位置列表
        """
        if not self.has_object_detector:
            return []
        
        try:
            # 物体检测
            objects = self.object_detector.detect(img, conf_th=self.object_confidence_threshold)
            
            # 过滤person类别
            persons = []
            for obj in objects:
                # COCO数据集中person类别的ID通常是0
                if obj.class_id == 0:  # person class
                    x, y, w, h = obj.x, obj.y, obj.w, obj.h
                    if w >= self.min_detection_size and h >= self.min_detection_size:
                        persons.append({
                            'type': 'person',
                            'bbox': (x, y, w, h),
                            'confidence': obj.score,
                            'class_name': 'person'
                        })
            
            return persons
            
        except Exception as e:
            print(f"人物检测错误: {e}")
            return []
    
    def detect_all_persons(self, img):
        """
        综合检测所有人物（真实+动漫）
        
        Args:
            img: 输入图像
            
        Returns:
            list: 所有检测到的人物
        """
        all_detections = []
        
        # 检测真实人脸
        faces = self.detect_faces(img)
        all_detections.extend(faces)
        
        # 检测人物轮廓
        persons = self.detect_persons(img)
        all_detections.extend(persons)
        
        # 去重重叠的检测结果
        filtered_detections = self.filter_overlapping_detections(all_detections)
        
        return filtered_detections
    
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
    
    def draw_detections(self, img, detections):
        """
        在图像上绘制检测结果（绿色框）
        
        Args:
            img: 输入图像
            detections: 检测结果列表
            
        Returns:
            image: 标记后的图像
        """
        for detection in detections:
            x, y, w, h = detection['bbox']
            detection_type = detection['type']
            confidence = detection['confidence']
            
            # 绘制绿色边界框
            color = image.COLOR_GREEN
            img.draw_rectangle(x, y, w, h, color=color, thickness=2)
            
            # 绘制标签
            label = f"{detection_type}: {confidence:.2f}"
            img.draw_string(x, y-20, label, color=color, scale=1)
            
            # 如果是人脸检测，绘制关键点
            if detection_type == 'face' and detection.get('landmarks'):
                landmarks = detection['landmarks']
                for point in landmarks:
                    img.draw_circle(point[0], point[1], 2, color=color, thickness=-1)
        
        return img

def test_detection():
    """
    测试人物检测功能
    """
    print("人物检测测试开始...")
    print("支持真实人物和动漫人物检测")
    print("按 Ctrl+C 退出测试")
    
    # 1. 初始化摄像头和检测器
    cam = camera.Camera(512, 320)
    disp = display.Display()
    detector = PersonDetector()
    
    if not detector.has_face_detector and not detector.has_object_detector:
        print("错误: 没有可用的检测器")
        return
    
    try:
        frame_count = 0
        detection_count = 0
        
        while not app.need_exit():
            # 2. 采集图像
            img = cam.read()
            if img is None:
                continue
            
            frame_count += 1
            
            # 3. 检测人物
            detections = detector.detect_all_persons(img)
            
            if detections:
                detection_count += len(detections)
                # 4. 绘制绿色框
                img = detector.draw_detections(img, detections)
                
                # 打印检测信息
                print(f"帧 {frame_count}: 检测到 {len(detections)} 个人物")
                for i, det in enumerate(detections):
                    print(f"  {i+1}. {det['type']}: 置信度 {det['confidence']:.3f}, 位置 {det['bbox']}")
            
            # 5. 显示结果
            disp.show(img)
            
            # 计算FPS
            fps = time.fps()
            
            # 每30帧显示统计信息
            if frame_count % 30 == 0:
                avg_detections = detection_count / frame_count
                print(f"统计: 总帧数 {frame_count}, 平均检测 {avg_detections:.2f}/帧, FPS: {fps:.1f}")
            
            # 短暂延时
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        print("\n检测到 Ctrl+C，正在退出...")
    except Exception as e:
        print(f"检测测试出错: {e}")
    finally:
        # 清理资源
        cam.close()
        print("人物检测测试完成")

def test_static_image(image_path):
    """
    测试静态图像的人物检测
    
    Args:
        image_path: 图像文件路径
    """
    print(f"测试静态图像: {image_path}")
    
    try:
        # 加载图像
        img = image.load(image_path)
        detector = PersonDetector()
        
        # 检测人物
        detections = detector.detect_all_persons(img)
        
        if detections:
            print(f"检测到 {len(detections)} 个人物:")
            for i, det in enumerate(detections):
                print(f"  {i+1}. {det['type']}: 置信度 {det['confidence']:.3f}")
            
            # 绘制检测结果
            img_result = detector.draw_detections(img, detections)
            
            # 保存结果
            output_path = image_path.replace('.', '_detected.')
            img_result.save(output_path)
            print(f"检测结果已保存到: {output_path}")
        else:
            print("未检测到人物")
            
    except Exception as e:
        print(f"静态图像检测错误: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # 测试静态图像
        test_static_image(sys.argv[1])
    else:
        # 实时检测
        test_detection()
