"""
CNN人脸识别模块 - MaixCAM端实现
使用预训练的CNN模型进行高精度人脸识别
"""

import os
import json
import numpy as np
from maix import nn, image as _image

class CNNFaceRecognizer:
    """基于CNN的人脸识别器"""
    
    def __init__(self, model_path="models/face_encoder.mud", 
                 features_path="models/person_features.npy",
                 labels_path="models/person_labels.json",
                 similarity_threshold=0.7):
        """
        初始化CNN人脸识别器
        
        Args:
            model_path: CNN特征提取模型路径
            features_path: 预计算的人物特征向量文件
            labels_path: 人物标签映射文件
            similarity_threshold: 识别相似度阈值
        """
        print("🧠 初始化CNN人脸识别器...")
        
        self.similarity_threshold = similarity_threshold
        self.model = None
        self.person_features = None
        self.person_labels = {}
        self.registered_persons = {}
        
        # 尝试加载CNN模型
        self._load_cnn_model(model_path)
        
        # 加载预计算的人物特征
        self._load_person_features(features_path, labels_path)
        
        print(f"✓ CNN识别器初始化完成")
        print(f"   📊 已加载 {len(self.person_labels)} 个人物特征")
        print(f"   🎯 相似度阈值: {similarity_threshold}")
    
    def _load_cnn_model(self, model_path):
        """加载CNN特征提取模型"""
        try:
            if os.path.exists(model_path):
                self.model = nn.load(model_path)
                print(f"✓ 成功加载CNN模型: {model_path}")
            else:
                print(f"⚠️ CNN模型不存在: {model_path}")
                print("   请先训练并转换CNN模型")
        except Exception as e:
            print(f"✗ CNN模型加载失败: {e}")
            self.model = None
    
    def _load_person_features(self, features_path, labels_path):
        """加载预计算的人物特征向量"""
        try:
            # 加载特征向量
            if os.path.exists(features_path):
                self.person_features = np.load(features_path)
                print(f"✓ 加载人物特征向量: {self.person_features.shape}")
            
            # 加载标签映射
            if os.path.exists(labels_path):
                with open(labels_path, 'r', encoding='utf-8') as f:
                    self.person_labels = json.load(f)
                
                # 构建registered_persons格式（兼容性）
                for idx, (label_id, name) in enumerate(self.person_labels.items()):
                    person_id = f"person_{int(label_id)+1:02d}"
                    self.registered_persons[person_id] = {
                        'name': name,
                        'feature_index': int(label_id),
                        'sample_count': 1
                    }
                
                print(f"✓ 加载人物标签: {len(self.person_labels)} 个")
            
        except Exception as e:
            print(f"✗ 人物特征加载失败: {e}")
            self.person_features = None
            self.person_labels = {}
    
    def extract_features(self, face_img):
        """
        使用CNN提取人脸特征
        
        Args:
            face_img: 人脸图像 (64x64)
            
        Returns:
            np.array: 特征向量 (128维)
        """
        if self.model is None:
            return None
        
        try:
            # 预处理图像
            processed_img = self._preprocess_image(face_img)
            
            # CNN特征提取
            features = self.model.forward(processed_img)
            
            # 转换为numpy数组并归一化
            if hasattr(features, 'numpy'):
                features = features.numpy()
            elif hasattr(features, 'to_numpy'):
                features = features.to_numpy()
            
            # L2归一化
            norm = np.linalg.norm(features)
            if norm > 0:
                features = features / norm
            
            return features
            
        except Exception as e:
            print(f"✗ CNN特征提取失败: {e}")
            return None
    
    def _preprocess_image(self, img):
        """
        预处理图像用于CNN输入
        
        Args:
            img: MaixPy图像对象
            
        Returns:
            预处理后的图像张量
        """
        try:
            # 调整尺寸到64x64
            if img.width() != 64 or img.height() != 64:
                img = img.resize(64, 64)
            
            # 转换为RGB格式（如果需要）
            # 注意：这里需要根据MaixPy的实际API进行调整
            
            return img
            
        except Exception as e:
            print(f"✗ 图像预处理失败: {e}")
            return img
    
    def recognize_person(self, img, bbox=None):
        """
        识别人物
        
        Args:
            img: 输入图像
            bbox: 人脸边界框
            
        Returns:
            tuple: (person_id, confidence, person_name)
        """
        if self.model is None or self.person_features is None:
            return None, 0.0, "未知"
        
        try:
            # 提取人脸区域
            if bbox is not None:
                x, y, w, h = bbox
                face_img = img.crop(x, y, w, h)
                face_img = face_img.resize(64, 64)
            else:
                # 如果没有bbox，假设整个图像就是人脸
                face_img = img.resize(64, 64)
            
            # 提取CNN特征
            query_features = self.extract_features(face_img)
            if query_features is None:
                return None, 0.0, "未知"
            
            # 与所有已知人物比较
            best_person_id = None
            best_confidence = 0.0
            best_name = "未知"
            
            for person_id, person_info in self.registered_persons.items():
                feature_idx = person_info['feature_index']
                person_features = self.person_features[feature_idx]
                
                # 计算余弦相似度
                similarity = self._cosine_similarity(query_features, person_features)
                
                print(f"🔍 与{person_info['name']}的CNN相似度: {similarity:.3f}")
                
                if similarity > best_confidence:
                    best_confidence = similarity
                    best_person_id = person_id
                    best_name = person_info['name']
            
            # 判断是否达到识别阈值
            if best_confidence >= self.similarity_threshold:
                return best_person_id, best_confidence, best_name
            else:
                return None, best_confidence, "未知"
                
        except Exception as e:
            print(f"✗ CNN识别失败: {e}")
            return None, 0.0, "未知"
    
    def _cosine_similarity(self, vec1, vec2):
        """计算余弦相似度"""
        try:
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            print(f"✗ 相似度计算失败: {e}")
            return 0.0
    
    def register_person(self, img, person_name, bbox=None):
        """
        注册新人物（CNN版本需要重新训练）
        
        Args:
            img: 输入图像
            person_name: 人物姓名
            bbox: 人脸边界框
            
        Returns:
            tuple: (success, person_id, message)
        """
        # CNN版本的注册需要重新训练模型
        # 这里只是保存图像供后续训练使用
        
        try:
            # 创建数据目录
            data_dir = f"training_data/{person_name}"
            os.makedirs(data_dir, exist_ok=True)
            
            # 提取并保存人脸图像
            if bbox is not None:
                x, y, w, h = bbox
                face_img = img.crop(x, y, w, h)
            else:
                face_img = img
            
            face_img = face_img.resize(64, 64)
            
            # 生成文件名
            existing_files = len([f for f in os.listdir(data_dir) if f.endswith('.jpg')])
            filename = f"sample_{existing_files+1:03d}.jpg"
            filepath = os.path.join(data_dir, filename)
            
            # 保存图像
            face_img.save(filepath, quality=95)
            
            print(f"✓ 已保存训练图像: {filepath}")
            print("📝 提示: 收集足够样本后，请重新训练CNN模型")
            
            return True, f"temp_{person_name}", f"已保存 {person_name} 的训练样本"
            
        except Exception as e:
            print(f"✗ 保存训练样本失败: {e}")
            return False, None, f"保存失败: {str(e)}"
    
    def get_registered_persons(self):
        """获取已注册人物列表（兼容性接口）"""
        return self.registered_persons
    
    def get_status_info(self):
        """获取状态信息"""
        return {
            'registered_count': len(self.registered_persons),
            'max_persons': len(self.person_labels),
            'has_face_detector': True,
            'has_cnn_model': self.model is not None,
            'has_person_features': self.person_features is not None,
            'model_type': 'CNN'
        }
    
    def clear_all_persons(self):
        """清空所有人物（CNN版本需要重新训练）"""
        return True, "CNN版本需要重新训练模型来清空人物"
    
    def get_person_thumbnail(self, person_id):
        """获取人物缩略图（暂不支持）"""
        return None
