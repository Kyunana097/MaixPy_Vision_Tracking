#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级人物检测测试示例
支持配置文件和多种检测模式
"""

import sys
import os
from maix import camera, display, app, time, image
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vision.detection.person_detector import PersonDetector
from src.utils.config_manager import ConfigManager

class AdvancedDetectionTest:
    """
    高级检测测试类
    """
    
    def __init__(self, config_path="config/system_config.json"):
        """
        初始化高级检测测试
        
        Args:
            config_path: 配置文件路径
        """
        self.config_manager = ConfigManager(config_path)
        self.load_config()
        
        # 初始化检测器
        self.detector = PersonDetector()
        
        # 统计信息
        self.stats = {
            'total_frames': 0,
            'detection_frames': 0,
            'total_detections': 0,
            'face_detections': 0,
            'person_detections': 0
        }
        
    def load_config(self):
        """
        加载配置参数
        """
        try:
            with open(self.config_manager.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            self.camera_config = config.get('camera', {})
            self.detection_config = config.get('detection', {})
            
            print("配置加载成功:")
            print(f"  摄像头: {self.camera_config}")
            print(f"  检测: {self.detection_config}")
            
        except Exception as e:
            print(f"配置加载失败: {e}")
            # 使用默认配置
            self.camera_config = {'width': 512, 'height': 320}
            self.detection_config = {
                'confidence_threshold': 0.7,
                'min_detection_size': 30,
                'max_detections': 3
            }
    
    def test_realtime_detection(self):
        """
        实时检测测试
        """
        print("开始实时人物检测...")
        print("支持真实人物和动漫人物")
        print("按 Ctrl+C 退出")
        
        # 初始化摄像头
        width = self.camera_config.get('width', 512)
        height = self.camera_config.get('height', 320)
        cam = camera.Camera(width, height)
        disp = display.Display()
        
        try:
            while not app.need_exit():
                img = cam.read()
                if img is None:
                    continue
                
                self.stats['total_frames'] += 1
                
                # 检测人物
                detections = self.detector.detect_persons(img)
                
                if detections:
                    self.stats['detection_frames'] += 1
                    self.stats['total_detections'] += len(detections)
                    
                    # 统计检测类型
                    for det in detections:
                        if det['type'] == 'face':
                            self.stats['face_detections'] += 1
                        elif det['type'] == 'person':
                            self.stats['person_detections'] += 1
                    
                    # 绘制检测结果
                    img = self.detector.draw_green_boxes(img, detections)
                    
                    # 显示检测信息
                    info_text = f"检测: {len(detections)}"
                    img.draw_string(10, 10, info_text, color=image.COLOR_WHITE, scale=1)
                
                # 显示FPS
                fps = time.fps()
                fps_text = f"FPS: {fps:.1f}"
                img.draw_string(10, height-30, fps_text, color=image.COLOR_WHITE, scale=1)
                
                disp.show(img)
                
                # 每100帧显示统计
                if self.stats['total_frames'] % 100 == 0:
                    self.print_statistics()
                
                time.sleep_ms(10)
                
        except KeyboardInterrupt:
            print("\n用户中断退出")
        except Exception as e:
            print(f"检测错误: {e}")
        finally:
            cam.close()
            self.print_final_statistics()
    
    def test_batch_detection(self, image_dir):
        """
        批量图像检测测试
        
        Args:
            image_dir: 图像目录路径
        """
        print(f"批量检测图像目录: {image_dir}")
        
        if not os.path.exists(image_dir):
            print(f"目录不存在: {image_dir}")
            return
        
        # 支持的图像格式
        supported_formats = ['.jpg', '.jpeg', '.png', '.bmp']
        
        image_files = []
        for file in os.listdir(image_dir):
            if any(file.lower().endswith(fmt) for fmt in supported_formats):
                image_files.append(os.path.join(image_dir, file))
        
        if not image_files:
            print("未找到支持的图像文件")
            return
        
        print(f"找到 {len(image_files)} 个图像文件")
        
        results = []
        for i, image_path in enumerate(image_files):
            print(f"处理 {i+1}/{len(image_files)}: {os.path.basename(image_path)}")
            
            try:
                img = image.load(image_path)
                detections = self.detector.detect_persons(img)
                
                result = {
                    'file': os.path.basename(image_path),
                    'detections': len(detections),
                    'details': detections
                }
                results.append(result)
                
                if detections:
                    # 保存检测结果
                    img_result = self.detector.draw_green_boxes(img, detections)
                    output_path = image_path.replace('.', '_detected.')
                    img_result.save(output_path)
                    print(f"  检测到 {len(detections)} 个人物，结果已保存")
                else:
                    print("  未检测到人物")
                    
            except Exception as e:
                print(f"  处理失败: {e}")
        
        # 生成报告
        self.generate_batch_report(results, image_dir)
    
    def generate_batch_report(self, results, image_dir):
        """
        生成批量检测报告
        
        Args:
            results: 检测结果列表
            image_dir: 图像目录
        """
        report = {
            'summary': {
                'total_images': len(results),
                'images_with_detections': sum(1 for r in results if r['detections'] > 0),
                'total_detections': sum(r['detections'] for r in results),
                'avg_detections_per_image': sum(r['detections'] for r in results) / len(results) if results else 0
            },
            'details': results
        }
        
        # 保存报告
        report_path = os.path.join(image_dir, 'detection_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n批量检测报告:")
        print(f"  总图像数: {report['summary']['total_images']}")
        print(f"  有检测的图像: {report['summary']['images_with_detections']}")
        print(f"  总检测数: {report['summary']['total_detections']}")
        print(f"  平均检测/图像: {report['summary']['avg_detections_per_image']:.2f}")
        print(f"  报告已保存到: {report_path}")
    
    def print_statistics(self):
        """
        打印当前统计信息
        """
        if self.stats['total_frames'] > 0:
            detection_rate = self.stats['detection_frames'] / self.stats['total_frames'] * 100
            avg_detections = self.stats['total_detections'] / self.stats['detection_frames'] if self.stats['detection_frames'] > 0 else 0
            
            print(f"统计 - 总帧数: {self.stats['total_frames']}, "
                  f"检测率: {detection_rate:.1f}%, "
                  f"平均检测: {avg_detections:.2f}/帧")
    
    def print_final_statistics(self):
        """
        打印最终统计信息
        """
        print("\n=== 检测统计报告 ===")
        print(f"总帧数: {self.stats['total_frames']}")
        print(f"有检测的帧数: {self.stats['detection_frames']}")
        print(f"检测率: {self.stats['detection_frames']/self.stats['total_frames']*100:.2f}%")
        print(f"总检测数: {self.stats['total_detections']}")
        print(f"人脸检测: {self.stats['face_detections']}")
        print(f"人物检测: {self.stats['person_detections']}")
        
        if self.stats['detection_frames'] > 0:
            avg_detections = self.stats['total_detections'] / self.stats['detection_frames']
            print(f"平均检测数/帧: {avg_detections:.2f}")

def main():
    """
    主函数
    """
    print("高级人物检测测试")
    print("使用方法:")
    print("  python test_detection_advanced.py              - 实时检测")
    print("  python test_detection_advanced.py batch <dir>  - 批量检测")
    
    if len(sys.argv) == 1:
        # 实时检测
        tester = AdvancedDetectionTest()
        tester.test_realtime_detection()
    elif len(sys.argv) >= 3 and sys.argv[1] == "batch":
        # 批量检测
        image_dir = sys.argv[2]
        tester = AdvancedDetectionTest()
        tester.test_batch_detection(image_dir)
    else:
        print("参数错误")

if __name__ == "__main__":
    main()
