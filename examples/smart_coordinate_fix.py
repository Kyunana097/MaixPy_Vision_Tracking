#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能坐标映射修复工具
基于实际触摸数据分析自动计算最佳映射参数
"""

from maix import touchscreen, app, display, image, camera
import time

class SmartCoordinateFix:
    def __init__(self):
        """初始化"""
        # 硬件
        self.disp = display.Display()
        self.cam = camera.Camera(640, 480)  # 使用检测到的分辨率
        
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
        
        # 基于你的实际数据分析
        # 触摸范围: X(60-566) Y(44-352) 
        # 显示范围: X(0-640) Y(0-480)
        self.observed_touch_min_x = 60
        self.observed_touch_max_x = 566
        self.observed_touch_min_y = 44
        self.observed_touch_max_y = 352
        
        # 计算映射参数
        self.calculate_mapping_from_observations()
        
        # 触摸数据收集
        self.touch_samples = []
        self.max_samples = 50
        self.collecting_data = True
        
        # 测试按键 (调整到更容易触摸的位置)
        button_size = 100
        margin = 50
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
        
    def calculate_mapping_from_observations(self):
        """基于观察数据计算映射参数"""
        # 触摸范围
        touch_width = self.observed_touch_max_x - self.observed_touch_min_x
        touch_height = self.observed_touch_max_y - self.observed_touch_min_y
        
        # 计算缩放比例 - 将触摸范围映射到显示范围
        self.scale_x = self.display_width / touch_width
        self.scale_y = self.display_height / touch_height
        
        # 计算偏移 - 将触摸最小值映射到显示0点
        self.offset_x = -self.observed_touch_min_x
        self.offset_y = -self.observed_touch_min_y
        
        print(f"Calculated mapping based on observations:")
        print(f"  Touch range: X({self.observed_touch_min_x}-{self.observed_touch_max_x}) Y({self.observed_touch_min_y}-{self.observed_touch_max_y})")
        print(f"  Touch size: {touch_width} x {touch_height}")
        print(f"  Scale: ({self.scale_x:.3f}, {self.scale_y:.3f})")
        print(f"  Offset: ({self.offset_x}, {self.offset_y})")
    
    def update_mapping_from_samples(self):
        """根据收集的样本更新映射参数"""
        if len(self.touch_samples) < 10:
            return
        
        # 分析收集到的触摸数据
        x_values = [sample['x'] for sample in self.touch_samples]
        y_values = [sample['y'] for sample in self.touch_samples]
        
        actual_min_x = min(x_values)
        actual_max_x = max(x_values)
        actual_min_y = min(y_values)
        actual_max_y = max(y_values)
        
        # 更新观察范围
        self.observed_touch_min_x = actual_min_x
        self.observed_touch_max_x = actual_max_x
        self.observed_touch_min_y = actual_min_y
        self.observed_touch_max_y = actual_max_y
        
        # 重新计算映射
        self.calculate_mapping_from_observations()
        
        print(f"Updated mapping based on {len(self.touch_samples)} samples:")
        print(f"  Actual touch range: X({actual_min_x}-{actual_max_x}) Y({actual_min_y}-{actual_max_y})")
    
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
                
                # 收集触摸数据
                if self.collecting_data and len(self.touch_samples) < self.max_samples:
                    self.touch_samples.append({'x': raw_x, 'y': raw_y})
                    
                    # 每10个样本更新一次映射
                    if len(self.touch_samples) % 10 == 0:
                        self.update_mapping_from_samples()
                        
                    # 收集完成
                    if len(self.touch_samples) >= self.max_samples:
                        self.collecting_data = False
                        print(f"Data collection complete! Final mapping calculated.")
                        
            else:
                if self.touch_pressed_already:
                    self.touch_pressed_already = False
                    
                    # 映射坐标
                    mapped_x, mapped_y = self.map_coordinates(raw_x, raw_y)
                    
                    print(f"Touch: raw({raw_x}, {raw_y}) -> mapped({mapped_x}, {mapped_y})")
                    
                    # 检查按键点击
                    if self.check_button_hit(mapped_x, mapped_y):
                        print("✓ Test button HIT! Mapping is working correctly!")
                    else:
                        btn = self.test_button
                        btn_center_x = btn['x'] + btn['w']//2
                        btn_center_y = btn['y'] + btn['h']//2
                        distance = ((mapped_x - btn_center_x)**2 + 
                                  (mapped_y - btn_center_y)**2)**0.5
                        print(f"✗ Missed button by {distance:.1f} pixels")
                        
                        # 如果还在收集数据，给出提示
                        if self.collecting_data:
                            remaining = self.max_samples - len(self.touch_samples)
                            print(f"  Still collecting data ({remaining} samples remaining)")
        
        except Exception as e:
            print(f"Touch error: {e}")
    
    def draw_interface(self, img):
        """绘制界面"""
        try:
            # 背景信息
            img.draw_string(10, 10, "Smart Coordinate Fix Tool", 
                          image.Color.from_rgb(255, 255, 255))
            
            # 映射参数
            param_text = f"Scale: ({self.scale_x:.3f}, {self.scale_y:.3f}) Offset: ({self.offset_x}, {self.offset_y})"
            img.draw_string(10, 30, param_text, 
                          image.Color.from_rgb(255, 255, 0))
            
            # 触摸范围
            range_text = f"Touch range: X({self.observed_touch_min_x}-{self.observed_touch_max_x}) Y({self.observed_touch_min_y}-{self.observed_touch_max_y})"
            img.draw_string(10, 50, range_text, 
                          image.Color.from_rgb(0, 255, 255))
            
            # 数据收集状态
            if self.collecting_data:
                collected = len(self.touch_samples)
                collection_text = f"Collecting data: {collected}/{self.max_samples} samples"
                color = image.Color.from_rgb(255, 255, 0)
            else:
                collection_text = "Data collection complete - mapping optimized"
                color = image.Color.from_rgb(0, 255, 0)
            
            img.draw_string(10, 70, collection_text, color)
            
            # 指令
            if self.collecting_data:
                instruction = "Touch all areas of screen to collect data"
            else:
                instruction = "Touch the TEST button to verify mapping"
            
            img.draw_string(10, 90, instruction, 
                          image.Color.from_rgb(255, 255, 255))
            
            # 当前触摸状态
            if hasattr(self, 'last_raw_x'):
                mapped_x, mapped_y = self.map_coordinates(self.last_raw_x, self.last_raw_y)
                status_text = f"Last: raw({self.last_raw_x}, {self.last_raw_y}) -> mapped({mapped_x}, {mapped_y})"
                img.draw_string(10, 110, status_text, 
                              image.Color.from_rgb(200, 200, 200))
            
            # 绘制测试按键
            btn = self.test_button
            x, y, w, h = btn['x'], btn['y'], btn['w'], btn['h']
            
            # 按键背景
            if self.collecting_data:
                button_color = image.Color.from_rgb(100, 100, 100)  # 灰色 - 数据收集中
            else:
                button_color = image.Color.from_rgb(0, 255, 0)      # 绿色 - 可测试
            
            img.draw_rect(x, y, w, h, color=button_color, thickness=-1)
            
            # 按键边框
            img.draw_rect(x, y, w, h, color=image.Color.from_rgb(255, 255, 255), thickness=3)
            
            # 按键文字
            text_x = x + (w - len(btn['text']) * 12) // 2
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
                
                # 绘制映射后的触摸点
                img.draw_circle(mapped_x, mapped_y, 15, 
                              image.Color.from_rgb(255, 0, 0), 2)
                img.draw_circle(mapped_x, mapped_y, 5, 
                              image.Color.from_rgb(255, 0, 0), -1)
                
                # 显示坐标
                coord_display = f"({mapped_x},{mapped_y})"
                img.draw_string(mapped_x + 20, mapped_y - 10, coord_display, 
                              image.Color.from_rgb(255, 255, 255))
            
            # 绘制收集到的触摸点（小点）
            if self.touch_samples:
                for sample in self.touch_samples[-20:]:  # 只显示最近20个
                    sx, sy = self.map_coordinates(sample['x'], sample['y'])
                    img.draw_circle(sx, sy, 2, image.Color.from_rgb(0, 255, 255), -1)
            
        except Exception as e:
            print(f"Draw error: {e}")
    
    def run(self):
        """主循环"""
        print("\n=== Smart Coordinate Fix Tool ===")
        print("This tool automatically learns your touchscreen mapping")
        print("Step 1: Touch all areas of the screen to collect data")
        print("Step 2: Touch the TEST button to verify accuracy")
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
            # 输出最终的映射参数
            print("\n=== Final Mapping Parameters ===")
            print(f"Touch range: X({self.observed_touch_min_x}-{self.observed_touch_max_x}) Y({self.observed_touch_min_y}-{self.observed_touch_max_y})")
            print(f"Scale factors: X={self.scale_x:.6f}, Y={self.scale_y:.6f}")
            print(f"Offsets: X={self.offset_x}, Y={self.offset_y}")
            print()
            print("Add these parameters to your code:")
            print(f"self.touch_scale_x = {self.scale_x:.6f}")
            print(f"self.touch_scale_y = {self.scale_y:.6f}")
            print(f"self.touch_offset_x = {self.offset_x}")
            print(f"self.touch_offset_y = {self.offset_y}")
            print("================================")
            
            self.cam.close()
            print("Program ended")

def main():
    tool = SmartCoordinateFix()
    tool.run()

if __name__ == "__main__":
    main()
