#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试校准后的触摸映射精度
验证新的映射参数是否准确
"""

from maix import touchscreen, app, display, image, camera
import time

class TestCalibratedMapping:
    def __init__(self):
        """初始化"""
        # 硬件
        self.disp = display.Display()
        self.cam = camera.Camera(640, 480)
        
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
        
        # 校准后的精确映射参数
        self.touch_scale_x = 1.6615
        self.touch_scale_y = 1.7352
        self.touch_offset_x = -197.74
        self.touch_offset_y = -140.00
        
        print("Applied calibrated mapping parameters:")
        print(f"  Scale: ({self.touch_scale_x:.4f}, {self.touch_scale_y:.4f})")
        print(f"  Offset: ({self.touch_offset_x:.2f}, {self.touch_offset_y:.2f})")
        
        # 测试按键 (四个角落和中心)
        button_size = 80
        margin = 40
        
        self.test_buttons = {
            'top_left': {
                'x': margin, 'y': margin,
                'w': button_size, 'h': button_size,
                'text': 'TL', 'color': (255, 0, 0)
            },
            'top_right': {
                'x': self.display_width - button_size - margin, 'y': margin,
                'w': button_size, 'h': button_size,
                'text': 'TR', 'color': (0, 255, 0)
            },
            'bottom_left': {
                'x': margin, 'y': self.display_height - button_size - margin,
                'w': button_size, 'h': button_size,
                'text': 'BL', 'color': (0, 0, 255)
            },
            'bottom_right': {
                'x': self.display_width - button_size - margin, 
                'y': self.display_height - button_size - margin,
                'w': button_size, 'h': button_size,
                'text': 'BR', 'color': (255, 255, 0)
            },
            'center': {
                'x': self.display_width//2 - button_size//2, 
                'y': self.display_height//2 - button_size//2,
                'w': button_size, 'h': button_size,
                'text': 'CTR', 'color': (255, 0, 255)
            }
        }
        
        # 统计数据
        self.touch_stats = {name: {'hits': 0, 'misses': 0} for name in self.test_buttons.keys()}
        self.total_touches = 0
        
        # 触摸状态
        self.touch_pressed = False
        self.last_raw_x = 0
        self.last_raw_y = 0
        
        print(f"\nTest buttons positioned at:")
        for name, btn in self.test_buttons.items():
            print(f"  {name}: ({btn['x']}, {btn['y']}) to ({btn['x']+btn['w']}, {btn['y']+btn['h']})")
    
    def map_touch_coordinates(self, raw_x, raw_y):
        """映射触摸坐标"""
        mapped_x = int((raw_x + self.touch_offset_x) * self.touch_scale_x)
        mapped_y = int((raw_y + self.touch_offset_y) * self.touch_scale_y)
        
        # 限制范围
        mapped_x = max(0, min(mapped_x, self.display_width - 1))
        mapped_y = max(0, min(mapped_y, self.display_height - 1))
        
        return mapped_x, mapped_y
    
    def check_button_hit(self, x, y):
        """检查点击了哪个按键"""
        for name, btn in self.test_buttons.items():
            if (btn['x'] <= x <= btn['x'] + btn['w'] and 
                btn['y'] <= y <= btn['y'] + btn['h']):
                return name
        return None
    
    def calculate_accuracy(self):
        """计算整体精度"""
        total_hits = sum(stats['hits'] for stats in self.touch_stats.values())
        total_attempts = sum(stats['hits'] + stats['misses'] for stats in self.touch_stats.values())
        
        if total_attempts > 0:
            accuracy = (total_hits / total_attempts) * 100
            return accuracy, total_hits, total_attempts
        return 0, 0, 0
    
    def handle_touch(self):
        """处理触摸事件"""
        if not self.has_touchscreen:
            return
        
        try:
            raw_x, raw_y, pressed = self.ts.read()
            
            if pressed and not self.touch_pressed:
                self.touch_pressed = True
                
            elif not pressed and self.touch_pressed:
                self.touch_pressed = False
                self.total_touches += 1
                
                # 映射坐标
                mapped_x, mapped_y = self.map_touch_coordinates(raw_x, raw_y)
                
                print(f"Touch #{self.total_touches}: raw({raw_x}, {raw_y}) -> mapped({mapped_x}, {mapped_y})")
                
                # 检查按键点击
                hit_button = self.check_button_hit(mapped_x, mapped_y)
                
                if hit_button:
                    self.touch_stats[hit_button]['hits'] += 1
                    print(f"  ✓ HIT: {hit_button.upper()}")
                else:
                    # 找到最近的按键来记录miss
                    closest_button = None
                    min_distance = float('inf')
                    
                    for name, btn in self.test_buttons.items():
                        btn_center_x = btn['x'] + btn['w']//2
                        btn_center_y = btn['y'] + btn['h']//2
                        distance = ((mapped_x - btn_center_x)**2 + (mapped_y - btn_center_y)**2)**0.5
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_button = name
                    
                    if closest_button:
                        self.touch_stats[closest_button]['misses'] += 1
                        print(f"  ✗ MISS: closest to {closest_button.upper()} (distance: {min_distance:.1f}px)")
                
                # 显示当前统计
                accuracy, hits, attempts = self.calculate_accuracy()
                print(f"  Accuracy: {accuracy:.1f}% ({hits}/{attempts})")
                print()
        
        except Exception as e:
            print(f"Touch error: {e}")
    
    def draw_interface(self, img):
        """绘制界面"""
        try:
            # 标题
            img.draw_string(10, 10, "Calibrated Touch Mapping Test", 
                          image.Color.from_rgb(255, 255, 255))
            
            # 映射参数
            param_text = f"Scale: ({self.touch_scale_x:.4f}, {self.touch_scale_y:.4f})"
            img.draw_string(10, 30, param_text, 
                          image.Color.from_rgb(255, 255, 0))
            
            offset_text = f"Offset: ({self.touch_offset_x:.2f}, {self.touch_offset_y:.2f})"
            img.draw_string(10, 50, offset_text, 
                          image.Color.from_rgb(255, 255, 0))
            
            # 统计信息
            accuracy, hits, attempts = self.calculate_accuracy()
            stats_text = f"Accuracy: {accuracy:.1f}% ({hits}/{attempts}) Total: {self.total_touches}"
            img.draw_string(10, 70, stats_text, 
                          image.Color.from_rgb(0, 255, 255))
            
            # 指令
            img.draw_string(10, 90, "Touch the colored buttons to test mapping accuracy", 
                          image.Color.from_rgb(255, 255, 255))
            
            # 绘制测试按键
            for name, btn in self.test_buttons.items():
                x, y, w, h = btn['x'], btn['y'], btn['w'], btn['h']
                r, g, b = btn['color']
                color = image.Color.from_rgb(r, g, b)
                
                # 按键背景
                img.draw_rect(x, y, w, h, color=color, thickness=-1)
                
                # 按键边框
                img.draw_rect(x, y, w, h, color=image.Color.from_rgb(255, 255, 255), thickness=3)
                
                # 按键文字
                text = btn['text']
                text_x = x + (w - len(text) * 12) // 2
                text_y = y + (h - 16) // 2
                img.draw_string(text_x, text_y, text, 
                              color=image.Color.from_rgb(0, 0, 0))
                
                # 统计信息
                stats = self.touch_stats[name]
                hits = stats['hits']
                misses = stats['misses']
                total = hits + misses
                
                if total > 0:
                    accuracy = (hits / total) * 100
                    stats_text = f"{accuracy:.0f}%"
                else:
                    stats_text = "0%"
                
                img.draw_string(x, y - 20, stats_text, 
                              image.Color.from_rgb(255, 255, 255))
            
            # 当前触摸点
            if self.touch_pressed:
                mapped_x, mapped_y = self.map_touch_coordinates(self.last_raw_x, self.last_raw_y)
                img.draw_circle(mapped_x, mapped_y, 15, 
                              image.Color.from_rgb(255, 255, 255), 2)
                img.draw_circle(mapped_x, mapped_y, 5, 
                              image.Color.from_rgb(255, 255, 255), -1)
        
        except Exception as e:
            print(f"Draw error: {e}")
    
    def run(self):
        """主循环"""
        print("\n=== Calibrated Touch Mapping Test ===")
        print("Touch the colored buttons to test mapping accuracy:")
        print("- TL (Red): Top Left")
        print("- TR (Green): Top Right") 
        print("- BL (Blue): Bottom Left")
        print("- BR (Yellow): Bottom Right")
        print("- CTR (Magenta): Center")
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
            # 输出最终统计
            print("\n=== Final Test Results ===")
            accuracy, hits, attempts = self.calculate_accuracy()
            print(f"Overall Accuracy: {accuracy:.1f}% ({hits}/{attempts})")
            print(f"Total Touches: {self.total_touches}")
            print()
            
            print("Per-button results:")
            for name, stats in self.touch_stats.items():
                total = stats['hits'] + stats['misses']
                if total > 0:
                    btn_accuracy = (stats['hits'] / total) * 100
                    print(f"  {name.upper()}: {btn_accuracy:.1f}% ({stats['hits']}/{total})")
                else:
                    print(f"  {name.upper()}: No touches")
            
            print("===============================")
            
            self.cam.close()
            print("Test completed")

def main():
    test = TestCalibratedMapping()
    test.run()

if __name__ == "__main__":
    main()
