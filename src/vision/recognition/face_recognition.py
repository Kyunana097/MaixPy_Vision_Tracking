#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物识别模块
负责学习目标人物特征并进行匹配识别
支持最多3个人物的记录和识别
"""

import os
import json
import time

class PersonRecognizer:
    """
    人物识别器类
    支持最多3个人物的记录和识别
    """
    
    def __init__(self, model_path="data/models", max_persons=3, similarity_threshold=0.85):
        """
        初始化人物识别器
        
        Args:
            model_path: 模型和数据存储路径
            max_persons: 最大支持人数（默认3个）
            similarity_threshold: 相似度阈值（默认0.85）
        """
        print("🧠 初始化人物识别器...")
        
        self.model_path = model_path
        self.max_persons = max_persons
        self.similarity_threshold = similarity_threshold
        
        # 创建存储目录
        os.makedirs(model_path, exist_ok=True)
        
        # TODO: 初始化人脸特征提取器
        # try:
        #     from maix import nn
        #     self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
        #     self.has_face_detector = True
        #     print("✓ 人脸特征提取器初始化成功")
        # except Exception as e:
        #     print(f"✗ 人脸特征提取器初始化失败: {e}")
        #     self.has_face_detector = False
        
        self.has_face_detector = False
        
        # 存储已记录的人物信息
        self.registered_persons = {}  # person_id -> person_info
        self.features_database = {}   # person_id -> features_list
        
        # 当前选中的目标人物
        self.target_person_id = None
        
        # TODO: 加载已保存的人物数据
        # self._load_persons_database()
        
        print(f"✓ 人物识别器初始化完成（待集成实际识别模块）")
        print(f"   最大人数: {max_persons}, 相似度阈值: {similarity_threshold}")
    
    def register_person(self, img, person_name, bbox=None):
        """
        注册新人物
        
        Args:
            img: 包含人物的图像
            person_name: 人物姓名
            bbox: 人脸边界框，如果为None则自动检测
            
        Returns:
            tuple: (success: bool, person_id: str, message: str)
        """
        # TODO: 实现人物注册逻辑
        # 1. 检查是否已达到最大人数
        # 2. 检查姓名是否已存在
        # 3. 提取人脸特征
        # 4. 生成新的person_id
        # 5. 保存人物信息和特征
        # 6. 保存参考图像
        
        # 临时实现 - 简单注册
        if len(self.registered_persons) >= self.max_persons:
            return False, None, f"已达到最大注册人数 ({self.max_persons})"
        
        # 检查姓名是否已存在
        for person_id, info in self.registered_persons.items():
            if info['name'] == person_name:
                return False, None, f"人物 '{person_name}' 已存在"
        
        # 生成新的person_id
        person_id = f"person_{len(self.registered_persons) + 1:02d}"
        
        # 保存人物信息
        self.registered_persons[person_id] = {
            'name': person_name,
            'id': person_id,
            'registered_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'feature_count': 1
        }
        
        print(f"✓ 成功注册人物: {person_name} (ID: {person_id})")
        return True, person_id, f"成功注册人物: {person_name}"
    
    def add_person_sample(self, person_id, img, bbox=None):
        """
        为已注册人物添加新的样本
        
        Args:
            person_id: 人物ID
            img: 包含人物的图像
            bbox: 人脸边界框
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # TODO: 实现样本添加逻辑
        # 1. 验证person_id是否存在
        # 2. 提取特征
        # 3. 添加特征到数据库
        # 4. 更新样本计数
        # 5. 保存数据库
        
        if person_id not in self.registered_persons:
            return False, "人物ID不存在"
        
        self.registered_persons[person_id]['feature_count'] += 1
        
        return True, f"成功添加样本，总样本数: {self.registered_persons[person_id]['feature_count']}"
    
    def recognize_person(self, img, bbox=None):
        """
        识别图像中的人物
        
        Args:
            img: 输入图像
            bbox: 人脸边界框，如果为None则自动检测
            
        Returns:
            tuple: (person_id: str, confidence: float, person_name: str)
                  如果未识别到返回 (None, 0.0, "未知")
        """
        # TODO: 实现人物识别逻辑
        # 1. 提取特征
        # 2. 与数据库中的特征进行匹配
        # 3. 计算相似度
        # 4. 返回最佳匹配结果
        
        if not self.registered_persons:
            return None, 0.0, "未知"
        
        # 临时实现 - 简化的识别逻辑
        import random
        if random.random() > 0.5:  # 50%概率识别成功
            person_id = random.choice(list(self.registered_persons.keys()))
            person_name = self.registered_persons[person_id]['name']
            confidence = 0.85 + random.random() * 0.1  # 0.85-0.95
            return person_id, confidence, person_name
        
        return None, 0.3 + random.random() * 0.4, "未知"  # 0.3-0.7
    
    def delete_person(self, person_id):
        """
        删除已注册人物
        
        Args:
            person_id: 人物ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if person_id not in self.registered_persons:
            return False, "人物ID不存在"
        
        person_name = self.registered_persons[person_id]['name']
        del self.registered_persons[person_id]
        
        # 如果删除的是目标人物，清除目标设置
        if self.target_person_id == person_id:
            self.target_person_id = None
        
        return True, f"成功删除人物: {person_name}"
    
    def set_target_person(self, person_id):
        """
        设置目标人物
        
        Args:
            person_id: 人物ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if person_id not in self.registered_persons:
            return False, "人物ID不存在"
        
        self.target_person_id = person_id
        person_name = self.registered_persons[person_id]['name']
        return True, f"目标人物设置为: {person_name}"
    
    def get_target_person(self):
        """
        获取当前目标人物信息
        
        Returns:
            dict: 目标人物信息，如果未设置返回None
        """
        if self.target_person_id and self.target_person_id in self.registered_persons:
            return {
                'id': self.target_person_id,
                'name': self.registered_persons[self.target_person_id]['name'],
                'info': self.registered_persons[self.target_person_id]
            }
        return None
    
    def get_registered_persons(self):
        """
        获取所有已注册人物信息
        
        Returns:
            dict: 人物信息字典
        """
        return self.registered_persons.copy()
    
    def get_status_info(self):
        """
        获取识别器状态信息
        
        Returns:
            dict: 状态信息
        """
        target_info = self.get_target_person()
        
        return {
            'max_persons': self.max_persons,
            'registered_count': len(self.registered_persons),
            'available_slots': self.max_persons - len(self.registered_persons),
            'similarity_threshold': self.similarity_threshold,
            'has_face_detector': self.has_face_detector,
            'target_person': target_info,
            'registered_persons': list(self.registered_persons.keys())
        }

# TODO: 参考standalone_gui.py中的SimplePersonRecognizer实现
# 需要集成的功能：
# 1. 人脸特征提取器初始化
# 2. 人脸特征提取 (extract_face_features)
# 3. 特征相似度计算 (_calculate_similarity)
# 4. 数据库加载和保存 (_load_persons_database, _save_persons_database)
# 5. 完整的识别逻辑实现