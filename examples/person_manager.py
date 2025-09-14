#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物管理工具
用于注册、删除和管理人物数据库
"""

import sys
import os
from maix import camera, display, app, time, image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.recognition.face_recognition import PersonRecognizer
from src.vision.detection.person_detector import PersonDetector

class PersonManager:
    """
    人物管理器
    """
    
    def __init__(self):
        """
        初始化管理器
        """
        self.recognizer = PersonRecognizer()
        self.detector = PersonDetector(camera_width=512, camera_height=320)
        
    def show_status(self):
        """
        显示系统状态
        """
        print("=== 人物数据库状态 ===")
        status = self.recognizer.get_status_info()
        
        print(f"最大人数: {status['max_persons']}")
        print(f"已注册: {status['registered_count']}")
        print(f"可用槽位: {status['available_slots']}")
        print(f"相似度阈值: {status['similarity_threshold']}")
        print(f"人脸检测器: {'✓' if status['has_face_detector'] else '✗'}")
        
        if status['target_person']:
            print(f"目标人物: {status['target_person']['name']} (ID: {status['target_person']['id']})")
        else:
            print("目标人物: 未设置")
        
        if status['registered_persons']:
            print("\n已注册人物:")
            for person_id in status['registered_persons']:
                person_info = self.recognizer.registered_persons[person_id]
                print(f"  {person_id}: {person_info['name']}")
                print(f"    注册时间: {person_info['registered_time']}")
                print(f"    特征样本数: {person_info['feature_count']}")
        else:
            print("\n未注册任何人物")
        
        print()
    
    def register_person_interactive(self, person_name):
        """
        交互式注册人物
        
        Args:
            person_name: 人物姓名
        """
        print(f"开始注册人物: {person_name}")
        print("请将人物面向摄像头，按任意键开始捕获...")
        
        # 初始化摄像头
        cam = camera.Camera(512, 320)
        disp = display.Display()
        
        try:
            capture_count = 0
            max_captures = 3  # 捕获3张图片
            
            while capture_count < max_captures and not app.need_exit():
                img = cam.read()
                if img is None:
                    continue
                
                # 检测人物
                detections = self.detector.detect_persons(img)
                
                if detections:
                    # 绘制检测框
                    img_display = self.detector.draw_green_boxes(img, detections)
                    
                    # 显示捕获提示
                    try:
                        capture_text = f"捕获 {capture_count+1}/{max_captures} - 按空格捕获"
                        img_display.draw_string(10, 10, capture_text, 
                                              color=image.Color.from_rgb(255, 255, 0))
                    except:
                        pass
                    
                    disp.show(img_display)
                    
                    # 模拟按键捕获（实际应用中需要真实按键输入）
                    # 这里每2秒自动捕获一次
                    time.sleep(2)
                    
                    # 使用第一个检测结果进行注册
                    detection = detections[0]
                    face_bbox = detection.get('face_bbox')
                    
                    if face_bbox:
                        if capture_count == 0:
                            # 第一次捕获 - 注册新人物
                            success, person_id, message = self.recognizer.register_person(
                                img, person_name, face_bbox
                            )
                            
                            if success:
                                print(f"✓ {message}")
                                capture_count += 1
                            else:
                                print(f"✗ {message}")
                                break
                        else:
                            # 后续捕获 - 添加样本
                            success, message = self.recognizer.add_person_sample(
                                person_id, img, face_bbox
                            )
                            
                            if success:
                                print(f"✓ {message}")
                                capture_count += 1
                            else:
                                print(f"✗ {message}")
                    else:
                        print("未检测到人脸，请重新定位")
                else:
                    # 显示等待检测的提示
                    try:
                        wait_text = "等待检测人物..."
                        img.draw_string(10, 10, wait_text, 
                                       color=image.Color.from_rgb(255, 0, 0))
                    except:
                        pass
                    
                    disp.show(img)
                
                time.sleep_ms(100)
            
            if capture_count >= max_captures:
                print(f"✓ 人物 '{person_name}' 注册完成，共捕获 {capture_count} 个样本")
            
        except KeyboardInterrupt:
            print("\n注册过程中断")
        except Exception as e:
            print(f"注册过程出错: {e}")
        finally:
            cam.close()
    
    def list_persons(self):
        """
        列出所有已注册人物
        """
        persons = self.recognizer.get_registered_persons()
        
        if not persons:
            print("没有已注册的人物")
            return
        
        print("=== 已注册人物列表 ===")
        for person_id, person_info in persons.items():
            print(f"{person_id}: {person_info['name']}")
            print(f"  注册时间: {person_info['registered_time']}")
            print(f"  特征数量: {person_info['feature_count']}")
            print()
    
    def set_target(self, person_identifier):
        """
        设置目标人物
        
        Args:
            person_identifier: 人物ID或姓名
        """
        persons = self.recognizer.get_registered_persons()
        
        # 查找人物ID
        target_person_id = None
        
        # 首先按ID查找
        if person_identifier in persons:
            target_person_id = person_identifier
        else:
            # 按姓名查找
            for person_id, person_info in persons.items():
                if person_info['name'] == person_identifier:
                    target_person_id = person_id
                    break
        
        if target_person_id:
            success, message = self.recognizer.set_target_person(target_person_id)
            if success:
                print(f"✓ {message}")
            else:
                print(f"✗ {message}")
        else:
            print(f"✗ 未找到人物: {person_identifier}")
    
    def delete_person(self, person_identifier):
        """
        删除人物
        
        Args:
            person_identifier: 人物ID或姓名
        """
        persons = self.recognizer.get_registered_persons()
        
        # 查找人物ID
        target_person_id = None
        
        # 首先按ID查找
        if person_identifier in persons:
            target_person_id = person_identifier
        else:
            # 按姓名查找
            for person_id, person_info in persons.items():
                if person_info['name'] == person_identifier:
                    target_person_id = person_id
                    break
        
        if target_person_id:
            person_name = persons[target_person_id]['name']
            confirm = input(f"确认删除人物 '{person_name}' (ID: {target_person_id})? (y/N): ")
            
            if confirm.lower() == 'y':
                success, message = self.recognizer.delete_person(target_person_id)
                if success:
                    print(f"✓ {message}")
                else:
                    print(f"✗ {message}")
            else:
                print("取消删除")
        else:
            print(f"✗ 未找到人物: {person_identifier}")
    
    def clear_all(self):
        """
        清除所有人物数据
        """
        persons = self.recognizer.get_registered_persons()
        
        if not persons:
            print("没有已注册的人物")
            return
        
        print(f"将删除 {len(persons)} 个已注册人物:")
        for person_id, person_info in persons.items():
            print(f"  {person_id}: {person_info['name']}")
        
        confirm = input("确认删除所有人物? (y/N): ")
        
        if confirm.lower() == 'y':
            deleted_count = 0
            for person_id in list(persons.keys()):
                success, message = self.recognizer.delete_person(person_id)
                if success:
                    deleted_count += 1
                    print(f"✓ 已删除: {message}")
                else:
                    print(f"✗ 删除失败: {message}")
            
            print(f"共删除 {deleted_count} 个人物")
        else:
            print("取消清除操作")

def show_help():
    """
    显示帮助信息
    """
    print("人物管理工具")
    print("用法: python person_manager.py <命令> [参数]")
    print()
    print("命令:")
    print("  status                    显示系统状态")
    print("  list                      列出所有已注册人物")
    print("  register <姓名>           注册新人物")
    print("  target <ID或姓名>         设置目标人物")
    print("  delete <ID或姓名>         删除指定人物")
    print("  clear                     清除所有人物数据")
    print("  help                      显示此帮助信息")
    print()
    print("示例:")
    print("  python person_manager.py register 张三")
    print("  python person_manager.py target person_01")
    print("  python person_manager.py delete 张三")

def main():
    """
    主函数
    """
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    manager = PersonManager()
    
    try:
        if command == "status":
            manager.show_status()
        
        elif command == "list":
            manager.list_persons()
        
        elif command == "register":
            if len(sys.argv) < 3:
                print("错误: 请提供人物姓名")
                print("用法: python person_manager.py register <姓名>")
                return
            
            person_name = sys.argv[2]
            manager.register_person_interactive(person_name)
        
        elif command == "target":
            if len(sys.argv) < 3:
                print("错误: 请提供人物ID或姓名")
                print("用法: python person_manager.py target <ID或姓名>")
                return
            
            person_identifier = sys.argv[2]
            manager.set_target(person_identifier)
        
        elif command == "delete":
            if len(sys.argv) < 3:
                print("错误: 请提供人物ID或姓名")
                print("用法: python person_manager.py delete <ID或姓名>")
                return
            
            person_identifier = sys.argv[2]
            manager.delete_person(person_identifier)
        
        elif command == "clear":
            manager.clear_all()
        
        elif command == "help":
            show_help()
        
        else:
            print(f"未知命令: {command}")
            show_help()
    
    except Exception as e:
        print(f"执行命令时出错: {e}")

if __name__ == "__main__":
    main()
