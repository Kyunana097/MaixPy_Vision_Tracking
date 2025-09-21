#!/usr/bin/env python3
"""
人脸数据收集脚本
使用MaixCAM收集训练数据，为CNN模型训练做准备
"""

import os
import sys
import time
from maix import camera, display, image, touchscreen, app

class DataCollector:
    """数据收集器"""
    
    def __init__(self, output_dir="training_data"):
        self.output_dir = output_dir
        self.current_person = None
        self.sample_count = 0
        self.target_samples = 30  # 每个人收集30张样本
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"📸 数据收集器初始化完成")
        print(f"   📁 输出目录: {output_dir}")
        print(f"   🎯 目标样本数: {self.target_samples}")
    
    def start_collection(self, person_name):
        """开始收集指定人物的数据"""
        self.current_person = person_name
        self.sample_count = 0
        
        # 创建人物目录
        person_dir = os.path.join(self.output_dir, person_name)
        os.makedirs(person_dir, exist_ok=True)
        
        # 检查已有样本数量
        existing_samples = len([f for f in os.listdir(person_dir) if f.endswith('.jpg')])
        self.sample_count = existing_samples
        
        print(f"🚀 开始收集 {person_name} 的数据")
        print(f"   📊 已有样本: {existing_samples}")
        print(f"   🎯 还需收集: {max(0, self.target_samples - existing_samples)}")
        
        return person_dir
    
    def save_sample(self, img):
        """保存一个样本"""
        if self.current_person is None:
            return False, "未设置当前人物"
        
        try:
            person_dir = os.path.join(self.output_dir, self.current_person)
            
            # 生成文件名
            self.sample_count += 1
            filename = f"sample_{self.sample_count:03d}.jpg"
            filepath = os.path.join(person_dir, filename)
            
            # 调整图像尺寸并保存
            face_img = img.resize(64, 64)
            face_img.save(filepath, quality=95)
            
            remaining = max(0, self.target_samples - self.sample_count)
            print(f"✓ 保存样本 {self.sample_count}/{self.target_samples}: {filename}")
            
            if remaining == 0:
                print(f"🎉 {self.current_person} 的数据收集完成!")
                return True, "collection_complete"
            else:
                print(f"   📊 还需 {remaining} 个样本")
                return True, f"saved_{self.sample_count}"
            
        except Exception as e:
            print(f"✗ 保存样本失败: {e}")
            return False, str(e)
    
    def get_collection_status(self):
        """获取收集状态"""
        if self.current_person is None:
            return "未开始收集"
        
        progress = (self.sample_count / self.target_samples) * 100
        return f"{self.current_person}: {self.sample_count}/{self.target_samples} ({progress:.1f}%)"

def main():
    """主程序"""
    print("=" * 60)
    print("🚀 MaixCAM 人脸数据收集工具")
    print("=" * 60)
    
    # 初始化
    collector = DataCollector()
    
    # 初始化相机和显示
    cam = camera.Camera(320, 240)
    disp = display.Display()
    ts = touchscreen.TouchScreen()
    
    # 人物列表
    persons = ["Person1", "Person2", "Person3"]  # 可以根据需要修改
    current_person_idx = 0
    collecting = False
    
    # 按钮区域定义
    button_height = 30
    button_width = 80
    
    start_btn = (10, 10, button_width, button_height)
    next_btn = (100, 10, button_width, button_height)
    save_btn = (190, 10, button_width, button_height)
    
    print("📋 操作说明:")
    print("   🟢 START: 开始收集当前人物数据")
    print("   🔄 NEXT: 切换到下一个人物")
    print("   💾 SAVE: 保存当前帧作为样本")
    print("   ❌ 点击右上角退出")
    
    while not app.need_exit():
        # 读取图像
        img = cam.read()
        
        # 绘制UI
        current_person = persons[current_person_idx]
        
        # 绘制按钮
        img.draw_rect(start_btn[0], start_btn[1], start_btn[2], start_btn[3], 
                     image.COLOR_GREEN if not collecting else image.COLOR_GRAY, 2)
        img.draw_string(start_btn[0] + 5, start_btn[1] + 8, "START", image.COLOR_WHITE)
        
        img.draw_rect(next_btn[0], next_btn[1], next_btn[2], next_btn[3], 
                     image.COLOR_BLUE, 2)
        img.draw_string(next_btn[0] + 15, next_btn[1] + 8, "NEXT", image.COLOR_WHITE)
        
        img.draw_rect(save_btn[0], save_btn[1], save_btn[2], save_btn[3], 
                     image.COLOR_RED if collecting else image.COLOR_GRAY, 2)
        img.draw_string(save_btn[0] + 15, save_btn[1] + 8, "SAVE", image.COLOR_WHITE)
        
        # 绘制状态信息
        img.draw_string(10, 50, f"当前人物: {current_person}", image.COLOR_WHITE)
        if collecting:
            status = collector.get_collection_status()
            img.draw_string(10, 70, status, image.COLOR_YELLOW)
        else:
            img.draw_string(10, 70, "点击START开始收集", image.COLOR_WHITE)
        
        # 绘制退出按钮
        img.draw_rect(280, 10, 30, 20, image.COLOR_RED, 2)
        img.draw_string(285, 15, "X", image.COLOR_WHITE)
        
        # 处理触摸事件
        x, y, pressed = ts.read()
        if pressed:
            # START按钮
            if (start_btn[0] <= x <= start_btn[0] + start_btn[2] and 
                start_btn[1] <= y <= start_btn[1] + start_btn[3]):
                if not collecting:
                    collector.start_collection(current_person)
                    collecting = True
                    print(f"🚀 开始收集 {current_person} 的数据")
            
            # NEXT按钮
            elif (next_btn[0] <= x <= next_btn[0] + next_btn[2] and 
                  next_btn[1] <= y <= next_btn[1] + next_btn[3]):
                current_person_idx = (current_person_idx + 1) % len(persons)
                collecting = False
                print(f"🔄 切换到: {persons[current_person_idx]}")
            
            # SAVE按钮
            elif (save_btn[0] <= x <= save_btn[0] + save_btn[2] and 
                  save_btn[1] <= y <= save_btn[1] + save_btn[3]):
                if collecting:
                    success, message = collector.save_sample(img)
                    if success and message == "collection_complete":
                        collecting = False
                        print("✅ 当前人物数据收集完成!")
            
            # 退出按钮
            elif (280 <= x <= 310 and 10 <= y <= 30):
                print("👋 退出数据收集")
                break
        
        # 显示图像
        disp.show(img)
        time.sleep(0.1)
    
    print("📊 数据收集总结:")
    for person in persons:
        person_dir = os.path.join(collector.output_dir, person)
        if os.path.exists(person_dir):
            count = len([f for f in os.listdir(person_dir) if f.endswith('.jpg')])
            print(f"   {person}: {count} 个样本")
    
    print("\n🎯 下一步:")
    print("   1. 将training_data目录复制到PC")
    print("   2. 运行: python train_cnn_model.py --data_dir training_data")
    print("   3. 将训练好的模型部署到MaixCAM")

if __name__ == '__main__':
    main()
