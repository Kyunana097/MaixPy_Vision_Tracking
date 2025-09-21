#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预训练人脸识别器 - 简化版
基于MaixHub模型库的预训练多人识别模型
模型来源: https://maixhub.com/model/zoo/155
"""

import os
import time

class PretrainedRecognizer:
    """使用预训练模型的人脸识别器"""
    
    def __init__(self, model_path="models/model-38558.kmodel"):
        """
        初始化预训练人脸识别器
        
        Args:
            model_path: 预训练模型文件路径
        """
        self.model_path = model_path
        self.model = None
        self.input_size = (224, 224)
        
        # 预训练模型中的人物标签
        self.labels = [
            'huge', 'jiangwen', 'pengyuyan', 'yueyunpeng', 'zhoudongyu', 
            'dilireba', 'fanbingbing', 'yaoming', 'liuyifei', 'zhoujielun'
        ]
        
        # 中文名称映射
        self.chinese_names = {
            'huge': '胡歌',
            'jiangwen': '姜文', 
            'pengyuyan': '彭于晏',
            'yueyunpeng': '岳云鹏',
            'zhoudongyu': '周冬雨',
            'dilireba': '迪丽热巴',
            'fanbingbing': '范冰冰',
            'yaoming': '姚明',
            'liuyifei': '刘亦菲',
            'zhoujielun': '周杰伦'
        }
        
        # 置信度阈值
        self.confidence_threshold = 0.6
        
        # 初始化模型
        self.model_loaded = self._init_model()
    
    def _init_model(self):
        """初始化KPU模型"""
        try:
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                print(f"❌ 模型文件不存在: {self.model_path}")
                return False
            
            print(f"📥 加载预训练人脸识别模型: {self.model_path}")
            
            # 尝试导入KPU模块
            try:
                import KPU as kpu
                self.kpu = kpu
                self.model = self.kpu.load(self.model_path)
                print("✅ KPU模型加载成功")
                return True
            except ImportError:
                print("❌ KPU模块不可用，尝试使用maix.nn")
                try:
                    from maix import nn
                    # 尝试使用maix.nn加载.kmodel文件
                    # 注意: 这可能不兼容，但我们尝试一下
                    print("⚠️ 警告: .kmodel文件可能与maix.nn不兼容")
                    return False
                except ImportError:
                    print("❌ 无法导入任何神经网络模块")
                    return False
            
        except Exception as e:
            print(f"❌ 模型初始化失败: {e}")
            return False
    
    def recognize(self, img):
        """
        识别图像中的人物
        
        Args:
            img: 输入图像
            
        Returns:
            tuple: (person_id, confidence, person_name)
        """
        try:
            if not self.model_loaded or not self.model:
                print("❌ 模型未加载")
                return None, 0.0, "unknown"
            
            # 调整图像尺寸到模型输入要求
            if hasattr(img, 'resize'):
                resized_img = img.resize(self.input_size[0], self.input_size[1])
            else:
                resized_img = img
            
            # 前向推理
            start_time = time.ticks_ms() if hasattr(time, 'ticks_ms') else int(time.time() * 1000)
            
            # 使用KPU进行推理
            fmap = self.kpu.forward(self.model, resized_img)
            predictions = fmap[:]
            
            inference_time = (time.ticks_ms() if hasattr(time, 'ticks_ms') else int(time.time() * 1000)) - start_time
            
            # 找到最高置信度的预测
            max_confidence = max(predictions)
            max_index = predictions.index(max_confidence)
            
            print(f"🔍 识别结果: 推理{inference_time}ms, 置信度{max_confidence:.3f}, 索引{max_index}")
            
            # 检查置信度是否达到阈值
            if max_confidence >= self.confidence_threshold:
                person_name = self.labels[max_index]
                chinese_name = self.chinese_names.get(person_name, person_name)
                person_id = f"pretrained_{max_index:02d}"
                
                print(f"✅ 识别成功: {chinese_name} ({person_name})")
                return person_id, max_confidence, chinese_name
            else:
                print(f"❌ 置信度过低: {max_confidence:.3f} < {self.confidence_threshold}")
                return None, max_confidence, "unknown"
                
        except Exception as e:
            print(f"✗ 识别失败: {e}")
            return None, 0.0, "unknown"
    
    def get_status_info(self):
        """获取识别器状态信息"""
        return {
            'model_loaded': self.model_loaded,
            'model_path': self.model_path,
            'supported_persons': len(self.labels),
            'person_list': list(self.chinese_names.values()),
            'confidence_threshold': self.confidence_threshold,
            'input_size': self.input_size
        }
    
    def get_supported_persons(self):
        """获取支持识别的人物列表"""
        return [
            {
                'id': f"pretrained_{i:02d}",
                'name': self.chinese_names.get(label, label),
                'english_name': label
            }
            for i, label in enumerate(self.labels)
        ]
    
    def set_confidence_threshold(self, threshold):
        """设置置信度阈值"""
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            print(f"✅ 置信度阈值已设置为: {threshold}")
            return True
        else:
            print(f"❌ 无效的置信度阈值: {threshold}")
            return False
    
    def __del__(self):
        """析构函数，清理资源"""
        try:
            if self.model and hasattr(self, 'kpu'):
                self.kpu.deinit(self.model)
                print("✅ KPU模型资源已清理")
        except:
            pass
