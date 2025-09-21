# MaixPy 预训练人脸识别系统

## 🎯 项目概述

这是基于MaixHub预训练模型的人脸识别系统，可以识别10位知名人物。

### 支持识别的人物
- 🎭 **胡歌** (huge)
- 🎬 **姜文** (jiangwen) 
- 💪 **彭于晏** (pengyuyan)
- 😂 **岳云鹏** (yueyunpeng)
- 👩 **周冬雨** (zhoudongyu)
- 💃 **迪丽热巴** (dilireba)
- ⭐ **范冰冰** (fanbingbing)
- 🏀 **姚明** (yaoming)
- 👸 **刘亦菲** (liuyifei)
- 🎵 **周杰伦** (zhoujielun)

## 📦 模型信息

- **模型来源**: [MaixHub模型库](https://maixhub.com/model/zoo/155)
- **模型文件**: `model-38558.kmodel`
- **输入尺寸**: 224x224x3
- **输出**: 10个类别的置信度分数
- **模型大小**: ~870KB

## 🚀 快速开始

### 1. 文件结构
```
MaixPy_Vision_Tracking/
├── main_pretrained.py                 # 预训练模型主程序
├── pretrained_model/                  # 预训练模型目录
│   ├── model-38558.kmodel            # KPU模型文件
│   ├── main.py                       # 原始示例代码
│   └── report.json                   # 模型报告
├── src/vision/recognition/
│   └── pretrained_face_recognizer.py # 预训练识别器
└── PRETRAINED_README.md              # 本文档
```

### 2. 运行程序

#### MaixCAM设备上运行:
```bash
# 方式1: 直接运行预训练版本
python main_pretrained.py

# 方式2: 设置环境变量使用预训练模型
export USE_PRETRAINED_MODEL=true
python main.py
```

#### 开发环境测试:
```bash
python main_pretrained.py
```

### 3. 操作说明

#### 虚拟按钮
- **EXIT**: 退出程序
- **DEBUG**: 显示系统调试信息
- **THRESHOLD**: 循环调整置信度阈值 (0.5 → 0.6 → 0.7 → 0.8 → 0.5)

#### 界面显示
- 实时显示FPS和系统版本
- 识别成功时显示人物姓名和置信度
- 未识别时显示"未识别到已知人物"
- 左侧显示支持识别的人物列表

## 🔧 技术特性

### 核心功能
- ✅ **实时人脸识别**: 基于KPU加速的神经网络推理
- ✅ **多人支持**: 可识别10位不同的知名人物
- ✅ **自适应阈值**: 可动态调整识别置信度阈值
- ✅ **性能优化**: 使用KPU硬件加速，推理速度快
- ✅ **用户友好**: 直观的UI界面和触摸操作

### 技术架构
```python
PretrainedVisionSystem
├── PretrainedFaceRecognizer    # 预训练模型封装
│   ├── KPU模型加载
│   ├── 图像预处理
│   ├── 前向推理
│   └── 结果后处理
├── VirtualButtonManager        # 虚拟按钮管理
└── UI渲染系统                  # 界面绘制
```

## 📊 性能指标

### 模型性能
- **输入尺寸**: 224×224×3
- **推理时间**: ~10-50ms (取决于硬件)
- **模型大小**: 870KB
- **参数量**: 834,666

### 系统性能
- **帧率**: 15-25 FPS (MaixCAM)
- **内存使用**: 低内存占用
- **启动时间**: ~2-3秒

## 🎛️ 配置选项

### 置信度阈值调整
```python
# 在PretrainedFaceRecognizer中调整
recognizer.set_confidence_threshold(0.7)  # 0.0-1.0
```

### 模型路径配置
```python
# 自定义模型路径
recognizer = PretrainedFaceRecognizer(
    model_path="your_custom_model.kmodel"
)
```

## 🐛 故障排除

### 常见问题

#### 1. 模型加载失败
```
❌ 模型文件不存在: pretrained_model/model-38558.kmodel
```
**解决方案**: 确保模型文件已正确复制到项目目录

#### 2. KPU模块导入失败
```
❌ KPU模块不可用，尝试使用maix.nn
```
**解决方案**: 确保在MaixCAM设备上运行，或检查MaixPy安装

#### 3. 识别率低
```
❌ 置信度过低: 0.450 < 0.600
```
**解决方案**: 
- 调整置信度阈值 (使用THRESHOLD按钮)
- 确保光照充足
- 保持人脸正对摄像头

### 调试模式
按下DEBUG按钮查看详细系统信息:
```
🐛 === SYSTEM DEBUG INFO ===
  Frame count: 1250
  FPS: 18.50
  Camera resolution: (512, 320)
  Display resolution: (640, 480)
  Recognizer status:
    Model loaded: True
    Supported persons: 10
    Confidence threshold: 0.6
  Last recognition: 胡歌 (0.856)
```

## 🔄 版本历史

### v6.0.0-pretrained (2025-09-21)
- ✅ 集成MaixHub预训练人脸识别模型
- ✅ 支持10位知名人物识别
- ✅ 实现KPU硬件加速推理
- ✅ 添加自适应置信度阈值调整
- ✅ 优化UI界面和用户体验

## 📝 开发说明

### 扩展新模型
1. 替换`pretrained_model/model-38558.kmodel`
2. 更新`PretrainedFaceRecognizer.labels`列表
3. 更新`chinese_names`映射字典
4. 调整`input_size`和其他参数

### 添加新功能
- 继承`PretrainedFaceRecognizer`类
- 在`PretrainedVisionSystem`中添加新的按钮和处理逻辑
- 扩展UI绘制功能

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目基于原项目许可证开源。

---

**注意**: 此预训练模型仅用于演示和学习目的，识别结果仅供参考。
