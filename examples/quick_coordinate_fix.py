#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速坐标映射修复工具
提供几种常见的坐标映射方案供测试
"""

from maix import touchscreen, app, display, image, camera
import time

class QuickCoordinateFix:
    def __init__(self):
        """初始化"""
        # 硬件
        self.disp = display.Display()
        self.cam = camera.Camera(512, 320)
        
        # 显示分辨率
        self.display_width = self.disp.width()
        self.display_height = self.disp.height()
        
        print(f"Display resolution: {self.display_width} x {self.display_height}")
        
        # 触摸屏
        try:
            self.ts = touchscreen.TouchScreen()
            self.has_touchscreen = True
            print("✓ Touchscreen initialized")
        except:
            self.ts = None
            self.has_touchscreen = False
            print("✗ Touchscreen not available")
            return
        
        # 预设的坐标映射方案
        self.mapping_presets = [
            {"name": "1:1 (No scaling)", "scale_x": 1.0, "scale_y": 1.0, "offset_x": 0, "offset_y": 0},
            {"name": "800x480->512x320", "scale_x": 512/800, "scale_y": 320/480, "offset_x": 0, "offset_y": 0},
            {"name": "1024x600->512x320", "scale_x": 512/1024, "scale_y": 320/600, "offset_x": 0, "offset_y": 0},
            {"name": "480x320->512x320", "scale_x": 512/480, "scale_y": 320/320, "offset_x": 0, "offset_y": 0},
            {"name": "Half scale", "scale_x": 0.5, "scale_y": 0.5, "offset_x": 0, "offset_y": 0},
            {"name": "Double scale", "scale_x": 2.0, "scale_y": 2.0, "offset_x": 0, "offset_y": 0},
        ]
        
        self.current_preset = 0
        self.apply_current_preset()
        
        # 测试按键 (在右下角)
        button_size = 80
        margin = 20
        self.test_button = {
            'x': self.display_width - button_size - margin,
            'y': self.display_height - button_size - margin,
            'w': button_size,
            'h': button_size,
            'text': 'TEST'
        }
        
        print(f"Test button area: ({self.test_button['x']}, {self.test_button['y']}) to ({self.test_button['x'] + self.test_button['w']}, {self.test_button['y'] + self.test_button['h']})")
        
        # 触摸状态
        self.touch_pressed_already = False
        self.last_raw_x = 0
        self.last_raw_y = 0
        self.last_pressed = False
        
    def apply_current_preset(self):
        """应用当前预设"""
        preset = self.mapping_presets[self.current_preset]
        self.scale_x = preset["scale_x"]
        self.scale_y = preset["scale_y"]
        self.offset_x = preset["offset_x"]
        self.offset_y = preset["offset_y"]
        
        print(f"\nApplied preset {self.current_preset + 1}/{len(self.mapping_presets)}: {preset['name']}")
        print(f"  Scale: ({self.scale_x:.3f}, {self.scale_y:.3f})")
        print(f"  Offset: ({self.offset_x}, {self.offset_y})")
    
    def map_coordinates(self, raw_x, raw_y):
        """映射坐标"""
        mapped_x = int((raw_x + self.offset_x) * self.scale_x)
        mapped_y = int((raw_y + self.offset_y) * self.scale_y)
        
        # 限制范围
        mapped_x = max(0, min(mapped_x, self.display_width - 1))
        mapped_y = max(0, min(mapped_y, self.display_height - 1))
        
        return mapped_x, mapped_y
    
    def check_button_hit(self, x, y):
        """检查是否点击了测试按键"""
        btn = self.test_button
        return (btn['x'] <= x <= btn['x'] + btn['w'] and 
                btn['y'] <= y <= btn['y'] + btn['h'])
    
    def handle_touch(self):
        """处理触摸事件"""
        if not self.has_touchscreen:
            return
        
        try:
            raw_x, raw_y, pressed = self.ts.read()
            
            # 检查状态变化
            if (raw_x != self.last_raw_x or raw_y != self.last_raw_y or 
                pressed != self.last_pressed):
                
                self.last_raw_x = raw_x
                self.last_raw_y = raw_y
                self.last_pressed = pressed
            
            # 处理触摸
            if pressed:
                self.touch_pressed_already = True
            else:
                if self.touch_pressed_already:
                    self.touch_pressed_already = False
                    
                    # 映射坐标
                    mapped_x, mapped_y = self.map_coordinates(raw_x, raw_y)
                    
                    print(f"Touch: raw({raw_x}, {raw_y}) -> mapped({mapped_x}, {mapped_y})")
                    
                    # 检查按键点击
                    if self.check_button_hit(mapped_x, mapped_y):
                        print("✓ Test button HIT! Switching to next preset...")
                        self.current_preset = (self.current_preset + 1) % len(self.mapping_presets)
                        self.apply_current_preset()
                    else:
                        btn = self.test_button
                        distance = ((mapped_x - (btn['x'] + btn['w']//2))**2 + 
                                  (mapped_y - (btn['y'] + btn['h']//2))**2)**0.5
                        print(f"✗ Missed button by {distance:.1f} pixels")
        
        except Exception as e:
            print(f"Touch error: {e}")
    
    def draw_interface(self, img):
        """绘制界面"""
        try:
            # 背景信息
            img.draw_string(10, 10, "Quick Coordinate Fix Tool", 
                          image.Color.from_rgb(255, 255, 255))
            
            # 当前预设信息
            preset = self.mapping_presets[self.current_preset]
            preset_text = f"Preset {self.current_preset + 1}/{len(self.mapping_presets)}: {preset['name']}"
            img.draw_string(10, 30, preset_text, 
                          image.Color.from_rgb(0, 255, 255))
            
            # 映射参数
            param_text = f"Scale: ({self.scale_x:.3f}, {self.scale_y:.3f}) Offset: ({self.offset_x}, {self.offset_y})"
            img.draw_string(10, 50, param_text, 
                          image.Color.from_rgb(255, 255, 0))
            
            # 指令
            img.draw_string(10, 70, "Touch the TEST button to cycle presets", 
                          image.Color.from_rgb(255, 255, 255))
            
            # 当前触摸状态
            if hasattr(self, 'last_raw_x'):
                mapped_x, mapped_y = self.map_coordinates(self.last_raw_x, self.last_raw_y)
                status_text = f"Last: raw({self.last_raw_x}, {self.last_raw_y}) -> mapped({mapped_x}, {mapped_y})"
                img.draw_string(10, 90, status_text, 
                              image.Color.from_rgb(200, 200, 200))
            
            # 绘制测试按键
            btn = self.test_button
            x, y, w, h = btn['x'], btn['y'], btn['w'], btn['h']
            
            # 按键背景
            button_color = image.Color.from_rgb(0, 255, 0)
            img.draw_rect(x, y, w, h, color=button_color, thickness=-1)
            
            # 按键边框
            img.draw_rect(x, y, w, h, color=image.Color.from_rgb(255, 255, 255), thickness=3)
            
            # 按键文字
            text_x = x + (w - len(btn['text']) * 8) // 2
            text_y = y + (h - 16) // 2
            img.draw_string(text_x, text_y, btn['text'], 
                          color=image.Color.from_rgb(0, 0, 0))
            
            # 按键坐标标注
            coord_text = f"({x},{y})"
            img.draw_string(x, y - 20, coord_text, 
                          image.Color.from_rgb(255, 255, 0))
            
            # 触摸点可视化
            if self.touch_pressed_already and hasattr(self, 'last_raw_x'):
                mapped_x, mapped_y = self.map_coordinates(self.last_raw_x, self.last_raw_y)
                img.draw_circle(mapped_x, mapped_y, 10, 
                              image.Color.from_rgb(255, 0, 0), 2)
                img.draw_circle(mapped_x, mapped_y, 3, 
                              image.Color.from_rgb(255, 0, 0), -1)
            
        except Exception as e:
            print(f"Draw error: {e}")
    
    def run(self):
        """主循环"""
        print("\n=== Quick Coordinate Fix Tool ===")
        print("This tool tests different coordinate mapping presets")
        print("Touch the green TEST button to cycle through presets")
        print("Find the preset that makes the button respond accurately")
        print()
        
        if not self.has_touchscreen:
            print("⚠️  Touchscreen not available")
            return
        
        try:
            while not app.need_exit():
                # 获取图像
                img = self.cam.read()
                if img is None:
                    img = image.Image(self.display_width, self.display_height)
                
                # 处理触摸
                self.handle_touch()
                
                # 绘制界面
                self.draw_interface(img)
                
                # 显示
                self.disp.show(img)
                
                # 控制帧率
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
    tool = QuickCoordinateFix()
    tool.run()

if __name__ == "__main__":
    main()
