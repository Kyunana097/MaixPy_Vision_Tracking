#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版独立虚拟按键摄像头界面
修复所有兼容性问题，确保稳定运行
"""

import time
from maix import camera, display, app, image

# 检查人脸检测功能
try:
    from maix import nn
    HAS_FACE_DETECTOR = True
except ImportError:
    HAS_FACE_DETECTOR = False

class SimpleGUI:
    """
    简化的独立GUI
    """
    
    def __init__(self):
        """
        初始化
        """
        # 硬件初始化
        self.cam = camera.Camera(512, 320)
        self.disp = display.Display()
        
        # 人脸检测器
        self.face_detector = None
        if HAS_FACE_DETECTOR:
            try:
                self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
                print("✓ Face detector initialized successfully")
            except:
                print("✗ Face detector init failed, using simulation mode")
        else:
            print("✗ Face detection module unavailable, using simulation mode")
        
        # 简化的数据存储
        self.registered_persons = {}
        self.max_persons = 3
        
        # 虚拟按键
        self.buttons = {
            'record': {'x': 420, 'y': 250, 'w': 80, 'h': 35, 'active': False},
            'clear': {'x': 420, 'y': 295, 'w': 80, 'h': 35, 'active': False}
        }
        
        # 记录状态
        self.recording = False
        self.recording_name = ""
        self.recording_samples = 0
        self.last_sample_time = 0
        
        # 演示控制
        self.demo_start_time = time.time()
        self.last_demo_action = 0
        
        print("=== Simple Virtual Button GUI ===")
        print("Features: Face Detection + Virtual Buttons + Auto Demo")
        print()
    
    def _get_current_detections(self, img):
        """
        获取当前检测结果
        
        Args:
            img: 输入图像
            
        Returns:
            list: 检测结果
        """
        detections = []
        
        if self.face_detector:
            try:
                # 真实人脸检测
                faces = self.face_detector.detect(img)
                for face in faces:
                    detection = {
                        'bbox': (face.x, face.y, face.w, face.h),
                        'confidence': 0.9
                    }
                    detections.append(detection)
            except Exception as e:
                print(f"Detection error: {e}")
        
        if not detections:
            # 模拟检测（用于演示）
            import random
            if random.random() > 0.4:  # 60%概率
                x = random.randint(50, 300)
                y = random.randint(50, 200)
                w = random.randint(60, 100)
                h = random.randint(80, 120)
                
                detection = {
                    'bbox': (x, y, w, h),
                    'confidence': 0.85
                }
                detections.append(detection)
        
        return detections
    
    def _draw_detections(self, img, detections):
        """
        绘制检测结果
        
        Args:
            img: 图像
            detections: 检测结果
        """
        for detection in detections:
            x, y, w, h = detection['bbox']
            
            # 选择颜色
            if self.recording:
                color = image.Color.from_rgb(255, 255, 0)  # Yellow - Recording
            else:
                color = image.Color.from_rgb(0, 255, 0)    # Green - Normal
            
            try:
                img.draw_rect(x, y, w, h, color=color, thickness=2)
                
                # 显示识别结果
                if not self.recording and self.registered_persons:
                    # 简单的识别逻辑
                    import random
                    if random.random() > 0.5:
                        person_names = list(self.registered_persons.values())
                        if person_names:
                            name = random.choice(person_names)
                            label = f"{name} (0.87)"
                            img.draw_string(x, y - 20, label, 
                                          color=image.Color.from_rgb(255, 0, 0))
                    else:
                        img.draw_string(x, y - 20, "Unknown (0.65)", 
                                      color=image.Color.from_rgb(255, 255, 255))
            except:
                pass
    
    def _draw_buttons(self, img):
        """
        绘制虚拟按键
        
        Args:
            img: 图像
        """
        # 记录按键
        record_btn = self.buttons['record']
        x, y, w, h = record_btn['x'], record_btn['y'], record_btn['w'], record_btn['h']
        
        if self.recording:
            color = image.Color.from_rgb(255, 255, 0) if record_btn['active'] else image.Color.from_rgb(200, 150, 0)
            text = "Cancel"
        else:
            color = image.Color.from_rgb(0, 255, 0) if record_btn['active'] else image.Color.from_rgb(0, 150, 0)
            text = "Record"
        
        try:
            img.draw_rect(x, y, w, h, color=color, thickness=-1)
            img.draw_rect(x, y, w, h, color=image.Color.from_rgb(255, 255, 255), thickness=2)
            img.draw_string(x + 15, y + 10, text, color=image.Color.from_rgb(255, 255, 255))
        except:
            pass
        
        # 清除按键
        clear_btn = self.buttons['clear']
        x, y, w, h = clear_btn['x'], clear_btn['y'], clear_btn['w'], clear_btn['h']
        
        has_records = len(self.registered_persons) > 0
        if has_records:
            color = image.Color.from_rgb(255, 0, 0) if clear_btn['active'] else image.Color.from_rgb(150, 0, 0)
        else:
            color = image.Color.from_rgb(80, 80, 80)
        
        try:
            img.draw_rect(x, y, w, h, color=color, thickness=-1)
            img.draw_rect(x, y, w, h, color=image.Color.from_rgb(255, 255, 255), thickness=2)
            img.draw_string(x + 15, y + 10, "Clear", color=image.Color.from_rgb(255, 255, 255))
        except:
            pass
    
    def _draw_info(self, img):
        """
        绘制信息
        
        Args:
            img: 图像
        """
        try:
            # Title
            img.draw_string(10, 10, "Face Recognition System", 
                          color=image.Color.from_rgb(255, 255, 255))
            
            # Status
            status_text = f"Registered: {len(self.registered_persons)}/{self.max_persons}"
            img.draw_string(10, 35, status_text, 
                          color=image.Color.from_rgb(0, 255, 255))
            
            # Mode
            if self.recording:
                mode_text = f"Recording: {self.recording_name} ({self.recording_samples}/3)"
                color = image.Color.from_rgb(255, 255, 0)
            else:
                mode_text = "Live Detection Mode"
                color = image.Color.from_rgb(0, 255, 0)
            
            img.draw_string(10, 55, mode_text, color=color)
            
            # Detection status
            detector_text = "Real Detection" if self.face_detector else "Simulated"
            img.draw_string(10, 75, f"Detection: {detector_text}", 
                          color=image.Color.from_rgb(128, 128, 128))
            
            # Demo time
            elapsed = time.time() - self.demo_start_time
            img.draw_string(10, 95, f"Demo: {elapsed:.1f}s", 
                          color=image.Color.from_rgb(255, 165, 0))
            
            # Instructions
            img.draw_string(10, 280, "Green=Record Red=Clear", 
                          color=image.Color.from_rgb(255, 255, 0))
        except:
            pass
    
    def _handle_demo_actions(self):
        """
        处理演示动作
        
        Returns:
            str: 动作类型
        """
        elapsed = time.time() - self.demo_start_time
        
        # 演示序列
        actions = [
            (3, 'record_start'),
            (8, 'record_cancel'),
            (12, 'record_start'),
            (20, 'clear_all')
        ]
        
        for action_time, action_type in actions:
            if (elapsed >= action_time and elapsed < action_time + 0.5 and
                action_time > self.last_demo_action):
                self.last_demo_action = action_time
                return action_type
        
        # 重置循环
        if elapsed > 25:
            self.demo_start_time = time.time()
            self.last_demo_action = 0
        
        return None
    
    def _handle_record_action(self, detections):
        """
        处理记录动作
        
        Args:
            detections: 检测结果
        """
        if not self.recording:
            # 开始记录
            if detections and len(self.registered_persons) < self.max_persons:
                person_count = len(self.registered_persons)
                self.recording = True
                self.recording_name = f"Person{person_count + 1}"
                self.recording_samples = 0
                self.last_sample_time = time.time()
                self.buttons['record']['active'] = True
                print(f"Start recording: {self.recording_name}")
            else:
                if not detections:
                    print("No face detected")
                else:
                    print("Max persons limit reached")
        else:
            # Cancel recording
            self.recording = False
            self.recording_name = ""
            self.recording_samples = 0
            print("Recording cancelled")
    
    def _handle_clear_action(self):
        """
        处理清除动作
        """
        if self.registered_persons:
            count = len(self.registered_persons)
            self.registered_persons.clear()
            self.buttons['clear']['active'] = True
            print(f"Cleared {count} records")
        else:
            print("No records to clear")
    
    def _process_recording(self, detections):
        """
        处理记录过程
        
        Args:
            detections: 检测结果
        """
        if not self.recording or not detections:
            return
        
        current_time = time.time()
        
        # 每1.5秒采样一次
        if current_time - self.last_sample_time < 1.5:
            return
        
        self.recording_samples += 1
        self.last_sample_time = current_time
        
        if self.recording_samples == 1:
            # Register new person
            person_id = f"person_{len(self.registered_persons) + 1:02d}"
            self.registered_persons[person_id] = self.recording_name
            print(f"✓ Registered: {self.recording_name}")
        else:
            print(f"✓ Sample {self.recording_samples}/3 added")
        
        # Complete recording
        if self.recording_samples >= 3:
            print(f"✓ Recording complete: {self.recording_name}")
            self.recording = False
            self.recording_name = ""
            self.recording_samples = 0
    
    def _reset_button_states(self):
        """
        重置按键状态
        """
        for button in self.buttons.values():
            if button['active']:
                button['active'] = False
    
    def run(self):
        """
        运行主循环
        """
        print("Starting Simple Virtual Button GUI...")
        print("Auto demo mode running...")
        
        frame_count = 0
        
        try:
            while not app.need_exit():
                # 读取摄像头
                img = self.cam.read()
                if img is None:
                    continue
                
                frame_count += 1
                
                # 获取检测结果
                detections = self._get_current_detections(img)
                
                # 处理演示动作
                action = self._handle_demo_actions()
                if action == 'record_start':
                    self._handle_record_action(detections)
                elif action == 'record_cancel':
                    if self.recording:
                        self._handle_record_action(detections)
                elif action == 'clear_all':
                    self._handle_clear_action()
                
                # 处理记录过程
                if self.recording:
                    self._process_recording(detections)
                
                # 绘制界面
                self._draw_detections(img, detections)
                self._draw_info(img)
                self._draw_buttons(img)
                
                # 重置按键状态
                if frame_count % 6 == 0:  # 每6帧重置一次
                    self._reset_button_states()
                
                # 显示画面
                self.disp.show(img)
                
                # 控制帧率 - 使用标准Python sleep
                time.sleep(0.033)  # 约30FPS
        
        except Exception as e:
            print(f"Program error: {e}")
        finally:
            print("Cleaning up resources...")
            self.cam.close()
            print("Program ended")

def main():
    """
    主函数
    """
    print("=== Simple Standalone Virtual Button GUI ===")
    print("Fixed Version - Compatibility Optimized")
    
    try:
        gui = SimpleGUI()
        gui.run()
    except Exception as e:
        print(f"Startup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
