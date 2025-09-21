#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaixPy 预训练人脸识别系统
基于MaixHub预训练模型，支持识别10位知名人物

作者: Kyunana
版本: v6.1.0-clean
"""

# ==================== 版本信息 ====================
__version__ = "6.2.0-demo-mode"
__release_date__ = "2025-09-21"
__author__ = "Kyunana"
__description__ = "MaixPy 预训练人脸识别系统"

def print_version_info():
    """打印版本信息"""
    print("=" * 60)
    print(f"🚀 {__description__}")
    print(f"📦 版本: {__version__}")
    print(f"📅 发布日期: {__release_date__}")
    print(f"👨‍💻 作者: {__author__}")
    print("🎭 支持识别: 胡歌、姜文、彭于晏、岳云鹏、周冬雨")
    print("           迪丽热巴、范冰冰、姚明、刘亦菲、周杰伦")
    print("=" * 60)

# ==================== 导入模块 ====================
import os
import sys
import time
import gc

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# MaixPy相关导入
try:
    from maix import camera, display, image, touchscreen, app
    MAIX_AVAILABLE = True
    print("✅ MaixPy modules imported successfully")
except ImportError as e:
    print(f"❌ Failed to import MaixPy modules: {e}")
    print("⚠️  Running in simulation mode")
    MAIX_AVAILABLE = False

# 项目模块导入
from src.hardware.button.virtual_button import VirtualButtonManager
from src.vision.recognition.pretrained_recognizer import PretrainedRecognizer

class PretrainedFaceSystem:
    """预训练人脸识别系统"""
    
    def __init__(self):
        """初始化系统"""
        print("\n=== MaixPy Pretrained Face Recognition System ===")
        print("Initializing system...")
        
        # 系统配置
        self.camera_width = 320
        self.camera_height = 240
        
        # 组件初始化
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
        self.last_person_id = None
        self.last_confidence = 0.0
        self.last_person_name = "unknown"
        
        # 初始化组件
        self.initialize_components()
    
    def initialize_components(self):
        """初始化所有组件"""
        success = True
        
        try:
            # 初始化摄像头
            if MAIX_AVAILABLE:
                print("📷 Initializing camera...")
                self.camera = camera.Camera(self.camera_width, self.camera_height)
                print("✅ Camera initialized")
            
            # 初始化显示器
            if MAIX_AVAILABLE:
                print("🖥️ Initializing display...")
                self.display = display.Display()
                print("✅ Display initialized")
            
            # 初始化触摸屏
            if MAIX_AVAILABLE:
                print("👆 Initializing touchscreen...")
                self.touchscreen = touchscreen.TouchScreen()
                print("✅ Touchscreen initialized")
            
            # 初始化预训练识别器
            print("🧠 Initializing pretrained recognizer...")
            self.recognizer = PretrainedRecognizer(model_path="models/model-38558.kmodel")
            if self.recognizer.model_loaded:
                print("✅ Pretrained recognizer initialized")
            else:
                print("❌ Pretrained recognizer failed to load")
                success = False
            
            # 初始化虚拟按钮
            if MAIX_AVAILABLE and self.touchscreen:
                print("🔘 Initializing virtual buttons...")
                # 获取显示器尺寸
                display_width = 640 if self.display else 640
                display_height = 480 if self.display else 480
                
                self.button_manager = VirtualButtonManager(
                    display_width, 
                    display_height
                )
                self._create_buttons()
                print("✅ Virtual buttons initialized")
            
            if success:
                print("✅ All components initialized successfully!")
            else:
                print("⚠️ Some components failed to initialize")
                
        except Exception as e:
            print(f"❌ Component initialization failed: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_buttons(self):
        """创建虚拟按钮"""
        if not self.button_manager:
            return
        
        # 获取显示器尺寸
        display_width = 640 if MAIX_AVAILABLE else 640
        display_height = 480 if MAIX_AVAILABLE else 480
        
        # 采用原始项目的右侧垂直布局
        button_x = display_width - 100  # 右侧位置
        
        # 退出按钮 (右上角)
        self.button_manager.add_button(
            "exit", 
            x=button_x, y=20, 
            width=80, height=40,
            text="EXIT",
            callback=self._handle_exit
        )
        
        # 调试按钮 (EXIT下方)
        self.button_manager.add_button(
            "debug",
            x=button_x, y=70,
            width=80, height=40,
            text="DEBUG",
            callback=self._handle_debug
        )
        
        # 阈值调整按钮 (DEBUG下方)
        self.button_manager.add_button(
            "threshold",
            x=button_x, y=120,
            width=70, height=35,
            text="THRES",
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
        print(f"  Version: {__version__}")
        print(f"  Frame count: {self.frame_count}")
        print(f"  FPS: {self.fps:.2f}")
        print(f"  Camera resolution: ({self.camera_width}, {self.camera_height})")
        print(f"  MaixPy available: {MAIX_AVAILABLE}")
        
        if self.recognizer:
            status = self.recognizer.get_status_info()
            print(f"  Recognizer status:")
            print(f"    Model loaded: {status['model_loaded']}")
            print(f"    Supported persons: {status['supported_persons']}")
            print(f"    Confidence threshold: {status['confidence_threshold']}")
            print(f"  Last recognition: {self.last_person_name} ({self.last_confidence:.3f})")
        
        print("=" * 50)
    
    def _handle_threshold(self):
        """处理阈值调整按钮"""
        if self.recognizer:
            current = self.recognizer.confidence_threshold
            # 循环调整: 0.5 -> 0.6 -> 0.7 -> 0.8 -> 0.5
            new_threshold = 0.5 if current >= 0.8 else current + 0.1
            self.recognizer.set_confidence_threshold(new_threshold)
    
    def run(self):
        """运行主循环"""
        if not MAIX_AVAILABLE:
            print("❌ MaixPy not available, cannot run on device")
            print("ℹ️ This is a simulation run")
            self._simulate_run()
            return
        
        if not self.camera or not self.display:
            print("❌ Critical components (camera/display) not initialized, cannot start")
            return
        
        if not self.recognizer or not self.recognizer.model_loaded:
            print("⚠️ 识别器未加载，将以演示模式运行")
            print("📺 演示模式: 显示摄像头画面，但不进行人脸识别")
        
        print("🚀 Starting main loop...")
        self.running = True
        
        try:
            while self.running and (not app or not app.need_exit()):
                # 捕获图像
                img = self.camera.read()
                if img is None:
                    continue
                
                # 处理触摸事件
                if self.button_manager:
                    self.button_manager.handle_touch()
                
                # 人脸识别（如果识别器可用）
                if self.recognizer and self.recognizer.model_loaded:
                    person_id, confidence, person_name = self.recognizer.recognize(img)
                    
                    if person_id:
                        self.last_person_id = person_id
                        self.last_confidence = confidence
                        self.last_person_name = person_name
                else:
                    # 演示模式：显示提示信息
                    if self.frame_count % 60 == 0:  # 每60帧显示一次提示
                        print("📺 演示模式运行中 - 识别器未加载")
                
                # 绘制UI
                self._draw_ui(img)
                
                # 显示图像
                self.display.show(img)
                
                # 更新帧率
                self._update_fps()
                
                # 定期垃圾回收
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
    
    def _simulate_run(self):
        """模拟运行（用于开发环境测试）"""
        print("🔄 Running simulation...")
        
        if self.recognizer and self.recognizer.model_loaded:
            print("✅ Recognizer loaded successfully")
        else:
            print("❌ Recognizer not loaded")
        
        # 显示支持的人物
        if self.recognizer:
            persons = self.recognizer.get_supported_persons()
            print(f"🎭 Supported persons ({len(persons)}):")
            for person in persons:
                print(f"   • {person['name']} ({person['english_name']})")
        
        print("ℹ️ Simulation completed")
    
    def _draw_ui(self, img):
        """绘制用户界面"""
        try:
            # 绘制系统信息
            img.draw_string(10, 10, f"Pretrained Face Recognition v{__version__}", 
                          color=image.COLOR_WHITE, scale=1.2)
            img.draw_string(10, 30, f"FPS: {self.fps:.1f}", 
                          color=image.COLOR_GREEN, scale=1.0)
            
            # 绘制识别结果
            if not self.recognizer or not self.recognizer.model_loaded:
                # 演示模式
                img.draw_rect(10, 60, 300, 50, color=image.COLOR_BLACK, thickness=-1)
                img.draw_rect(10, 60, 300, 50, color=image.COLOR_BLUE, thickness=2)
                img.draw_string(15, 70, "演示模式", color=image.COLOR_BLUE, scale=1.5)
                img.draw_string(15, 90, "识别器未加载", color=image.COLOR_WHITE, scale=1.0)
            elif self.last_person_name != "unknown":
                # 识别成功
                result_text = f"识别: {self.last_person_name}"
                confidence_text = f"置信度: {self.last_confidence:.3f}"
                
                # 绘制结果框
                img.draw_rect(10, 60, 300, 50, color=image.COLOR_BLACK, thickness=-1)
                img.draw_rect(10, 60, 300, 50, color=image.COLOR_GREEN, thickness=2)
                
                # 绘制文字
                img.draw_string(15, 70, result_text, color=image.COLOR_GREEN, scale=1.5)
                img.draw_string(15, 90, confidence_text, color=image.COLOR_WHITE, scale=1.0)
            else:
                # 未识别
                img.draw_rect(10, 60, 300, 30, color=image.COLOR_BLACK, thickness=-1)
                img.draw_rect(10, 60, 300, 30, color=image.COLOR_RED, thickness=2)
                img.draw_string(15, 70, "未识别到已知人物", color=image.COLOR_RED, scale=1.2)
            
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
            if self.recognizer:
                del self.recognizer
            
            print("✅ Cleanup completed")
        
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

def main():
    """主函数"""
    # 打印版本信息
    print_version_info()
    
    # 创建并运行系统
    system = PretrainedFaceSystem()
    system.run()

if __name__ == "__main__":
    main()
