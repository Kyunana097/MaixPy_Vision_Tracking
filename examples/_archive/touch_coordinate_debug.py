#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
触摸坐标调试工具
用于检测和修复触摸坐标与显示分辨率的映射问题
"""

from maix import touchscreen, app, display, image, camera
import time

class TouchCoordinateDebug:
    def __init__(self):
        """初始化"""
        # 硬件
        self.disp = display.Display()
        self.cam = camera.Camera(512, 320)
        
        # 获取实际分辨率
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
        
        # 触摸历史记录
        self.touch_history = []
        self.max_history = 20
        
        # 校准参数
        self.touch_scale_x = 1.0
        self.touch_scale_y = 1.0
        self.touch_offset_x = 0
        self.touch_offset_y = 0
        
        # 测试点（在显示屏的四角和中心）
        margin = 50
        self.test_points = [
            {"name": "Top-Left", "x": margin, "y": margin},
            {"name": "Top-Right", "x": self.display_width - margin, "y": margin},
            {"name": "Bottom-Left", "x": margin, "y": self.display_height - margin},
            {"name": "Bottom-Right", "x": self.display_width - margin, "y": self.display_height - margin},
            {"name": "Center", "x": self.display_width // 2, "y": self.display_height // 2}
        ]
        
        self.current_test_point = 0
        self.calibration_data = []
        
    def add_touch_to_history(self, x, y, pressed):
        """添加触摸点到历史记录"""
        current_time = time.time()
        self.touch_history.append({
            'x': x, 'y': y, 'pressed': pressed, 'time': current_time
        })
        
        # 保持历史记录长度
        if len(self.touch_history) > self.max_history:
            self.touch_history.pop(0)
    
    def map_touch_coordinates(self, raw_x, raw_y):
        """映射触摸坐标到显示坐标"""
        mapped_x = int((raw_x + self.touch_offset_x) * self.touch_scale_x)
        mapped_y = int((raw_y + self.touch_offset_y) * self.touch_scale_y)
        
        # 限制在显示范围内
        mapped_x = max(0, min(mapped_x, self.display_width - 1))
        mapped_y = max(0, min(mapped_y, self.display_height - 1))
        
        return mapped_x, mapped_y
    
    def check_touch(self):
        """检查触摸事件"""
        if not self.has_touchscreen:
            return None, None, False
        
        try:
            raw_x, raw_y, pressed = self.ts.read()
            
            # 映射坐标
            mapped_x, mapped_y = self.map_touch_coordinates(raw_x, raw_y)
            
            # 添加到历史记录
            self.add_touch_to_history(mapped_x, mapped_y, pressed)
            
            return raw_x, raw_y, mapped_x, mapped_y, pressed
            
        except Exception as e:
            print(f"Touch detection error: {e}")
            return None, None, None, None, False
    
    def draw_test_points(self, img):
        """绘制测试点"""
        for i, point in enumerate(self.test_points):
            x, y = point["x"], point["y"]
            name = point["name"]
            
            # 选择颜色
            if i == self.current_test_point:
                color = image.Color.from_rgb(255, 255, 0)  # 黄色 - 当前测试点
                radius = 15
            else:
                color = image.Color.from_rgb(0, 255, 255)  # 青色 - 其他测试点
                radius = 10
            
            try:
                # 绘制圆圈
                img.draw_circle(x, y, radius, color, 2)
                
                # 绘制十字
                img.draw_line(x - radius, y, x + radius, y, color, 2)
                img.draw_line(x, y - radius, x, y + radius, color, 2)
                
                # 标签
                img.draw_string(x - 30, y - 35, name, color)
                img.draw_string(x - 20, y - 20, f"({x},{y})", 
                              image.Color.from_rgb(255, 255, 255))
                
            except Exception as e:
                print(f"Draw test point error: {e}")
    
    def draw_touch_history(self, img):
        """绘制触摸历史轨迹"""
        if len(self.touch_history) < 2:
            return
        
        try:
            # 绘制轨迹线
            for i in range(1, len(self.touch_history)):
                prev_touch = self.touch_history[i-1]
                curr_touch = self.touch_history[i]
                
                if prev_touch['pressed'] and curr_touch['pressed']:
                    # 绘制轨迹线
                    img.draw_line(prev_touch['x'], prev_touch['y'],
                                 curr_touch['x'], curr_touch['y'],
                                 image.Color.from_rgb(255, 0, 255), 2)
            
            # 绘制最新触摸点
            latest = self.touch_history[-1]
            if latest['pressed']:
                img.draw_circle(latest['x'], latest['y'], 8, 
                              image.Color.from_rgb(255, 0, 0), -1)
                
        except Exception as e:
            print(f"Draw touch history error: {e}")
    
    def draw_info(self, img):
        """绘制信息面板"""
        try:
            # 背景
            info_height = 120
            img.draw_rect(0, 0, self.display_width, info_height, 
                         image.Color.from_rgb(0, 0, 0), -1)
            img.draw_rect(0, 0, self.display_width, info_height, 
                         image.Color.from_rgb(255, 255, 255), 2)
            
            # 标题
            img.draw_string(10, 10, "Touch Coordinate Debug", 
                          image.Color.from_rgb(255, 255, 255))
            
            # 显示分辨率
            resolution_text = f"Display: {self.display_width}x{self.display_height}"
            img.draw_string(10, 30, resolution_text, 
                          image.Color.from_rgb(0, 255, 255))
            
            # 当前触摸状态
            if self.touch_history:
                latest = self.touch_history[-1]
                status_color = image.Color.from_rgb(0, 255, 0) if latest['pressed'] else image.Color.from_rgb(255, 255, 255)
                status_text = f"Touch: ({latest['x']}, {latest['y']}) {'PRESSED' if latest['pressed'] else 'RELEASED'}"
                img.draw_string(10, 50, status_text, status_color)
            
            # 校准信息
            calib_text = f"Scale: {self.touch_scale_x:.2f}, {self.touch_scale_y:.2f} Offset: {self.touch_offset_x}, {self.touch_offset_y}"
            img.draw_string(10, 70, calib_text, image.Color.from_rgb(255, 255, 0))
            
            # 当前测试点
            if self.current_test_point < len(self.test_points):
                point = self.test_points[self.current_test_point]
                test_text = f"Touch: {point['name']} at ({point['x']}, {point['y']})"
                img.draw_string(10, 90, test_text, image.Color.from_rgb(255, 255, 0))
            else:
                img.draw_string(10, 90, "Calibration complete! Touch anywhere to test", 
                              image.Color.from_rgb(0, 255, 0))
            
        except Exception as e:
            print(f"Draw info error: {e}")
    
    def handle_calibration_touch(self, raw_x, raw_y, mapped_x, mapped_y):
        """处理校准触摸"""
        if self.current_test_point >= len(self.test_points):
            return
        
        target_point = self.test_points[self.current_test_point]
        target_x, target_y = target_point["x"], target_point["y"]
        
        print(f"Calibration {self.current_test_point + 1}/{len(self.test_points)}:")
        print(f"  Target: ({target_x}, {target_y})")
        print(f"  Raw touch: ({raw_x}, {raw_y})")
        print(f"  Mapped touch: ({mapped_x}, {mapped_y})")
        print(f"  Error: ({mapped_x - target_x}, {mapped_y - target_y})")
        
        # 记录校准数据
        self.calibration_data.append({
            'target_x': target_x, 'target_y': target_y,
            'raw_x': raw_x, 'raw_y': raw_y,
            'mapped_x': mapped_x, 'mapped_y': mapped_y
        })
        
        self.current_test_point += 1
        
        # 如果完成校准，计算校准参数
        if self.current_test_point >= len(self.test_points):
            self.calculate_calibration()
    
    def calculate_calibration(self):
        """计算校准参数"""
        if len(self.calibration_data) < 4:
            return
        
        print("\n=== Calibration Analysis ===")
        
        # 计算原始坐标范围
        raw_x_values = [d['raw_x'] for d in self.calibration_data]
        raw_y_values = [d['raw_y'] for d in self.calibration_data]
        target_x_values = [d['target_x'] for d in self.calibration_data]
        target_y_values = [d['target_y'] for d in self.calibration_data]
        
        raw_x_range = max(raw_x_values) - min(raw_x_values)
        raw_y_range = max(raw_y_values) - min(raw_y_values)
        target_x_range = max(target_x_values) - min(target_x_values)
        target_y_range = max(target_y_values) - min(target_y_values)
        
        if raw_x_range > 0 and raw_y_range > 0:
            # 计算缩放比例
            scale_x = target_x_range / raw_x_range
            scale_y = target_y_range / raw_y_range
            
            print(f"Recommended scale factors:")
            print(f"  Scale X: {scale_x:.4f}")
            print(f"  Scale Y: {scale_y:.4f}")
            
            # 计算偏移
            avg_raw_x = sum(raw_x_values) / len(raw_x_values)
            avg_raw_y = sum(raw_y_values) / len(raw_y_values)
            avg_target_x = sum(target_x_values) / len(target_x_values)
            avg_target_y = sum(target_y_values) / len(target_y_values)
            
            offset_x = avg_target_x - avg_raw_x * scale_x
            offset_y = avg_target_y - avg_raw_y * scale_y
            
            print(f"Recommended offsets:")
            print(f"  Offset X: {offset_x:.2f}")
            print(f"  Offset Y: {offset_y:.2f}")
            
            # 应用建议的校准参数
            self.touch_scale_x = scale_x
            self.touch_scale_y = scale_y
            self.touch_offset_x = offset_x
            self.touch_offset_y = offset_y
            
            print(f"\nCalibration applied! Touch anywhere to test accuracy.")
        
        print("========================\n")
    
    def run(self):
        """主循环"""
        print("=== Touch Coordinate Debug Tool ===")
        print("This tool helps debug touch coordinate mapping issues")
        print(f"Display resolution: {self.display_width} x {self.display_height}")
        print()
        
        if not self.has_touchscreen:
            print("⚠️  Warning: Touchscreen not available")
            return
        
        print("Calibration mode: Touch each yellow point in sequence")
        print("After calibration, touch anywhere to test accuracy")
        print()
        
        last_pressed = False
        
        try:
            while not app.need_exit():
                # 获取摄像头图像或创建空白图像
                img = self.cam.read()
                if img is None:
                    img = image.Image(self.display_width, self.display_height)
                
                # 检查触摸
                result = self.check_touch()
                if result[0] is not None:
                    raw_x, raw_y, mapped_x, mapped_y, pressed = result
                    
                    # 检测触摸释放事件
                    if last_pressed and not pressed:
                        print(f"\nTouch detected:")
                        print(f"  Raw coordinates: ({raw_x}, {raw_y})")
                        print(f"  Mapped coordinates: ({mapped_x}, {mapped_y})")
                        
                        # 处理校准
                        if self.current_test_point < len(self.test_points):
                            self.handle_calibration_touch(raw_x, raw_y, mapped_x, mapped_y)
                    
                    last_pressed = pressed
                
                # 绘制界面
                self.draw_info(img)
                self.draw_test_points(img)
                self.draw_touch_history(img)
                
                # 显示
                self.disp.show(img)
                
                # 帧率控制
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
    debug = TouchCoordinateDebug()
    debug.run()

if __name__ == "__main__":
    main()
