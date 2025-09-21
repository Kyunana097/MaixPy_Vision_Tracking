#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaixPy 智能视觉识别云台系统 - 预训练模型版本
基于MaixHub预训练人脸识别模型
支持识别10位名人: 胡歌、姜文、彭于晏、岳云鹏、周冬雨、迪丽热巴、范冰冰、姚明、刘亦菲、周杰伦

作者: Kyunana
描述: 使用预训练模型进行人脸识别的主程序
"""

# ==================== 版本信息 ====================
__version__ = "6.0.0-pretrained"
__release_date__ = "2025-09-21"
__author__ = "Kyunana"
__description__ = "MaixPy 智能视觉识别云台系统 - 预训练模型版本"

def print_version_info():
    """打印版本信息"""
    print("=" * 60)
    print(f"🚀 {__description__}")
    print(f"📦 版本: {__version__}")
    print(f"📅 发布日期: {__release_date__}")
    print(f"👨‍💻 作者: {__author__}")
    print("=" * 60)

# ==================== 导入模块 ====================
import os
import sys
import time
import gc
import json

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# MaixPy相关导入
try:
    from maix import camera, display, image, touchscreen, app
    _maix_camera = camera
    _maix_display = display
    _maix_image = image
    _maix_touchscreen = touchscreen
    _maix_app = app
    print("✅ MaixPy modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import MaixPy modules: {e}")
    print("⚠️  Running in simulation mode")
    _maix_camera = None
    _maix_display = None
    _maix_image = None
    _maix_touchscreen = None
    _maix_app = None

# 项目模块导入
from src.hardware.button.virtual_button import VirtualButtonManager
from src.vision.recognition.pretrained_face_recognizer import PretrainedFaceRecognizer

class PretrainedVisionSystem:
    """预训练模型视觉识别系统"""
    
    def __init__(self):
        """初始化系统"""
        print("\n=== MaixPy Vision Tracking System - Pretrained ===")
        print("Initializing system...")
        
        # 系统配置
        self.camera_width = 512
        self.camera_height = 320
        self.display_width = 640
        self.display_height = 480
        
        # 组件初始化状态
        self.camera = None
        self.display = None
        self.touchscreen = None
        self.recognizer = None
        self.button_manager = None
        
        # 系统状态
        self.running = False
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0.0
        
        # 识别状态
        self.last_recognition = None
        self.recognition_confidence = 0.0
        self.recognition_person = "unknown"
        
        # 初始化所有组件
        self.initialize_modules()
    
    def initialize_modules(self):
        """初始化所有模块"""
        try:
            # 初始化摄像头
            if _maix_camera:
                print("📷 Initializing camera...")
                self.camera = _maix_camera.Camera(self.camera_width, self.camera_height)
                print("✅ Camera initialized")
            
            # 初始化显示器
            if _maix_display:
                print("🖥️ Initializing display...")
                self.display = _maix_display.Display()
                print("✅ Display initialized")
            
            # 初始化触摸屏
            if _maix_touchscreen:
                print("👆 Initializing touchscreen...")
                self.touchscreen = _maix_touchscreen.TouchScreen()
                print("✅ Touchscreen initialized")
            
            # 初始化预训练人脸识别器
            print("🧠 Initializing pretrained face recognizer...")
            self.recognizer = PretrainedFaceRecognizer(
                model_path="pretrained_model/model-38558.kmodel"
            )
            print("✅ Pretrained face recognizer initialized")
            
            # 初始化虚拟按钮
            print("🔘 Initializing virtual buttons...")
            if self.touchscreen:
                self.button_manager = VirtualButtonManager(self.touchscreen)
                self._create_buttons()
                print("✅ Virtual buttons initialized")
            
            print("✅ All modules initialized successfully!")
            
        except Exception as e:
            print(f"❌ Module initialization failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_buttons(self):
        """创建虚拟按钮"""
        if not self.button_manager:
            return
        
        # 退出按钮
        self.button_manager.add_button(
            "exit", 
            x=self.display_width - 80, y=10, 
            width=70, height=30,
            text="EXIT",
            callback=self._handle_exit
        )
        
        # 调试信息按钮
        self.button_manager.add_button(
            "debug",
            x=10, y=self.display_height - 50,
            width=80, height=30,
            text="DEBUG",
            callback=self._handle_debug
        )
        
        # 设置阈值按钮
        self.button_manager.add_button(
            "threshold",
            x=100, y=self.display_height - 50,
            width=100, height=30,
            text="THRESHOLD",
            callback=self._handle_threshold
        )
    
    def _handle_exit(self):
        """处理退出按钮"""
        print("🚪 Exit button pressed - stopping system")
        self.running = False
    
    def _handle_debug(self):
        """处理调试按钮"""
        print("\n" + "=" * 50)
        print("🐛 === SYSTEM DEBUG INFO ===")
        print(f"  Frame count: {self.frame_count}")
        print(f"  FPS: {self.fps:.2f}")
        print(f"  Camera resolution: ({self.camera_width}, {self.camera_height})")
        print(f"  Display resolution: ({self.display_width}, {self.display_height})")
        
        if self.recognizer:
            status = self.recognizer.get_status_info()
            print(f"  Recognizer status:")
            print(f"    Model loaded: {status['model_loaded']}")
            print(f"    Supported persons: {status['supported_persons']}")
            print(f"    Confidence threshold: {status['confidence_threshold']}")
            print(f"  Supported persons:")
            for person in self.recognizer.get_supported_persons():
                print(f"    {person['name']} ({person['english_name']})")
        
        print(f"  Last recognition: {self.recognition_person} ({self.recognition_confidence:.3f})")
        print("=" * 50)
    
    def _handle_threshold(self):
        """处理阈值调整按钮"""
        if self.recognizer:
            current = self.recognizer.confidence_threshold
            # 循环调整阈值: 0.5 -> 0.6 -> 0.7 -> 0.8 -> 0.5
            new_threshold = 0.5 if current >= 0.8 else current + 0.1
            self.recognizer.set_confidence_threshold(new_threshold)
            print(f"🎯 置信度阈值调整: {current:.1f} -> {new_threshold:.1f}")
    
    def run(self):
        """运行主循环"""
        if not self.camera or not self.display or not self.recognizer:
            print("❌ Critical components not initialized, cannot start")
            return
        
        print("🚀 Starting main loop...")
        self.running = True
        
        try:
            while self.running and (_maix_app is None or not _maix_app.need_exit()):
                # 捕获图像
                img = self.camera.read()
                if img is None:
                    continue
                
                # 处理触摸事件
                if self.button_manager:
                    self.button_manager.handle_touch()
                
                # 人脸识别
                person_id, confidence, person_name = self.recognizer.recognize_person(img)
                
                if person_id:
                    self.last_recognition = person_id
                    self.recognition_confidence = confidence
                    self.recognition_person = person_name
                
                # 绘制UI
                self._draw_ui(img)
                
                # 显示图像
                self.display.show(img)
                
                # 更新帧率
                self._update_fps()
                
                # 垃圾回收
                if self.frame_count % 100 == 0:
                    gc.collect()
        
        except KeyboardInterrupt:
            print("\n⚠️ Keyboard interrupt received")
        except Exception as e:
            print(f"❌ Main loop error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def _draw_ui(self, img):
        """绘制用户界面"""
        try:
            # 绘制系统信息
            img.draw_string(10, 10, f"Pretrained Face Recognition v{__version__}", 
                          color=(255, 255, 255), scale=1.2)
            img.draw_string(10, 30, f"FPS: {self.fps:.1f}", 
                          color=(0, 255, 0), scale=1.0)
            
            # 绘制识别结果
            if self.recognition_person != "unknown":
                # 识别成功
                result_text = f"识别: {self.recognition_person}"
                confidence_text = f"置信度: {self.recognition_confidence:.3f}"
                
                # 绘制结果背景
                img.draw_rectangle(10, 60, 300, 50, color=(0, 0, 0), thickness=-1)
                img.draw_rectangle(10, 60, 300, 50, color=(0, 255, 0), thickness=2)
                
                # 绘制文字
                img.draw_string(15, 70, result_text, color=(0, 255, 0), scale=1.5)
                img.draw_string(15, 90, confidence_text, color=(255, 255, 255), scale=1.0)
            else:
                # 未识别
                img.draw_rectangle(10, 60, 300, 30, color=(0, 0, 0), thickness=-1)
                img.draw_rectangle(10, 60, 300, 30, color=(255, 0, 0), thickness=2)
                img.draw_string(15, 70, "未识别到已知人物", color=(255, 0, 0), scale=1.2)
            
            # 绘制支持的人物列表
            if self.recognizer:
                persons = self.recognizer.get_supported_persons()
                y_offset = 130
                img.draw_string(10, y_offset, "支持识别的人物:", color=(255, 255, 255), scale=1.0)
                
                for i, person in enumerate(persons[:5]):  # 只显示前5个
                    y_pos = y_offset + 20 + i * 15
                    img.draw_string(15, y_pos, f"• {person['name']}", 
                                  color=(200, 200, 200), scale=0.8)
                
                if len(persons) > 5:
                    img.draw_string(15, y_offset + 20 + 5 * 15, "...", 
                                  color=(200, 200, 200), scale=0.8)
            
            # 绘制按钮
            if self.button_manager:
                self.button_manager.draw_buttons(img)
        
        except Exception as e:
            print(f"UI draw error: {e}")
    
    def _update_fps(self):
        """更新帧率"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def cleanup(self):
        """清理资源"""
        print("🧹 Cleaning up...")
        
        try:
            if self.camera:
                # MaixPy camera通常不需要显式关闭
                pass
            
            if self.recognizer:
                # 清理识别器资源
                del self.recognizer
            
            print("✅ Cleanup completed")
        
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

def main():
    """主函数"""
    # 打印版本信息
    print_version_info()
    
    # 创建并运行系统
    system = PretrainedVisionSystem()
    system.run()

if __name__ == "__main__":
    main()
