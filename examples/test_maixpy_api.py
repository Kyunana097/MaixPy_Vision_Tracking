#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaixPy API测试脚本
用于检查正确的绘制方法
"""

from maix import camera, display, app, time, image
import inspect

def test_image_api():
    """
    测试MaixPy图像API
    """
    print("测试MaixPy图像API...")
    
    # 初始化摄像头
    cam = camera.Camera(320, 240)
    disp = display.Display()
    
    try:
        # 获取一帧图像
        img = cam.read()
        if img is None:
            print("无法获取图像")
            return
        
        print(f"图像类型: {type(img)}")
        print(f"图像大小: {img.width} x {img.height}")
        
        # 检查可用的绘制方法
        print("\n可用的绘制方法:")
        methods = [method for method in dir(img) if method.startswith('draw')]
        for method in methods:
            print(f"  - {method}")
        
        # 检查颜色相关的属性
        print("\n颜色相关属性:")
        color_attrs = [attr for attr in dir(image) if 'color' in attr.lower() or 'Color' in attr]
        for attr in color_attrs:
            print(f"  - image.{attr}")
        
        # 尝试不同的绘制方法
        test_x, test_y, test_w, test_h = 50, 50, 100, 80
        
        print(f"\n测试绘制矩形 ({test_x}, {test_y}, {test_w}, {test_h}):")
        
        # 方法1: draw_rect
        try:
            color = image.Color.from_rgb(0, 255, 0)
            img.draw_rect(test_x, test_y, test_w, test_h, color=color, thickness=2)
            print("✓ draw_rect 成功")
        except Exception as e:
            print(f"✗ draw_rect 失败: {e}")
        
        # 方法2: draw_rectangle
        try:
            color = image.Color.from_rgb(255, 0, 0)
            img.draw_rectangle(test_x+10, test_y+10, test_x+test_w+10, test_y+test_h+10, color=color)
            print("✓ draw_rectangle 成功")
        except Exception as e:
            print(f"✗ draw_rectangle 失败: {e}")
        
        # 方法3: 检查是否有其他绘制方法
        try:
            # 检查所有draw开头的方法的签名
            for method_name in methods:
                method = getattr(img, method_name)
                if callable(method):
                    try:
                        sig = inspect.signature(method)
                        print(f"  {method_name}{sig}")
                    except:
                        print(f"  {method_name}: 无法获取签名")
        except Exception as e:
            print(f"检查方法签名失败: {e}")
        
        # 测试文本绘制
        print(f"\n测试文本绘制:")
        test_text = "Test"
        
        # 尝试draw_string
        try:
            color = image.Color.from_rgb(255, 255, 0)
            img.draw_string(10, 10, test_text, color=color)
            print("✓ draw_string 成功")
        except Exception as e:
            print(f"✗ draw_string 失败: {e}")
        
        # 尝试draw_text
        try:
            color = image.Color.from_rgb(0, 255, 255)
            img.draw_text(10, 30, test_text, color=color)
            print("✓ draw_text 成功")
        except Exception as e:
            print(f"✗ draw_text 失败: {e}")
        
        # 显示测试结果
        disp.show(img)
        print("\n测试图像已显示到屏幕")
        
        # 保存测试图像
        try:
            save_path = "data/temp/api_test.jpg"
            img.save(save_path)
            print(f"测试图像已保存到: {save_path}")
        except Exception as e:
            print(f"保存图像失败: {e}")
        
        time.sleep(3)  # 显示3秒
        
    except Exception as e:
        print(f"API测试出错: {e}")
    finally:
        cam.close()
        print("API测试完成")

def test_color_api():
    """
    测试颜色API
    """
    print("\n测试颜色API...")
    
    try:
        # 测试不同的颜色创建方法
        print("测试颜色创建方法:")
        
        # 方法1: Color.from_rgb
        try:
            color1 = image.Color.from_rgb(255, 0, 0)
            print(f"✓ Color.from_rgb: {color1}")
        except Exception as e:
            print(f"✗ Color.from_rgb 失败: {e}")
        
        # 方法2: 检查预定义颜色
        try:
            predefined_colors = [attr for attr in dir(image) if attr.startswith('COLOR_')]
            print(f"预定义颜色: {predefined_colors}")
            
            if predefined_colors:
                for color_name in predefined_colors[:3]:  # 只测试前3个
                    color_val = getattr(image, color_name)
                    print(f"  {color_name}: {color_val}")
        except Exception as e:
            print(f"✗ 预定义颜色检查失败: {e}")
        
        # 方法3: 检查Color类的其他方法
        try:
            color_methods = [method for method in dir(image.Color) if not method.startswith('_')]
            print(f"Color类方法: {color_methods}")
        except Exception as e:
            print(f"✗ Color类方法检查失败: {e}")
            
    except Exception as e:
        print(f"颜色API测试出错: {e}")

if __name__ == "__main__":
    print("开始MaixPy API测试...")
    test_color_api()
    test_image_api()
    print("API测试结束")
