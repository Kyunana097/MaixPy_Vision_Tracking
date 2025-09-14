#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按键控制的实时摄像头界面
支持物理按键的记录和清除功能
"""

import sys
import os
import time
from maix import camera, display, app, image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.recognition.face_recognition import PersonRecognizer
from src.vision.detection.person_detector import PersonDetector

class ButtonCameraGUI:
    """
    按键控制的摄像头界面
    """
    
    def __init__(self):
        """
        初始化界面
        """
        # 硬件初始化
        self.cam = camera.Camera(512, 320)
        self.disp = display.Display()
        
        # 功能模块
        self.detector = PersonDetector(camera_width=512, camera_height=320)
        self.recognizer = PersonRecognizer()
        
        # 按键状态
        self.button_states = {
            'record': False,
            'clear': False,
            'last_record_time': 0,
            'last_clear_time': 0,
            'long_press_threshold': 2.0,  # 长按阈值（秒）
            'debounce_time': 0.3          # 防抖时间（秒）
        }
        
        # 记录状态
        self.recording = {
            'active': False,
            'name': '',
            'samples': 0,
            'max_samples': 3,
            'person_id': None,
            'last_sample_time': 0
        }
        
        # 界面状态
        self.frame_count = 0
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        print("=== 按键控制摄像头界面 ===")
        print("硬件连接:")
        print("  - 记录按键: 连接到GPIO引脚")
        print("  - 清除按键: 连接到另一个GPIO引脚")
        print("  - 或使用设备自带按键")
        print()
        
        self._show_system_info()
    
    def _show_system_info(self):
        """
        显示系统信息
        """
        status = self.recognizer.get_status_info()
        print("系统状态:")
        print(f"  检测器: {'✓' if self.detector.has_face_detector else '✗'}")
        print(f"  识别器: {'✓' if status['has_face_detector'] else '✗'}")
        print(f"  已注册人物: {status['registered_count']}/{status['max_persons']}")
        
        if status['registered_persons']:
            print("  人物列表:")
            for person_id in status['registered_persons']:
                info = self.recognizer.registered_persons[person_id]
                print(f"    {info['name']} (样本: {info['feature_count']})")
        print()
    
    def _read_buttons(self):
        """
        读取按键状态
        这里需要根据实际硬件连接进行调整
        
        Returns:
            dict: 按键状态字典
        """
        current_time = time.time()
        button_events = {'record': None, 'clear': None}
        
        try:
            # 方法1: 使用GPIO按键（需要根据实际硬件调整）
            # 这里提供一个通用的框架
            
            # 假设记录按键连接到某个GPIO引脚
            # record_button_pressed = read_gpio_pin(RECORD_BUTTON_PIN)
            # clear_button_pressed = read_gpio_pin(CLEAR_BUTTON_PIN)
            
            # 方法2: 使用设备自带按键（如果可用）
            # 这里使用模拟按键状态进行演示
            
            # 模拟按键检测（实际应用中需要替换为真实的按键读取）
            record_pressed = self._simulate_record_button()
            clear_pressed = self._simulate_clear_button()
            
            # 处理记录按键
            if record_pressed and not self.button_states['record']:
                # 按键按下
                self.button_states['record'] = True
                self.button_states['last_record_time'] = current_time
                
            elif not record_pressed and self.button_states['record']:
                # 按键释放
                press_duration = current_time - self.button_states['last_record_time']
                self.button_states['record'] = False
                
                if press_duration >= self.button_states['long_press_threshold']:
                    button_events['record'] = 'long'
                elif press_duration >= self.button_states['debounce_time']:
                    button_events['record'] = 'short'
            
            # 处理清除按键
            if clear_pressed and not self.button_states['clear']:
                # 按键按下
                self.button_states['clear'] = True
                self.button_states['last_clear_time'] = current_time
                
            elif not clear_pressed and self.button_states['clear']:
                # 按键释放
                press_duration = current_time - self.button_states['last_clear_time']
                self.button_states['clear'] = False
                
                if press_duration >= self.button_states['debounce_time']:
                    button_events['clear'] = 'press'
        
        except Exception as e:
            print(f"按键读取错误: {e}")
        
        return button_events
    
    def _simulate_record_button(self):
        """
        模拟记录按键状态（用于演示）
        在实际应用中应该替换为真实的GPIO读取
        
        Returns:
            bool: 按键是否被按下
        """
        # 这里使用时间来模拟按键按下
        # 每20秒模拟一次按键操作
        cycle_time = time.time() % 20
        return 1 <= cycle_time <= 3  # 模拟按键按下2秒
    
    def _simulate_clear_button(self):
        """
        模拟清除按键状态（用于演示）
        
        Returns:
            bool: 按键是否被按下
        """
        # 每30秒模拟一次清除按键
        cycle_time = time.time() % 30
        return 25 <= cycle_time <= 26  # 模拟按键按下1秒
    
    def _draw_ui(self, img):
        """
        绘制用户界面
        
        Args:
            img: 图像对象
        """
        try:
            # 主标题
            img.draw_string(10, 10, "按键控制人脸识别", 
                          color=image.Color.from_rgb(255, 255, 255), scale=1.2)
            
            # 系统状态
            status = self.recognizer.get_status_info()
            status_text = f"人物: {status['registered_count']}/{status['max_persons']}"
            img.draw_string(10, 35, status_text, color=image.Color.from_rgb(0, 255, 255))
            
            # 记录状态
            if self.recording['active']:
                record_text = f"记录中: {self.recording['name']} ({self.recording['samples']}/{self.recording['max_samples']})"
                img.draw_string(10, 55, record_text, color=image.Color.from_rgb(255, 255, 0))
            else:
                img.draw_string(10, 55, "待机模式", color=image.Color.from_rgb(0, 255, 0))
            
            # 按键状态指示
            record_status = "按下" if self.button_states['record'] else "释放"
            clear_status = "按下" if self.button_states['clear'] else "释放"
            
            img.draw_string(10, 75, f"记录键: {record_status}", 
                          color=image.Color.from_rgb(255, 128, 0))
            img.draw_string(10, 95, f"清除键: {clear_status}", 
                          color=image.Color.from_rgb(255, 128, 0))
            
            # FPS显示
            img.draw_string(10, 115, f"FPS: {self.current_fps:.1f}", 
                          color=image.Color.from_rgb(128, 128, 128))
            
            # 操作说明（底部）
            help_y = 280
            img.draw_string(10, help_y, "操作说明:", color=image.Color.from_rgb(255, 255, 255))
            img.draw_string(10, help_y + 15, "记录键短按: 记录人脸", color=image.Color.from_rgb(255, 255, 0))
            img.draw_string(10, help_y + 30, "清除键: 删除所有记录", color=image.Color.from_rgb(255, 255, 0))
            
        except Exception as e:
            print(f"UI绘制错误: {e}")
    
    def _process_detections(self, img):
        """
        处理人脸检测并绘制结果
        
        Args:
            img: 图像对象
            
        Returns:
            list: 检测结果
        """
        detections = self.detector.detect_persons(img)
        
        if detections:
            for detection in detections:
                bbox = detection['bbox']
                face_bbox = detection.get('face_bbox')
                x, y, w, h = bbox
                
                # 选择框颜色
                if self.recording['active']:
                    box_color = image.Color.from_rgb(255, 255, 0)  # 黄色 - 记录中
                    text_color = image.Color.from_rgb(255, 255, 0)
                else:
                    box_color = image.Color.from_rgb(0, 255, 0)    # 绿色 - 检测
                    text_color = image.Color.from_rgb(255, 255, 255)
                
                # 绘制边界框
                try:
                    img.draw_rect(x, y, w, h, color=box_color, thickness=2)
                    
                    if face_bbox:
                        fx, fy, fw, fh = face_bbox
                        img.draw_rect(fx, fy, fw, fh, color=image.Color.from_rgb(0, 255, 255), thickness=1)
                except:
                    pass
                
                # 识别和标注
                if face_bbox and not self.recording['active']:
                    person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                    
                    if person_id:
                        # 已知人物
                        label = f"{person_name} ({confidence:.2f})"
                        label_color = image.Color.from_rgb(255, 0, 0)
                    else:
                        # 未知人物
                        label = f"未知 ({confidence:.2f})"
                        label_color = image.Color.from_rgb(255, 255, 255)
                    
                    try:
                        img.draw_string(x, y - 20, label, color=label_color)
                    except:
                        pass
        
        return detections
    
    def _handle_record_button(self, press_type, detections):
        """
        处理记录按键事件
        
        Args:
            press_type: 按键类型 ('short', 'long')
            detections: 当前检测结果
        """
        if press_type == 'short':
            if not self.recording['active']:
                # 开始记录
                if detections:
                    # 检查是否还有空位
                    status = self.recognizer.get_status_info()
                    if status['available_slots'] > 0:
                        self._start_recording()
                    else:
                        print("✗ 已达到最大人数限制")
                else:
                    print("✗ 未检测到人脸，无法开始记录")
            else:
                # 取消记录
                self._cancel_recording()
        
        elif press_type == 'long':
            # 长按可以用于其他功能，比如重置系统
            print("记录按键长按 - 保留功能")
    
    def _handle_clear_button(self, press_type):
        """
        处理清除按键事件
        
        Args:
            press_type: 按键类型
        """
        if press_type == 'press':
            self._clear_all_records()
    
    def _start_recording(self):
        """
        开始记录新人物
        """
        # 生成人物名称
        person_count = len(self.recognizer.get_registered_persons())
        
        self.recording.update({
            'active': True,
            'name': f"人物{person_count + 1}",
            'samples': 0,
            'person_id': None,
            'last_sample_time': time.time()
        })
        
        print(f"开始记录: {self.recording['name']}")
    
    def _cancel_recording(self):
        """
        取消记录
        """
        print(f"取消记录: {self.recording['name']}")
        
        # 如果已经开始记录，需要删除部分数据
        if self.recording['person_id']:
            self.recognizer.delete_person(self.recording['person_id'])
        
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
        
        # 控制采样频率（每1秒采样一次）
        if current_time - self.recording['last_sample_time'] < 1.0:
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
            
            elif self.recording['samples'] < self.recording['max_samples']:
                # 添加更多样本
                success, message = self.recognizer.add_person_sample(
                    self.recording['person_id'], img, face_bbox
                )
                
                if success:
                    print(f"✓ {message}")
                    self.recording['samples'] += 1
                    self.recording['last_sample_time'] = current_time
                    
                    # 检查是否完成
                    if self.recording['samples'] >= self.recording['max_samples']:
                        print(f"✓ 记录完成: {self.recording['name']}")
                        self.recording['active'] = False
                        self._show_system_info()
                else:
                    print(f"✗ {message}")
    
    def _clear_all_records(self):
        """
        清除所有记录
        """
        persons = self.recognizer.get_registered_persons()
        
        if not persons:
            print("没有记录需要清除")
            return
        
        print(f"清除 {len(persons)} 个人物记录...")
        
        for person_id in list(persons.keys()):
            success, message = self.recognizer.delete_person(person_id)
            if success:
                print(f"✓ 已删除: {message}")
            else:
                print(f"✗ 删除失败: {message}")
        
        print("所有记录已清除")
        self._show_system_info()
    
    def _update_fps(self):
        """
        更新FPS计算
        """
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def run(self):
        """
        运行主循环
        """
        print("启动按键控制界面...")
        print("注意: 当前使用模拟按键进行演示")
        print("实际使用时需要连接物理按键到GPIO引脚")
        print()
        
        try:
            while not app.need_exit():
                # 读取摄像头
                img = self.cam.read()
                if img is None:
                    continue
                
                self.frame_count += 1
                
                # 处理检测
                detections = self._process_detections(img)
                
                # 读取按键
                button_events = self._read_buttons()
                
                # 处理按键事件
                if button_events['record']:
                    self._handle_record_button(button_events['record'], detections)
                
                if button_events['clear']:
                    self._handle_clear_button(button_events['clear'])
                
                # 处理记录过程
                if self.recording['active']:
                    self._process_recording(img, detections)
                
                # 绘制界面
                self._draw_ui(img)
                
                # 显示画面
                self.disp.show(img)
                
                # 更新FPS
                self._update_fps()
                
                # 控制帧率
                time.sleep_ms(33)  # 约30FPS
        
        except KeyboardInterrupt:
            print("\n程序被用户中断")
        except Exception as e:
            print(f"程序运行错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("清理资源...")
            self.cam.close()
            print("程序结束")

def main():
    """
    主函数
    """
    print("启动按键控制摄像头GUI")
    
    # 检查硬件连接（可选）
    print("检查硬件连接...")
    print("注意: 请确保按键正确连接到GPIO引脚")
    
    # 运行GUI
    gui = ButtonCameraGUI()
    gui.run()

if __name__ == "__main__":
    main()
