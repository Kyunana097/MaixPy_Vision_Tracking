#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摄像头测试示例
用于测试摄像头基本功能
"""

import sys
import os
from maix import camera, display, app, time

cam = camera.Camera(512, 320)   # Manually set resolution
                                # | 手动设置分辨率
disp = display.Display()        # MaixCAM default is 522x368
                                # | MaixCAM 默认是 522x368
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from src.hardware.camera.camera_controller import CameraController
# from src.utils.image_processor import ImageProcessor

def test_camera():
    """
    测试摄像头功能
    """
    print("摄像头测试开始...")
    print("按 Ctrl+C 退出测试")
    
    try:
        # 1. 初始化摄像头 (已在全局初始化)
        # 2. 持续采集图像
        frame_count = 0
        
        while not app.need_exit():  # 检查是否需要退出
            # 3. 采集图像
            img = cam.read()            # Get one frame from camera, img is maix.image.Image type object
                                        # | 从摄像头获取一帧图像，img 是 maix.image.Image 类型的对象
            
            if img is None:
                print("获取图像失败")
                continue
            
            # 4. 显示图像
            disp.show(img)              # Show image to screen
                                        # | 将图像显示到屏幕
            
            # 计算和显示帧率
            fps = time.fps()            # Calculate FPS between last time fps() call and this time call.
                                        # | 计算两次 fps 函数调用之间的帧率
            
            frame_count += 1
            
            # 每30帧打印一次信息
            if frame_count % 30 == 0:
                print(f"帧数: {frame_count}, 时间: {1000/fps:.02f}ms, FPS: {fps:.02f}")
            
            # 5. 可选：保存测试图像（每100帧保存一张）
            if frame_count % 100 == 0:
                try:
                    save_path = f"data/temp/test_frame_{frame_count}.jpg"
                    img.save(save_path)
                    print(f"保存测试图像: {save_path}")
                except Exception as e:
                    print(f"保存图像失败: {e}")
            
            # 短暂延时，避免过度占用CPU
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        print("\n检测到 Ctrl+C，正在退出...")
    except Exception as e:
        print(f"摄像头测试出错: {e}")
    finally:
        # 清理资源
        print("摄像头测试完成")
        try:
            cam.close()
            print("摄像头资源已释放")
        except:
            pass

if __name__ == "__main__":
    test_camera()
