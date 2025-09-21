# MaixPy Vision - 集成版本

## 🎯 项目概述

基于您原始成功版本的完整MaixPy视觉识别系统，集成了官方AI模型。

**版本**: 5.0.0-official  
**特点**: 完整功能 + 官方FaceRecognize API + 高性能  

## ✨ 主要特性

- ✅ **完整UI系统** - 基于您调试成功的布局
- ✅ **虚拟按钮** - 所有交互功能正常
- ✅ **三种模式** - record/recognize/track
- ✅ **官方AI模型** - 自动检测并使用官方模型
- ✅ **智能回退** - 模型不可用时使用简化实现
- ✅ **数据持久化** - 注册信息自动保存

## 🚀 使用方法

### 在MaixVision中运行

1. **打开项目** - 将此文件夹作为项目打开
2. **运行程序** - 直接运行 `main.py`
3. **开始使用** - 所有按钮和功能都可用

### 功能说明

- **DEBUG按钮** - 显示系统状态信息
- **MODE按钮** - 切换模式 (record/recognize/track)
- **ADD按钮** - 注册新人物 (record模式)
- **CLEAR按钮** - 清空所有人物 (record模式)
- **EXIT按钮** - 退出程序

## 🧠 AI模型集成

### 自动检测模型
- 优先使用官方模型 (`models/retinaface.mud` + `models/fe_resnet.mud`)
- 模型不可用时自动使用简化实现
- 支持真实人脸检测和识别

### 数据存储
- 人物信息: `data/registered_persons.json`
- 人脸图像: `data/faces/person_xx/`

## 📁 项目结构

```
minimal_test/
├── main.py                    # 主程序 (您的成功版本)
├── src/                       # 源代码模块
│   ├── hardware/              # 硬件控制 (按钮、摄像头等)
│   ├── vision/                # 视觉处理
│   │   ├── detection/         # 人物检测
│   │   └── recognition/       # 人脸识别
│   └── utils/                 # 工具模块
├── models/                    # AI模型文件 (8.5MB)
├── data/                      # 数据存储 (自动创建)
└── system_config.json         # 系统配置
```

## 🎯 优势

1. **稳定可靠** - 基于您调试成功的版本
2. **AI增强** - 集成官方高性能模型
3. **向后兼容** - 保持所有原有功能
4. **自适应** - 根据环境自动选择最佳方案

**这个版本结合了您成功的UI布局和官方AI模型的强大功能！** 🚀