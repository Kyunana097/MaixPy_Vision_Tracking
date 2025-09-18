#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaixPy 视觉识别云台系统 - 主程序
作者: Kyunana
描述: 主程序入口，负责系统初始化和主循环控制
"""

import sys
import os
import time

# 可选的MaixPy模块（显示与退出标志）
try:
    from maix import display as _maix_display
except Exception:
    _maix_display = None
try:
    from maix import app as _maix_app
except Exception:
    _maix_app = None


# 路径设置：确保能导入 src 包（兼容 /tmp/maixpy_run 等环境）
project_root = os.path.dirname(os.path.abspath(__file__))
candidate_roots = [
    project_root,
    os.path.abspath(os.path.join(project_root, "..")),
    "/home/kyunana/MaixPy_Vision_Tracking",
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
    print("[Warn] 'src' package not found. Using embedded CameraController fallback.")
    try:
        from maix import camera as _maix_camera
    except Exception as _e:
        print("[Error] Maix camera module not available:", _e)
        raise

class MaixVisionSystem:
    def __init__(self):
        print("=== MaixPy Vision Tracking System ===")
        print("Initializing system...")

        self.camera = CameraController(width=512, height=320)
        self.detector = None  # 待集成：检测模块
        self.recognizer = None  # 待集成：识别模块
        self.gimbal = None  # 待集成：云台模块
        self.running = False
        self.disp = None
        self.mode = os.getenv("MODE", "recognize")  # record | recognize | track
        if self.mode not in ("record", "recognize", "track"):
            self.mode = "recognize"
        print(f"Mode: {self.mode}")
        self.max_persons = 3
        
        # 虚拟按钮管理器
        self.button_manager = None
        self.button_click_count = 0
        
        # FPS计算相关
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0
        self.last_fps_update = time.time()

    def initialize_modules(self):
        try:
            print("📷 Initializing camera...")
            ok = self.camera.initialize_camera()
            if not ok:
                print("❌ Camera init failed")
                return False
            print("✅ Camera ok")

            # 初始化人物检测器
            print("🔍 Initializing person detector...")
            try:
                from src.vision.detection.person_detector import PersonDetector
                camera_width, camera_height = self.camera.get_resolution()
                self.detector = PersonDetector(camera_width, camera_height)
                print("✅ Person detector initialized")
            except Exception as e:
                print(f"✗ Person detector initialization failed: {e}")
                self.detector = None

            print("🧠 Initializing recognizer... (skipped - to be integrated)")
            print("🎮 Initializing gimbal... (skipped - to be integrated)")

            # 初始化显示（如果可用）
            if _maix_display is not None:
                try:
                    self.disp = _maix_display.Display()
                except Exception:
                    self.disp = None
            
            # 初始化虚拟按钮
            print("🔘 Initializing virtual buttons...")
            try:
                from src.hardware.button import VirtualButtonManager, ButtonPresets
                camera_width, camera_height = self.camera.get_resolution()
                self.button_manager = VirtualButtonManager(camera_width, camera_height)
                self._setup_buttons()
                print("✅ Virtual buttons initialized")
            except Exception as e:
                print(f"✗ Virtual buttons initialization failed: {e}")
                self.button_manager = None

            print("✅ All modules initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize modules: {e}")
            return False

    def start_system(self):
        if not self.initialize_modules():
            print("Failed to start system")
            return

        print("🚀 Starting main loop...")
        self.running = True
        try:
            self.main_loop()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ System error: {e}")
        finally:
            self.cleanup()

    def main_loop(self):
        while self.running and (_maix_app is None or not _maix_app.need_exit()):
            img = self.camera.capture_image()
            if img is None:
                continue

            # 显示画面
            if self.disp is not None:
                try:
                    # 处理虚拟按钮输入
                    if self.button_manager:
                        clicked_button = self.button_manager.check_touch_input()
                        self.button_manager.update()
                    
                    # 运行当前模式（占位，待模块接入）
                    if self.mode == "record":
                        self._mode_record(img)
                    elif self.mode == "recognize":
                        self._mode_recognize(img)
                    elif self.mode == "track":
                        self._mode_track(img)
                    
                    # 绘制界面信息
                    self._draw_ui_info(img)
                    
                    # 绘制虚拟按钮
                    if self.button_manager:
                        self.button_manager.draw_all(img)
                        self.button_manager.draw_touch_indicator(img)
                    
                    # 显示
                    self.disp.show(img)
                except Exception:
                    pass

            # TODO: 检测/识别/云台/触摸UI等

            # 初始化帧计数器（如果还没有）
            if not hasattr(self, 'frame_count'):
                self.frame_count = 0
            self.frame_count += 1
            
            # 更新FPS计算
            self._update_fps()
            
            time.sleep(0.01)

    def cleanup(self):
        print("🧹 Cleaning up...")
        try:
            if self.camera:
                self.camera.release_camera()
            # 云台模块尚未集成
        finally:
            print("✅ Cleanup completed")

    # =============== 虚拟按钮相关 ===============
    def _update_fps(self):
        """更新FPS计算（每半秒更新一次）"""
        self.fps_counter += 1
        current_time = time.time()
        
        # 每半秒更新一次FPS显示
        if current_time - self.last_fps_update >= 0.5:
            time_diff = current_time - self.fps_start_time
            if time_diff > 0:
                self.current_fps = self.fps_counter / time_diff
                
            # 重置计数器
            self.fps_counter = 0
            self.fps_start_time = current_time
            self.last_fps_update = current_time
    
    def _setup_buttons(self):
        """设置虚拟按钮"""
        if not self.button_manager:
            return
        
        try:
            from src.hardware.button import ButtonPresets
            
            # 创建简化的控制按钮（适合调试）
            width, height = self.camera.get_resolution()
            
            # 调试按钮
            debug_btn = self.button_manager.create_button(
                button_id='debug',
                x=width - 100,
                y=20,
                width=80,
                height=40,
                text='DEBUG'
            )
            debug_btn.set_colors(
                normal=(100, 100, 200),  # 蓝色
                active=(150, 150, 255),  # 亮蓝色
                disabled=(60, 60, 60)
            )
            debug_btn.set_click_callback(self._on_button_click)
            
            # 模式切换按钮
            mode_btn = self.button_manager.create_button(
                button_id='mode',
                x=width - 100,
                y=70,
                width=80,
                height=40,
                text=self.mode.upper()
            )
            mode_btn.set_colors(
                normal=(200, 100, 0),    # 橙色
                active=(255, 150, 0),    # 亮橙色
                disabled=(60, 60, 60)
            )
            mode_btn.set_click_callback(self._on_button_click)
            
            # 退出按钮
            exit_btn = self.button_manager.create_button(
                button_id='exit',
                x=20,
                y=20,
                width=60,
                height=30,
                text='EXIT'
            )
            exit_btn.set_colors(
                normal=(150, 0, 0),      # 红色
                active=(200, 0, 0),      # 亮红色
                disabled=(60, 60, 60)
            )
            exit_btn.set_click_callback(self._on_button_click)
            
            print(f"Created {len(self.button_manager.buttons)} virtual buttons")
            
        except Exception as e:
            print(f"Button setup error: {e}")
    
    def _on_button_click(self, button_id: str):
        """
        按钮点击回调函数
        
        Args:
            button_id: 被点击的按钮ID
        """
        self.button_click_count += 1
        print(f"🔘 Button clicked: {button_id} (total clicks: {self.button_click_count})")
        
        if button_id == 'debug':
            self._handle_debug_button()
        elif button_id == 'mode':
            self._handle_mode_button()
        elif button_id == 'exit':
            self._handle_exit_button()
    
    def _handle_debug_button(self):
        """处理调试按钮点击"""
        print("🐛 Debug button pressed!")
        print(f"  Current mode: {self.mode}")
        print(f"  Frame count: {getattr(self, 'frame_count', 0)}")
        print(f"  Camera resolution: {self.camera.get_resolution()}")
        if self.button_manager:
            print(f"  Touch available: {self.button_manager.has_touchscreen}")
        if self.detector:
            debug_info = self.detector.get_debug_info()
            print(f"  Detector status: {debug_info}")
        else:
            print("  Detector: Not initialized")
    
    def _handle_mode_button(self):
        """处理模式切换按钮"""
        modes = ["record", "recognize", "track"]
        current_idx = modes.index(self.mode)
        next_idx = (current_idx + 1) % len(modes)
        self.mode = modes[next_idx]
        
        print(f"🔄 Mode switched to: {self.mode}")
        
        # 更新按钮文字
        if self.button_manager:
            mode_btn = self.button_manager.get_button('mode')
            if mode_btn:
                mode_btn.set_text(self.mode.upper())
    
    def _handle_exit_button(self):
        """处理退出按钮"""
        print("🚪 Exit button pressed - stopping system")
        self.running = False
    
    def _draw_ui_info(self, img):
        """
        绘制界面信息
        
        Args:
            img: 图像对象
        """
        try:
            # 检查是否有MaixPy的image模块
            try:
                from maix import image as _image
            except:
                return
            
            # 系统标题
            title = f"{self.mode.upper()} Mode"
            img.draw_string(200, 10, title, color=_image.COLOR_WHITE, scale=1.0)
            
            # 在EXIT按钮下方显示FPS
            fps_text = f"FPS: {self.current_fps:.1f}"
            img.draw_string(20, 105, fps_text, color=_image.COLOR_BLUE, scale=0.8)
            
        except Exception as e:
            # 绘制错误时输出调试信息
            print(f"UI draw error: {e}")
            import traceback
            traceback.print_exc()

    # =============== 模式实现（占位，用于分模块调试） ===============
    def _mode_record(self, img):
        # 检测+注册流程模式
        if self.detector:
            # 检测人物
            detections = self.detector.detect_persons(img)
            
            if detections:
                # 绘制检测框（录制模式用黄色）
                try:
                    from maix import image as _image
                    for detection in detections:
                        bbox = detection['bbox']
                        x, y, w, h = bbox
                        yellow_color = _image.Color.from_rgb(255, 255, 0)
                        img.draw_rect(x, y, w, h, color=yellow_color, thickness=3)
                        
                        # 绘制提示
                        img.draw_string(x, max(y-20, 0), "Recording...", color=yellow_color)
                except:
                    pass
                
                # TODO: 添加注册逻辑
                # if self.recognizer:
                #     for detection in detections:
                #         face_bbox = detection.get('face_bbox')
                #         if face_bbox:
                #             success, person_id, message = self.recognizer.register_person(img, "NewPerson", face_bbox)
        else:
            # 检测器未初始化时显示提示
            try:
                from maix import image as _image
                img.draw_string(10, 200, "Person detector not available", color=_image.COLOR_WHITE)
            except:
                pass

    def _mode_recognize(self, img):
        # 检测+识别+目标标记模式
        if self.detector:
            # 检测人物
            detections = self.detector.detect_persons(img)
            
            if detections:
                # 绘制检测框
                img = self.detector.draw_detection_boxes(img, detections)
                
                # TODO: 添加识别逻辑
                # for detection in detections:
                #     face_bbox = detection.get('face_bbox')
                #     if face_bbox and self.recognizer:
                #         person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                #         # 绘制识别结果
        else:
            # 检测器未初始化时显示提示
            try:
                from maix import image as _image
                img.draw_string(10, 200, "Person detector not available", color=_image.COLOR_WHITE)
            except:
                pass

    def _mode_track(self, img):
        # 待接入：检测+识别+云台追踪。当前仅显示原图。
        pass


def main():
    system = MaixVisionSystem()
    system.start_system()


if __name__ == "__main__":
    main()
