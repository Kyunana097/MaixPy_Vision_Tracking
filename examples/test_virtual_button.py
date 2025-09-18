#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟按钮模块测试示例
演示如何使用新的虚拟按钮模块
"""

import sys
import os
import time

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from maix import camera, display, app
    from src.hardware.button import VirtualButtonManager, ButtonPresets
    HAS_MAIX = True
except ImportError:
    print("MaixPy modules not available, running in simulation mode")
    HAS_MAIX = False


class VirtualButtonDemo:
    """
    虚拟按钮演示类
    """
    
    def __init__(self, width=512, height=320):
        """
        初始化演示
        
        Args:
            width: 显示宽度
            height: 显示高度
        """
        self.width = width
        self.height = height
        
        # 硬件初始化
        if HAS_MAIX:
            print("Initializing camera and display...")
            self.cam = camera.Camera(width, height)
            self.disp = display.Display()
        
        # 创建虚拟按钮管理器
        print("Creating virtual button manager...")
        self.button_manager = VirtualButtonManager(width, height)
        self.button_manager.enable_debug(True)  # 启用调试模式
        
        # 创建按钮
        self._create_buttons()
        
        # 状态变量
        self.running = True
        self.frame_count = 0
        self.button_click_count = {'record': 0, 'clear': 0, 'exit': 0}
        
        print("Virtual button demo initialized!")
        print("Available buttons:", list(self.button_manager.buttons.keys()))
    
    def _create_buttons(self):
        """创建演示按钮"""
        # 使用预设按钮布局
        buttons = ButtonPresets.create_simple_control_buttons(self.button_manager)
        
        # 为按钮设置回调函数
        for button_id, button in buttons.items():
            button.set_click_callback(self._on_button_click)
        
        print(f"Created {len(buttons)} buttons:")
        for button_id, button in buttons.items():
            print(f"  - {button_id}: {button.text} at ({button.x}, {button.y})")
    
    def _on_button_click(self, button_id: str):
        """
        按钮点击回调函数
        
        Args:
            button_id: 被点击的按钮ID
        """
        self.button_click_count[button_id] = self.button_click_count.get(button_id, 0) + 1
        
        print(f"Button clicked: {button_id} (count: {self.button_click_count[button_id]})")
        
        if button_id == 'record':
            self._handle_record_click()
        elif button_id == 'clear':
            self._handle_clear_click()
        elif button_id == 'exit':
            self._handle_exit_click()
    
    def _handle_record_click(self):
        """处理记录按钮点击"""
        print("📹 Record function triggered!")
        # TODO: 实际的记录逻辑
        
        # 示例：临时改变按钮文字
        record_btn = self.button_manager.get_button('record')
        if record_btn:
            if record_btn.text == 'REC':
                record_btn.set_text('STOP')
                record_btn.set_colors(normal=(200, 100, 0))  # 橙色
            else:
                record_btn.set_text('REC')
                record_btn.set_colors(normal=(0, 120, 0))    # 绿色
    
    def _handle_clear_click(self):
        """处理清除按钮点击"""
        print("🗑️ Clear function triggered!")
        # TODO: 实际的清除逻辑
        
        # 重置记录按钮状态
        record_btn = self.button_manager.get_button('record')
        if record_btn:
            record_btn.set_text('REC')
            record_btn.set_colors(normal=(0, 120, 0))
    
    def _handle_exit_click(self):
        """处理退出按钮点击"""
        print("🚪 Exit function triggered!")
        self.running = False
    
    def _draw_info(self, img):
        """
        绘制信息文字
        
        Args:
            img: 图像对象
        """
        if not HAS_MAIX:
            return
        
        try:
            from maix import image
            
            # 标题
            img.draw_string(10, 10, "Virtual Button Demo", 
                          color=image.Color.from_rgb(255, 255, 255), scale=1.2)
            
            # 点击统计
            y_offset = 40
            for button_id, count in self.button_click_count.items():
                text = f"{button_id}: {count} clicks"
                img.draw_string(10, y_offset, text, 
                              color=image.Color.from_rgb(0, 255, 255))
                y_offset += 20
            
            # 帧数
            img.draw_string(10, self.height - 30, f"Frame: {self.frame_count}", 
                          color=image.Color.from_rgb(128, 128, 128))
            
            # 使用说明
            img.draw_string(10, self.height - 60, "Touch buttons to test", 
                          color=image.Color.from_rgb(255, 255, 0))
        
        except Exception as e:
            print(f"Draw info error: {e}")
    
    def run(self):
        """运行演示主循环"""
        print("Starting virtual button demo...")
        print("Touch the buttons to test functionality")
        print()
        
        try:
            while self.running and (not HAS_MAIX or not app.need_exit()):
                # 获取图像
                if HAS_MAIX:
                    img = self.cam.read()
                    if img is None:
                        continue
                else:
                    # 模拟模式：创建一个虚拟图像
                    import time
                    time.sleep(0.033)  # 模拟30FPS
                    print(f"Frame {self.frame_count} (simulation mode)")
                    self.frame_count += 1
                    
                    # 检查模拟退出条件
                    if self.frame_count > 300:  # 10秒后自动退出
                        print("Demo complete in simulation mode")
                        break
                    continue
                
                self.frame_count += 1
                
                # 检查触摸输入
                clicked_button = self.button_manager.check_touch_input()
                # 注意：回调函数已经在button内部处理了
                
                # 更新按钮状态
                self.button_manager.update()
                
                # 绘制界面
                self._draw_info(img)
                self.button_manager.draw_all(img)
                self.button_manager.draw_touch_indicator(img)
                
                # 显示图像
                self.disp.show(img)
                
                # 控制帧率
                time.sleep(0.033)  # 约30FPS
        
        except KeyboardInterrupt:
            print("\nDemo interrupted by user")
        except Exception as e:
            print(f"Demo runtime error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """清理资源"""
        print("Cleaning up demo resources...")
        if HAS_MAIX and hasattr(self, 'cam'):
            self.cam.close()
        print("Virtual button demo ended")


def main():
    """主函数"""
    print("=== Virtual Button Module Test ===")
    print("Testing the new virtual button module")
    print()
    
    # 解析命令行参数
    width, height = 512, 320
    if len(sys.argv) > 1:
        try:
            width = int(sys.argv[1])
            if len(sys.argv) > 2:
                height = int(sys.argv[2])
        except ValueError:
            print("Invalid resolution, using default 512x320")
    
    print(f"Resolution: {width}x{height}")
    
    # 创建并运行演示
    try:
        demo = VirtualButtonDemo(width, height)
        demo.run()
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
