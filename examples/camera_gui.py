#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时摄像头GUI界面
支持人脸记录和清除功能
"""

import sys
import os
import time
from maix import camera, display, app, image, key

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.recognition.face_recognition import PersonRecognizer
from src.vision.detection.person_detector import PersonDetector

class CameraGUI:
    """
    摄像头GUI界面类
    """
    
    def __init__(self, width=512, height=320):
        """
        初始化GUI
        
        Args:
            width: 画面宽度
            height: 画面高度
        """
        self.width = width
        self.height = height
        
        # 初始化摄像头和显示
        self.cam = camera.Camera(width, height)
        self.disp = display.Display()
        
        # 初始化检测器和识别器
        self.detector = PersonDetector(camera_width=width, camera_height=height)
        self.recognizer = PersonRecognizer()
        
        # GUI状态
        self.current_mode = "live"  # live, record, confirm
        self.recording_person = None
        self.recording_name = ""
        self.recording_count = 0
        self.max_recording_samples = 3
        
        # 按键状态
        self.key_pressed = False
        self.last_key_time = 0
        self.key_cooldown = 0.5  # 按键冷却时间
        
        # 统计信息
        self.frame_count = 0
        self.detection_count = 0
        
        print("=== 实时摄像头GUI ===")
        print("功能:")
        print("  - 实时显示摄像头画面")
        print("  - 自动检测人脸并绘制绿框")
        print("  - 识别已注册人物并显示姓名")
        print()
        print("按键操作:")
        print("  USER按键 (短按) - 记录当前检测到的人脸")
        print("  USER按键 (长按) - 清除所有记录")
        print("  BOOT按键 - 退出程序")
        print()
        
        # 显示当前状态
        self._show_system_status()
    
    def _show_system_status(self):
        """
        显示系统状态
        """
        status = self.recognizer.get_status_info()
        print("当前状态:")
        print(f"  已注册人物: {status['registered_count']}/{status['max_persons']}")
        print(f"  可用槽位: {status['available_slots']}")
        
        if status['registered_persons']:
            print("  已注册人物:")
            for person_id in status['registered_persons']:
                person_info = self.recognizer.registered_persons[person_id]
                print(f"    {person_info['name']} (ID: {person_id})")
        
        print()
    
    def _draw_ui_elements(self, img):
        """
        绘制UI元素
        
        Args:
            img: 图像对象
        """
        try:
            # 绘制标题
            title = "实时人脸识别系统"
            img.draw_string(10, 10, title, color=image.Color.from_rgb(255, 255, 255), scale=1.5)
            
            # 绘制模式信息
            if self.current_mode == "live":
                mode_text = "实时模式"
                mode_color = image.Color.from_rgb(0, 255, 0)
            elif self.current_mode == "record":
                mode_text = f"记录模式 {self.recording_count}/{self.max_recording_samples}"
                mode_color = image.Color.from_rgb(255, 255, 0)
            elif self.current_mode == "confirm":
                mode_text = "确认模式"
                mode_color = image.Color.from_rgb(255, 165, 0)
            else:
                mode_text = "未知模式"
                mode_color = image.Color.from_rgb(255, 0, 0)
            
            img.draw_string(10, 35, mode_text, color=mode_color)
            
            # 绘制统计信息
            status = self.recognizer.get_status_info()
            stats_text = f"注册: {status['registered_count']}/{status['max_persons']}"
            img.draw_string(10, 55, stats_text, color=image.Color.from_rgb(0, 255, 255))
            
            # 绘制帧计数
            frame_text = f"帧: {self.frame_count}"
            img.draw_string(10, 75, frame_text, color=image.Color.from_rgb(128, 128, 128))
            
            # 绘制按键提示
            if self.current_mode == "live":
                hint1 = "USER键: 记录人脸"
                hint2 = "长按USER: 清除所有"
                hint3 = "BOOT键: 退出"
            elif self.current_mode == "record":
                hint1 = f"正在记录: {self.recording_name}"
                hint2 = "检测到人脸时自动记录"
                hint3 = "USER键: 取消记录"
            elif self.current_mode == "confirm":
                hint1 = "请输入姓名后按USER确认"
                hint2 = "或按BOOT取消"
                hint3 = ""
            else:
                hint1 = hint2 = hint3 = ""
            
            # 绘制提示文字（底部）
            y_offset = self.height - 60
            if hint1:
                img.draw_string(10, y_offset, hint1, color=image.Color.from_rgb(255, 255, 0))
            if hint2:
                img.draw_string(10, y_offset + 15, hint2, color=image.Color.from_rgb(255, 255, 0))
            if hint3:
                img.draw_string(10, y_offset + 30, hint3, color=image.Color.from_rgb(255, 255, 0))
                
        except Exception as e:
            print(f"UI绘制错误: {e}")
    
    def _handle_detections(self, img, detections):
        """
        处理检测结果
        
        Args:
            img: 图像对象
            detections: 检测结果列表
            
        Returns:
            processed_img: 处理后的图像
        """
        if not detections:
            return img
        
        for i, detection in enumerate(detections):
            bbox = detection['bbox']
            face_bbox = detection.get('face_bbox')
            x, y, w, h = bbox
            
            # 根据模式绘制不同颜色的框
            if self.current_mode == "live":
                # 实时模式：绿色框 + 识别结果
                box_color = image.Color.from_rgb(0, 255, 0)
                
                # 尝试识别人物
                if face_bbox:
                    person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                    
                    if person_id:
                        # 已知人物：红色框
                        box_color = image.Color.from_rgb(255, 0, 0)
                        name_text = f"{person_name} ({confidence:.2f})"
                    else:
                        # 未知人物：绿色框
                        name_text = f"未知 ({confidence:.2f})"
                    
                    try:
                        img.draw_string(x, y - 20, name_text, color=box_color)
                    except:
                        pass
                
            elif self.current_mode == "record":
                # 记录模式：黄色框
                box_color = image.Color.from_rgb(255, 255, 0)
                
                try:
                    record_text = f"记录中 {self.recording_count}/{self.max_recording_samples}"
                    img.draw_string(x, y - 20, record_text, color=box_color)
                except:
                    pass
            
            else:
                # 其他模式：白色框
                box_color = image.Color.from_rgb(255, 255, 255)
            
            # 绘制边界框
            try:
                img.draw_rect(x, y, w, h, color=box_color, thickness=2)
                
                # 如果有人脸框，也绘制出来（青色）
                if face_bbox:
                    fx, fy, fw, fh = face_bbox
                    img.draw_rect(fx, fy, fw, fh, color=image.Color.from_rgb(0, 255, 255), thickness=1)
                    
            except Exception as e:
                print(f"绘制检测框错误: {e}")
        
        return img
    
    def _check_keys(self):
        """
        检查按键状态
        
        Returns:
            str: 按键类型 ('user_short', 'user_long', 'boot', None)
        """
        current_time = time.time()
        
        # 按键冷却检查
        if current_time - self.last_key_time < self.key_cooldown:
            return None
        
        # 这里需要根据实际MaixPy的按键API进行调整
        # 由于MaixPy的按键API可能因版本而异，我提供一个通用的框架
        
        try:
            # 检查BOOT按键（退出）
            if hasattr(key, 'is_pressed'):
                if key.is_pressed(key.BOOT):
                    self.last_key_time = current_time
                    return 'boot'
                
                # 检查USER按键
                if key.is_pressed(key.USER):
                    if not self.key_pressed:
                        self.key_pressed = True
                        self.key_press_start = current_time
                    else:
                        # 检查长按（1秒以上）
                        if current_time - self.key_press_start > 1.0:
                            self.key_pressed = False
                            self.last_key_time = current_time
                            return 'user_long'
                else:
                    if self.key_pressed:
                        # 按键释放
                        self.key_pressed = False
                        press_duration = current_time - self.key_press_start
                        self.last_key_time = current_time
                        
                        if press_duration < 1.0:
                            return 'user_short'
            
            # 备用方案：使用app.need_exit()检测退出
            if app.need_exit():
                return 'boot'
                
        except Exception as e:
            # 如果按键API不可用，使用简化的检测方法
            # 可以通过其他方式模拟按键，比如定时器或文件标记
            pass
        
        return None
    
    def _handle_user_short_press(self, detections):
        """
        处理USER按键短按
        
        Args:
            detections: 当前检测结果
        """
        if self.current_mode == "live":
            # 开始记录模式
            if detections:
                # 有检测到人脸，准备记录
                available_slots = self.recognizer.get_status_info()['available_slots']
                if available_slots > 0:
                    self.current_mode = "confirm"
                    print("请输入要记录的人物姓名...")
                    # 在实际应用中，这里可能需要语音输入或其他输入方式
                    # 为了演示，我们使用自动生成的名字
                    person_count = len(self.recognizer.get_registered_persons())
                    self.recording_name = f"人物{person_count + 1}"
                    self._start_recording(detections[0])
                else:
                    print("已达到最大人数限制，无法记录新人物")
            else:
                print("未检测到人脸，无法开始记录")
        
        elif self.current_mode == "record":
            # 取消记录
            self._cancel_recording()
        
        elif self.current_mode == "confirm":
            # 确认记录
            self._confirm_recording()
    
    def _handle_user_long_press(self):
        """
        处理USER按键长按（清除所有记录）
        """
        if self.current_mode == "live":
            print("长按检测到，准备清除所有记录...")
            self._clear_all_records()
    
    def _start_recording(self, detection):
        """
        开始记录人脸
        
        Args:
            detection: 检测结果
        """
        self.current_mode = "record"
        self.recording_person = detection
        self.recording_count = 0
        print(f"开始记录人物: {self.recording_name}")
    
    def _cancel_recording(self):
        """
        取消记录
        """
        print("取消记录")
        self.current_mode = "live"
        self.recording_person = None
        self.recording_name = ""
        self.recording_count = 0
    
    def _confirm_recording(self):
        """
        确认并完成记录
        """
        print(f"记录完成: {self.recording_name}")
        self.current_mode = "live"
        self.recording_person = None
        self.recording_name = ""
        self.recording_count = 0
        self._show_system_status()
    
    def _process_recording(self, img, detections):
        """
        处理记录过程
        
        Args:
            img: 当前图像
            detections: 检测结果
        """
        if self.current_mode != "record" or not detections:
            return
        
        # 使用第一个检测结果进行记录
        detection = detections[0]
        face_bbox = detection.get('face_bbox')
        
        if face_bbox:
            if self.recording_count == 0:
                # 第一次记录 - 注册新人物
                success, person_id, message = self.recognizer.register_person(
                    img, self.recording_name, face_bbox
                )
                
                if success:
                    print(f"✓ {message}")
                    self.recording_count = 1
                    self.current_person_id = person_id
                else:
                    print(f"✗ {message}")
                    self._cancel_recording()
                    return
            
            elif self.recording_count < self.max_recording_samples:
                # 后续记录 - 添加样本
                success, message = self.recognizer.add_person_sample(
                    self.current_person_id, img, face_bbox
                )
                
                if success:
                    print(f"✓ {message}")
                    self.recording_count += 1
                else:
                    print(f"✗ {message}")
            
            # 检查是否完成记录
            if self.recording_count >= self.max_recording_samples:
                self._confirm_recording()
    
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
        self._show_system_status()
    
    def run(self):
        """
        运行GUI主循环
        """
        print("GUI启动中...")
        print("按键说明:")
        print("  - 短按USER键: 记录当前人脸")
        print("  - 长按USER键: 清除所有记录")
        print("  - 按BOOT键或Ctrl+C: 退出")
        print()
        
        try:
            start_time = time.time()
            
            while True:
                # 读取摄像头画面
                img = self.cam.read()
                if img is None:
                    continue
                
                self.frame_count += 1
                
                # 检测人脸
                detections = self.detector.detect_persons(img)
                if detections:
                    self.detection_count += 1
                
                # 处理检测结果
                img = self._handle_detections(img, detections)
                
                # 绘制UI元素
                self._draw_ui_elements(img)
                
                # 检查按键
                key_action = self._check_keys()
                
                if key_action == 'boot':
                    print("退出程序")
                    break
                elif key_action == 'user_short':
                    self._handle_user_short_press(detections)
                elif key_action == 'user_long':
                    self._handle_user_long_press()
                
                # 处理记录过程
                if self.current_mode == "record":
                    self._process_recording(img, detections)
                
                # 显示画面
                self.disp.show(img)
                
                # 每30帧显示一次统计信息
                if self.frame_count % 30 == 0:
                    elapsed_time = time.time() - start_time
                    fps = self.frame_count / elapsed_time
                    detection_rate = (self.detection_count / self.frame_count) * 100
                    print(f"统计: 帧数={self.frame_count}, FPS={fps:.1f}, 检测率={detection_rate:.1f}%")
                
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
    # 检查命令行参数
    width = 512
    height = 320
    
    if len(sys.argv) > 1:
        try:
            width = int(sys.argv[1])
            if len(sys.argv) > 2:
                height = int(sys.argv[2])
        except ValueError:
            print("无效的分辨率参数，使用默认值 512x320")
    
    print(f"启动实时摄像头GUI - 分辨率: {width}x{height}")
    
    # 创建并运行GUI
    gui = CameraGUI(width, height)
    gui.run()

if __name__ == "__main__":
    main()
