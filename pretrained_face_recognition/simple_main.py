#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaixPy 简化人脸识别系统
不依赖外部训练集，使用基础检测功能

作者: Kyunana
版本: v1.0.0-simple
"""

# ==================== 版本信息 ====================
__version__ = "1.0.0-simple"
__release_date__ = "2025-09-21"
__author__ = "Kyunana"
__description__ = "MaixPy 简化人脸识别系统"

def print_version_info():
    print("=" * 60)
    print(f"🚀 {__description__}")
    print(f"📦 版本: {__version__}")
    print(f"📅 发布日期: {__release_date__}")
    print(f"👨‍💻 作者: {__author__}")
    print("=" * 60)

# ==================== MaixPy模块导入 ====================
try:
    from maix import camera, display, image, touchscreen, app
    MAIX_AVAILABLE = True
    print("✅ MaixPy modules imported successfully")
except ImportError:
    MAIX_AVAILABLE = False
    print("❌ Failed to import MaixPy modules")
    print("⚠️ Running in simulation mode")

class SimpleVisionSystem:
    """简化版视觉系统"""
    
    def __init__(self):
        self.running = False
        self.frame_count = 0
        self.fps = 0.0
        self.last_time = 0
        
        # 初始化组件
        self.camera = None
        self.display = None
        self.touchscreen = None
        
        # 按钮状态
        self.buttons = {
            'exit': {'x': 540, 'y': 20, 'w': 80, 'h': 40, 'text': 'EXIT', 'pressed': False},
            'debug': {'x': 540, 'y': 70, 'w': 80, 'h': 40, 'text': 'DEBUG', 'pressed': False},
            'mode': {'x': 540, 'y': 120, 'w': 80, 'h': 40, 'text': 'MODE', 'pressed': False}
        }
        
        self.current_mode = "detect"  # detect, record, track
        self.modes = ["detect", "record", "track"]
        self.mode_index = 0
        
        # 检测结果
        self.detection_results = []
        
    def initialize_components(self):
        """初始化组件"""
        print("=== MaixPy Simple Vision System ===")
        print("Initializing system...")
        
        try:
            # 初始化摄像头
            if MAIX_AVAILABLE:
                print("📷 Initializing camera...")
                self.camera = camera.Camera()
                print("✅ Camera initialized")
                
                # 初始化显示器
                print("🖥️ Initializing display...")
                self.display = display.Display()
                print("✅ Display initialized")
                
                # 初始化触摸屏
                print("👆 Initializing touchscreen...")
                self.touchscreen = touchscreen.TouchScreen()
                print("✅ Touchscreen initialized")
            else:
                print("⚠️ MaixPy not available, using simulation mode")
                
            print("✅ All components initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Component initialization failed: {e}")
            return False
    
    def is_point_in_button(self, x, y, button):
        """检查点是否在按钮内"""
        return (button['x'] <= x <= button['x'] + button['w'] and 
                button['y'] <= y <= button['y'] + button['h'])
    
    def handle_touch(self):
        """处理触摸事件"""
        if not MAIX_AVAILABLE or not self.touchscreen:
            return
            
        try:
            x, y, pressed = self.touchscreen.read()
            
            if pressed:
                # 检查按钮点击
                for button_name, button in self.buttons.items():
                    if self.is_point_in_button(x, y, button):
                        button['pressed'] = True
                        self.on_button_click(button_name)
            else:
                # 释放所有按钮
                for button in self.buttons.values():
                    button['pressed'] = False
                    
        except Exception as e:
            print(f"Touch error: {e}")
    
    def on_button_click(self, button_name):
        """处理按钮点击"""
        print(f"🔘 Button clicked: {button_name}")
        
        if button_name == 'exit':
            print("🚪 Exit button pressed - stopping system")
            self.running = False
            
        elif button_name == 'debug':
            self.show_debug_info()
            
        elif button_name == 'mode':
            self.switch_mode()
    
    def show_debug_info(self):
        """显示调试信息"""
        print("=" * 50)
        print("🐛 === SYSTEM DEBUG INFO ===")
        print(f"  Current mode: {self.current_mode}")
        print(f"  Frame count: {self.frame_count}")
        print(f"  FPS: {self.fps:.2f}")
        print(f"  MaixPy available: {MAIX_AVAILABLE}")
        print(f"  Camera: {'✅' if self.camera else '❌'}")
        print(f"  Display: {'✅' if self.display else '❌'}")
        print(f"  Touchscreen: {'✅' if self.touchscreen else '❌'}")
        print("=" * 50)
    
    def switch_mode(self):
        """切换模式"""
        self.mode_index = (self.mode_index + 1) % len(self.modes)
        self.current_mode = self.modes[self.mode_index]
        self.buttons['mode']['text'] = self.current_mode.upper()
        print(f"🔄 Mode switched to: {self.current_mode}")
    
    def draw_ui(self, img):
        """绘制UI"""
        try:
            # 绘制标题
            img.draw_string(10, 10, f"Simple Vision System v{__version__}", 
                          color=image.COLOR_WHITE, scale=1.2)
            img.draw_string(10, 30, f"FPS: {self.fps:.1f}", 
                          color=image.COLOR_GREEN, scale=1.0)
            
            # 绘制模式信息
            mode_text = f"Mode: {self.current_mode.upper()}"
            img.draw_string(10, 50, mode_text, color=image.COLOR_CYAN, scale=1.0)
            
            # 绘制状态信息
            if self.current_mode == "detect":
                img.draw_string(10, 70, "Detection Mode", color=image.COLOR_YELLOW, scale=1.0)
                img.draw_string(10, 90, "Looking for faces...", color=image.COLOR_WHITE, scale=0.8)
            elif self.current_mode == "record":
                img.draw_string(10, 70, "Record Mode", color=image.COLOR_RED, scale=1.0)
                img.draw_string(10, 90, "Ready to record", color=image.COLOR_WHITE, scale=0.8)
            elif self.current_mode == "track":
                img.draw_string(10, 70, "Track Mode", color=image.COLOR_GREEN, scale=1.0)
                img.draw_string(10, 90, "Tracking faces", color=image.COLOR_WHITE, scale=0.8)
            
            # 绘制按钮
            for button_name, button in self.buttons.items():
                # 按钮背景
                bg_color = image.COLOR_BLUE if button['pressed'] else image.COLOR_GRAY
                img.draw_rect(button['x'], button['y'], button['w'], button['h'], 
                            color=bg_color, thickness=-1)
                
                # 按钮边框
                border_color = image.COLOR_WHITE
                img.draw_rect(button['x'], button['y'], button['w'], button['h'], 
                            color=border_color, thickness=2)
                
                # 按钮文字
                text_x = button['x'] + 10
                text_y = button['y'] + 15
                img.draw_string(text_x, text_y, button['text'], 
                              color=image.COLOR_WHITE, scale=1.0)
            
        except Exception as e:
            print(f"UI draw error: {e}")
    
    def update_fps(self):
        """更新FPS"""
        current_time = 0
        if MAIX_AVAILABLE:
            import time
            current_time = time.ticks_ms()
        else:
            current_time = self.frame_count * 100  # 模拟时间
        
        if self.last_time > 0:
            delta_time = current_time - self.last_time
            if delta_time > 0:
                self.fps = 1000.0 / delta_time
        
        self.last_time = current_time
        self.frame_count += 1
    
    def run(self):
        """运行主循环"""
        if not self.initialize_components():
            print("❌ Failed to initialize components")
            return
        
        if not MAIX_AVAILABLE:
            print("❌ MaixPy not available, cannot run on device")
            print("ℹ️ This is a simulation run")
            self._simulate_run()
            return
        
        print("🚀 Starting main loop...")
        self.running = True
        
        try:
            while self.running and not app.need_exit():
                # 捕获图像
                img = self.camera.read()
                if img is None:
                    continue
                
                # 处理触摸事件
                self.handle_touch()
                
                # 更新FPS
                self.update_fps()
                
                # 绘制UI
                self.draw_ui(img)
                
                # 显示图像
                self.display.show(img)
                
        except KeyboardInterrupt:
            print("Program interrupted by user.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def _simulate_run(self):
        """模拟运行"""
        print("📺 Running in simulation mode...")
        print("Press Ctrl+C to exit")
        
        try:
            while True:
                import time
                time.sleep(0.1)
                self.update_fps()
                
                if self.frame_count % 100 == 0:
                    print(f"📺 Simulation running... FPS: {self.fps:.1f}")
                    
        except KeyboardInterrupt:
            print("Simulation stopped by user.")
    
    def cleanup(self):
        """清理资源"""
        print("🧹 Cleaning up...")
        # MaixPy会自动清理资源
        print("✅ Cleanup completed")

if __name__ == "__main__":
    print_version_info()
    system = SimpleVisionSystem()
    try:
        system.run()
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        system.cleanup()
