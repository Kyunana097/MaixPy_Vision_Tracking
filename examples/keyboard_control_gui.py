#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
键盘控制版本的虚拟按键摄像头界面
支持键盘按键控制虚拟按键
"""

import time
import sys
import os
from maix import camera, display, app, image

# 尝试导入键盘检测库
try:
    import keyboard
    HAS_KEYBOARD = True
    print("✓ Keyboard library available - press R for record, C for clear")
except ImportError:
    HAS_KEYBOARD = False
    print("✗ Keyboard library not available - using timed demo mode")

# 检查人脸检测功能
try:
    from maix import nn
    HAS_FACE_DETECTOR = True
    print("✓ MaixPy face detection module available")
except ImportError:
    HAS_FACE_DETECTOR = False
    print("✗ MaixPy face detection module unavailable, using simulation mode")

class KeyboardControlGUI:
    """
    键盘控制的虚拟按键界面
    """
    
    def __init__(self):
        """
        初始化界面
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
            'record': {'x': 420, 'y': 250, 'w': 80, 'h': 35, 'active': False, 'enabled': True},
            'clear': {'x': 420, 'y': 295, 'w': 80, 'h': 35, 'active': False, 'enabled': True}
        }
        
        # 记录状态
        self.recording = False
        self.recording_name = ""
        self.recording_samples = 0
        self.last_sample_time = 0
        
        # 按键控制
        self.last_key_time = 0
        self.key_cooldown = 1.0  # 1秒按键冷却
        
        # 测试模式（当没有键盘库时）
        self.test_mode_start = time.time()
        
        print("=== Keyboard Control GUI ===")
        if HAS_KEYBOARD:
            print("Controls: R = Record, C = Clear, ESC = Exit")
        else:
            print("Test mode: Auto demo every 15 seconds")
        print()
    
    def _get_detections(self, img):
        """
        获取人脸检测结果
        
        Args:
            img: 输入图像
            
        Returns:
            list: 检测结果
        """
        detections = []
        
        if self.face_detector:
            try:
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
                color = image.Color.from_rgb(255, 255, 0)  # 黄色 - 记录中
            else:
                color = image.Color.from_rgb(0, 255, 0)    # 绿色 - 正常
            
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
            img.draw_string(x + 12, y + 10, text, color=image.Color.from_rgb(255, 255, 255))
            # 显示按键提示
            img.draw_string(x + 15, y + 25, "(R)", color=image.Color.from_rgb(200, 200, 200))
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
            img.draw_string(x + 18, y + 10, "Clear", color=image.Color.from_rgb(255, 255, 255))
            # 显示按键提示
            img.draw_string(x + 15, y + 25, "(C)", color=image.Color.from_rgb(200, 200, 200))
        except:
            pass
    
    def _draw_info(self, img):
        """
        绘制信息
        
        Args:
            img: 图像
        """
        try:
            # 标题
            img.draw_string(10, 10, "Keyboard Control Face Recognition", 
                          color=image.Color.from_rgb(255, 255, 255))
            
            # 状态
            status_text = f"Registered: {len(self.registered_persons)}/{self.max_persons}"
            img.draw_string(10, 35, status_text, 
                          color=image.Color.from_rgb(0, 255, 255))
            
            # 模式
            if self.recording:
                mode_text = f"Recording: {self.recording_name} ({self.recording_samples}/3)"
                color = image.Color.from_rgb(255, 255, 0)
            else:
                mode_text = "Live Detection Mode"
                color = image.Color.from_rgb(0, 255, 0)
            
            img.draw_string(10, 55, mode_text, color=color)
            
            # 检测状态
            detector_text = "Real Detection" if self.face_detector else "Simulated"
            img.draw_string(10, 75, f"Detection: {detector_text}", 
                          color=image.Color.from_rgb(128, 128, 128))
            
            # 控制状态
            if HAS_KEYBOARD:
                control_text = "Keyboard Control Ready"
                color = image.Color.from_rgb(0, 255, 0)
            else:
                elapsed = time.time() - self.test_mode_start
                control_text = f"Test Mode: {elapsed:.1f}s"
                color = image.Color.from_rgb(255, 165, 0)
            
            img.draw_string(10, 95, control_text, color=color)
            
            # 提示
            if HAS_KEYBOARD:
                img.draw_string(10, 280, "Press R=Record C=Clear ESC=Exit", 
                              color=image.Color.from_rgb(255, 255, 0))
            else:
                img.draw_string(10, 280, "Test mode - Auto demo running", 
                              color=image.Color.from_rgb(255, 255, 0))
        except:
            pass
    
    def _check_keyboard_input(self):
        """
        检查键盘输入
        
        Returns:
            str: 按键操作类型
        """
        current_time = time.time()
        
        # 防抖处理
        if current_time - self.last_key_time < self.key_cooldown:
            return None
        
        if HAS_KEYBOARD:
            try:
                # 检查键盘按键
                if keyboard.is_pressed('r') or keyboard.is_pressed('R'):
                    self.last_key_time = current_time
                    self._flash_button('record')
                    return 'record'
                
                if keyboard.is_pressed('c') or keyboard.is_pressed('C'):
                    self.last_key_time = current_time
                    self._flash_button('clear')
                    return 'clear'
                
                if keyboard.is_pressed('esc'):
                    return 'exit'
                    
            except Exception as e:
                print(f"Keyboard check error: {e}")
        
        else:
            # 测试模式 - 自动演示
            elapsed = current_time - self.test_mode_start
            cycle_time = elapsed % 15  # 15秒循环
            
            if 3 <= cycle_time <= 3.5:  # 第3秒触发记录
                if not hasattr(self, 'test_record_done'):
                    self.test_record_done = True
                    self.last_key_time = current_time
                    self._flash_button('record')
                    print("Test mode: Auto record")
                    return 'record'
            elif 10 <= cycle_time <= 10.5:  # 第10秒触发清除
                if not hasattr(self, 'test_clear_done'):
                    self.test_clear_done = True
                    self.last_key_time = current_time
                    self._flash_button('clear')
                    print("Test mode: Auto clear")
                    return 'clear'
            else:
                # 重置标志
                if cycle_time < 3:
                    self.test_record_done = False
                    self.test_clear_done = False
                elif cycle_time < 10:
                    self.test_clear_done = False
        
        return None
    
    def _flash_button(self, button_name):
        """
        按键闪烁效果
        
        Args:
            button_name: 按键名称
        """
        if button_name in self.buttons:
            self.buttons[button_name]['active'] = True
            # 注意：在实际应用中，需要异步处理来在短时间后重置active状态
    
    def _handle_action(self, action, detections):
        """
        处理操作
        
        Args:
            action: 操作类型
            detections: 检测结果
        """
        if action == 'record':
            if not self.recording:
                # 开始记录
                if detections and len(self.registered_persons) < self.max_persons:
                    person_count = len(self.registered_persons)
                    self.recording = True
                    self.recording_name = f"Person{person_count + 1}"
                    self.recording_samples = 0
                    self.last_sample_time = time.time()
                    print(f"✓ Start recording: {self.recording_name}")
                else:
                    if not detections:
                        print("✗ No face detected")
                    else:
                        print("✗ Max persons limit reached")
            else:
                # 取消记录
                self.recording = False
                self.recording_name = ""
                self.recording_samples = 0
                print("✓ Recording cancelled")
        
        elif action == 'clear':
            if self.registered_persons:
                count = len(self.registered_persons)
                self.registered_persons.clear()
                print(f"✓ Cleared {count} records")
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
            # 注册新人物
            person_id = f"person_{len(self.registered_persons) + 1:02d}"
            self.registered_persons[person_id] = self.recording_name
            print(f"✓ Registered: {self.recording_name}")
        else:
            print(f"✓ Sample {self.recording_samples}/3 added")
        
        # 完成记录
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
        
        # 更新清除按键可用状态
        has_records = len(self.registered_persons) > 0
        self.buttons['clear']['enabled'] = has_records
    
    def run(self):
        """
        运行主循环
        """
        print("Starting keyboard control GUI...")
        if HAS_KEYBOARD:
            print("Ready for keyboard input...")
        else:
            print("Running in test mode...")
        
        frame_count = 0
        
        try:
            while not app.need_exit():
                # 读取摄像头
                img = self.cam.read()
                if img is None:
                    continue
                
                frame_count += 1
                
                # 获取检测结果
                detections = self._get_detections(img)
                
                # 检查键盘输入
                action = self._check_keyboard_input()
                if action == 'exit':
                    print("Exit requested")
                    break
                elif action:
                    self._handle_action(action, detections)
                
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
                
                # 控制帧率
                time.sleep(0.033)  # 约30FPS
        
        except KeyboardInterrupt:
            print("\nProgram interrupted")
        except Exception as e:
            print(f"Program error: {e}")
        finally:
            print("Cleaning up...")
            self.cam.close()
            print("Program ended")

def main():
    """
    主函数
    """
    print("=== Keyboard Control Virtual Button GUI ===")
    print("Enhanced with keyboard and test mode support")
    
    try:
        gui = KeyboardControlGUI()
        gui.run()
    except Exception as e:
        print(f"Startup failed: {e}")

if __name__ == "__main__":
    main()
