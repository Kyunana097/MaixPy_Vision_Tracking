#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
触摸屏虚拟按键摄像头界面
在屏幕上显示虚拟按键，支持触摸操作
"""

import sys
import os
import time
from maix import camera, display, app, image, touchscreen

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.recognition.face_recognition import PersonRecognizer
from src.vision.detection.person_detector import PersonDetector

class TouchscreenCameraGUI:
    """
    触摸屏虚拟按键摄像头界面
    """
    
    def __init__(self):
        """
        初始化界面
        """
        # 硬件初始化
        self.cam = camera.Camera(512, 320)
        self.disp = display.Display()
        
        # 尝试初始化触摸屏
        try:
            self.touch = touchscreen.TouchScreen()
            self.has_touchscreen = True
            print("✓ 触摸屏初始化成功")
        except Exception as e:
            print(f"✗ 触摸屏初始化失败: {e}")
            print("将使用模拟触摸进行演示")
            self.touch = None
            self.has_touchscreen = False
        
        # 功能模块
        self.detector = PersonDetector(camera_width=512, camera_height=320)
        self.recognizer = PersonRecognizer()
        
        # 虚拟按键配置
        self.buttons = {
            'record': {
                'x': 400, 'y': 250, 'w': 100, 'h': 40,
                'text': '记录',
                'color_normal': image.Color.from_rgb(0, 150, 0),
                'color_pressed': image.Color.from_rgb(0, 255, 0),
                'color_disabled': image.Color.from_rgb(100, 100, 100),
                'text_color': image.Color.from_rgb(255, 255, 255),
                'pressed': False,
                'enabled': True
            },
            'clear': {
                'x': 400, 'y': 300, 'w': 100, 'h': 40,
                'text': '清除',
                'color_normal': image.Color.from_rgb(150, 0, 0),
                'color_pressed': image.Color.from_rgb(255, 0, 0),
                'color_disabled': image.Color.from_rgb(100, 100, 100),
                'text_color': image.Color.from_rgb(255, 255, 255),
                'pressed': False,
                'enabled': True
            }
        }
        
        # 触摸状态
        self.touch_state = {
            'last_touch_time': 0,
            'touch_cooldown': 0.3,
            'current_touch': None,
            'touch_start_time': 0
        }
        
        # 记录状态
        self.recording = {
            'active': False,
            'name': '',
            'samples': 0,
            'max_samples': 3,
            'person_id': None,
            'last_sample_time': 0,
            'auto_sample_interval': 1.0
        }
        
        # 界面状态
        self.frame_count = 0
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # 模拟触摸演示（当没有真实触摸屏时）
        self.demo_mode = not self.has_touchscreen
        self.demo_timer = 0
        self.demo_cycle = 15  # 15秒循环演示
        
        print("=== 触摸屏虚拟按键界面 ===")
        print("功能:")
        print("  - 实时摄像头显示")
        print("  - 屏幕虚拟按键")
        print("  - 触摸操作支持")
        
        if self.demo_mode:
            print("  - 自动演示模式（无触摸屏）")
        
        print()
        self._show_system_info()
    
    def _show_system_info(self):
        """
        显示系统信息
        """
        status = self.recognizer.get_status_info()
        print("系统状态:")
        print(f"  触摸屏: {'✓' if self.has_touchscreen else '✗ (演示模式)'}")
        print(f"  检测器: {'✓' if self.detector.has_face_detector else '✗'}")
        print(f"  识别器: {'✓' if status['has_face_detector'] else '✗'}")
        print(f"  已注册: {status['registered_count']}/{status['max_persons']}")
        
        if status['registered_persons']:
            print("  已注册人物:")
            for person_id in status['registered_persons']:
                info = self.recognizer.registered_persons[person_id]
                print(f"    {info['name']} (样本: {info['feature_count']})")
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
            if not button['enabled']:
                color = button['color_disabled']
            elif button['pressed']:
                color = button['color_pressed']
            else:
                color = button['color_normal']
            
            try:
                # 绘制按键背景
                img.draw_rect(x, y, w, h, color=color, thickness=-1)
                
                # 绘制按键边框
                border_color = image.Color.from_rgb(255, 255, 255)
                img.draw_rect(x, y, w, h, color=border_color, thickness=2)
                
                # 绘制按键文字
                text_x = x + (w - len(button['text']) * 8) // 2
                text_y = y + (h - 16) // 2
                img.draw_string(text_x, text_y, button['text'], 
                              color=button['text_color'], scale=1.5)
                
                # 如果按键被禁用，添加禁用标记
                if not button['enabled']:
                    img.draw_line(x, y, x + w, y + h, 
                                color=image.Color.from_rgb(255, 0, 0), thickness=3)
                    img.draw_line(x + w, y, x, y + h, 
                                color=image.Color.from_rgb(255, 0, 0), thickness=3)
            
            except Exception as e:
                print(f"绘制按键 {button_name} 错误: {e}")
    
    def _draw_ui_info(self, img):
        """
        绘制界面信息
        
        Args:
            img: 图像对象
        """
        try:
            # 主标题
            title = "触摸屏人脸识别"
            img.draw_string(10, 10, title, 
                          color=image.Color.from_rgb(255, 255, 255), scale=1.2)
            
            # 系统状态
            status = self.recognizer.get_status_info()
            status_text = f"人物: {status['registered_count']}/{status['max_persons']}"
            img.draw_string(10, 35, status_text, 
                          color=image.Color.from_rgb(0, 255, 255))
            
            # 当前模式
            if self.recording['active']:
                mode_text = f"记录: {self.recording['name']} ({self.recording['samples']}/{self.recording['max_samples']})"
                mode_color = image.Color.from_rgb(255, 255, 0)
            else:
                mode_text = "实时模式"
                mode_color = image.Color.from_rgb(0, 255, 0)
            
            img.draw_string(10, 55, mode_text, color=mode_color)
            
            # FPS显示
            fps_text = f"FPS: {self.current_fps:.1f}"
            img.draw_string(10, 75, fps_text, 
                          color=image.Color.from_rgb(128, 128, 128))
            
            # 触摸状态（演示模式）
            if self.demo_mode:
                demo_text = "演示模式 - 自动触摸"
                img.draw_string(10, 95, demo_text, 
                              color=image.Color.from_rgb(255, 165, 0))
            
            # 操作说明
            help_y = 200
            img.draw_string(10, help_y, "操作说明:", 
                          color=image.Color.from_rgb(255, 255, 255))
            img.draw_string(10, help_y + 20, "点击右侧按键进行操作", 
                          color=image.Color.from_rgb(255, 255, 0))
            
            if self.demo_mode:
                img.draw_string(10, help_y + 40, "当前为演示模式", 
                              color=image.Color.from_rgb(255, 165, 0))
        
        except Exception as e:
            print(f"UI信息绘制错误: {e}")
    
    def _process_detections(self, img):
        """
        处理人脸检测并绘制
        
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
                else:
                    box_color = image.Color.from_rgb(0, 255, 0)    # 绿色 - 正常
                
                # 绘制检测框
                try:
                    img.draw_rect(x, y, w, h, color=box_color, thickness=2)
                    
                    # 绘制人脸框
                    if face_bbox:
                        fx, fy, fw, fh = face_bbox
                        img.draw_rect(fx, fy, fw, fh, 
                                    color=image.Color.from_rgb(0, 255, 255), thickness=1)
                except:
                    pass
                
                # 识别和标注（非记录模式）
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
    
    def _check_touch_input(self):
        """
        检查触摸输入
        
        Returns:
            str: 触摸的按键名称，如果没有则返回None
        """
        current_time = time.time()
        
        # 触摸冷却检查
        if current_time - self.touch_state['last_touch_time'] < self.touch_state['touch_cooldown']:
            return None
        
        touch_x, touch_y = None, None
        
        if self.has_touchscreen:
            # 真实触摸屏输入
            try:
                touch_data = self.touch.read()
                if touch_data and len(touch_data) > 0:
                    # 获取第一个触摸点
                    touch_point = touch_data[0]
                    if hasattr(touch_point, 'x') and hasattr(touch_point, 'y'):
                        touch_x, touch_y = touch_point.x, touch_point.y
                    elif isinstance(touch_point, (list, tuple)) and len(touch_point) >= 2:
                        touch_x, touch_y = touch_point[0], touch_point[1]
            except Exception as e:
                print(f"触摸屏读取错误: {e}")
        
        elif self.demo_mode:
            # 演示模式 - 模拟触摸
            touch_x, touch_y = self._simulate_touch(current_time)
        
        # 检查触摸是否在按键区域内
        if touch_x is not None and touch_y is not None:
            for button_name, button in self.buttons.items():
                if (button['enabled'] and 
                    button['x'] <= touch_x <= button['x'] + button['w'] and
                    button['y'] <= touch_y <= button['y'] + button['h']):
                    
                    self.touch_state['last_touch_time'] = current_time
                    return button_name
        
        return None
    
    def _simulate_touch(self, current_time):
        """
        模拟触摸输入（演示模式）
        
        Args:
            current_time: 当前时间
            
        Returns:
            tuple: (x, y) 触摸坐标，如果没有触摸返回 (None, None)
        """
        # 基于时间循环模拟触摸
        cycle_position = (current_time % self.demo_cycle) / self.demo_cycle
        
        if 0.1 <= cycle_position <= 0.15:
            # 模拟点击记录按键
            button = self.buttons['record']
            return button['x'] + button['w']//2, button['y'] + button['h']//2
        
        elif 0.6 <= cycle_position <= 0.65:
            # 模拟点击清除按键（仅当有记录时）
            if self.recognizer.get_registered_persons():
                button = self.buttons['clear']
                return button['x'] + button['w']//2, button['y'] + button['h']//2
        
        return None, None
    
    def _handle_button_press(self, button_name, detections):
        """
        处理按键点击
        
        Args:
            button_name: 按键名称
            detections: 当前检测结果
        """
        current_time = time.time()
        
        if button_name == 'record':
            if not self.recording['active']:
                # 开始记录
                if detections:
                    # 检查是否还有空位
                    status = self.recognizer.get_status_info()
                    if status['available_slots'] > 0:
                        self._start_recording()
                        print("开始记录新人物")
                    else:
                        print("✗ 已达到最大人数限制")
                else:
                    print("✗ 未检测到人脸，无法开始记录")
            else:
                # 取消记录
                self._cancel_recording()
                print("取消记录")
        
        elif button_name == 'clear':
            # 清除所有记录
            self._clear_all_records()
        
        # 设置按键按下效果
        self.buttons[button_name]['pressed'] = True
        # 0.2秒后恢复按键状态
        self._schedule_button_release(button_name, current_time + 0.2)
    
    def _schedule_button_release(self, button_name, release_time):
        """
        计划按键释放（简化实现）
        
        Args:
            button_name: 按键名称
            release_time: 释放时间
        """
        # 这里使用简单的标记，在主循环中检查
        self.buttons[button_name]['release_time'] = release_time
    
    def _update_button_states(self):
        """
        更新按键状态
        """
        current_time = time.time()
        
        for button_name, button in self.buttons.items():
            # 检查按键释放
            if button['pressed'] and 'release_time' in button:
                if current_time >= button['release_time']:
                    button['pressed'] = False
                    del button['release_time']
            
            # 更新按键可用状态
            if button_name == 'record':
                # 记录按键在记录模式下显示为不同状态
                button['enabled'] = True
                if self.recording['active']:
                    button['text'] = '取消'
                    button['color_normal'] = image.Color.from_rgb(150, 100, 0)
                else:
                    button['text'] = '记录'
                    button['color_normal'] = image.Color.from_rgb(0, 150, 0)
            
            elif button_name == 'clear':
                # 清除按键只在有记录时可用
                has_records = len(self.recognizer.get_registered_persons()) > 0
                button['enabled'] = has_records
    
    def _start_recording(self):
        """
        开始记录新人物
        """
        person_count = len(self.recognizer.get_registered_persons())
        
        self.recording.update({
            'active': True,
            'name': f"人物{person_count + 1}",
            'samples': 0,
            'person_id': None,
            'last_sample_time': time.time()
        })
    
    def _cancel_recording(self):
        """
        取消记录
        """
        # 如果已经开始记录，删除部分数据
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
        
        # 控制采样频率
        if current_time - self.recording['last_sample_time'] < self.recording['auto_sample_interval']:
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
        print("启动触摸屏界面...")
        
        if self.demo_mode:
            print("演示模式运行中...")
            print(f"将每 {self.demo_cycle} 秒循环演示功能")
        else:
            print("触摸屏模式运行中...")
            print("请触摸屏幕上的虚拟按键进行操作")
        
        print("按 Ctrl+C 退出程序")
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
                
                # 检查触摸输入
                touched_button = self._check_touch_input()
                if touched_button:
                    self._handle_button_press(touched_button, detections)
                
                # 处理记录过程
                if self.recording['active']:
                    self._process_recording(img, detections)
                
                # 绘制界面元素
                self._draw_ui_info(img)
                self._draw_virtual_buttons(img)
                
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
            if self.touch:
                try:
                    self.touch.close()
                except:
                    pass
            print("程序结束")

def main():
    """
    主函数
    """
    print("启动触摸屏虚拟按键摄像头GUI")
    print("支持屏幕虚拟按键操作")
    
    # 创建并运行GUI
    gui = TouchscreenCameraGUI()
    gui.run()

if __name__ == "__main__":
    main()
