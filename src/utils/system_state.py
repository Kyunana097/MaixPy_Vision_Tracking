#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统状态管理模块
负责管理系统的各种状态和模式
"""

from enum import Enum

class SystemMode(Enum):
    """
    系统工作模式枚举
    """
    IDLE = "idle"                    # 空闲模式
    DETECTION = "detection"          # 人物检测模式
    LEARNING = "learning"            # 目标学习模式
    TRACKING = "tracking"            # 目标跟踪模式
    ALARM = "alarm"                  # 报警模式

class SafetyState(Enum):
    """
    安全状态枚举
    """
    SAFE = "SAFE"                    # 安全状态
    WARNING = "WARNING"              # 警告状态

class SystemState:
    """
    系统状态管理器类
    """
    
    def __init__(self):
        """
        初始化系统状态管理器
        """
        # TODO: 初始化系统状态
        self.current_mode = SystemMode.IDLE
        self.safety_state = SafetyState.SAFE
        self.target_learned = False
        self.alarm_active = False
        pass
    
    def set_mode(self, mode):
        """
        设置系统工作模式
        
        Args:
            mode: 系统工作模式
        """
        # TODO: 设置系统模式
        pass
    
    def get_mode(self):
        """
        获取当前系统工作模式
        
        Returns:
            SystemMode: 当前工作模式
        """
        return self.current_mode
    
    def set_safety_state(self, state):
        """
        设置安全状态
        
        Args:
            state: 安全状态
        """
        # TODO: 设置安全状态
        pass
    
    def get_safety_state(self):
        """
        获取当前安全状态
        
        Returns:
            SafetyState: 当前安全状态
        """
        return self.safety_state
    
    def set_target_learned(self, learned):
        """
        设置目标学习状态
        
        Args:
            learned: 是否已学习目标
        """
        self.target_learned = learned
    
    def is_target_learned(self):
        """
        检查是否已学习目标
        
        Returns:
            bool: 目标学习状态
        """
        return self.target_learned
    
    def set_alarm_active(self, active):
        """
        设置报警激活状态
        
        Args:
            active: 报警是否激活
        """
        self.alarm_active = active
    
    def is_alarm_active(self):
        """
        检查报警是否激活
        
        Returns:
            bool: 报警激活状态
        """
        return self.alarm_active
    
    def reset_system(self):
        """
        重置系统状态
        """
        # TODO: 重置所有状态到初始值
        pass
