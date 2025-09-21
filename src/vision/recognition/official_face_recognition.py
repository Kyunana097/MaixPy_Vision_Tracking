"""
官方人脸识别模块 - 基于MaixHub官方模型和API
使用官方FaceRecognize API，确保最佳性能和兼容性
模型来源: https://maixhub.com/model/zoo/59
"""

import os
import json
import time
from maix import nn, image as _image
from maix.nn.app import face
from maix.nn.app.face import FaceRecognize

class OfficialFaceRecognizer:
    """基于官方FaceRecognize API的人脸识别器"""
    
    def __init__(self, 
                 detect_model_path="models/retinaface.mud",
                 feature_model_path="models/fe_resnet.mud",
                 registered_faces_path="data/models/registered_faces.json",
                 similarity_threshold=70.0,  # 官方示例使用70分
                 max_persons=10):
        """
        初始化官方人脸识别器
        
        Args:
            detect_model_path: RetinaFace检测模型路径
            feature_model_path: ResNet特征提取模型路径  
            registered_faces_path: 已注册人脸数据文件
            similarity_threshold: 识别相似度阈值 (0-100分)
            max_persons: 最大注册人数
        """
        print("🧠 初始化官方FaceRecognize识别器...")
        
        self.similarity_threshold = similarity_threshold
        self.max_persons = max_persons
        self.detect_model_path = detect_model_path
        self.feature_model_path = feature_model_path
        self.registered_faces_path = registered_faces_path
        
        # 官方模型参数
        self.detect_threshold = 0.5  # 检测置信度阈值
        self.detect_nms = 0.3        # NMS阈值
        self.max_face_num = 4        # 最大检测人脸数
        self.input_size = (224, 224, 3)  # 输入尺寸
        self.feature_len = 256       # 特征向量长度
        
        # 存储已注册人脸
        self.registered_persons = {}  # {person_id: {name, register_time, ...}}
        self.face_features = []       # [[name, feature], ...] 官方格式
        
        # 初始化识别器
        self.recognizer = None
        self._load_official_recognizer()
        
        # 加载已注册的人脸数据
        self._load_registered_faces()
        
        print(f"✅ 官方识别器初始化完成")
        print(f"   🎯 检测模型: {detect_model_path}")
        print(f"   🧠 特征模型: {feature_model_path}")
        print(f"   📊 已注册人物: {len(self.registered_persons)}")
        print(f"   🎯 相似度阈值: {similarity_threshold}")
        print(f"   🔗 模型来源: MaixHub官方模型")
    
    def _load_official_recognizer(self):
        """加载官方FaceRecognize"""
        try:
            if not os.path.exists(self.detect_model_path):
                raise FileNotFoundError(f"检测模型不存在: {self.detect_model_path}")
            if not os.path.exists(self.feature_model_path):
                raise FileNotFoundError(f"特征模型不存在: {self.feature_model_path}")
            
            print(f"-- 加载检测模型: {self.detect_model_path}")
            m_detect = nn.load(self.detect_model_path)
            print("-- 检测模型加载完成")
            
            print(f"-- 加载特征模型: {self.feature_model_path}")
            m_feature = nn.load(self.feature_model_path)
            print("-- 特征模型加载完成")
            
            # 创建官方FaceRecognize实例
            self.recognizer = FaceRecognize(
                m_detect, 
                m_feature, 
                self.feature_len, 
                self.input_size, 
                self.detect_threshold, 
                self.detect_nms, 
                self.max_face_num
            )
            
            print("✓ 官方FaceRecognize初始化成功")
            print(f"   📐 输入尺寸: {self.input_size}")
            print(f"   🧠 特征维度: {self.feature_len}")
            print(f"   🎯 检测阈值: {self.detect_threshold}")
            
        except Exception as e:
            print(f"✗ 官方识别器加载失败: {e}")
            self.recognizer = None
            raise e
    
    def _load_registered_faces(self):
        """加载已注册的人脸数据"""
        try:
            if os.path.exists(self.registered_faces_path):
                with open(self.registered_faces_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.registered_persons = data.get('persons', {})
                    
                    # 重建face_features列表 (官方格式)
                    features_data = data.get('features', {})
                    for person_id, person_info in self.registered_persons.items():
                        if person_id in features_data:
                            name = person_info['name']
                            feature = features_data[person_id]
                            self.face_features.append([name, feature])
                    
                    print(f"✓ 加载已注册人脸: {len(self.registered_persons)} 个")
            else:
                print("📝 未找到已注册人脸数据，将从空白开始")
                os.makedirs(os.path.dirname(self.registered_faces_path), exist_ok=True)
                
        except Exception as e:
            print(f"✗ 人脸数据加载失败: {e}")
            self.registered_persons = {}
            self.face_features = []
    
    def _save_registered_faces(self):
        """保存已注册的人脸数据"""
        try:
            os.makedirs(os.path.dirname(self.registered_faces_path), exist_ok=True)
            
            # 重建features字典
            features_data = {}
            for person_id, person_info in self.registered_persons.items():
                # 从face_features中找到对应的特征
                for name, feature in self.face_features:
                    if name == person_info['name']:
                        features_data[person_id] = feature
                        break
            
            data = {
                'persons': self.registered_persons,
                'features': features_data,
                'timestamp': time.time(),
                'model_info': {
                    'detect_model': self.detect_model_path,
                    'feature_model': self.feature_model_path,
                    'feature_len': self.feature_len,
                    'similarity_threshold': self.similarity_threshold
                }
            }
            
            with open(self.registered_faces_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print(f"✓ 保存人脸数据: {len(self.registered_persons)} 个人物")
            
        except Exception as e:
            print(f"✗ 人脸数据保存失败: {e}")
    
    def register_person(self, img, person_name, bbox=None):
        """
        注册新人物
        
        Args:
            img: 输入图像 (maix.image.Image)
            person_name: 人物姓名
            bbox: 人脸边界框 (可选，暂不使用)
            
        Returns:
            tuple: (success, person_id, message)
        """
        if self.recognizer is None:
            return False, None, "人脸识别器未初始化"
        
        if len(self.registered_persons) >= self.max_persons:
            return False, None, f"已达到最大注册人数限制 ({self.max_persons})"
        
        try:
            print(f"🔄 开始注册人物: {person_name}")
            
            # 调整图像尺寸到模型要求
            if img.width() != self.input_size[0] or img.height() != self.input_size[1]:
                img_resized = img.resize(self.input_size[0], self.input_size[1])
            else:
                img_resized = img
            
            # 使用官方API检测人脸
            faces = self.recognizer.get_faces(img_resized)
            
            if not faces:
                return False, None, "未检测到人脸"
            
            # 使用第一个检测到的人脸
            face_data = faces[0]
            # face_data = [prob, box, landmarks, feature]
            prob, box, landmarks, feature = face_data
            
            print(f"✓ 检测到人脸，置信度: {prob:.3f}")
            print(f"✓ 人脸位置: {box}")
            print(f"✓ 特征维度: {len(feature) if hasattr(feature, '__len__') else 'unknown'}")
            
            # 生成person_id
            person_id = f"person_{len(self.registered_persons) + 1:02d}"
            
            # 保存人物信息
            self.registered_persons[person_id] = {
                'name': person_name,
                'register_time': time.time(),
                'sample_count': 1,
                'face_box': box,
                'confidence': prob
            }
            
            # 添加到官方格式的特征列表
            self.face_features.append([person_name, feature])
            
            # 保存人脸图像 (可选)
            try:
                face_dir = f"data/faces/{person_id}"
                os.makedirs(face_dir, exist_ok=True)
                
                # 裁剪人脸区域
                x, y, w, h = box
                face_img = img_resized.crop(int(x), int(y), int(w), int(h))
                face_path = os.path.join(face_dir, "face_001.jpg")
                face_img.save(face_path, quality=95)
                print(f"✓ 保存人脸图像: {face_path}")
            except Exception as e:
                print(f"⚠️ 人脸图像保存失败: {e}")
            
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
            img: 输入图像 (maix.image.Image)
            bbox: 人脸边界框 (可选，暂不使用)
            
        Returns:
            tuple: (person_id, confidence, person_name)
        """
        if self.recognizer is None:
            return None, 0.0, "未知"
        
        if not self.face_features:
            return None, 0.0, "未知"
        
        try:
            # 调整图像尺寸到模型要求
            if img.width() != self.input_size[0] or img.height() != self.input_size[1]:
                img_resized = img.resize(self.input_size[0], self.input_size[1])
            else:
                img_resized = img
            
            # 使用官方API检测人脸
            faces = self.recognizer.get_faces(img_resized)
            
            if not faces:
                return None, 0.0, "未知"
            
            # 处理第一个检测到的人脸
            face_data = faces[0]
            prob, box, landmarks, feature = face_data
            
            # 使用官方API进行识别
            recognized_name, score = self._recognize_with_official_api(feature)
            
            if recognized_name and score >= self.similarity_threshold:
                # 查找对应的person_id
                for person_id, person_info in self.registered_persons.items():
                    if person_info['name'] == recognized_name:
                        print(f"🎯 识别成功: {recognized_name} (相似度: {score:.1f})")
                        return person_id, score / 100.0, recognized_name  # 转换为0-1范围
                
                # 如果找不到person_id，说明数据不一致
                print(f"⚠️ 识别到 {recognized_name} 但找不到对应的person_id")
                return None, score / 100.0, recognized_name
            else:
                if recognized_name:
                    print(f"🔍 可能是: {recognized_name} (相似度: {score:.1f}, 低于阈值 {self.similarity_threshold})")
                return None, score / 100.0 if score > 0 else 0.0, "未知"
                
        except Exception as e:
            print(f"✗ 识别失败: {e}")
            return None, 0.0, "未知"
    
    def _recognize_with_official_api(self, query_feature):
        """使用官方API进行特征比较"""
        try:
            max_score = 0
            best_name = None
            
            # 与每个已注册人物比较
            for name, registered_feature in self.face_features:
                # 使用官方compare方法
                score = self.recognizer.compare(registered_feature, query_feature)
                
                if score > max_score:
                    max_score = score
                    best_name = name
            
            return best_name, max_score
            
        except Exception as e:
            print(f"✗ 官方API识别失败: {e}")
            return None, 0
    
    def get_registered_persons(self):
        """获取已注册人物列表 (兼容性接口)"""
        return self.registered_persons
    
    def get_status_info(self):
        """获取状态信息"""
        # 计算总样本数
        total_samples = sum(person_info.get('sample_count', 1) for person_info in self.registered_persons.values())
        
        return {
            'registered_count': len(self.registered_persons),
            'max_persons': self.max_persons,
            'total_samples': total_samples,  # 添加总样本数
            'has_face_detector': self.recognizer is not None,
            'has_official_api': True,
            'model_type': 'Official FaceRecognize API',
            'model_source': 'MaixHub Official Models',
            'detect_model': self.detect_model_path,
            'feature_model': self.feature_model_path,
            'feature_dimension': self.feature_len,
            'similarity_threshold': self.similarity_threshold
        }
    
    def clear_all_persons(self):
        """清空所有已注册人物"""
        try:
            self.registered_persons.clear()
            self.face_features.clear()
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
        except Exception as e:
            print(f"✗ 缩略图加载失败: {e}")
        return None
    
    def get_input_size(self):
        """获取模型输入尺寸 (兼容官方API)"""
        return self.input_size
    
    def get_feature_len(self):
        """获取特征向量长度 (兼容官方API)"""
        return self.feature_len
