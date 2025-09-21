"""
预训练人脸识别模块 - 基于MaixHub官方模型
使用官方预训练的人脸识别模型，无需重新训练
模型来源: https://maixhub.com/model/zoo/59
"""

import os
import json
import time
import numpy as np
from maix import nn, image as _image

class PretrainedFaceRecognizer:
    """基于官方预训练模型的人脸识别器"""
    
    def __init__(self, 
                 detect_model_path="models/face_detect.mud",
                 feature_model_path="models/face_feature.mud", 
                 registered_faces_path="models/registered_faces.json",
                 similarity_threshold=0.7):
        """
        初始化预训练人脸识别器
        
        Args:
            detect_model_path: 人脸检测模型路径
            feature_model_path: 人脸特征提取模型路径  
            registered_faces_path: 已注册人脸数据文件
            similarity_threshold: 识别相似度阈值
        """
        print("🧠 初始化官方预训练人脸识别器...")
        
        self.similarity_threshold = similarity_threshold
        self.detect_model = None
        self.feature_model = None
        self.face_recognizer = None
        self.registered_persons = {}
        self.person_features = {}
        
        # 尝试加载官方FaceRecognizer
        self._load_face_recognizer(detect_model_path, feature_model_path)
        
        # 加载已注册的人脸数据
        self._load_registered_faces(registered_faces_path)
        
        print(f"✓ 预训练识别器初始化完成")
        print(f"   📊 已注册人物: {len(self.registered_persons)}")
        print(f"   🎯 相似度阈值: {similarity_threshold}")
        print(f"   🔗 模型来源: MaixHub官方模型库")
    
    def _load_face_recognizer(self, detect_model_path, feature_model_path):
        """加载官方FaceRecognizer"""
        try:
            # 方法1: 使用官方FaceRecognizer (推荐)
            if os.path.exists(detect_model_path) and os.path.exists(feature_model_path):
                self.face_recognizer = nn.FaceRecognizer(
                    detect_model=detect_model_path,
                    feature_model=feature_model_path,
                    dual_buff=True
                )
                print(f"✓ 成功加载官方FaceRecognizer")
                print(f"   🎯 检测模型: {detect_model_path}")
                print(f"   🧠 特征模型: {feature_model_path}")
                return
            
            # 方法2: 分别加载模型
            if os.path.exists(detect_model_path):
                self.detect_model = nn.load(detect_model_path)
                print(f"✓ 加载检测模型: {detect_model_path}")
            
            if os.path.exists(feature_model_path):
                self.feature_model = nn.load(feature_model_path)
                print(f"✓ 加载特征模型: {feature_model_path}")
            
            if self.detect_model is None and self.feature_model is None:
                print("⚠️ 未找到预训练模型文件")
                print("   请从 https://maixhub.com/model/zoo/59 下载模型")
                
        except Exception as e:
            print(f"✗ 预训练模型加载失败: {e}")
            self.face_recognizer = None
            self.detect_model = None
            self.feature_model = None
    
    def _load_registered_faces(self, registered_faces_path):
        """加载已注册的人脸数据"""
        try:
            if os.path.exists(registered_faces_path):
                with open(registered_faces_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.registered_persons = data.get('persons', {})
                    self.person_features = data.get('features', {})
                    print(f"✓ 加载已注册人脸: {len(self.registered_persons)} 个")
            else:
                print("📝 未找到已注册人脸数据，将从空白开始")
                
        except Exception as e:
            print(f"✗ 人脸数据加载失败: {e}")
            self.registered_persons = {}
            self.person_features = {}
    
    def _save_registered_faces(self, registered_faces_path="models/registered_faces.json"):
        """保存已注册的人脸数据"""
        try:
            os.makedirs(os.path.dirname(registered_faces_path), exist_ok=True)
            
            data = {
                'persons': self.registered_persons,
                'features': self.person_features,
                'timestamp': time.time()
            }
            
            with open(registered_faces_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"✓ 保存人脸数据: {len(self.registered_persons)} 个人物")
            
        except Exception as e:
            print(f"✗ 人脸数据保存失败: {e}")
    
    def register_person(self, img, person_name, bbox=None):
        """
        注册新人物
        
        Args:
            img: 输入图像
            person_name: 人物姓名
            bbox: 人脸边界框 (可选)
            
        Returns:
            tuple: (success, person_id, message)
        """
        if self.face_recognizer is None:
            return False, None, "人脸识别器未初始化"
        
        try:
            print(f"🔄 开始注册人物: {person_name}")
            
            # 检测人脸
            faces = self.face_recognizer.recognize(
                img, 
                conf_th=0.5,    # 检测置信度
                iou_th=0.45,    # NMS阈值
                compare_th=0.1, # 比较阈值（注册时设置较低）
                get_feature=True,  # 获取特征
                get_face=True      # 获取人脸图像
            )
            
            if not faces:
                return False, None, "未检测到人脸"
            
            # 使用第一个检测到的人脸
            face = faces[0]
            
            # 生成person_id
            person_id = f"person_{len(self.registered_persons) + 1:02d}"
            
            # 保存人物信息
            self.registered_persons[person_id] = {
                'name': person_name,
                'face_id': len(self.registered_persons),
                'register_time': time.time(),
                'sample_count': 1
            }
            
            # 保存特征向量
            if hasattr(face, 'feature') and face.feature is not None:
                # 将特征转换为列表以便JSON序列化
                if hasattr(face.feature, 'tolist'):
                    feature_list = face.feature.tolist()
                elif hasattr(face.feature, 'numpy'):
                    feature_list = face.feature.numpy().tolist()
                else:
                    feature_list = list(face.feature)
                
                self.person_features[person_id] = feature_list
                print(f"✓ 提取特征向量: {len(feature_list)} 维")
            
            # 保存人脸图像 (可选)
            if hasattr(face, 'face') and face.face is not None:
                face_dir = f"data/faces/{person_id}"
                os.makedirs(face_dir, exist_ok=True)
                face_path = os.path.join(face_dir, "face_001.jpg")
                face.face.save(face_path, quality=95)
                print(f"✓ 保存人脸图像: {face_path}")
            
            # 保存到文件
            self._save_registered_faces()
            
            print(f"✅ 成功注册人物: {person_name} (ID: {person_id})")
            return True, person_id, f"成功注册 {person_name}"
            
        except Exception as e:
            print(f"✗ 注册失败: {e}")
            return False, None, f"注册失败: {str(e)}"
    
    def recognize_person(self, img, bbox=None):
        """
        识别人物
        
        Args:
            img: 输入图像
            bbox: 人脸边界框 (可选)
            
        Returns:
            tuple: (person_id, confidence, person_name)
        """
        if self.face_recognizer is None:
            return None, 0.0, "未知"
        
        if not self.registered_persons:
            return None, 0.0, "未知"
        
        try:
            # 识别人脸
            faces = self.face_recognizer.recognize(
                img,
                conf_th=0.5,     # 检测置信度
                iou_th=0.45,     # NMS阈值  
                compare_th=0.7,  # 识别比较阈值
                get_feature=True,   # 获取特征
                get_face=False      # 不需要人脸图像
            )
            
            if not faces:
                return None, 0.0, "未知"
            
            # 处理第一个检测到的人脸
            face = faces[0]
            
            # 如果使用内置识别功能
            if hasattr(face, 'class_id') and face.class_id > 0:
                # 官方模型已经完成识别
                confidence = face.score if hasattr(face, 'score') else 0.0
                
                # 查找对应的人物
                for person_id, person_info in self.registered_persons.items():
                    if person_info.get('face_id') == face.class_id - 1:
                        print(f"🎯 官方模型识别: {person_info['name']} (置信度: {confidence:.3f})")
                        return person_id, confidence, person_info['name']
            
            # 如果有特征向量，进行手动比较
            if hasattr(face, 'feature') and face.feature is not None:
                return self._compare_with_registered(face.feature)
            
            return None, 0.0, "未知"
            
        except Exception as e:
            print(f"✗ 识别失败: {e}")
            return None, 0.0, "未知"
    
    def _compare_with_registered(self, query_feature):
        """与已注册人脸进行特征比较"""
        try:
            best_person_id = None
            best_confidence = 0.0
            best_name = "未知"
            
            # 转换查询特征
            if hasattr(query_feature, 'numpy'):
                query_feature = query_feature.numpy()
            elif hasattr(query_feature, 'tolist'):
                query_feature = np.array(query_feature.tolist())
            
            # 与每个已注册人物比较
            for person_id, person_info in self.registered_persons.items():
                if person_id in self.person_features:
                    registered_feature = np.array(self.person_features[person_id])
                    
                    # 计算余弦相似度
                    similarity = self._cosine_similarity(query_feature, registered_feature)
                    
                    print(f"🔍 与{person_info['name']}的相似度: {similarity:.3f}")
                    
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
            print(f"✗ 特征比较失败: {e}")
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
    
    def get_registered_persons(self):
        """获取已注册人物列表 (兼容性接口)"""
        return self.registered_persons
    
    def get_status_info(self):
        """获取状态信息"""
        return {
            'registered_count': len(self.registered_persons),
            'max_persons': 100,  # 理论上无限制
            'has_face_detector': self.face_recognizer is not None,
            'has_pretrained_model': self.face_recognizer is not None,
            'model_type': 'Official Pretrained',
            'model_source': 'MaixHub Model Zoo ID:59'
        }
    
    def clear_all_persons(self):
        """清空所有已注册人物"""
        try:
            self.registered_persons.clear()
            self.person_features.clear()
            self._save_registered_faces()
            print("✅ 已清空所有注册人物")
            return True, "已清空所有人物数据"
        except Exception as e:
            print(f"✗ 清空失败: {e}")
            return False, f"清空失败: {str(e)}"
    
    def get_person_thumbnail(self, person_id):
        """获取人物缩略图"""
        try:
            face_path = f"data/faces/{person_id}/face_001.jpg"
            if os.path.exists(face_path):
                return _image.load(face_path)
        except:
            pass
        return None
