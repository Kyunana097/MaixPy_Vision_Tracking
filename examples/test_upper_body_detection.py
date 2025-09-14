#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实人物上半身检测测试
专门用于5x5cm照片，距离50cm+的检测场景
"""

import sys
import os
from maix import camera, display, app, time, image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.detection.person_detector import PersonDetector

def test_upper_body_detection():
    """
    测试真实人物上半身检测功能
    """
    print("=== 真实人物上半身检测测试 ===")
    print("专用于5x5cm人物照片检测")
    print("建议距离: 50cm以上")
    print("按 Ctrl+C 退出测试")
    print()
    
    # 初始化摄像头
    cam = camera.Camera(512, 320)
    disp = display.Display()
    
    # 初始化检测器
    detector = PersonDetector(camera_width=512, camera_height=320)
    
    # 显示调试信息
    debug_info = detector.get_debug_info()
    print("检测器参数:")
    for key, value in debug_info.items():
        print(f"  {key}: {value}")
    print()
    
    if not detector.has_face_detector:
        print("错误: 人脸检测器未成功初始化")
        return
    
    try:
        frame_count = 0
        detection_stats = {'total_frames': 0, 'detection_frames': 0, 'total_detections': 0}
        
        while not app.need_exit():
            img = cam.read()
            if img is None:
                continue
            
            frame_count += 1
            detection_stats['total_frames'] += 1
            
            # 检测人物上半身
            detections = detector.detect_persons(img)
            
            if detections:
                detection_stats['detection_frames'] += 1
                detection_stats['total_detections'] += len(detections)
                
                # 绘制检测结果
                img = detector.draw_green_boxes(img, detections)
                
                # 显示详细信息
                print(f"帧 {frame_count}: 检测到 {len(detections)} 个人物")
                for i, det in enumerate(detections):
                    bbox = det['bbox']
                    face_bbox = det.get('face_bbox', 'None')
                    print(f"  人物 {i+1}:")
                    print(f"    上半身: {bbox}")
                    print(f"    人脸: {face_bbox}")
                    print(f"    置信度: {det['confidence']:.3f}")
                    
                    # 计算物理尺寸估算
                    _, _, w, h = bbox
                    estimated_distance = detector._estimate_distance(w, h)
                    print(f"    估算距离: {estimated_distance:.1f}cm")
            
            # 显示帧信息
            info_text = f"帧:{frame_count} 检测:{len(detections)}"
            try:
                img.draw_string(10, 10, info_text, color=image.Color.from_rgb(255, 255, 255))
            except:
                pass
            
            # 显示检测范围提示
            range_text = f"像素范围:{detector.min_pixel_size}-{detector.max_pixel_size}px"
            try:
                img.draw_string(10, 25, range_text, color=image.Color.from_rgb(255, 255, 255))
            except:
                pass
            
            disp.show(img)
            
            # 每30帧显示统计
            if frame_count % 30 == 0:
                fps = time.fps()
                detection_rate = detection_stats['detection_frames'] / detection_stats['total_frames'] * 100
                avg_detections = detection_stats['total_detections'] / max(detection_stats['detection_frames'], 1)
                print(f"统计 - FPS: {fps:.1f}, 检测率: {detection_rate:.1f}%, 平均检测: {avg_detections:.2f}/帧")
            
            time.sleep_ms(10)
            
    except KeyboardInterrupt:
        print("\n检测测试结束")
    except Exception as e:
        print(f"测试出错: {e}")
    finally:
        cam.close()
        
        # 显示最终统计
        print("\n=== 检测统计报告 ===")
        print(f"总帧数: {detection_stats['total_frames']}")
        print(f"有检测的帧数: {detection_stats['detection_frames']}")
        if detection_stats['total_frames'] > 0:
            detection_rate = detection_stats['detection_frames'] / detection_stats['total_frames'] * 100
            print(f"检测率: {detection_rate:.2f}%")
        print(f"总检测数: {detection_stats['total_detections']}")

def test_static_image(image_path):
    """
    测试静态图像的上半身检测
    
    Args:
        image_path: 图像文件路径
    """
    print(f"测试静态图像: {image_path}")
    
    try:
        img = image.load(image_path)
        detector = PersonDetector(camera_width=img.width, camera_height=img.height)
        
        # 显示图像信息
        print(f"图像尺寸: {img.width}x{img.height}")
        
        # 检测人物
        detections = detector.detect_persons(img)
        
        if detections:
            print(f"检测到 {len(detections)} 个人物:")
            for i, det in enumerate(detections):
                print(f"  人物 {i+1}:")
                print(f"    类型: {det['type']}")
                print(f"    上半身: {det['bbox']}")
                print(f"    人脸: {det.get('face_bbox', 'None')}")
                print(f"    置信度: {det['confidence']:.3f}")
            
            # 绘制检测结果
            img_result = detector.draw_green_boxes(img, detections)
            
            # 保存结果
            output_path = image_path.replace('.', '_upper_body_detected.')
            img_result.save(output_path)
            print(f"检测结果已保存到: {output_path}")
        else:
            print("未检测到人物上半身")
            
    except Exception as e:
        print(f"静态图像检测错误: {e}")

def main():
    """
    主函数
    """
    if len(sys.argv) > 1:
        # 测试静态图像
        test_static_image(sys.argv[1])
    else:
        # 实时检测
        test_upper_body_detection()

if __name__ == "__main__":
    main()
