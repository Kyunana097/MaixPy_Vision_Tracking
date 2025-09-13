#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人物检测模块
负责检测A4纸上的三个人物并用绿色框标记
"""

class PersonDetector:
    """
    人物检测器类
    """
    
    def __init__(self):
        """
        初始化人物检测器
        """
        # TODO: 初始化检测参数
        pass
    
    def detect_persons(self, image):
        """
        检测图像中的人物
        
        Args:
            image: 输入图像
            
        Returns:
            list: 检测到的人物位置列表
        """
        # TODO: 实现人物检测算法
        pass
    
    def draw_green_boxes(self, image, detections):
        """
        在检测到的人物周围绘制绿色框
        
        Args:
            image: 输入图像
            detections: 检测结果
            
        Returns:
            image: 标记后的图像
        """
        # TODO: 绘制绿色标记框
        pass
