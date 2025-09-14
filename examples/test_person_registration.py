#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物注册和识别测试
支持最多3个人物的注册、识别和管理
"""

import sys
import os
from maix import camera, display, app, time, image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.recognition.face_recognition import PersonRecognizer
from src.vision.detection.person_detector import PersonDetector

class PersonRegistrationTest:
    """
    人物注册测试类
    """
    
    def __init__(self):
        """
        初始化测试
        """
        print("=== 人物注册和识别测试 ===")
        print("支持最多3个人物的注册和识别")
        print()
        
        # 初始化摄像头
        self.cam = camera.Camera(512, 320)
        self.disp = display.Display()
        
        # 初始化检测器和识别器
        self.detector = PersonDetector(camera_width=512, camera_height=320)
        self.recognizer = PersonRecognizer()
        
        # 显示系统状态
        self._show_system_status()
        
        # 测试模式
        self.current_mode = "detect"  # detect, register, recognize
        self.registration_name = ""
        
    def _show_system_status(self):
        """
        显示系统状态
        """
        status = self.recognizer.get_status_info()
        print("系统状态:")
        print(f"  最大人数: {status['max_persons']}")
        print(f"  已注册: {status['registered_count']}")
        print(f"  可用槽位: {status['available_slots']}")
        print(f"  相似度阈值: {status['similarity_threshold']}")
        print(f"  人脸检测器: {'✓' if status['has_face_detector'] else '✗'}")
        
        if status['target_person']:
            print(f"  目标人物: {status['target_person']['name']} (ID: {status['target_person']['id']})")
        else:
            print("  目标人物: 未设置")
        
        if status['registered_persons']:
            print("  已注册人物:")
            for person_id in status['registered_persons']:
                person_info = self.recognizer.registered_persons[person_id]
                print(f"    {person_id}: {person_info['name']} (特征数: {person_info['feature_count']})")
        
        print()
    
    def _draw_ui_info(self, img):
        """
        绘制UI信息
        
        Args:
            img: 图像对象
        """
        try:
            # 模式信息
            mode_text = f"模式: {self.current_mode}"
            img.draw_string(10, 10, mode_text, color=image.Color.from_rgb(255, 255, 255))
            
            # 操作提示
            if self.current_mode == "detect":
                hint = "按键: R-注册 T-识别 Q-退出"
            elif self.current_mode == "register":
                hint = f"注册模式: {self.registration_name} 按S保存 C取消"
            elif self.current_mode == "recognize":
                hint = "识别模式: 按D返回检测"
            else:
                hint = ""
            
            img.draw_string(10, 25, hint, color=image.Color.from_rgb(255, 255, 0))
            
            # 状态信息
            status = self.recognizer.get_status_info()
            status_text = f"注册: {status['registered_count']}/{status['max_persons']}"
            img.draw_string(10, 40, status_text, color=image.Color.from_rgb(0, 255, 255))
            
        except Exception as e:
            print(f"UI绘制错误: {e}")
    
    def _handle_detection_mode(self, img):
        """
        处理检测模式
        
        Args:
            img: 图像对象
            
        Returns:
            processed_img: 处理后的图像
        """
        # 检测人物
        detections = self.detector.detect_persons(img)
        
        if detections:
            # 绘制检测框
            img = self.detector.draw_green_boxes(img, detections)
            
            # 尝试识别已注册的人物
            for detection in detections:
                bbox = detection['bbox']
                x, y, w, h = bbox
                
                # 使用人脸区域进行识别
                face_bbox = detection.get('face_bbox')
                if face_bbox:
                    person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                    
                    if person_id:
                        # 绘制识别结果
                        try:
                            recognition_text = f"{person_name} ({confidence:.2f})"
                            img.draw_string(x, y - 20, recognition_text, 
                                          color=image.Color.from_rgb(255, 0, 0))
                        except:
                            pass
        
        return img
    
    def _handle_register_mode(self, img):
        """
        处理注册模式
        
        Args:
            img: 图像对象
            
        Returns:
            processed_img: 处理后的图像
        """
        # 检测人物
        detections = self.detector.detect_persons(img)
        
        if detections:
            # 只处理第一个检测到的人物
            detection = detections[0]
            bbox = detection['bbox']
            face_bbox = detection.get('face_bbox')
            
            # 绘制检测框（黄色表示准备注册）
            try:
                x, y, w, h = bbox
                img.draw_rect(x, y, w, h, color=image.Color.from_rgb(255, 255, 0), thickness=3)
                
                # 显示注册提示
                register_text = f"注册: {self.registration_name}"
                img.draw_string(x, y - 20, register_text, 
                              color=image.Color.from_rgb(255, 255, 0))
            except:
                pass
        
        return img
    
    def _handle_recognize_mode(self, img):
        """
        处理识别模式
        
        Args:
            img: 图像对象
            
        Returns:
            processed_img: 处理后的图像
        """
        # 检测人物
        detections = self.detector.detect_persons(img)
        
        if detections:
            for detection in detections:
                bbox = detection['bbox']
                face_bbox = detection.get('face_bbox')
                x, y, w, h = bbox
                
                if face_bbox:
                    # 进行人物识别
                    person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                    
                    if person_id:
                        # 已知人物 - 红色框
                        color = image.Color.from_rgb(255, 0, 0)
                        result_text = f"{person_name} ({confidence:.3f})"
                    else:
                        # 未知人物 - 蓝色框
                        color = image.Color.from_rgb(0, 0, 255)
                        result_text = f"未知 ({confidence:.3f})"
                    
                    try:
                        img.draw_rect(x, y, w, h, color=color, thickness=3)
                        img.draw_string(x, y - 20, result_text, color=color)
                    except:
                        pass
        
        return img
    
    def run_interactive_test(self):
        """
        运行交互式测试
        """
        print("交互式测试开始...")
        print("操作说明:")
        print("  D - 检测模式")
        print("  R - 注册新人物")
        print("  T - 识别模式")
        print("  1/2/3 - 设置目标人物")
        print("  L - 列出已注册人物")
        print("  C - 清除所有注册")
        print("  Q - 退出")
        print()
        
        try:
            frame_count = 0
            
            while not app.need_exit():
                img = self.cam.read()
                if img is None:
                    continue
                
                frame_count += 1
                
                # 根据当前模式处理图像
                if self.current_mode == "detect":
                    img = self._handle_detection_mode(img)
                elif self.current_mode == "register":
                    img = self._handle_register_mode(img)
                elif self.current_mode == "recognize":
                    img = self._handle_recognize_mode(img)
                
                # 绘制UI信息
                self._draw_ui_info(img)
                
                # 显示图像
                self.disp.show(img)
                
                # 简单的按键处理（这里用时间模拟，实际应用中需要真实按键输入）
                # 在实际MaixPy环境中，可以使用按键中断或其他输入方法
                
                time.sleep_ms(50)
                
        except KeyboardInterrupt:
            print("\n测试结束")
        except Exception as e:
            print(f"测试出错: {e}")
        finally:
            self.cam.close()
    
    def test_registration_workflow(self):
        """
        测试注册工作流程（静态测试）
        """
        print("=== 注册工作流程测试 ===")
        
        # 模拟注册3个人物
        test_persons = [
            {"name": "张三", "description": "第一个测试人物"},
            {"name": "李四", "description": "第二个测试人物"},
            {"name": "王五", "description": "第三个测试人物"}
        ]
        
        print("开始模拟注册流程...")
        
        for i, person_info in enumerate(test_persons):
            print(f"\n注册第 {i+1} 个人物: {person_info['name']}")
            
            # 捕获图像
            img = self.cam.read()
            if img is None:
                print("无法获取图像")
                continue
            
            # 检测人物
            detections = self.detector.detect_persons(img)
            
            if detections:
                detection = detections[0]  # 使用第一个检测结果
                face_bbox = detection.get('face_bbox')
                
                if face_bbox:
                    # 注册人物
                    success, person_id, message = self.recognizer.register_person(
                        img, person_info['name'], face_bbox
                    )
                    
                    if success:
                        print(f"✓ {message}")
                        
                        # 设置为目标人物（可选）
                        if i == 0:  # 设置第一个人物为目标
                            target_success, target_msg = self.recognizer.set_target_person(person_id)
                            if target_success:
                                print(f"✓ {target_msg}")
                    else:
                        print(f"✗ {message}")
                else:
                    print("✗ 未检测到人脸，无法注册")
            else:
                print("✗ 未检测到人物，无法注册")
            
            time.sleep(2)  # 等待2秒
        
        # 显示最终状态
        print("\n=== 注册完成 ===")
        self._show_system_status()
    
    def test_recognition_accuracy(self):
        """
        测试识别准确性
        """
        print("=== 识别准确性测试 ===")
        
        if not self.recognizer.registered_persons:
            print("没有已注册的人物，无法进行识别测试")
            return
        
        print("开始识别测试，请依次展示已注册的人物...")
        
        test_count = 20
        recognition_results = []
        
        try:
            for i in range(test_count):
                print(f"测试 {i+1}/{test_count}")
                
                img = self.cam.read()
                if img is None:
                    continue
                
                # 检测人物
                detections = self.detector.detect_persons(img)
                
                if detections:
                    for detection in detections:
                        face_bbox = detection.get('face_bbox')
                        if face_bbox:
                            person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                            
                            result = {
                                'frame': i+1,
                                'detected': True,
                                'recognized': person_id is not None,
                                'person_id': person_id,
                                'person_name': person_name,
                                'confidence': confidence
                            }
                            recognition_results.append(result)
                            
                            print(f"  检测: ✓, 识别: {'✓' if person_id else '✗'}, "
                                  f"人物: {person_name}, 置信度: {confidence:.3f}")
                else:
                    result = {
                        'frame': i+1,
                        'detected': False,
                        'recognized': False,
                        'person_id': None,
                        'person_name': '未检测到',
                        'confidence': 0.0
                    }
                    recognition_results.append(result)
                    print(f"  检测: ✗")
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\n识别测试中断")
        
        # 统计结果
        if recognition_results:
            total_frames = len(recognition_results)
            detected_frames = sum(1 for r in recognition_results if r['detected'])
            recognized_frames = sum(1 for r in recognition_results if r['recognized'])
            
            print("\n=== 识别测试结果 ===")
            print(f"总测试帧数: {total_frames}")
            print(f"检测成功帧数: {detected_frames}")
            print(f"识别成功帧数: {recognized_frames}")
            if detected_frames > 0:
                print(f"检测成功率: {detected_frames/total_frames*100:.1f}%")
                print(f"识别成功率: {recognized_frames/detected_frames*100:.1f}%")

def main():
    """
    主函数
    """
    test = PersonRegistrationTest()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "register":
            test.test_registration_workflow()
        elif mode == "recognize":
            test.test_recognition_accuracy()
        elif mode == "interactive":
            test.run_interactive_test()
        else:
            print("使用方法:")
            print("  python test_person_registration.py register    # 测试注册流程")
            print("  python test_person_registration.py recognize   # 测试识别准确性")
            print("  python test_person_registration.py interactive # 交互式测试")
    else:
        # 默认运行交互式测试
        test.run_interactive_test()

if __name__ == "__main__":
    main()
