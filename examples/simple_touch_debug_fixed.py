#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的触摸调试工具（修复f-string错误）
基于 standalone_gui.py 的核心触摸逻辑，但简化为最小测试版本
"""

from maix import touchscreen, app, display, image, camera
import time

class SimpleTouchDebug:
    def __init__(self):
        """初始化"""
        # 硬件
        self.disp = display.Display()
        self.cam = camera.Camera(512, 320)
        
        # 触摸屏
        try:
            self.ts = touchscreen.TouchScreen()
            self.has_touchscreen = True
            print("✓ Touchscreen initialized")
        except:
            self.ts = None
            self.has_touchscreen = False
            print("✗ Touchscreen not available")
        
        # 触摸状态
        self.touch_pressed_already = False
        self.last_touch_x = 0
        self.last_touch_y = 0
        self.last_touch_pressed = False
        
        # 按键配置 (与standalone_gui一致)
        width, height = 512, 320
        button_width = 80
        button_height = 35
        button_margin = 10
        
        self.buttons = {
            'record': {
                'x': width - button_width - button_margin,
                'y': height - 2 * button_height - 2 * button_margin,
                'w': button_width,
                'h': button_height,
                'text': 'Record',
                'enabled': True
            },
            'clear': {
                'x': width - button_width - button_margin,
                'y': height - button_height - button_margin,
                'w': button_width,
                'h': button_height,
                'text': 'Clear',
                'enabled': True
            }
        }
        
        print("Button areas:")
        for name, btn in self.buttons.items():
            x1, y1 = btn['x'], btn['y']
            x2, y2 = btn['x'] + btn['w'], btn['y'] + btn['h']
            print(f"  {name}: ({x1},{y1}) to ({x2},{y2})")
    
    def check_touch(self):
        """检查触摸（与standalone_gui逻辑一致）"""
        if not self.has_touchscreen:
            return None
        
        try:
            # 读取触摸屏状态
            x, y, pressed = self.ts.read()
            
            # 检查触摸状态变化
            if x != self.last_touch_x or y != self.last_touch_y or pressed != self.last_touch_pressed:
                if pressed != self.last_touch_pressed:  # 按压状态变化时打印
                    print(f"Touch state: ({x}, {y}) pressed={pressed}")
                self.last_touch_x = x
                self.last_touch_y = y
                self.last_touch_pressed = pressed
            
            # 处理触摸事件
            if pressed:
                self.touch_pressed_already = True
            else:
                # 触摸释放时检查是否点击了按键
                if self.touch_pressed_already:
                    print(f"Touch released at: ({x}, {y})")
                    self.touch_pressed_already = False
                    
                    # 检查按键区域
                    button_clicked = self.check_button_touch(x, y)
                    if button_clicked:
                        print(f"✓ Button clicked: {button_clicked}")
                        return button_clicked
                    else:
                        print("✗ Touch outside button areas")
        
        except Exception as e:
            print(f"Touch detection error: {e}")
        
        return None
    
    def check_button_touch(self, touch_x, touch_y):
        """检查按键触摸（与standalone_gui逻辑一致）"""
        for button_name, button in self.buttons.items():
            x, y, w, h = button['x'], button['y'], button['w'], button['h']
            
            x2, y2 = x + w, y + h
            print(f"  Checking {button_name}: touch({touch_x},{touch_y}) vs button({x},{y})-({x2},{y2})")
            
            # 检查触摸点是否在按键区域内
            if (x <= touch_x <= x + w and 
                y <= touch_y <= y + h and 
                button['enabled']):
                
                return button_name
        
        return None
    
    def draw_buttons(self, img):
        """绘制按键"""
        for button_name, button in self.buttons.items():
            x, y, w, h = button['x'], button['y'], button['w'], button['h']
            
            # 选择颜色
            if button_name == 'record':
                color = image.Color.from_rgb(0, 255, 0)  # 绿色
            else:
                color = image.Color.from_rgb(255, 0, 0)  # 红色
            
            try:
                # 绘制按键
                img.draw_rect(x, y, w, h, color=color, thickness=-1)
                img.draw_rect(x, y, w, h, color=image.Color.from_rgb(255, 255, 255), thickness=2)
                
                # 绘制文字
                text = button['text']
                text_x = x + 10
                text_y = y + 10
                img.draw_string(text_x, text_y, text, color=image.Color.from_rgb(255, 255, 255))
                
                # 显示坐标 - 避免f-string中的方括号
                coord_text = f"{x},{y}"
                img.draw_string(x, y - 15, coord_text, color=image.Color.from_rgb(255, 255, 0))
                
            except Exception as e:
                print(f"Draw button error: {e}")
    
    def draw_info(self, img):
        """绘制信息"""
        try:
            # 标题
            img.draw_string(10, 10, "Simple Touch Debug", color=image.Color.from_rgb(255, 255, 255))
            
            # 触摸状态
            if self.has_touchscreen:
                status = "Touchscreen Ready"
                color = image.Color.from_rgb(0, 255, 0)
            else:
                status = "No Touchscreen"
                color = image.Color.from_rgb(255, 0, 0)
            
            img.draw_string(10, 30, status, color=color)
            
            # 触摸坐标
            if hasattr(self, 'last_touch_x'):
                touch_info = f"Last: ({self.last_touch_x}, {self.last_touch_y}) pressed={self.last_touch_pressed}"
                img.draw_string(10, 50, touch_info, color=image.Color.from_rgb(200, 200, 200))
            
            # 指令
            img.draw_string(10, 280, "Touch the buttons to test", color=image.Color.from_rgb(255, 255, 0))
            
        except Exception as e:
            print(f"Draw info error: {e}")
    
    def run(self):
        """主循环"""
        print("Starting simple touch debug...")
        
        try:
            while not app.need_exit():
                # 获取摄像头图像
                img = self.cam.read()
                if img is None:
                    img = image.Image(512, 320)
                
                # 检查触摸
                clicked_button = self.check_touch()
                if clicked_button:
                    print(f"🎯 BUTTON PRESSED: {clicked_button}")
                
                # 绘制界面
                self.draw_info(img)
                self.draw_buttons(img)
                
                # 绘制触摸点
                if self.touch_pressed_already and hasattr(self, 'last_touch_x'):
                    try:
                        img.draw_circle(self.last_touch_x, self.last_touch_y, 8, 
                                      image.Color.from_rgb(255, 255, 255), 2)
                    except:
                        pass
                
                # 显示
                self.disp.show(img)
                
                # 帧率
                time.sleep(0.033)
                
        except KeyboardInterrupt:
            print("\nProgram interrupted")
        except Exception as e:
            print(f"Program error: {e}")
        finally:
            print("Cleaning up...")
            self.cam.close()
            print("Program ended")

def main():
    debug = SimpleTouchDebug()
    debug.run()

if __name__ == "__main__":
    main()
