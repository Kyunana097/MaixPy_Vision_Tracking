#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物识别详细教程
演示MaixPy中人物识别的每个步骤
"""

import sys
import os
from maix import camera, display, app, time, image, nn

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class PersonDetectionTutorial:
    """
    人物识别教程类
    详细演示识别过程的每个步骤
    """
    
    def __init__(self):
        """
        初始化教程
        """
        print("=== MaixPy人物识别详细教程 ===")
        print()
        
        self.camera_width = 512
        self.camera_height = 320
        
        # 初始化摄像头
        print("1. 初始化摄像头...")
        self.cam = camera.Camera(self.camera_width, self.camera_height)
        self.disp = display.Display()
        print(f"   摄像头分辨率: {self.camera_width}x{self.camera_height}")
        print()
        
        # 初始化检测器
        print("2. 初始化AI检测模型...")
        self.init_detectors()
        print()
    
    def init_detectors(self):
        """
        初始化检测器并详细说明
        """
        # 人脸检测器
        print("   2.1 人脸检测器 (专用于真实人物)")
        try:
            self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
            self.has_face_detector = True
            print("       ✓ 加载成功 - 可检测真实人脸")
            print("       - 检测精度: 高")
            print("       - 适用场景: 真人照片")
            print("       - 特征: 可检测人脸关键点")
        except Exception as e:
            print(f"       × 加载失败: {e}")
            self.has_face_detector = False
        
        print()
        
        # 物体检测器  
        print("   2.2 通用物体检测器 (支持动漫人物)")
        try:
            self.object_detector = nn.YOLOv5(model="/root/models/yolov5s.mud")
            self.has_object_detector = True
            print("       ✓ 加载成功 - 可检测各种人物形象")
            print("       - 检测精度: 中高")
            print("       - 适用场景: 真人、动漫、卡通")
            print("       - 特征: 检测整个人物轮廓")
        except Exception as e:
            print(f"       × 加载失败: {e}")
            self.has_object_detector = False
    
    def detect_step_by_step(self, img):
        """
        逐步演示检测过程
        """
        print("\n=== 检测过程详解 ===")
        
        all_detections = []
        
        # 步骤1: 人脸检测
        if self.has_face_detector:
            print("步骤1: 人脸检测")
            try:
                faces = self.face_detector.detect(img, conf_th=0.7)
                print(f"   原始检测结果: 发现 {len(faces)} 个人脸")
                
                valid_faces = []
                for i, face in enumerate(faces):
                    print(f"   人脸 {i+1}:")
                    print(f"     位置: ({face.x}, {face.y})")
                    print(f"     尺寸: {face.w} x {face.h}")
                    print(f"     置信度: {face.score:.3f}")
                    
                    if face.w >= 30 and face.h >= 30:
                        detection = {
                            'type': 'face',
                            'bbox': (face.x, face.y, face.w, face.h),
                            'confidence': face.score,
                            'landmarks': getattr(face, 'landmarks', None)
                        }
                        valid_faces.append(detection)
                        all_detections.append(detection)
                        print(f"     ✓ 有效检测")
                    else:
                        print(f"     × 尺寸过小，忽略")
                
                print(f"   有效人脸: {len(valid_faces)} 个")
                
            except Exception as e:
                print(f"   人脸检测错误: {e}")
        
        print()
        
        # 步骤2: 物体检测
        if self.has_object_detector:
            print("步骤2: 通用人物检测")
            try:
                objects = self.object_detector.detect(img, conf_th=0.5)
                print(f"   原始检测结果: 发现 {len(objects)} 个物体")
                
                persons = []
                for i, obj in enumerate(objects):
                    if obj.class_id == 0:  # person class in COCO
                        print(f"   人物 {i+1}:")
                        print(f"     位置: ({obj.x}, {obj.y})")
                        print(f"     尺寸: {obj.w} x {obj.h}")
                        print(f"     置信度: {obj.score:.3f}")
                        print(f"     类别: person (ID: {obj.class_id})")
                        
                        if obj.w >= 30 and obj.h >= 30:
                            detection = {
                                'type': 'person',
                                'bbox': (obj.x, obj.y, obj.w, obj.h),
                                'confidence': obj.score,
                                'class_name': 'person'
                            }
                            persons.append(detection)
                            all_detections.append(detection)
                            print(f"     ✓ 有效检测")
                        else:
                            print(f"     × 尺寸过小，忽略")
                
                print(f"   有效人物: {len(persons)} 个")
                
            except Exception as e:
                print(f"   物体检测错误: {e}")
        
        print()
        
        # 步骤3: 结果融合
        print("步骤3: 结果融合与去重")
        print(f"   融合前总数: {len(all_detections)}")
        
        if len(all_detections) > 1:
            filtered_detections = self.remove_overlapping(all_detections)
            print(f"   去重后总数: {len(filtered_detections)}")
            
            for i, det in enumerate(filtered_detections):
                print(f"   最终结果 {i+1}: {det['type']} (置信度: {det['confidence']:.3f})")
        else:
            filtered_detections = all_detections
            print("   无需去重")
        
        # 限制最多3个
        final_detections = filtered_detections[:3]
        print(f"   最终输出: {len(final_detections)} 个检测结果")
        
        return final_detections
    
    def remove_overlapping(self, detections, overlap_threshold=0.5):
        """
        去除重叠检测结果
        """
        if len(detections) <= 1:
            return detections
        
        # 按置信度排序
        detections.sort(key=lambda x: x['confidence'], reverse=True)
        
        filtered = []
        for detection in detections:
            bbox1 = detection['bbox']
            
            overlapped = False
            for selected in filtered:
                bbox2 = selected['bbox']
                iou = self.calculate_iou(bbox1, bbox2)
                if iou > overlap_threshold:
                    print(f"     重叠检测 (IoU: {iou:.3f}) - 移除较低置信度的结果")
                    overlapped = True
                    break
            
            if not overlapped:
                filtered.append(detection)
        
        return filtered
    
    def calculate_iou(self, bbox1, bbox2):
        """
        计算IoU（交并比）
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
    
    def draw_detections_with_info(self, img, detections):
        """
        绘制检测结果并显示详细信息
        """
        for i, detection in enumerate(detections):
            x, y, w, h = detection['bbox']
            detection_type = detection['type']
            confidence = detection['confidence']
            
            # 根据类型选择颜色
            if detection_type == 'face':
                color = image.Color.from_rgb(0, 255, 0)  # 绿色 - 人脸
                type_text = "人脸"
            else:
                color = image.Color.from_rgb(0, 255, 255)  # 青色 - 人物
                type_text = "人物"
            
            # 绘制边界框
            try:
                img.draw_rect(x, y, w, h, color=color, thickness=2)
            except:
                print(f"绘制边界框: ({x}, {y}, {w}, {h}) - {detection_type}")
            
            # 绘制标签
            label = f"{type_text} {i+1}: {confidence:.2f}"
            try:
                img.draw_string(x, max(y-20, 0), label, color=color)
            except:
                print(f"检测标签: {label} at ({x}, {y})")
            
            # 如果是人脸，绘制关键点
            if detection_type == 'face' and detection.get('landmarks'):
                landmarks = detection['landmarks']
                for point in landmarks:
                    try:
                        img.draw_circle(point[0], point[1], 2, color=color)
                    except:
                        print(f"关键点: ({point[0]}, {point[1]})")
        
        return img
    
    def run_tutorial(self):
        """
        运行完整的教程演示
        """
        print("3. 开始实时检测演示...")
        print("   按 Ctrl+C 退出")
        print("   前3帧会显示详细的检测过程")
        print()
        
        frame_count = 0
        
        try:
            while not app.need_exit():
                img = self.cam.read()
                if img is None:
                    continue
                
                frame_count += 1
                
                # 前3帧显示详细过程
                if frame_count <= 3:
                    print(f"\n=== 第 {frame_count} 帧详细分析 ===")
                    detections = self.detect_step_by_step(img)
                else:
                    # 后续帧快速检测
                    detections = self.detect_quietly(img)
                
                # 绘制结果
                img = self.draw_detections_with_info(img, detections)
                
                # 显示统计信息
                info_text = f"帧:{frame_count} 检测:{len(detections)}"
                try:
                    img.draw_string(10, 10, info_text, color=image.Color.from_rgb(255, 255, 255))
                except:
                    print(info_text)
                
                # 显示图像
                self.disp.show(img)
                
                # 显示FPS
                fps = time.fps()
                if frame_count % 30 == 0:
                    print(f"FPS: {fps:.1f}, 总检测: {len(detections)}")
                
                time.sleep_ms(10)
                
        except KeyboardInterrupt:
            print("\n\n=== 教程结束 ===")
            print("感谢您学习MaixPy人物识别！")
        finally:
            self.cam.close()
    
    def detect_quietly(self, img):
        """
        静默检测（不打印详细信息）
        """
        all_detections = []
        
        # 人脸检测
        if self.has_face_detector:
            try:
                faces = self.face_detector.detect(img, conf_th=0.7)
                for face in faces:
                    if face.w >= 30 and face.h >= 30:
                        all_detections.append({
                            'type': 'face',
                            'bbox': (face.x, face.y, face.w, face.h),
                            'confidence': face.score,
                            'landmarks': getattr(face, 'landmarks', None)
                        })
            except:
                pass
        
        # 物体检测
        if self.has_object_detector:
            try:
                objects = self.object_detector.detect(img, conf_th=0.5)
                for obj in objects:
                    if obj.class_id == 0 and obj.w >= 30 and obj.h >= 30:
                        all_detections.append({
                            'type': 'person',
                            'bbox': (obj.x, obj.y, obj.w, obj.h),
                            'confidence': obj.score,
                            'class_name': 'person'
                        })
            except:
                pass
        
        # 去重并限制数量
        filtered = self.remove_overlapping(all_detections) if len(all_detections) > 1 else all_detections
        return filtered[:3]

def main():
    """
    主函数
    """
    tutorial = PersonDetectionTutorial()
    tutorial.run_tutorial()

if __name__ == "__main__":
    main()
