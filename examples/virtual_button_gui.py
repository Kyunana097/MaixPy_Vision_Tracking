#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟按键摄像头界面
在屏幕上显示虚拟按键，使用简单的区域检测
"""

import sys
import os
import time
from maix import camera, display, app, image

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

# 尝试多种导入方式
try:
    from src.vision.recognition.face_recognition import PersonRecognizer
    from src.vision.detection.person_detector import PersonDetector
    print("✓ 从src目录导入模块成功")
except ImportError:
    try:
        # 尝试直接从当前目录导入
        sys.path.insert(0, os.path.join(project_root, 'src', 'vision', 'recognition'))
        sys.path.insert(0, os.path.join(project_root, 'src', 'vision', 'detection'))
        from face_recognition import PersonRecognizer
        from person_detector import PersonDetector
        print("✓ 从直接路径导入模块成功")
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        print("当前工作目录:", os.getcwd())
        print("项目根目录:", project_root)
        print("Python路径:", sys.path[:3])
        
        # 创建简化版本以便测试
        print("使用简化版本运行...")
        
        class PersonRecognizer:
            def __init__(self):
                self.registered_persons = {}
                self.features_database = {}
                self.target_person_id = None
                self.max_persons = 3
                self.similarity_threshold = 0.85
                
            def get_status_info(self):
                return {
                    'max_persons': self.max_persons,
                    'registered_count': len(self.registered_persons),
                    'available_slots': self.max_persons - len(self.registered_persons),
                    'similarity_threshold': self.similarity_threshold,
                    'has_face_detector': False,
                    'target_person': None,
                    'registered_persons': list(self.registered_persons.keys())
                }
            
            def register_person(self, img, person_name, bbox=None):
                person_id = f"person_{len(self.registered_persons) + 1:02d}"
                self.registered_persons[person_id] = {
                    'name': person_name,
                    'id': person_id,
                    'feature_count': 1
                }
                return True, person_id, f"成功注册人物: {person_name}"
            
            def add_person_sample(self, person_id, img, bbox=None):
                if person_id in self.registered_persons:
                    self.registered_persons[person_id]['feature_count'] += 1
                    return True, "成功添加样本"
                return False, "人物ID不存在"
            
            def recognize_person(self, img, bbox=None):
                return None, 0.0, "未知"
            
            def delete_person(self, person_id):
                if person_id in self.registered_persons:
                    person_name = self.registered_persons[person_id]['name']
                    del self.registered_persons[person_id]
                    return True, f"成功删除人物: {person_name}"
                return False, "人物ID不存在"
            
            def get_registered_persons(self):
                return self.registered_persons.copy()
        
        class PersonDetector:
            def __init__(self, camera_width=512, camera_height=320):
                self.has_face_detector = False
                
            def detect_persons(self, img):
                # 模拟检测结果
                import random
                if random.random() > 0.3:  # 70%概率检测到人脸
                    return [{
                        'bbox': (100, 100, 80, 120),
                        'face_bbox': (110, 110, 60, 80),
                        'confidence': 0.9,
                        'type': 'upper_body'
                    }]
                return []

class VirtualButtonGUI:
    """
    虚拟按键摄像头界面
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
        self.cam = camera.Camera(width, height)
        self.disp = display.Display()
        
        # 功能模块
        self.detector = PersonDetector(camera_width=width, camera_height=height)
        self.recognizer = PersonRecognizer()
        
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
            'sample_interval': 1.5  # 1.5秒采样间隔
        }
        
        # 界面状态
        self.frame_count = 0
        self.click_cooldown = 0.5  # 点击冷却时间
        
        # 模拟点击演示
        self.demo_mode = True
        self.demo_timer_start = time.time()
        self.demo_sequence = [
            {'time': 3, 'button': 'record', 'description': '模拟点击记录按键'},
            {'time': 8, 'button': 'record', 'description': '模拟取消记录'},
            {'time': 12, 'button': 'record', 'description': '再次记录'},
            {'time': 20, 'button': 'clear', 'description': '模拟清除记录'}
        ]
        self.last_demo_action = 0
        
        print("=== 虚拟按键摄像头界面 ===")
        print("功能特点:")
        print("  - 屏幕右下角显示虚拟按键")
        print("  - 自动演示点击功能")
        print("  - 实时人脸检测和识别")
        print()
        
        self._show_system_status()
    
    def _show_system_status(self):
        """
        显示系统状态
        """
        status = self.recognizer.get_status_info()
        print("系统状态:")
        print(f"  已注册人物: {status['registered_count']}/{status['max_persons']}")
        
        if status['registered_persons']:
            print("  人物列表:")
            for person_id in status['registered_persons']:
                info = self.recognizer.registered_persons[person_id]
                print(f"    {info['name']} (样本数: {info['feature_count']})")
        else:
            print("  暂无已注册人物")
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
                        color = image.Color.from_rgb(255, 255, 0)  # 亮黄色 - 激活状态
                    else:
                        color = image.Color.from_rgb(200, 150, 0)  # 暗黄色 - 记录中
                    text = '取消'
                else:
                    if button['active']:
                        color = image.Color.from_rgb(0, 255, 0)    # 亮绿色 - 激活状态
                    else:
                        color = image.Color.from_rgb(0, 150, 0)    # 暗绿色 - 正常状态
                    text = '记录'
            
            elif button_name == 'clear':
                if button['enabled']:
                    if button['active']:
                        color = image.Color.from_rgb(255, 0, 0)    # 亮红色 - 激活状态
                    else:
                        color = image.Color.from_rgb(150, 0, 0)    # 暗红色 - 正常状态
                else:
                    color = image.Color.from_rgb(80, 80, 80)       # 灰色 - 禁用状态
                text = '清除'
            
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
                
                # 如果按键被点击，添加点击效果
                if button['active']:
                    # 绘制内边框显示点击效果
                    inner_color = image.Color.from_rgb(255, 255, 255)
                    img.draw_rect(x + 2, y + 2, w - 4, h - 4, 
                                color=inner_color, thickness=1)
            
            except Exception as e:
                print(f"绘制按键错误: {e}")
    
    def _draw_ui_info(self, img):
        """
        绘制界面信息
        
        Args:
            img: 图像对象
        """
        try:
            # 半透明背景（信息区域）
            info_bg_color = image.Color.from_rgb(0, 0, 0)
            
            # 主标题
            title = "虚拟按键人脸识别"
            img.draw_string(10, 10, title, 
                          color=image.Color.from_rgb(255, 255, 255), scale=1.2)
            
            # 系统状态
            status = self.recognizer.get_status_info()
            status_text = f"注册: {status['registered_count']}/{status['max_persons']}"
            img.draw_string(10, 35, status_text, 
                          color=image.Color.from_rgb(0, 255, 255))
            
            # 当前模式
            if self.recording['active']:
                mode_text = f"记录中: {self.recording['name']} ({self.recording['samples']}/{self.recording['max_samples']})"
                mode_color = image.Color.from_rgb(255, 255, 0)
            else:
                mode_text = "实时检测模式"
                mode_color = image.Color.from_rgb(0, 255, 0)
            
            img.draw_string(10, 55, mode_text, color=mode_color)
            
            # 演示信息
            if self.demo_mode:
                demo_elapsed = time.time() - self.demo_timer_start
                demo_text = f"演示模式 - 运行时间: {demo_elapsed:.1f}s"
                img.draw_string(10, 75, demo_text, 
                              color=image.Color.from_rgb(255, 165, 0))
            
            # 操作提示（底部左侧）
            help_y = self.height - 80
            img.draw_string(10, help_y, "虚拟按键:", 
                          color=image.Color.from_rgb(255, 255, 255))
            img.draw_string(10, help_y + 20, "绿色=记录人脸", 
                          color=image.Color.from_rgb(0, 255, 0))
            img.draw_string(10, help_y + 40, "红色=清除记录", 
                          color=image.Color.from_rgb(255, 0, 0))
            
        except Exception as e:
            print(f"UI信息绘制错误: {e}")
    
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
                    box_color = image.Color.from_rgb(255, 255, 0)  # 黄色 - 记录中
                    thickness = 3
                else:
                    box_color = image.Color.from_rgb(0, 255, 0)    # 绿色 - 正常检测
                    thickness = 2
                
                # 绘制人体检测框
                try:
                    img.draw_rect(x, y, w, h, color=box_color, thickness=thickness)
                    
                    # 绘制人脸框
                    if face_bbox:
                        fx, fy, fw, fh = face_bbox
                        face_color = image.Color.from_rgb(0, 255, 255)
                        img.draw_rect(fx, fy, fw, fh, color=face_color, thickness=1)
                except:
                    pass
                
                # 识别并标注（非记录模式）
                if face_bbox and not self.recording['active']:
                    person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                    
                    if person_id:
                        # 已知人物 - 红色标注
                        label = f"{person_name} ({confidence:.2f})"
                        label_color = image.Color.from_rgb(255, 0, 0)
                    else:
                        # 未知人物 - 白色标注
                        label = f"未知 ({confidence:.2f})"
                        label_color = image.Color.from_rgb(255, 255, 255)
                    
                    try:
                        img.draw_string(x, y - 20, label, color=label_color)
                    except:
                        pass
        
        return detections
    
    def _simulate_button_click(self):
        """
        模拟按键点击（演示模式）
        
        Returns:
            str: 被点击的按键名称，如果没有则返回None
        """
        if not self.demo_mode:
            return None
        
        current_time = time.time()
        demo_elapsed = current_time - self.demo_timer_start
        
        # 检查演示序列
        for i, action in enumerate(self.demo_sequence):
            if (i > self.last_demo_action and 
                demo_elapsed >= action['time'] and 
                demo_elapsed < action['time'] + 0.5):  # 0.5秒点击窗口
                
                self.last_demo_action = i
                print(f"演示: {action['description']}")
                return action['button']
        
        # 循环演示
        if demo_elapsed > 25:  # 25秒后重新开始
            self.demo_timer_start = current_time
            self.last_demo_action = 0
        
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
                        print("✓ 开始记录新人物")
                    else:
                        print("✗ 已达到最大人数限制")
                else:
                    print("✗ 未检测到人脸，无法开始记录")
            else:
                # 取消记录
                self._cancel_recording()
                print("✓ 已取消记录")
        
        elif button_name == 'clear':
            if button['enabled']:
                self._clear_all_records()
                print("✓ 已清除所有记录")
    
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
                # 第一次记录 - 注册新人物
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
                        self._show_system_status()
                else:
                    print(f"✗ 添加样本失败: {message}")
    
    def _clear_all_records(self):
        """
        清除所有记录
        """
        persons = self.recognizer.get_registered_persons()
        
        if not persons:
            print("没有记录需要清除")
            return
        
        deleted_count = 0
        for person_id in list(persons.keys()):
            success, message = self.recognizer.delete_person(person_id)
            if success:
                deleted_count += 1
                print(f"✓ 已删除: {message}")
            else:
                print(f"✗ 删除失败: {message}")
        
        print(f"清除完成，共删除 {deleted_count} 个记录")
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
        print("启动虚拟按键界面...")
        print("界面布局:")
        print("  - 左侧: 摄像头画面 + 检测结果")
        print("  - 右下角: 虚拟按键 (记录/清除)")
        print("  - 自动演示: 每25秒循环一次")
        print()
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
                
                # 模拟按键点击（演示模式）
                clicked_button = self._simulate_button_click()
                if clicked_button:
                    self._handle_button_click(clicked_button, detections)
                
                # 处理记录过程
                if self.recording['active']:
                    self._process_recording(img, detections)
                
                # 绘制界面
                self._draw_ui_info(img)
                self._draw_virtual_buttons(img)
                
                # 显示画面
                self.disp.show(img)
                
                # 控制帧率
                time.sleep(0.033)  # 约30FPS
        
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
    # 解析命令行参数
    width, height = 512, 320
    
    if len(sys.argv) > 1:
        try:
            width = int(sys.argv[1])
            if len(sys.argv) > 2:
                height = int(sys.argv[2])
        except ValueError:
            print("无效的分辨率参数，使用默认值 512x320")
    
    print(f"启动虚拟按键摄像头GUI - 分辨率: {width}x{height}")
    
    # 创建并运行GUI
    gui = VirtualButtonGUI(width, height)
    gui.run()

if __name__ == "__main__":
    main()
