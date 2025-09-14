# 人物识别功能使用指南

## 功能概述

本系统支持最多3个人物的注册、识别和管理功能，包括：

- **人物注册**: 学习并保存人物特征
- **人物识别**: 实时识别已注册的人物
- **目标跟踪**: 设置特定人物为目标进行跟踪
- **数据管理**: 删除、清空人物数据库

## 核心组件

### 1. PersonRecognizer 类
位置: `src/vision/recognition/face_recognition.py`

主要功能：
- 人物特征提取和存储
- 人物识别和匹配
- 数据库管理
- 目标人物设置

### 2. PersonDetector 类
位置: `src/vision/detection/person_detector.py`

主要功能：
- 实时人物检测
- 上半身识别
- 物理尺寸约束验证

## 使用方法

### 1. 基本使用

```python
from src.vision.recognition.face_recognition import PersonRecognizer
from src.vision.detection.person_detector import PersonDetector

# 初始化
recognizer = PersonRecognizer()
detector = PersonDetector(camera_width=512, camera_height=320)

# 检测人物
detections = detector.detect_persons(img)

# 注册人物
success, person_id, message = recognizer.register_person(img, "张三", face_bbox)

# 识别人物
person_id, confidence, person_name = recognizer.recognize_person(img, face_bbox)
```

### 2. 命令行管理工具

```bash
# 显示系统状态
python examples/person_manager.py status

# 注册新人物
python examples/person_manager.py register 张三

# 列出所有人物
python examples/person_manager.py list

# 设置目标人物
python examples/person_manager.py target person_01

# 删除人物
python examples/person_manager.py delete 张三

# 清空所有数据
python examples/person_manager.py clear
```

### 3. 交互式测试

```bash
# 完整测试流程
python examples/test_person_registration.py

# 注册测试
python examples/test_person_registration.py register

# 识别测试
python examples/test_person_registration.py recognize

# 交互式测试
python examples/test_person_registration.py interactive
```

## 系统限制

### 人物数量
- 最大支持：3个人物
- 每个人物可以有多个特征样本
- 超过限制时会拒绝新的注册

### 识别参数
- 相似度阈值：0.85（可调整）
- 人脸尺寸：自动检测和标准化
- 特征维度：64维向量

### 物理约束
- 人物照片尺寸：5x5cm
- 最小距离：50cm
- 检测像素范围：25-150px

## 数据存储

### 文件结构
```
data/models/
├── persons_database.json      # 人物基本信息
├── features_person_01.npy     # 人物1特征数据
├── features_person_02.npy     # 人物2特征数据
├── features_person_03.npy     # 人物3特征数据
├── reference_person_01.jpg    # 人物1参考图像
├── reference_person_02.jpg    # 人物2参考图像
└── reference_person_03.jpg    # 人物3参考图像
```

### 数据格式
```json
{
  "registered_persons": {
    "person_01": {
      "name": "张三",
      "id": "person_01",
      "registered_time": "2024-01-01 12:00:00",
      "feature_count": 3
    }
  },
  "target_person_id": "person_01",
  "last_updated": "2024-01-01 12:00:00"
}
```

## API 参考

### PersonRecognizer 主要方法

#### register_person(img, person_name, bbox=None)
注册新人物
- **参数**: 图像、姓名、人脸边界框
- **返回**: (成功标志, 人物ID, 消息)

#### recognize_person(img, bbox=None)
识别人物
- **参数**: 图像、人脸边界框
- **返回**: (人物ID, 置信度, 姓名)

#### set_target_person(person_id)
设置目标人物
- **参数**: 人物ID
- **返回**: (成功标志, 消息)

#### get_status_info()
获取系统状态
- **返回**: 状态信息字典

### PersonDetector 主要方法

#### detect_persons(img)
检测人物
- **参数**: 输入图像
- **返回**: 检测结果列表

#### draw_green_boxes(img, detections)
绘制检测框
- **参数**: 图像、检测结果
- **返回**: 绘制后的图像

## 性能优化

### 特征提取
- 使用简化的图像块特征
- 标准化人脸尺寸为112x112
- 64维特征向量

### 相似度计算
- 余弦相似度算法
- 多样本匹配取最高值
- 阈值过滤减少误识别

### 存储优化
- JSON格式存储基本信息
- NumPy格式存储特征数据
- 自动压缩和清理

## 故障排除

### 常见问题

1. **人脸检测失败**
   - 确保光照充足
   - 人脸正面朝向摄像头
   - 检查摄像头是否正常

2. **识别准确率低**
   - 增加训练样本数量
   - 调整相似度阈值
   - 确保注册时人脸清晰

3. **注册失败**
   - 检查是否达到最大人数限制
   - 确认姓名未重复
   - 验证人脸检测是否成功

### 调试方法

```python
# 显示调试信息
status = recognizer.get_status_info()
print(status)

# 检查检测参数
debug_info = detector.get_debug_info()
print(debug_info)

# 测试特征提取
features = recognizer.extract_face_features(img, bbox)
print(f"特征长度: {len(features) if features else 'None'}")
```

## 未来扩展

### 可能的改进
- 使用更先进的人脸识别模型
- 支持更多人物数量
- 添加年龄、性别等属性识别
- 实现人脸活体检测
- 优化识别速度和准确率
