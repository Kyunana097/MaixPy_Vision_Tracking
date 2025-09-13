#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物检测调试版本
用于调试MaixPy API兼容性问题
"""

from maix import camera, display, app, time, image, nn
import sys

def debug_image_api():
    """
    调试图像API
    """
    print("=== MaixPy图像API调试 ===")
    
    # 初始化摄像头
    cam = camera.Camera(512, 320)
    
    # 获取一帧图像
    img = cam.read()
    
    if img is None:
        print("错误: 无法获取图像")
        cam.close()
        return
    
    print(f"图像类型: {type(img)}")
    print(f"图像尺寸: {img.width} x {img.height}")
    
    # 测试可用的绘制方法
    methods_to_test = [
        'draw_rect',
        'draw_rectangle', 
        'draw_box',
        'draw_string',
        'draw_text',
        'draw_circle'
    ]
    
    available_methods = []
    for method in methods_to_test:
        if hasattr(img, method):
            available_methods.append(method)
            print(f"✓ 可用方法: {method}")
        else:
            print(f"× 不可用方法: {method}")
    
    # 测试颜色API
    color_methods = []
    if hasattr(image, 'COLOR_GREEN'):
        color_methods.append('COLOR_GREEN')
        print(f"✓ 可用颜色: COLOR_GREEN = {image.COLOR_GREEN}")
    if hasattr(image, 'Color'):
        color_methods.append('Color')
        print(f"✓ 可用颜色类: Color")
        try:
            green = image.Color.from_rgb(0, 255, 0)
            print(f"  Color.from_rgb(0, 255, 0) = {green}")
        except Exception as e:
            print(f"  Color.from_rgb() 错误: {e}")
    
    # 尝试实际绘制
    print("\n=== 绘制测试 ===")
    
    # 测试位置
    x, y, w, h = 50, 50, 100, 100
    
    # 尝试不同的绘制方法
    if 'draw_rect' in available_methods:
        try:
            if 'Color' in color_methods:
                color = image.Color.from_rgb(0, 255, 0)
                img.draw_rect(x, y, w, h, color=color, thickness=2)
                print("✓ draw_rect 成功")
            else:
                img.draw_rect(x, y, w, h, color=(0, 255, 0), thickness=2)
                print("✓ draw_rect (元组颜色) 成功")
        except Exception as e:
            print(f"× draw_rect 失败: {e}")
    
    if 'draw_rectangle' in available_methods:
        try:
            if 'COLOR_GREEN' in color_methods:
                img.draw_rectangle(x+110, y, w, h, color=image.COLOR_GREEN, thickness=2)
                print("✓ draw_rectangle 成功")
        except Exception as e:
            print(f"× draw_rectangle 失败: {e}")
    
    # 测试文本绘制
    if 'draw_string' in available_methods:
        try:
            if 'Color' in color_methods:
                color = image.Color.from_rgb(255, 255, 255)
                img.draw_string(x, y-20, "Test", color=color)
                print("✓ draw_string 成功")
        except Exception as e:
            print(f"× draw_string 失败: {e}")
    
    cam.close()
    print("\n=== API调试完成 ===")

def simple_detection_test():
    """
    简化的检测测试，不绘制图形
    """
    print("\n=== 简化检测测试 ===")
    
    # 初始化检测器
    print("正在初始化检测器...")
    
    face_detector = None
    object_detector = None
    
    # 尝试初始化人脸检测器
    try:
        face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
        print("✓ 人脸检测器初始化成功")
    except Exception as e:
        print(f"× 人脸检测器初始化失败: {e}")
    
    # 尝试初始化物体检测器
    try:
        object_detector = nn.YOLOv5(model="/root/models/yolov5s.mud") 
        print("✓ 物体检测器初始化成功")
    except Exception as e:
        print(f"× 物体检测器初始化失败: {e}")
    
    if face_detector is None and object_detector is None:
        print("错误: 没有可用的检测器")
        return
    
    # 初始化摄像头
    cam = camera.Camera(512, 320)
    disp = display.Display()
    
    print("开始检测（不绘制图形）...")
    print("按 Ctrl+C 退出")
    
    try:
        frame_count = 0
        detection_count = 0
        
        while not app.need_exit():
            img = cam.read()
            if img is None:
                continue
            
            frame_count += 1
            detections = []
            
            # 人脸检测
            if face_detector:
                try:
                    faces = face_detector.detect(img, conf_th=0.7)
                    for face in faces:
                        detections.append({
                            'type': 'face',
                            'bbox': (face.x, face.y, face.w, face.h),
                            'confidence': face.score
                        })
                except Exception as e:
                    if frame_count % 100 == 1:  # 只偶尔打印错误
                        print(f"人脸检测错误: {e}")
            
            # 物体检测
            if object_detector:
                try:
                    objects = object_detector.detect(img, conf_th=0.5)
                    for obj in objects:
                        if obj.class_id == 0:  # person class
                            detections.append({
                                'type': 'person',
                                'bbox': (obj.x, obj.y, obj.w, obj.h),
                                'confidence': obj.score
                            })
                except Exception as e:
                    if frame_count % 100 == 1:  # 只偶尔打印错误
                        print(f"物体检测错误: {e}")
            
            if detections:
                detection_count += len(detections)
                print(f"帧 {frame_count}: 检测到 {len(detections)} 个目标")
                for i, det in enumerate(detections):
                    print(f"  {i+1}. {det['type']}: {det['confidence']:.3f}")
            
            # 显示原始图像（不绘制检测框）
            disp.show(img)
            
            # 每30帧显示统计
            if frame_count % 30 == 0:
                fps = time.fps()
                print(f"统计: 帧数 {frame_count}, FPS {fps:.1f}, 检测数 {detection_count}")
            
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        print("\n用户中断退出")
    except Exception as e:
        print(f"检测错误: {e}")
    finally:
        cam.close()
        print("检测测试完成")

def main():
    """
    主函数
    """
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # 只调试API
        debug_image_api()
    elif len(sys.argv) > 1 and sys.argv[1] == "simple":
        # 简化检测测试
        simple_detection_test()
    else:
        # 完整调试
        debug_image_api()
        simple_detection_test()

if __name__ == "__main__":
    main()
