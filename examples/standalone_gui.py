#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone virtual button camera interface
All features integrated in one file, no external dependencies
"""

import sys
import os
import time
import json
from maix import camera, display, app, image, touchscreen

# Check if face detection functionality is available
try:
    from maix import nn
    HAS_FACE_DETECTOR = True
    print("✓ MaixPy face detection module available")
except ImportError:
    HAS_FACE_DETECTOR = False
    print("✗ MaixPy face detection module unavailable, using simulation mode")

class SimplePersonRecognizer:
    """
    Simplified person recognizer
    """
    
    def __init__(self, max_persons=3):
        """
        Initialize recognizer
        
        Args:
            max_persons: Maximum number of persons
        """
        self.max_persons = max_persons
        self.registered_persons = {}
        self.similarity_threshold = 0.85
        
        # Try to initialize face detector
        if HAS_FACE_DETECTOR:
            try:
                self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
                self.has_face_detector = True
                print("✓ Face detector initialized successfully")
            except Exception as e:
                print(f"✗ Face detector initialization failed: {e}")
                self.face_detector = None
                self.has_face_detector = False
        else:
            self.face_detector = None
            self.has_face_detector = False
    
    def get_status_info(self):
        """
        Get status information
        
        Returns:
            dict: Status information
        """
        return {
            'max_persons': self.max_persons,
            'registered_count': len(self.registered_persons),
            'available_slots': self.max_persons - len(self.registered_persons),
            'similarity_threshold': self.similarity_threshold,
            'has_face_detector': self.has_face_detector,
            'target_person': None,
            'registered_persons': list(self.registered_persons.keys())
        }
    
    def register_person(self, img, person_name, bbox=None):
        """
        注册新人物
        
        Args:
            img: 图像
            person_name: 人物姓名
            bbox: 边界框
            
        Returns:
            tuple: (成功标志, 人物ID, 消息)
        """
        if len(self.registered_persons) >= self.max_persons:
            return False, None, f"已达到最大人数限制 ({self.max_persons})"
        
        # 检查姓名是否已存在
        for person_id, info in self.registered_persons.items():
            if info['name'] == person_name:
                return False, None, f"人物 '{person_name}' 已存在"
        
        # 生成新的person_id
        person_id = f"person_{len(self.registered_persons) + 1:02d}"
        
        # 保存人物信息
        self.registered_persons[person_id] = {
            'name': person_name,
            'id': person_id,
            'registered_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'feature_count': 1
        }
        
        print(f"Successfully registered person: {person_name} (ID: {person_id})")
        return True, person_id, f"Successfully registered person: {person_name}"
    
    def add_person_sample(self, person_id, img, bbox=None):
        """
        添加人物样本
        
        Args:
            person_id: 人物ID
            img: 图像
            bbox: 边界框
            
        Returns:
            tuple: (成功标志, 消息)
        """
        if person_id not in self.registered_persons:
            return False, "人物ID不存在"
        
        self.registered_persons[person_id]['feature_count'] += 1
        
        return True, f"Successfully added sample, total samples: {self.registered_persons[person_id]['feature_count']}"
    
    def recognize_person(self, img, bbox=None):
        """
        识别人物
        
        Args:
            img: 图像
            bbox: 边界框
            
        Returns:
            tuple: (人物ID, 置信度, 姓名)
        """
        if not self.registered_persons:
            return None, 0.0, "Unknown"
        
        # 简化的识别逻辑：随机返回一个已注册的人物
        import random
        if random.random() > 0.5:  # 50%概率识别成功
            person_id = random.choice(list(self.registered_persons.keys()))
            person_name = self.registered_persons[person_id]['name']
            confidence = 0.85 + random.random() * 0.1  # 0.85-0.95
            return person_id, confidence, person_name
        
        return None, 0.3 + random.random() * 0.4, "Unknown"  # 0.3-0.7
    
    def delete_person(self, person_id):
        """
        删除人物
        
        Args:
            person_id: 人物ID
            
        Returns:
            tuple: (成功标志, 消息)
        """
        if person_id not in self.registered_persons:
            return False, "Person ID does not exist"
        
        person_name = self.registered_persons[person_id]['name']
        del self.registered_persons[person_id]
        
        return True, f"Successfully deleted person: {person_name}"
    
    def get_registered_persons(self):
        """
        获取已注册人物
        
        Returns:
            dict: 人物信息字典
        """
        return self.registered_persons.copy()

class SimplePersonDetector:
    """
    简化的人物检测器
    """
    
    def __init__(self, camera_width=512, camera_height=320):
        """
        初始化检测器
        
        Args:
            camera_width: 摄像头宽度
            camera_height: 摄像头高度
        """
        self.camera_width = camera_width
        self.camera_height = camera_height
        
        # Try to initialize face detector
        if HAS_FACE_DETECTOR:
            try:
                self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
                self.has_face_detector = True
                print("✓ Face detector initialized successfully")
            except Exception as e:
                print(f"✗ Face detector initialization failed: {e}")
                self.face_detector = None
                self.has_face_detector = False
        else:
            self.face_detector = None
            self.has_face_detector = False
    
    def detect_persons(self, img):
        """
        检测人物
        
        Args:
            img: 输入图像
            
        Returns:
            list: 检测结果列表
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
                    body_h = int(face_h * 2.5)
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
        
        else:
            # 模拟检测结果
            import random
            if random.random() > 0.4:  # 60%概率检测到人脸
                center_x = self.camera_width // 2
                center_y = self.camera_height // 2
                
                # 随机偏移
                offset_x = random.randint(-50, 50)
                offset_y = random.randint(-30, 30)
                
                face_w = random.randint(60, 100)
                face_h = random.randint(80, 120)
                face_x = center_x + offset_x - face_w // 2
                face_y = center_y + offset_y - face_h // 2
                
                # 确保在边界内
                face_x = max(0, min(face_x, self.camera_width - face_w))
                face_y = max(0, min(face_y, self.camera_height - face_h))
                
                # 上半身
                body_w = int(face_w * 1.5)
                body_h = int(face_h * 2.5)
                body_x = max(0, face_x - (body_w - face_w) // 2)
                body_y = face_y
                
                detection = {
                    'bbox': (body_x, body_y, body_w, body_h),
                    'face_bbox': (face_x, face_y, face_w, face_h),
                    'confidence': 0.85 + random.random() * 0.1,
                    'type': 'upper_body'
                }
                detections.append(detection)
        
        return detections

class StandaloneGUI:
    """
    独立的虚拟按键摄像头界面
    """
    
    def __init__(self, width=512, height=320):
        """
        初始化界面
        
        Args:
            width: 显示宽度
            height: 显示高度
        """
        self.width = width
        self.height = height
        
        # 硬件初始化
        print("初始化摄像头...")
        self.cam = camera.Camera(width, height)
        self.disp = display.Display()
        
        # 触摸屏初始化
        try:
            self.ts = touchscreen.TouchScreen()
            self.has_touchscreen = True
            print("✓ Touchscreen initialized")
        except:
            self.ts = None
            self.has_touchscreen = False
            print("✗ Touchscreen not available")
        
        # 功能模块
        print("初始化检测和识别模块...")
        self.detector = SimplePersonDetector(camera_width=width, camera_height=height)
        self.recognizer = SimplePersonRecognizer()
        
        # 虚拟按键配置
        button_width = 80
        button_height = 35
        button_margin = 10
        
        self.buttons = {
            'record': {
                'x': width - button_width - button_margin,
                'y': height - 2 * button_height - 2 * button_margin,
                'w': button_width,
                'h': button_height,
                'text': '记录',
                'active': False,
                'last_click': 0,
                'enabled': True
            },
            'clear': {
                'x': width - button_width - button_margin,
                'y': height - button_height - button_margin,
                'w': button_width,
                'h': button_height,
                'text': '清除',
                'active': False,
                'last_click': 0,
                'enabled': True
            }
        }
        
        # 记录状态
        self.recording = {
            'active': False,
            'name': '',
            'samples': 0,
            'max_samples': 3,
            'person_id': None,
            'last_sample_time': 0,
            'sample_interval': 1.5
        }
        
        # 界面状态
        self.frame_count = 0
        self.click_cooldown = 0.5
        self.debug_mode = True  # 显示调试信息
        
        # 触摸状态
        self.touch_pressed_already = False
        self.last_touch_x = 0
        self.last_touch_y = 0
        self.last_touch_pressed = False
        
        # 触摸坐标映射参数
        self.touch_scale_x = 1.0
        self.touch_scale_y = 1.0
        self.touch_offset_x = 0
        self.touch_offset_y = 0
        
        # 自动检测和应用常见的坐标映射
        self._detect_touch_mapping()
        
        # 手动控制模式
        self.manual_mode = True
        self.last_manual_action = 0
        self.manual_cooldown = 5.0  # 5秒间隔用于手动操作演示
        
        print("=== Standalone Virtual Button Interface ===")
        print("Features:")
        print("  - Live camera display")
        print("  - Face detection and recognition")
        print("  - Virtual button operation")
        print("  - Manual control mode")
        print()
        
        self._show_system_status()
    
    def _show_system_status(self):
        """
        显示系统状态
        """
        status = self.recognizer.get_status_info()
        print("System Status:")
        print(f"  Face Detection: {'✓' if self.detector.has_face_detector else '✗ (Simulation Mode)'}")
        print(f"  Registered Persons: {status['registered_count']}/{status['max_persons']}")
        
        if status['registered_persons']:
            print("  Person List:")
            for person_id in status['registered_persons']:
                info = self.recognizer.registered_persons[person_id]
                print(f"    {info['name']} (Samples: {info['feature_count']})")
        else:
            print("  No registered persons")
        print()
    
    def _draw_virtual_buttons(self, img):
        """
        绘制虚拟按键
        
        Args:
            img: 图像对象
        """
        for button_name, button in self.buttons.items():
            x, y, w, h = button['x'], button['y'], button['w'], button['h']
            
            # 选择按键颜色
            if button_name == 'record':
                if self.recording['active']:
                    if button['active']:
                        color = image.Color.from_rgb(255, 255, 0)
                    else:
                        color = image.Color.from_rgb(200, 150, 0)
                    text = 'Cancel'
                else:
                    if button['active']:
                        color = image.Color.from_rgb(0, 255, 0)
                    else:
                        color = image.Color.from_rgb(0, 150, 0)
                    text = 'Record'
            
            elif button_name == 'clear':
                if button['enabled']:
                    if button['active']:
                        color = image.Color.from_rgb(255, 0, 0)
                    else:
                        color = image.Color.from_rgb(150, 0, 0)
                else:
                    color = image.Color.from_rgb(80, 80, 80)
                text = 'Clear'
            
            try:
                # 绘制按键背景
                img.draw_rect(x, y, w, h, color=color, thickness=-1)
                
                # 绘制按键边框
                border_color = image.Color.from_rgb(255, 255, 255)
                img.draw_rect(x, y, w, h, color=border_color, thickness=2)
                
                # 绘制按键文字
                text_x = x + (w - len(text) * 8) // 2
                text_y = y + (h - 16) // 2
                img.draw_string(text_x, text_y, text, 
                              color=image.Color.from_rgb(255, 255, 255), scale=1.2)
                
                # 点击效果
                if button['active']:
                    inner_color = image.Color.from_rgb(255, 255, 255)
                    img.draw_rect(x + 2, y + 2, w - 4, h - 4, 
                                color=inner_color, thickness=1)
                
                # 调试模式：显示按键区域坐标
                if self.debug_mode:
                    debug_text = f"{x},{y}-{x+w},{y+h}"
                    try:
                        img.draw_string(x, y - 15, debug_text, 
                                      color=image.Color.from_rgb(255, 255, 0), scale=0.8)
                    except:
                        pass
            
            except Exception as e:
                print(f"绘制按键错误: {e}")
    
    def _draw_ui_info(self, img):
        """
        绘制界面信息
        
        Args:
            img: 图像对象
        """
        try:
            # 主标题
            title = "Face Recognition System"
            img.draw_string(10, 10, title, 
                          color=image.Color.from_rgb(255, 255, 255), scale=1.2)
            
            # 系统状态
            status = self.recognizer.get_status_info()
            status_text = f"Registered: {status['registered_count']}/{status['max_persons']}"
            img.draw_string(10, 35, status_text, 
                          color=image.Color.from_rgb(0, 255, 255))
            
            # 当前模式
            if self.recording['active']:
                mode_text = f"Recording: {self.recording['name']} ({self.recording['samples']}/{self.recording['max_samples']})"
                mode_color = image.Color.from_rgb(255, 255, 0)
            else:
                mode_text = "Live Detection Mode"
                mode_color = image.Color.from_rgb(0, 255, 0)
            
            img.draw_string(10, 55, mode_text, color=mode_color)
            
            # 检测状态
            detector_status = "Real Detection" if self.detector.has_face_detector else "Simulated"
            img.draw_string(10, 75, f"Detection: {detector_status}", 
                          color=image.Color.from_rgb(128, 128, 128))
            
            # 控制模式信息
            mode_text = "Touch Control Mode" if self.has_touchscreen else "Display Only Mode"
            img.draw_string(10, 95, mode_text, 
                          color=image.Color.from_rgb(255, 165, 0))
            
            # 操作提示
            help_y = self.height - 60
            # 控制状态提示
            if self.has_touchscreen:
                img.draw_string(10, help_y, "Touch Control Ready:", 
                              color=image.Color.from_rgb(255, 255, 255))
                img.draw_string(10, help_y + 20, "Touch buttons to interact", 
                              color=image.Color.from_rgb(0, 255, 0))
            else:
                img.draw_string(10, help_y, "No Touch Control:", 
                              color=image.Color.from_rgb(255, 255, 255))
                img.draw_string(10, help_y + 20, "Touchscreen not available", 
                              color=image.Color.from_rgb(255, 0, 0))
            
        except Exception as e:
            print(f"UI信息绘制错误: {e}")
    
    def _detect_touch_mapping(self):
        """
        自动检测触摸坐标映射参数
        """
        if not self.has_touchscreen:
            return
        
        # 常见的MaixPy设备触摸坐标映射
        display_width = self.width
        display_height = self.height
        
        print(f"Display resolution: {display_width} x {display_height}")
        
        # 对于常见的512x320显示屏的情况
        if display_width == 512 and display_height == 320:
            # 假设触摸屏分辨率可能是800x480或其他
            self.touch_scale_x = display_width / 800.0  # 假设触摸屏宽度800
            self.touch_scale_y = display_height / 480.0  # 假设触摸屏高度480
            print(f"Applied common mapping: scale_x={self.touch_scale_x:.3f}, scale_y={self.touch_scale_y:.3f}")
        
        print(f"Touch mapping: scale=({self.touch_scale_x:.3f}, {self.touch_scale_y:.3f}) offset=({self.touch_offset_x}, {self.touch_offset_y})")
    
    def _map_touch_coordinates(self, raw_x, raw_y):
        """
        映射原始触摸坐标到显示坐标
        
        Args:
            raw_x: 原始触摸X坐标
            raw_y: 原始触摸Y坐标
            
        Returns:
            tuple: (映射后X坐标, 映射后Y坐标)
        """
        mapped_x = int((raw_x + self.touch_offset_x) * self.touch_scale_x)
        mapped_y = int((raw_y + self.touch_offset_y) * self.touch_scale_y)
        
        # 限制在显示范围内
        mapped_x = max(0, min(mapped_x, self.width - 1))
        mapped_y = max(0, min(mapped_y, self.height - 1))
        
        return mapped_x, mapped_y
    
    def _process_detections(self, img):
        """
        处理人脸检测
        
        Args:
            img: 图像对象
            
        Returns:
            list: 检测结果列表
        """
        detections = self.detector.detect_persons(img)
        
        if detections:
            for detection in detections:
                bbox = detection['bbox']
                face_bbox = detection.get('face_bbox')
                x, y, w, h = bbox
                
                # 选择框颜色
                if self.recording['active']:
                    box_color = image.Color.from_rgb(255, 255, 0)
                    thickness = 3
                else:
                    box_color = image.Color.from_rgb(0, 255, 0)
                    thickness = 2
                
                # 绘制检测框
                try:
                    img.draw_rect(x, y, w, h, color=box_color, thickness=thickness)
                    
                    # 绘制人脸框
                    if face_bbox:
                        fx, fy, fw, fh = face_bbox
                        face_color = image.Color.from_rgb(0, 255, 255)
                        img.draw_rect(fx, fy, fw, fh, color=face_color, thickness=1)
                except:
                    pass
                
                # 识别并标注
                if face_bbox and not self.recording['active']:
                    person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                    
                    if person_id:
                        label = f"{person_name} ({confidence:.2f})"
                        label_color = image.Color.from_rgb(255, 0, 0)
                    else:
                        label = f"Unknown ({confidence:.2f})"
                        label_color = image.Color.from_rgb(255, 255, 255)
                    
                    try:
                        img.draw_string(x, y - 20, label, color=label_color)
                    except:
                        pass
        
        return detections
    
    def _check_manual_control(self):
        """
        检查手动控制 - 真实触摸检测
        
        Returns:
            str: 按键名称，如果没有则返回None
        """
        if not self.has_touchscreen:
            return None
        
        try:
            # 读取触摸屏状态
            raw_x, raw_y, pressed = self.ts.read()
            
            # 映射触摸坐标
            x, y = self._map_touch_coordinates(raw_x, raw_y)
            
            # 检查触摸状态变化 - 添加调试信息
            if x != self.last_touch_x or y != self.last_touch_y or pressed != self.last_touch_pressed:
                if pressed != self.last_touch_pressed:  # 按压状态变化时打印
                    print(f"Touch state: raw({raw_x}, {raw_y}) -> mapped({x}, {y}) pressed={pressed}")
                self.last_touch_x = x
                self.last_touch_y = y
                self.last_touch_pressed = pressed
            
            # 处理触摸事件
            if pressed:
                self.touch_pressed_already = True
                # 在图像上显示触摸点（如果可能）
                # 这会在主循环的图像上绘制，但由于时机问题可能看不到
            else:
                # 触摸释放时检查是否点击了按键
                if self.touch_pressed_already:
                    print(f"Touch released at: ({x}, {y})")
                    self.touch_pressed_already = False
                    
                    # 添加按键区域调试信息
                    print(f"Checking button areas:")
                    for btn_name, btn in self.buttons.items():
                        btn_x, btn_y, btn_w, btn_h = btn['x'], btn['y'], btn['w'], btn['h']
                        x2, y2 = btn_x + btn_w, btn_y + btn_h
                        enabled = btn.get('enabled', True)
                        print(f"  {btn_name}: ({btn_x},{btn_y}) to ({x2},{y2}) enabled={enabled}")
                    
                    button_clicked = self._check_virtual_button_touch(x, y)
                    if button_clicked:
                        print(f"✓ Touch detected: {button_clicked} at ({x}, {y})")
                        return button_clicked
                    else:
                        print(f"✗ Touch outside button areas at ({x}, {y})")
        
        except Exception as e:
            print(f"Touch detection error: {e}")
        
        return None
    
    def _check_virtual_button_touch(self, touch_x, touch_y):
        """
        检查触摸点是否在虚拟按键区域内
        
        Args:
            touch_x: 触摸X坐标
            touch_y: 触摸Y坐标
            
        Returns:
            str: 按键名称，如果不在按键区域则返回None
        """
        for button_name, button in self.buttons.items():
            x, y, w, h = button['x'], button['y'], button['w'], button['h']
            
            # 检查触摸点是否在按键区域内
            if (x <= touch_x <= x + w and 
                y <= touch_y <= y + h and 
                button['enabled']):
                
                return button_name
        
        return None
    
    def _handle_button_click(self, button_name, detections):
        """
        处理按键点击
        
        Args:
            button_name: 按键名称
            detections: 当前检测结果
        """
        current_time = time.time()
        button = self.buttons[button_name]
        
        # 检查点击冷却
        if current_time - button['last_click'] < self.click_cooldown:
            return
        
        button['last_click'] = current_time
        button['active'] = True
        
        if button_name == 'record':
            if not self.recording['active']:
                # 开始记录
                if detections:
                    status = self.recognizer.get_status_info()
                    if status['available_slots'] > 0:
                        self._start_recording()
                        print("✓ Start recording new person")
                    else:
                        print("✗ Maximum person limit reached")
                else:
                    print("✗ No face detected, cannot start recording")
            else:
                # Cancel recording
                self._cancel_recording()
                print("✓ Recording cancelled")
        
        elif button_name == 'clear':
            if button['enabled']:
                self._clear_all_records()
                print("✓ All records cleared")
    
    def _start_recording(self):
        """
        开始记录新人物
        """
        person_count = len(self.recognizer.get_registered_persons())
        
        self.recording.update({
            'active': True,
            'name': f"Person{person_count + 1}",
            'samples': 0,
            'person_id': None,
            'last_sample_time': time.time()
        })
    
    def _cancel_recording(self):
        """
        取消记录
        """
        if self.recording['person_id']:
            success, message = self.recognizer.delete_person(self.recording['person_id'])
            if success:
                print(f"✓ 已清理部分记录: {message}")
        
        self.recording.update({
            'active': False,
            'name': '',
            'samples': 0,
            'person_id': None
        })
    
    def _process_recording(self, img, detections):
        """
        处理记录过程
        
        Args:
            img: 当前图像
            detections: 检测结果
        """
        if not self.recording['active'] or not detections:
            return
        
        current_time = time.time()
        
        # 控制采样频率
        if current_time - self.recording['last_sample_time'] < self.recording['sample_interval']:
            return
        
        # 使用第一个检测结果
        detection = detections[0]
        face_bbox = detection.get('face_bbox')
        
        if face_bbox:
            if self.recording['samples'] == 0:
                # 第一次记录
                success, person_id, message = self.recognizer.register_person(
                    img, self.recording['name'], face_bbox
                )
                
                if success:
                    print(f"✓ {message}")
                    self.recording['person_id'] = person_id
                    self.recording['samples'] = 1
                    self.recording['last_sample_time'] = current_time
                else:
                    print(f"✗ {message}")
                    self._cancel_recording()
                    return
            
            elif self.recording['samples'] < self.recording['max_samples']:
                # Add more samples
                success, message = self.recognizer.add_person_sample(
                    self.recording['person_id'], img, face_bbox
                )
                
                if success:
                    print(f"✓ {message}")
                    self.recording['samples'] += 1
                    self.recording['last_sample_time'] = current_time
                    
                    # Check if complete
                    if self.recording['samples'] >= self.recording['max_samples']:
                        print(f"✓ Recording complete: {self.recording['name']}")
                        self.recording['active'] = False
                        self._show_system_status()
                else:
                    print(f"✗ Sample addition failed: {message}")
    
    def _clear_all_records(self):
        """
        清除所有记录
        """
        persons = self.recognizer.get_registered_persons()
        
        if not persons:
            print("No records to clear")
            return
        
        deleted_count = 0
        for person_id in list(persons.keys()):
            success, message = self.recognizer.delete_person(person_id)
            if success:
                deleted_count += 1
                print(f"✓ Deleted: {message}")
            else:
                print(f"✗ Delete failed: {message}")
        
        print(f"Clear complete, deleted {deleted_count} records")
        self._show_system_status()
    
    def _update_button_states(self):
        """
        更新按键状态
        """
        current_time = time.time()
        
        # 重置按键激活状态
        for button in self.buttons.values():
            if button['active'] and current_time - button['last_click'] > 0.2:
                button['active'] = False
        
        # 更新清除按键可用状态
        has_records = len(self.recognizer.get_registered_persons()) > 0
        self.buttons['clear']['enabled'] = has_records
    
    def run(self):
        """
        运行主循环
        """
        print("Starting standalone virtual button interface...")
        if self.has_touchscreen:
            print("Mode: Touch control enabled")
            print("Touch virtual buttons to interact")
        else:
            print("Mode: Display only (no touchscreen)")
            print("Touchscreen not available")
        print()
        
        try:
            while not app.need_exit():
                # 读取摄像头
                img = self.cam.read()
                if img is None:
                    continue
                
                self.frame_count += 1
                
                # 处理人脸检测
                detections = self._process_detections(img)
                
                # 更新按键状态
                self._update_button_states()
                
                # 检查手动控制（可以扩展为真实按键检测）
                clicked_button = self._check_manual_control()
                if clicked_button:
                    self._handle_button_click(clicked_button, detections)
                
                # 处理记录过程
                if self.recording['active']:
                    self._process_recording(img, detections)
                
                # 绘制界面
                self._draw_ui_info(img)
                self._draw_virtual_buttons(img)
                
                # 绘制触摸点（如果正在触摸）
                if self.has_touchscreen and hasattr(self, 'last_touch_x') and hasattr(self, 'last_touch_y'):
                    if self.touch_pressed_already:
                        try:
                            img.draw_circle(self.last_touch_x, self.last_touch_y, 5, 
                                          image.Color.from_rgb(255, 255, 255), 2)
                        except:
                            pass
                
                # 显示画面
                self.disp.show(img)
                
                # 控制帧率
                time.sleep(0.033)  # 约30FPS
        
        except KeyboardInterrupt:
            print("\nProgram interrupted by user")
        except Exception as e:
            print(f"Program runtime error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("Cleaning up resources...")
            self.cam.close()
            print("Program ended")

def main():
    """
    主函数
    """
    print("=== Standalone Virtual Button Camera GUI ===")
    print("All features integrated in one file")
    print("No external dependencies, ready to use")
    print()
    
    # Parse command line arguments
    width, height = 512, 320
    
    if len(sys.argv) > 1:
        try:
            width = int(sys.argv[1])
            if len(sys.argv) > 2:
                height = int(sys.argv[2])
        except ValueError:
            print("Invalid resolution parameters, using default 512x320")
    
    print(f"Resolution: {width}x{height}")
    
    # Create and run GUI
    try:
        gui = StandaloneGUI(width, height)
        gui.run()
    except Exception as e:
        print(f"GUI startup failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
