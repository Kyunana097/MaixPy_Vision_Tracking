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
import hashlib
import numpy as np

class PersonRecognizer:
    """
    人物识别器类
    支持最多3个人物的记录和识别
    """
    
    def __init__(self, model_path="data/models", max_persons=3, similarity_threshold=0.60, detector=None):
        """
        初始化人物识别器
        
        Args:
            model_path: 模型和数据存储路径
            max_persons: 最大支持人数（默认3个）
            similarity_threshold: 相似度阈值（默认0.60）
            detector: 人物检测器实例，用于图像相似度计算
        """
        print("🧠 初始化人物识别器...")
        
        self.model_path = model_path
        self.max_persons = max_persons
        self.similarity_threshold = similarity_threshold
        self.detector = detector  # 保存检测器引用用于图像比较
        
        # 创建存储目录结构
        self.faces_path = os.path.join(model_path, "faces")
        self.db_file = os.path.join(model_path, "persons_db.json")
        os.makedirs(self.faces_path, exist_ok=True)
        
        # 初始化人脸检测器
        try:
            from maix import nn
            self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
            self.has_face_detector = True
            print("✓ 人脸检测器初始化成功")
        except Exception as e:
            print(f"✗ 人脸检测器初始化失败: {e}")
            print("  将使用简化的人脸检测模式")
            self.face_detector = None
            self.has_face_detector = False
        
        # 存储已记录的人物信息
        self.registered_persons = {}  # person_id -> person_info
        self.face_samples = {}        # person_id -> [sample_file_list]
        
        # 当前选中的目标人物
        self.target_person_id = None
        
        # 人脸图像标准尺寸
        self.face_size = (64, 64)
        
        # 加载已保存的人物数据
        self._load_persons_database()
        
        print(f"✓ 人物识别器初始化完成")
        print(f"   最大人数: {max_persons}, 相似度阈值: {similarity_threshold}")
        print(f"   已加载 {len(self.registered_persons)} 个人物")
    
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
        # 1. 检查是否已达到最大人数
        if len(self.registered_persons) >= self.max_persons:
            return False, None, f"已达到最大注册人数 ({self.max_persons})"
        
        # 2. 检查姓名是否已存在
        for person_id, info in self.registered_persons.items():
            if info['name'] == person_name:
                return False, None, f"人物 '{person_name}' 已存在"
        
        # 3. 检测和提取人脸
        face_bbox = bbox
        if face_bbox is None:
            face_bbox = self._detect_largest_face(img)
            if face_bbox is None:
                return False, None, "未检测到人脸"
        
        # 4. 提取并保存人脸图像
        face_img = self._extract_face_region(img, face_bbox)
        if face_img is None:
            return False, None, "人脸区域提取失败"
        
        # 5. 生成新的person_id
        person_id = f"person_{len(self.registered_persons) + 1:02d}"
        
        # 6. 创建人物存储目录
        person_dir = os.path.join(self.faces_path, person_id)
        os.makedirs(person_dir, exist_ok=True)
        
        # 7. 保存人脸图像
        sample_filename = f"sample_001.jpg"
        sample_path = os.path.join(person_dir, sample_filename)
        success = self._save_face_image(face_img, sample_path)
        
        if not success:
            return False, None, "人脸图像保存失败"
        
        # 8. 保存人物信息
        self.registered_persons[person_id] = {
            'name': person_name,
            'id': person_id,
            'registered_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'sample_count': 1
        }
        self.face_samples[person_id] = [sample_filename]
        
        # 9. 保存数据库
        self._save_persons_database()
        
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
        # 1. 验证person_id是否存在
        if person_id not in self.registered_persons:
            return False, "人物ID不存在"
        
        # 2. 检测和提取人脸
        face_bbox = bbox
        if face_bbox is None:
            face_bbox = self._detect_largest_face(img)
            if face_bbox is None:
                return False, "未检测到人脸"
        
        # 3. 提取人脸图像
        face_img = self._extract_face_region(img, face_bbox)
        if face_img is None:
            return False, "人脸区域提取失败"
        
        # 4. 保存新样本
        person_dir = os.path.join(self.faces_path, person_id)
        sample_count = self.registered_persons[person_id]['sample_count']
        sample_filename = f"sample_{sample_count + 1:03d}.jpg"
        sample_path = os.path.join(person_dir, sample_filename)
        
        success = self._save_face_image(face_img, sample_path)
        if not success:
            return False, "人脸图像保存失败"
        
        # 5. 更新数据库
        self.registered_persons[person_id]['sample_count'] += 1
        self.face_samples[person_id].append(sample_filename)
        self._save_persons_database()
        
        total_samples = self.registered_persons[person_id]['sample_count']
        return True, f"成功添加样本，总样本数: {total_samples}"
    
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
        # 1. 检查是否有已注册人物
        if not self.registered_persons:
            return None, 0.0, "未知"
        
        # 2. 检测和提取人脸
        face_bbox = bbox
        if face_bbox is None:
            face_bbox = self._detect_largest_face(img)
            if face_bbox is None:
                return None, 0.0, "未知"
        
        # 3. 提取人脸图像
        face_img = self._extract_face_region(img, face_bbox)
        if face_img is None:
            return None, 0.0, "未知"
        
        # 4. 与数据库中的样本进行匹配
        best_person_id = None
        best_confidence = 0.0
        
        for person_id in self.registered_persons:
            # 计算与该人物所有样本的相似度
            person_similarity = self._calculate_person_similarity(face_img, person_id)
            
            if person_similarity > best_confidence:
                best_confidence = person_similarity
                best_person_id = person_id
        
        # 5. 判断是否达到识别阈值
        if best_confidence >= self.similarity_threshold:
            person_name = self.registered_persons[best_person_id]['name']
            return best_person_id, best_confidence, person_name
        
        return None, best_confidence, "未知"
    
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
        
        # 删除人物文件夹
        person_dir = os.path.join(self.faces_path, person_id)
        if os.path.exists(person_dir):
            import shutil
            shutil.rmtree(person_dir)
        
        # 删除内存中的数据
        del self.registered_persons[person_id]
        if person_id in self.face_samples:
            del self.face_samples[person_id]
        
        # 如果删除的是目标人物，清除目标设置
        if self.target_person_id == person_id:
            self.target_person_id = None
        
        # 保存数据库
        self._save_persons_database()
        
        return True, f"成功删除人物: {person_name}"
    
    def clear_all_persons(self):
        """
        清空所有已注册人物
        
        Returns:
            tuple: (success: bool, message: str)
        """
        # 删除所有人物文件夹
        if os.path.exists(self.faces_path):
            import shutil
            shutil.rmtree(self.faces_path)
            os.makedirs(self.faces_path, exist_ok=True)
        
        # 清空内存数据
        person_count = len(self.registered_persons)
        self.registered_persons.clear()
        self.face_samples.clear()
        self.target_person_id = None
        
        # 保存数据库
        self._save_persons_database()
        
        return True, f"已清空所有人物数据 (共 {person_count} 个)"
    
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
    
    def get_person_thumbnail(self, person_id):
        """
        获取人物的缩略图
        
        Args:
            person_id: 人物ID
            
        Returns:
            Image: 人物缩略图，如果不存在返回None
        """
        if person_id not in self.face_samples:
            print(f"✗ 人物ID不存在: {person_id}")
            return None
            
        try:
            # 获取第一个样本作为缩略图
            person_dir = os.path.join(self.faces_path, person_id)
            
            if self.face_samples[person_id]:
                sample_filename = self.face_samples[person_id][0]
                sample_path = os.path.join(person_dir, sample_filename)
                
                if os.path.exists(sample_path):
                    try:
                        from maix import image as maix_image
                        thumbnail = maix_image.load(sample_path)
                        if thumbnail is not None:
                            return thumbnail
                        else:
                            print("✗ 图像加载返回None")
                    except Exception as load_e:
                        print(f"✗ 图像加载失败: {load_e}")
                else:
                    print(f"✗ 缩略图文件不存在: {sample_path}")
            else:
                print(f"✗ 没有样本文件: {person_id}")
                
        except Exception as e:
            print(f"✗ 获取缩略图失败: {e}")
        
        return None
    
    def get_all_thumbnails(self):
        """
        获取所有已注册人物的缩略图
        
        Returns:
            dict: person_id -> thumbnail_image 映射
        """
        thumbnails = {}
        for person_id in self.registered_persons:
            thumbnail = self.get_person_thumbnail(person_id)
            if thumbnail:
                thumbnails[person_id] = thumbnail
        return thumbnails
    
    def get_status_info(self):
        """
        获取识别器状态信息
        
        Returns:
            dict: 状态信息
        """
        target_info = self.get_target_person()
        
        # 统计样本总数
        total_samples = sum(person['sample_count'] for person in self.registered_persons.values())
        
        return {
            'max_persons': self.max_persons,
            'registered_count': len(self.registered_persons),
            'available_slots': self.max_persons - len(self.registered_persons),
            'total_samples': total_samples,
            'similarity_threshold': self.similarity_threshold,
            'has_face_detector': self.has_face_detector,
            'face_size': self.face_size,
            'target_person': target_info,
            'registered_persons': list(self.registered_persons.keys())
        }

    # =============== 私有辅助方法 ===============
    
    def _load_persons_database(self):
        """加载已保存的人物数据库"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.registered_persons = data.get('persons', {})
                    self.face_samples = data.get('samples', {})
                    self.target_person_id = data.get('target_person', None)
                    print(f"✓ 已加载 {len(self.registered_persons)} 个人物数据")
        except Exception as e:
            print(f"✗ 数据库加载失败: {e}")
            self.registered_persons = {}
            self.face_samples = {}
    
    def _save_persons_database(self):
        """保存人物数据库到文件"""
        try:
            data = {
                'persons': self.registered_persons,
                'samples': self.face_samples,
                'target_person': self.target_person_id,
                'last_update': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"✗ 数据库保存失败: {e}")
    
    def _detect_largest_face(self, img):
        """
        检测图像中最大的人脸
        
        Args:
            img: 输入图像
            
        Returns:
            tuple: (x, y, w, h) 或 None
        """
        # 如果有真实的人脸检测器，使用它
        if self.has_face_detector and self.face_detector is not None:
            try:
                faces = self.face_detector.detect(img)
                if not faces:
                    print("✗ 未检测到人脸")
                    return None
                
                # 找到最大的人脸
                largest_face = max(faces, key=lambda face: face.w * face.h)
                face_bbox = (largest_face.x, largest_face.y, largest_face.w, largest_face.h)
                print(f"✓ 检测到人脸: {face_bbox}")
                return face_bbox
                
            except Exception as e:
                print(f"✗ 人脸检测失败: {e}")
                return None
        else:
            # 没有人脸检测器时明确返回失败
            print("✗ 人脸检测器未初始化，无法检测人脸")
            return None
    
    def _extract_face_region(self, img, bbox):
        """
        从图像中提取人脸区域并调整为标准尺寸
        
        Args:
            img: 输入图像
            bbox: 人脸边界框 (x, y, w, h)
            
        Returns:
            cropped_img: 裁剪并调整尺寸的人脸图像，或None
        """
        try:
            x, y, w, h = bbox
            
            # 获取图像尺寸
            img_width = img.width() if callable(img.width) else img.width
            img_height = img.height() if callable(img.height) else img.height
            
            # 边界检查
            x = max(0, min(x, img_width - 1))
            y = max(0, min(y, img_height - 1))
            w = min(w, img_width - x)
            h = min(h, img_height - y)
            
            if w <= 0 or h <= 0:
                return None
            
            # 裁剪人脸区域
            face_img = img.crop(x, y, w, h)
            
            # 调整到标准尺寸
            face_img = face_img.resize(self.face_size[0], self.face_size[1])
            
            return face_img
            
        except Exception as e:
            print(f"✗ 人脸区域提取失败: {e}")
            return None
    
    def _save_face_image(self, face_img, file_path):
        """
        保存人脸图像到文件
        
        Args:
            face_img: 人脸图像
            file_path: 保存路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存图像
            face_img.save(file_path, quality=90)
            
            # 验证文件是否成功保存
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"✓ 人脸图像已保存: {file_path}")
                return True
            else:
                print(f"✗ 人脸图像保存验证失败: {file_path}")
                return False
                
        except Exception as e:
            print(f"✗ 人脸图像保存失败: {e}")
            print(f"  文件路径: {file_path}")
            return False
    
    def _calculate_person_similarity(self, face_img, person_id):
        """
        计算输入人脸与指定人物所有样本的相似度
        
        Args:
            face_img: 待比较的人脸图像
            person_id: 人物ID
            
        Returns:
            float: 最高相似度值 (0.0-1.0)
        """
        if person_id not in self.face_samples:
            return 0.0
        
        max_similarity = 0.0
        person_dir = os.path.join(self.faces_path, person_id)
        
        for sample_filename in self.face_samples[person_id]:
            sample_path = os.path.join(person_dir, sample_filename)
            
            if os.path.exists(sample_path):
                similarity = self._calculate_image_similarity(face_img, sample_path)
                max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_image_similarity(self, img1, img2_path):
        """
        计算两个图像的真实相似度
        使用检测器模块的图像比较功能
        
        Args:
            img1: 第一个图像对象
            img2_path: 第二个图像文件路径
            
        Returns:
            float: 相似度值 (0.0-1.0)
        """
        try:
            # 加载对比图像
            from maix import image as maix_image
            img2 = maix_image.load(img2_path)
            
            if img2 is None:
                print(f"✗ 无法加载图像: {img2_path}")
                return 0.0
            
            # 使用检测器模块的真实图像比较功能
            if self.detector and hasattr(self.detector, 'calculate_image_similarity'):
                similarity = self.detector.calculate_image_similarity(img1, img2)
                return similarity
            else:
                # 降级到基本比较（如果检测器不可用）
                return self._fallback_image_comparison(img1, img2)
            
        except Exception as e:
            return 0.0
    
    def _fallback_image_comparison(self, img1, img2):
        """
        降级图像比较方案
        当检测器不可用时使用
        
        Args:
            img1: 图像1
            img2: 图像2
            
        Returns:
            float: 相似度 (0.0-1.0)
        """
        try:
            # 基本的尺寸比较
            w1 = img1.width() if callable(img1.width) else img1.width
            h1 = img1.height() if callable(img1.height) else img1.height
            w2 = img2.width() if callable(img2.width) else img2.width
            h2 = img2.height() if callable(img2.height) else img2.height
            
            # 确保尺寸一致
            if (w1, h1) != (w2, h2):
                img2 = img2.resize(w1, h1)
            
            # 尺寸相似度
            size_sim = min(w1*h1, w2*h2) / max(w1*h1, w2*h2)
            
            # 宽高比相似度
            ratio1 = w1 / h1 if h1 > 0 else 1.0
            ratio2 = w2 / h2 if h2 > 0 else 1.0
            ratio_sim = 1.0 - abs(ratio1 - ratio2) / max(ratio1, ratio2)
            
            return (size_sim + ratio_sim) / 2.0
            
        except Exception as e:
            return 0.3
    
    