#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaixPy 视觉识别云台系统 - 主函数
作者：Kyunana
日期：2025-09-18
"""

import sys
import os
import time
# 可选显示支持（MaixPy）
try:
    from maix import display as _maix_display
except Exception:
    _maix_display = None
# 添加项目根目录到Python路径（必须在导入src之前）
project_root = os.path.dirname(os.path.abspath(__file__))
# 兼容MaixPy将文件复制到 /tmp/maixpy_run 的情况：尝试若干候选根目录，找包含 src/ 的路径
candidate_roots = [
    project_root,
    os.path.abspath(os.path.join(project_root, "..")),
    "/home/kyunana/MaixPy_Vision_Tracking",
    "/root",
    "/flash",
    "/sdcard",
]
for base in candidate_roots:
    try:
        if os.path.isdir(os.path.join(base, "src")) and base not in sys.path:
            sys.path.insert(0, base)
            break
    except Exception:
        pass
USING_EMBEDDED_CAMERA = False
try:
    from src.hardware.camera.camera_controller import CameraController
except Exception:
    # Fallback: embed a minimal CameraController so this script can run standalone on MaixPy
    print("[Warn] 'src' package not found. Using embedded CameraController fallback.")
    try:
        from maix import camera as _maix_camera
    except Exception as _e:
        print("[Error] Maix camera module not available:", _e)
        raise

    class CameraController:
        def __init__(self, width=512, height=320):
            self.width = width
            self.height = height
            self.camera = None

        def initialize_camera(self):
            try:
                self.camera = _maix_camera.Camera(self.width, self.height)
                return True
            except Exception:
                self.camera = None
                return False

        def capture_image(self):
            if self.camera is None:
                return None
            try:
                img = self.camera.read()
                time.sleep(0.001)
                return img
            except Exception:
                return None

        def release_camera(self):
            try:
                if self.camera is not None and hasattr(self.camera, "close"):
                    self.camera.close()
            finally:
                self.camera = None

        def set_resolution(self, width, height):
            self.width = width
            self.height = height
            if self.camera is not None:
                self.release_camera()
                self.initialize_camera()

        def get_resolution(self):
            return self.width, self.height

    USING_EMBEDDED_CAMERA = True

class MaixVisionSystem:
    """
    MaixPy视觉识别云台系统主类
    """
    
    def __init__(self):
        """
        初始化系统
        """
        print("=== MaixPy Vision Tracking System ===")
        print("Initializing system...")
        
        # 这里将来会初始化各个模块
        self.camera = CameraController(width=512, height=320)
        self.detector = None
        self.recognizer = None
        self.gimbal = None
        self.running = False
        self.disp = None
    
    def initialize_modules(self):
        """
        初始化所有模块
        返回: bool - 是否成功
        """
        try:
            print("📷 Initializing camera...")
            ok = self.camera.initialize_camera()
            if not ok:
                print("❌ Camera init failed")
                return False
            print("✅ Camera ok")
            
            print("🔍 Initializing detector...")
            # TODO: 初始化人脸检测模块
            
            print("🧠 Initializing recognizer...")
            # TODO: 初始化人脸识别模块
            
            print("🎮 Initializing gimbal...")
            # TODO: 初始化云台模块
            
            # 初始化显示（如果可用）
            if _maix_display is not None:
                try:
                    self.disp = _maix_display.Display()
                except Exception:
                    self.disp = None
            
            print("✅ All modules initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize modules: {e}")
            return False
    
    def start_system(self):
        """
        启动系统主循环
        """
        if not self.initialize_modules():
            print("Failed to start system")
            return
        
        print("🚀 Starting main loop...")
        self.running = True
        
        try:
            self.main_loop()
        except KeyboardInterrupt:
            print("\n👋 User requested exit")
        except Exception as e:
            print(f"❌ System error: {e}")
        finally:
            self.cleanup()
    
    def main_loop(self):
        """
        主循环 - 这是系统的核心
        """
        
        while self.running:
            img = self.camera.capture_image()
            if img is None:
                continue  # 本帧跳过
            # 显示画面（如显示可用）
            if self.disp is not None:
                try:
                    self.disp.show(img)
                except Exception:
                    pass
            # TODO: 检测人脸
            # TODO: 识别人脸
            # TODO: 更新显示
            # TODO: 处理用户输入
            # TODO: 控制云台
            time.sleep(0.01)  # 轻微限速
            
            
    
    def cleanup(self):
        """
        清理系统资源
        """
        print("🧹 Cleaning up...")
        try:
            if self.camera:
                self.camera.release_camera()
        # TODO: 关闭摄像头
        # TODO: 清理检测器
        # TODO: 保存识别数据
        # TODO: 停止云台
        finally:
            print("✅ Cleanup completed")


def main():
    """
    程序入口点
    """
    # 创建系统实例
    system = MaixVisionSystem()
    
    # 启动系统
    system.start_system()


if __name__ == "__main__":
    main()
