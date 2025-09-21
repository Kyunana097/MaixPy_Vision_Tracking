# CNN人脸识别预训练方案

## 🎯 方案概述

使用CNN在PC端预训练人脸识别模型，然后部署到MaixCAM进行实时识别。

## 🏗️ 技术架构

### 1. PC端训练阶段
```
数据采集 → 数据预处理 → CNN训练 → 模型导出 → 特征提取器
```

### 2. MaixCAM部署阶段  
```
实时图像 → 预处理 → 特征提取 → 相似度计算 → 识别结果
```

## 📊 数据流程

### PC端训练数据准备
```python
# 数据结构
training_data/
├── person1/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   └── ...
├── person2/
│   ├── img_001.jpg
│   ├── img_002.jpg  
│   └── ...
└── person3/
    ├── img_001.jpg
    └── ...
```

### MaixCAM部署数据
```python
# 模型文件
models/
├── face_encoder.onnx          # 特征提取模型
├── person_features.npy        # 预计算的人物特征向量
└── person_labels.json         # 人物标签映射
```

## 🧠 CNN模型设计

### 特征提取网络
```python
# 基于ResNet18的轻量化设计
class FaceEncoder(nn.Module):
    def __init__(self, feature_dim=128):
        super().__init__()
        self.backbone = models.resnet18(pretrained=True)
        self.backbone.fc = nn.Linear(512, feature_dim)
        
    def forward(self, x):
        return F.normalize(self.backbone(x), p=2, dim=1)
```

### 训练策略
- **Triplet Loss**: 同一人物特征相近，不同人物特征远离
- **数据增强**: 旋转、亮度、对比度变化
- **迁移学习**: 使用预训练的人脸识别模型

## 🔧 MaixCAM集成方案

### 1. 模型转换
```bash
# PyTorch → ONNX → MaixPy格式
python convert_model.py --input face_encoder.pth --output face_encoder.mud
```

### 2. 特征提取接口
```python
class CNNFaceRecognizer:
    def __init__(self):
        self.encoder = maix.nn.load("models/face_encoder.mud")
        self.person_features = np.load("models/person_features.npy")
        self.person_labels = json.load("models/person_labels.json")
    
    def extract_features(self, face_img):
        # 预处理：64x64, 归一化
        processed = self.preprocess(face_img)
        # CNN特征提取
        features = self.encoder.forward(processed)
        return features
    
    def recognize(self, face_img):
        query_features = self.extract_features(face_img)
        
        # 计算与所有已知人物的相似度
        similarities = []
        for person_features in self.person_features:
            sim = cosine_similarity(query_features, person_features)
            similarities.append(sim)
        
        # 返回最佳匹配
        best_idx = np.argmax(similarities)
        best_sim = similarities[best_idx]
        
        if best_sim > 0.7:  # 阈值
            return self.person_labels[best_idx], best_sim
        else:
            return "未知", best_sim
```

## 📋 实施步骤

### 阶段1: 数据采集 (1-2天)
1. 使用MaixCAM采集每个人物的多张照片 (20-50张)
2. 不同角度、光线、表情
3. 统一尺寸64x64，保存为训练数据集

### 阶段2: PC端训练 (2-3天)  
1. 搭建PyTorch训练环境
2. 实现Triplet Loss训练
3. 训练到收敛，验证识别准确率
4. 导出ONNX模型

### 阶段3: 模型转换 (1天)
1. ONNX转换为MaixPy支持的格式
2. 测试模型推理性能
3. 优化模型大小和速度

### 阶段4: MaixCAM集成 (2天)
1. 实现CNNFaceRecognizer类
2. 替换现有的PersonRecognizer
3. 测试实时识别效果
4. 性能调优

## ⚡ 性能预期

- **识别准确率**: >95% (真人vs玩偶应该100%区分)
- **推理速度**: 10-20 FPS
- **内存占用**: <100MB
- **模型大小**: <50MB

## 🎯 关键优势

1. **真正的深度学习**: CNN提取的特征具有语义意义
2. **高区分能力**: 能识别细微的人脸差异
3. **稳定性**: 预训练模型不受MaixPy底层限制
4. **可扩展**: 支持更多人物和复杂场景
5. **工业级**: 类似商业人脸识别系统的技术栈

## 🚀 立即开始

这个方案完全可行，而且是解决当前问题的最佳路径。我们可以：

1. **先验证概念**: 用简单的CNN模型快速验证
2. **逐步优化**: 根据效果调整网络结构和训练策略  
3. **完整部署**: 实现端到端的识别系统

您觉得这个方案如何？我们可以立即开始实施！
