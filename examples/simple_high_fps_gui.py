#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化高帧率人脸识别界面
- 优化分辨率提高帧数
- 大按键便于触摸
- 仅包含: 人物记录/识别, FPS显示, 退出按钮
"""

import time
from maix import camera, display, app, image, touchscreen

# 简化的人脸识别功能
try:
    from maix import nn
    HAS_FACE_DETECTOR = True
except ImportError:
    HAS_FACE_DETECTOR = False

class SimpleFaceRecognizer:
    """简化的人脸识别器"""
    
    def __init__(self):
        self.registered_faces = {}
        self.max_faces = 3
        self.current_id = 1
    
    def register_face(self, face_region):
        """注册人脸"""
        if len(self.registered_faces) >= self.max_faces:
            return False, "Max faces reached"
        
        face_id = f"Person{self.current_id}"
        # 简化的特征提取（实际中应该使用更复杂的算法）
        features = self._extract_simple_features(face_region)
        self.registered_faces[face_id] = {
            'features': features,
            'samples': 1
        }
        self.current_id += 1
        return True, face_id
    
    def recognize_face(self, face_region):
        """识别人脸"""
        if not self.registered_faces:
            return None, 0.0
        
        features = self._extract_simple_features(face_region)
        best_match = None
        best_score = 0.0
        
        for face_id, face_data in self.registered_faces.items():
            score = self._calculate_similarity(features, face_data['features'])
            if score > best_score and score > 0.6:  # 阈值
                best_score = score
                best_match = face_id
        
        return best_match, best_score
    
    def _extract_simple_features(self, face_region):
        """简化的特征提取"""
        # 这里使用简单的图像统计作为特征
        if hasattr(face_region, 'width'):
            w = face_region.width() if callable(face_region.width) else face_region.width
            h = face_region.height() if callable(face_region.height) else face_region.height
        else:
            w, h = 64, 64
        
        # 简单特征：区域大小比例
        return {'ratio': w/h if h > 0 else 1.0, 'size': w*h}
    
    def _calculate_similarity(self, features1, features2):
        """计算相似度"""
        ratio_diff = abs(features1['ratio'] - features2['ratio'])
        size_diff = abs(features1['size'] - features2['size']) / max(features1['size'], features2['size'])
        
        similarity = max(0, 1.0 - ratio_diff * 0.5 - size_diff * 0.3)
        return similarity
    
    def clear_all(self):
        """清除所有注册的人脸"""
        self.registered_faces.clear()
        self.current_id = 1
    
    def get_status(self):
        """获取状态"""
        return f"{len(self.registered_faces)}/{self.max_faces}"

class HighFpsGUI:
    """高帧率简化界面"""
    
    def __init__(self):
        # 使用较小分辨率提高帧数
        self.width = 640
        self.height = 480
        
        # 硬件初始化
        self.cam = camera.Camera(self.width, self.height)
        self.disp = display.Display()
        
        # 获取实际显示分辨率
        self.display_width = self.disp.width()
        self.display_height = self.disp.height()
        
        print(f"Camera: {self.width}x{self.height}")
        print(f"Display: {self.display_width}x{self.display_height}")
        
        # 触摸屏初始化
        try:
            self.ts = touchscreen.TouchScreen()
            self.has_touchscreen = True
            print("✓ Touchscreen ready")
        except:
            self.ts = None
            self.has_touchscreen = False
            print("✗ No touchscreen")
        
        # 人脸检测器
        if HAS_FACE_DETECTOR:
            try:
                self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
                print("✓ Face detector ready")
            except:
                self.face_detector = None
                print("✗ Face detector failed")
        else:
            self.face_detector = None
            print("✗ No face detection module")
        
        # 人脸识别器
        self.recognizer = SimpleFaceRecognizer()
        
        # 触摸坐标映射（基于之前的分析）
        self.setup_touch_mapping()
        
        # 大按键设计（便于触摸）
        button_size = 80
        margin = 20
        
        self.buttons = {
            'record': {
                'x': self.display_width - button_size - margin,
                'y': margin,
                'w': button_size,
                'h': button_size,
                'text': 'REC',
                'color': (0, 255, 0)
            },
            'clear': {
                'x': self.display_width - button_size - margin,
                'y': margin + button_size + 20,
                'w': button_size,
                'h': button_size,
                'text': 'CLR',
                'color': (255, 255, 0)
            },
            'exit': {
                'x': self.display_width - button_size - margin,
                'y': self.display_height - button_size - margin,
                'w': button_size,
                'h': button_size,
                'text': 'EXIT',
                'color': (255, 0, 0)
            }
        }
        
        # 状态
        self.recording = False
        self.recording_start_time = 0
        self.recording_duration = 2.0  # 2秒记录时间
        
        # FPS计算
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # 触摸状态
        self.touch_pressed = False
        self.last_touch_x = 0
        self.last_touch_y = 0
        
        print("✓ High FPS GUI initialized")
    
    def setup_touch_mapping(self):
        """设置触摸坐标映射"""
        # 基于校准工具计算出的精确参数
        if self.display_width == 640 and self.display_height == 480:
            # 精确校准后的映射参数
            self.touch_scale_x = 1.6615
            self.touch_scale_y = 1.7352
            self.touch_offset_x = -197.74
            self.touch_offset_y = -140.00
            print("Applied calibrated touch mapping for 640x480 display")
            print(f"  Scale: ({self.touch_scale_x:.4f}, {self.touch_scale_y:.4f})")
            print(f"  Offset: ({self.touch_offset_x:.2f}, {self.touch_offset_y:.2f})")
        else:
            # 默认1:1映射
            self.touch_scale_x = 1.0
            self.touch_scale_y = 1.0
            self.touch_offset_x = 0
            self.touch_offset_y = 0
            print("Using 1:1 touch mapping")
    
    def map_touch_coordinates(self, raw_x, raw_y):
        """映射触摸坐标"""
        mapped_x = int((raw_x + self.touch_offset_x) * self.touch_scale_x)
        mapped_y = int((raw_y + self.touch_offset_y) * self.touch_scale_y)
        
        # 限制范围
        mapped_x = max(0, min(mapped_x, self.display_width - 1))
        mapped_y = max(0, min(mapped_y, self.display_height - 1))
        
        return mapped_x, mapped_y
    
    def detect_faces(self, img):
        """检测人脸"""
        faces = []
        
        if self.face_detector:
            try:
                detected = self.face_detector.detect(img)
                for face in detected:
                    faces.append({
                        'x': face.x, 'y': face.y,
                        'w': face.w, 'h': face.h,
                        'confidence': 0.9
                    })
            except:
                pass
        
        # 如果没有检测到，添加模拟人脸（用于演示）
        if not faces and not self.face_detector:
            import random
            if random.random() > 0.3:  # 70%概率
                x = random.randint(20, self.width - 80)
                y = random.randint(20, self.height - 80)
                w = random.randint(40, 80)
                h = random.randint(50, 90)
                faces.append({'x': x, 'y': y, 'w': w, 'h': h, 'confidence': 0.8})
        
        return faces
    
    def handle_touch(self):
        """处理触摸事件"""
        if not self.has_touchscreen:
            return None
        
        try:
            raw_x, raw_y, pressed = self.ts.read()
            
            if pressed and not self.touch_pressed:
                # 触摸按下
                self.touch_pressed = True
                mapped_x, mapped_y = self.map_touch_coordinates(raw_x, raw_y)
                self.last_touch_x = mapped_x
                self.last_touch_y = mapped_y
                
            elif not pressed and self.touch_pressed:
                # 触摸释放
                self.touch_pressed = False
                
                # 检查按键点击
                for btn_name, btn in self.buttons.items():
                    if (btn['x'] <= self.last_touch_x <= btn['x'] + btn['w'] and
                        btn['y'] <= self.last_touch_y <= btn['y'] + btn['h']):
                        return btn_name
        
        except:
            pass
        
        return None
    
    def handle_button_click(self, button_name, faces):
        """处理按键点击"""
        if button_name == 'record':
            if not self.recording and faces:
                self.recording = True
                self.recording_start_time = time.time()
                print("Started recording...")
            elif self.recording:
                self.recording = False
                print("Recording cancelled")
        
        elif button_name == 'clear':
            self.recognizer.clear_all()
            print("All faces cleared")
        
        elif button_name == 'exit':
            app.set_exit_flag(True)
            print("Exit requested")
    
    def process_recording(self, faces):
        """处理记录过程"""
        if not self.recording:
            return
        
        current_time = time.time()
        if current_time - self.recording_start_time >= self.recording_duration:
            # 记录完成
            if faces:
                face = faces[0]  # 使用第一个检测到的人脸
                success, result = self.recognizer.register_face(face)
                if success:
                    print(f"✓ Registered: {result}")
                else:
                    print(f"✗ Failed: {result}")
            
            self.recording = False
    
    def update_fps(self):
        """更新FPS"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def draw_faces(self, img, faces):
        """绘制人脸框"""
        for face in faces:
            x, y, w, h = face['x'], face['y'], face['w'], face['h']
            
            # 选择颜色
            if self.recording:
                color = image.Color.from_rgb(255, 255, 0)  # 黄色-记录中
            else:
                # 尝试识别
                match, score = self.recognizer.recognize_face(face)
                if match:
                    color = image.Color.from_rgb(0, 255, 0)  # 绿色-已识别
                else:
                    color = image.Color.from_rgb(255, 0, 0)   # 红色-未知
            
            try:
                # 绘制人脸框
                img.draw_rect(x, y, w, h, color=color, thickness=2)
                
                # 绘制标签
                if not self.recording:
                    match, score = self.recognizer.recognize_face(face)
                    if match:
                        label = f"{match} ({score:.2f})"
                        img.draw_string(x, y - 20, label, color=color)
                    else:
                        img.draw_string(x, y - 20, "Unknown", color=color)
                else:
                    img.draw_string(x, y - 20, "Recording...", color=color)
            
            except:
                pass
    
    def draw_buttons(self, img):
        """绘制按键"""
        for btn_name, btn in self.buttons.items():
            x, y, w, h = btn['x'], btn['y'], btn['w'], btn['h']
            r, g, b = btn['color']
            
            # 选择颜色
            if btn_name == 'record' and self.recording:
                color = image.Color.from_rgb(255, 255, 0)  # 黄色-记录中
            elif btn_name == 'clear' and len(self.recognizer.registered_faces) == 0:
                color = image.Color.from_rgb(100, 100, 100)  # 灰色-无可清除
            else:
                color = image.Color.from_rgb(r, g, b)
            
            try:
                # 绘制按键
                img.draw_rect(x, y, w, h, color=color, thickness=-1)
                img.draw_rect(x, y, w, h, color=image.Color.from_rgb(255, 255, 255), thickness=3)
                
                # 绘制文字
                text = btn['text']
                text_x = x + (w - len(text) * 12) // 2
                text_y = y + (h - 16) // 2
                img.draw_string(text_x, text_y, text, 
                              color=image.Color.from_rgb(255, 255, 255))
            except:
                pass
    
    def draw_info(self, img):
        """绘制信息"""
        try:
            # FPS
            fps_text = f"FPS: {self.current_fps}"
            img.draw_string(10, 10, fps_text, 
                          color=image.Color.from_rgb(0, 255, 255))
            
            # 注册状态
            status = self.recognizer.get_status()
            status_text = f"Faces: {status}"
            img.draw_string(10, 30, status_text, 
                          color=image.Color.from_rgb(255, 255, 255))
            
            # 记录状态
            if self.recording:
                elapsed = time.time() - self.recording_start_time
                remaining = max(0, self.recording_duration - elapsed)
                record_text = f"Recording: {remaining:.1f}s"
                img.draw_string(10, 50, record_text, 
                              color=image.Color.from_rgb(255, 255, 0))
            
            # 触摸点可视化
            if self.touch_pressed:
                img.draw_circle(self.last_touch_x, self.last_touch_y, 10, 
                              image.Color.from_rgb(255, 0, 255), 2)
        
        except:
            pass
    
    def run(self):
        """主循环"""
        print("\n=== High FPS Face Recognition GUI ===")
        print("Features:")
        print("- REC: Record new face (2s)")
        print("- CLR: Clear all faces")
        print("- EXIT: Exit program")
        print("- FPS display")
        print()
        
        try:
            while not app.need_exit():
                # 读取摄像头
                img = self.cam.read()
                if img is None:
                    continue
                
                # 检测人脸
                faces = self.detect_faces(img)
                
                # 处理触摸
                clicked_button = self.handle_touch()
                if clicked_button:
                    self.handle_button_click(clicked_button, faces)
                
                # 处理记录
                self.process_recording(faces)
                
                # 绘制界面
                self.draw_faces(img, faces)
                self.draw_info(img)
                self.draw_buttons(img)
                
                # 显示
                self.disp.show(img)
                
                # 更新FPS
                self.update_fps()
        
        except KeyboardInterrupt:
            print("\nProgram interrupted")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            print("Cleaning up...")
            self.cam.close()
            print(f"Final FPS: {self.current_fps}")
            print("Program ended")

def main():
    gui = HighFpsGUI()
    gui.run()

if __name__ == "__main__":
    main()
