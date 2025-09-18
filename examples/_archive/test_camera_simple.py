#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单摄像头测试示例
用于快速测试摄像头功能
"""

from maix import camera, display, app, time
import os

def test_camera_simple():
    """
    简单的摄像头测试（手动按键退出）
    """
    print("简单摄像头测试开始...")
    print("程序会持续显示摄像头画面")
    print("在MaixCAM设备上按按键退出，或在终端按 Ctrl+C")
    
    # 初始化摄像头和显示器
    cam = camera.Camera(512, 320)
    disp = display.Display()
    
    try:
        while not app.need_exit():
            # 捕获图像
            img = cam.read()
            
            if img is not None:
                # 显示图像
                disp.show(img)
            
            # 计算FPS
            fps = time.fps()
            if fps > 0:
                print(f"\rFPS: {fps:.1f}", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\n用户中断退出")
    except Exception as e:
        print(f"\n错误: {e}")
    finally:
        print("\n关闭摄像头...")
        cam.close()
        print("测试完成")

def test_camera_frames(num_frames=100):
    """
    测试捕获指定数量的帧
    
    Args:
        num_frames: 要捕获的帧数
    """
    print(f"测试捕获 {num_frames} 帧图像...")
    
    cam = camera.Camera(512, 320)
    disp = display.Display()
    
    try:
        for i in range(num_frames):
            if app.need_exit():
                break
                
            img = cam.read()
            if img is not None:
                disp.show(img)
                
                # 每10帧保存一张图像
                if i % 10 == 0:
                    try:
                        save_path = f"data/temp/frame_{i:04d}.jpg"
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        img.save(save_path)
                        print(f"保存: {save_path}")
                    except Exception as e:
                        print(f"保存失败: {e}")
            
            # 显示进度
            if (i + 1) % 10 == 0:
                fps = time.fps()
                print(f"进度: {i+1}/{num_frames}, FPS: {fps:.1f}")
                
    except Exception as e:
        print(f"测试出错: {e}")
    finally:
        cam.close()
        print("帧测试完成")

if __name__ == "__main__":
    import sys
    
    print("选择测试模式:")
    print("1. 持续显示模式")
    print("2. 定量帧测试模式")
    
    if len(sys.argv) > 1 and sys.argv[1] == "frames":
        # 使用命令行参数指定帧数
        frames = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        test_camera_frames(frames)
    else:
        # 默认持续显示模式
        test_camera_simple()
