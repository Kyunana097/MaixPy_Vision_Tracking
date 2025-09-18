#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版实时摄像头界面
支持按键记录和清除人脸功能
"""

import sys
import os
import time
from maix import camera, display, app, image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.recognition.face_recognition import PersonRecognizer
from src.vision.detection.person_detector import PersonDetector

class SimpleCameraGUI:
    """
    简化的摄像头GUI
    """
    
    def __init__(self):
        """
        初始化
        """
        # 摄像头设置
        self.cam = camera.Camera(512, 320)
        self.disp = display.Display()
        
        # 检测和识别
        self.detector = PersonDetector(camera_width=512, camera_height=320)
        self.recognizer = PersonRecognizer()
        
        # 状态控制
        self.recording_mode = False
        self.recording_name = ""
        self.recording_samples = 0
        self.max_samples = 3
        self.current_person_id = None
        
        # 计数器
        self.frame_count = 0
        self.auto_record_timer = 0
        self.last_operation_time = 0
        
        print("=== 简化摄像头界面 ===")
        print("功能说明:")
        print("  1. 实时显示摄像头画面")
        print("  2. 自动检测和识别人脸")
        print("  3. 按键控制记录和清除")
        print()
        self._show_status()
    
    def _show_status(self):
        """
        显示当前状态
        """
        status = self.recognizer.get_status_info()
        print(f"当前状态: {status['registered_count']}/{status['max_persons']} 人已注册")
        
        if status['registered_persons']:
            print("已注册人物:")
            for person_id in status['registered_persons']:
                person_info = self.recognizer.registered_persons[person_id]
                print(f"  - {person_info['name']}")
        print()
    
    def _draw_interface(self, img):
        """
        绘制界面元素
        
        Args:
            img: 图像对象
        """
        try:
            # 标题
            title = "人脸识别系统"
            img.draw_string(10, 10, title, color=image.Color.from_rgb(255, 255, 255))
            
            # 状态信息
            status = self.recognizer.get_status_info()
            status_text = f"已注册: {status['registered_count']}/{status['max_persons']}"
            img.draw_string(10, 30, status_text, color=image.Color.from_rgb(0, 255, 255))
            
            # 模式显示
            if self.recording_mode:
                mode_text = f"记录模式: {self.recording_name} ({self.recording_samples}/{self.max_samples})"
                mode_color = image.Color.from_rgb(255, 255, 0)
            else:
                mode_text = "实时模式"
                mode_color = image.Color.from_rgb(0, 255, 0)
            
            img.draw_string(10, 50, mode_text, color=mode_color)
            
            # 操作提示
            if not self.recording_mode:
                hint = "操作: R-记录 C-清除 Q-退出"
            else:
                hint = "正在记录... X-取消"
            
            img.draw_string(10, 280, hint, color=image.Color.from_rgb(255, 255, 0))
            
            # 帧计数
            frame_text = f"帧: {self.frame_count}"
            img.draw_string(10, 300, frame_text, color=image.Color.from_rgb(128, 128, 128))
            
        except Exception as e:
            print(f"界面绘制错误: {e}")
    
    def _process_detections(self, img):
        """
        处理人脸检测
        
        Args:
            img: 图像对象
            
        Returns:
            tuple: (处理后的图像, 检测结果列表)
        """
        detections = self.detector.detect_persons(img)
        
        if detections:
            for detection in detections:
                bbox = detection['bbox']
                face_bbox = detection.get('face_bbox')
                x, y, w, h = bbox
                
                # 根据模式选择框颜色
                if self.recording_mode:
                    box_color = image.Color.from_rgb(255, 255, 0)  # 黄色 - 记录中
                else:
                    box_color = image.Color.from_rgb(0, 255, 0)    # 绿色 - 正常检测
                
                # 绘制人体框
                try:
                    img.draw_rect(x, y, w, h, color=box_color, thickness=2)
                except:
                    pass
                
                # 绘制人脸框
                if face_bbox:
                    fx, fy, fw, fh = face_bbox
                    try:
                        img.draw_rect(fx, fy, fw, fh, color=image.Color.from_rgb(0, 255, 255), thickness=1)
                    except:
                        pass
                    
                    # 在非记录模式下尝试识别
                    if not self.recording_mode:
                        person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                        
                        if person_id:
                            # 已知人物 - 红色标注
                            name_text = f"{person_name} ({confidence:.2f})"
                            text_color = image.Color.from_rgb(255, 0, 0)
                        else:
                            # 未知人物 - 白色标注
                            name_text = f"未知 ({confidence:.2f})"
                            text_color = image.Color.from_rgb(255, 255, 255)
                        
                        try:
                            img.draw_string(x, y - 20, name_text, color=text_color)
                        except:
                            pass
        
        return img, detections
    
    def _handle_recording(self, img, detections):
        """
        处理记录过程
        
        Args:
            img: 图像对象
            detections: 检测结果
        """
        if not self.recording_mode or not detections:
            return
        
        # 自动记录定时器（每1秒记录一次）
        current_time = time.time()
        if current_time - self.auto_record_timer < 1.0:
            return
        
        # 使用第一个检测结果
        detection = detections[0]
        face_bbox = detection.get('face_bbox')
        
        if face_bbox:
            if self.recording_samples == 0:
                # 第一次记录 - 注册新人物
                success, person_id, message = self.recognizer.register_person(
                    img, self.recording_name, face_bbox
                )
                
                if success:
                    print(f"✓ {message}")
                    self.current_person_id = person_id
                    self.recording_samples = 1
                    self.auto_record_timer = current_time
                else:
                    print(f"✗ {message}")
                    self._stop_recording()
            
            elif self.recording_samples < self.max_samples:
                # 添加更多样本
                success, message = self.recognizer.add_person_sample(
                    self.current_person_id, img, face_bbox
                )
                
                if success:
                    print(f"✓ {message}")
                    self.recording_samples += 1
                    self.auto_record_timer = current_time
                    
                    # 检查是否完成
                    if self.recording_samples >= self.max_samples:
                        print(f"✓ 记录完成: {self.recording_name}")
                        self._stop_recording()
                        self._show_status()
                else:
                    print(f"✗ {message}")
    
    def _start_recording(self):
        """
        开始记录模式
        """
        # 检查是否还有空位
        status = self.recognizer.get_status_info()
        if status['available_slots'] <= 0:
            print("✗ 已达到最大人数限制，无法记录新人物")
            return False
        
        # 生成新的人物名称
        person_count = status['registered_count']
        self.recording_name = f"人物{person_count + 1}"
        
        self.recording_mode = True
        self.recording_samples = 0
        self.auto_record_timer = time.time()
        
        print(f"开始记录: {self.recording_name}")
        print("请保持人脸在画面中...")
        return True
    
    def _stop_recording(self):
        """
        停止记录模式
        """
        self.recording_mode = False
        self.recording_name = ""
        self.recording_samples = 0
        self.current_person_id = None
        print("记录模式已停止")
    
    def _clear_all_records(self):
        """
        清除所有记录
        """
        persons = self.recognizer.get_registered_persons()
        
        if not persons:
            print("没有记录需要清除")
            return
        
        print(f"清除 {len(persons)} 个人物记录...")
        
        success_count = 0
        for person_id in list(persons.keys()):
            success, message = self.recognizer.delete_person(person_id)
            if success:
                success_count += 1
                print(f"✓ 已删除: {message}")
            else:
                print(f"✗ 删除失败: {message}")
        
        print(f"清除完成，共删除 {success_count} 个记录")
        self._show_status()
    
    def _check_keyboard_input(self):
        """
        检查键盘输入（模拟按键）
        这里使用简单的时间间隔来模拟不同的操作
        在实际应用中应该使用真实的按键检测
        
        Returns:
            str: 操作类型 ('record', 'clear', 'cancel', 'quit', None)
        """
        current_time = time.time()
        
        # 防止过于频繁的操作
        if current_time - self.last_operation_time < 2.0:
            return None
        
        # 这里可以根据实际的按键API进行修改
        # 目前使用简单的循环计数来模拟不同操作
        
        # 每10秒循环一次演示操作
        cycle_time = int(current_time) % 20
        
        if cycle_time == 0:
            # 模拟记录操作
            return 'record'
        elif cycle_time == 10:
            # 模拟清除操作（仅当有记录时）
            if self.recognizer.get_registered_persons():
                return 'clear'
        
        # 检查程序退出
        if app.need_exit():
            return 'quit'
        
        return None
    
    def run(self):
        """
        运行主循环
        """
        print("启动实时摄像头...")
        print("操作说明:")
        print("  - 程序会自动演示记录和清除操作")
        print("  - 在实际应用中可以连接真实按键")
        print("  - 按Ctrl+C或设备按键退出")
        print()
        
        try:
            start_time = time.time()
            
            while True:
                # 读取摄像头
                img = self.cam.read()
                if img is None:
                    continue
                
                self.frame_count += 1
                
                # 处理检测
                img, detections = self._process_detections(img)
                
                # 处理记录
                if self.recording_mode:
                    self._handle_recording(img, detections)
                
                # 绘制界面
                self._draw_interface(img)
                
                # 检查输入（模拟按键）
                key_action = self._check_keyboard_input()
                
                if key_action == 'quit':
                    print("退出程序")
                    break
                elif key_action == 'record' and not self.recording_mode:
                    if detections:
                        self._start_recording()
                        self.last_operation_time = time.time()
                    else:
                        print("未检测到人脸，无法开始记录")
                elif key_action == 'clear':
                    self._clear_all_records()
                    self.last_operation_time = time.time()
                elif key_action == 'cancel' and self.recording_mode:
                    self._stop_recording()
                    self.last_operation_time = time.time()
                
                # 显示画面
                self.disp.show(img)
                
                # 控制帧率
                time.sleep_ms(33)  # 约30FPS
                
                # 定期显示统计
                if self.frame_count % 90 == 0:  # 每3秒
                    elapsed = time.time() - start_time
                    fps = self.frame_count / elapsed
                    print(f"运行状态: 帧数={self.frame_count}, FPS={fps:.1f}")
        
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

# 为了支持真实按键，这里提供一个按键处理的示例框架
class ButtonHandler:
    """
    按键处理器（示例）
    """
    
    def __init__(self):
        """
        初始化按键处理
        """
        self.last_press_time = 0
        self.press_cooldown = 0.5
    
    def check_buttons(self):
        """
        检查按键状态
        
        Returns:
            str: 按键操作类型
        """
        current_time = time.time()
        
        # 防抖处理
        if current_time - self.last_press_time < self.press_cooldown:
            return None
        
        # 这里需要根据实际的MaixPy按键API进行实现
        # 示例代码：
        
        try:
            # 假设的按键检测代码
            # if some_button_api.is_pressed('record'):
            #     self.last_press_time = current_time
            #     return 'record'
            # 
            # if some_button_api.is_pressed('clear'):
            #     self.last_press_time = current_time
            #     return 'clear'
            
            pass
        except:
            pass
        
        return None

def main():
    """
    主函数
    """
    print("启动简化摄像头GUI")
    
    # 运行GUI
    gui = SimpleCameraGUI()
    gui.run()

if __name__ == "__main__":
    main()
