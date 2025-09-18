# 模块迁移指导：从standalone_gui.py拆分功能

## 📋 概述

本指导将帮助你将 `standalone_gui.py` 中的功能分别迁移到 `person_detector.py` 和 `face_recognition.py` 模块中。

## 🎯 拆分策略

### **检测模块 (person_detector.py)**
负责：人脸检测 → 上半身推算 → 边界框绘制

### **识别模块 (face_recognition.py)**  
负责：特征提取 → 数据库管理 → 人物识别 → 样本记录

---

## 🔍 检测模块迁移 (person_detector.py)

### **1. 需要迁移的类和方法**

从 `standalone_gui.py` 第174-285行的 `SimplePersonDetector` 类：

```python
# 源文件位置：examples/standalone_gui.py:174-285
class SimplePersonDetector:
    def __init__(self, camera_width=512, camera_height=320)
    def detect_persons(self, img)
```

### **2. 具体迁移步骤**

#### **步骤1：人脸检测器初始化**
```python
# 迁移到：src/vision/detection/person_detector.py:28-36
# 源代码：examples/standalone_gui.py:190-202

# 需要取消注释并完善：
try:
    from maix import nn
    self.face_detector = nn.FaceDetector(model="/root/models/face_detector.mud")
    self.has_face_detector = True
    print("✓ 人脸检测器初始化成功")
except Exception as e:
    print(f"✗ 人脸检测器初始化失败: {e}")
    self.has_face_detector = False
```

#### **步骤2：人脸检测逻辑**
```python
# 迁移到：src/vision/detection/person_detector.py:43-65 (detect_persons方法)
# 源代码：examples/standalone_gui.py:216-249

关键逻辑：
1. faces = self.face_detector.detect(img)  # 检测人脸
2. 从人脸推算上半身：
   - body_w = int(face_w * 1.5)
   - body_h = int(face_h * 2.5)
   - body_x = max(0, face_x - (body_w - face_w) // 2)
   - body_y = face_y
3. 边界检查和数据结构构建
```

#### **步骤3：检测结果处理**
```python
# 返回格式（已在接口中定义）：
detection = {
    'bbox': (body_x, body_y, body_w, body_h),      # 上半身边界框
    'face_bbox': (face_x, face_y, face_w, face_h), # 人脸边界框
    'confidence': 0.9,                             # 置信度
    'type': 'upper_body'                           # 检测类型
}
```

#### **步骤4：绘制检测框**
```python
# 迁移到：src/vision/detection/person_detector.py:67-79 (draw_detection_boxes方法)
# 参考：examples/standalone_gui.py:600-625 和 615-624

关键绘制逻辑：
1. 绘制上半身绿色边界框：img.draw_rect(x, y, w, h, color=green, thickness=2)
2. 绘制人脸青色边界框：img.draw_rect(fx, fy, fw, fh, color=cyan, thickness=1)
3. 添加标签和置信度信息
```

### **3. 模拟检测逻辑（可选）**
```python
# 源代码：examples/standalone_gui.py:252-284
# 当没有真实检测器时的随机检测逻辑
# 可以作为测试和调试时的后备方案
```

---

## 🧠 识别模块迁移 (face_recognition.py)

### **1. 需要迁移的类和方法**

从 `standalone_gui.py` 第23-172行的 `SimplePersonRecognizer` 类：

```python
# 源文件位置：examples/standalone_gui.py:23-172
class SimplePersonRecognizer:
    def __init__(self, max_persons=3)
    def register_person(self, img, person_name, bbox=None)
    def add_person_sample(self, person_id, img, bbox=None)
    def recognize_person(self, img, bbox=None)
    def delete_person(self, person_id)
    def get_registered_persons(self)
    def get_status_info(self)
```

### **2. 具体迁移步骤**

#### **步骤1：数据结构管理**
```python
# 已在接口中定义，需要完善：
# src/vision/recognition/face_recognition.py:49-55

self.registered_persons = {}  # person_id -> person_info
self.features_database = {}   # person_id -> features_list
self.target_person_id = None
```

#### **步骤2：人物注册逻辑**
```python
# 迁移到：src/vision/recognition/face_recognition.py:58-84
# 源代码：examples/standalone_gui.py:70-102

关键逻辑：
1. 检查人数限制：len(self.registered_persons) >= self.max_persons
2. 检查姓名重复
3. 生成person_id：f"person_{len(self.registered_persons) + 1:02d}"
4. 保存人物信息和特征
```

#### **步骤3：样本添加**
```python
# 迁移到：src/vision/recognition/face_recognition.py:86-102
# 源代码：examples/standalone_gui.py:104-121

关键逻辑：
1. 验证person_id存在
2. 增加feature_count计数
3. 更新数据库
```

#### **步骤4：人物识别**
```python
# 迁移到：src/vision/recognition/face_recognition.py:104-126
# 源代码：examples/standalone_gui.py:123-145

目前是简化实现，需要添加：
1. 真实的特征提取
2. 特征相似度计算
3. 最佳匹配算法
```

#### **步骤5：数据管理方法**
```python
# 已有接口需要完善：
- delete_person()：examples/standalone_gui.py:147-163
- get_registered_persons()：examples/standalone_gui.py:165-172
- get_status_info()：examples/standalone_gui.py:53-68
```

---

## 🔄 GUI集成部分迁移

### **检测使用示例**
```python
# 在standalone_gui.py:588-643 (_process_detections方法)
detections = self.detector.detect_persons(img)
```

### **识别使用示例** 
```python
# 在standalone_gui.py:626-640
person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
```

### **记录流程迁移**
```python
# 源代码：examples/standalone_gui.py:793-849 (_process_recording方法)
# 这部分逻辑可以保留在GUI中，调用识别模块的接口
```

---

## 📝 迁移优先级

### **第一阶段：基础功能**
1. ✅ 检测器初始化（person_detector.py）
2. ✅ 基础检测逻辑（detect_persons）
3. ✅ 识别器数据结构（face_recognition.py）
4. ✅ 人物注册和管理

### **第二阶段：完整功能**
1. 🔲 检测框绘制（draw_detection_boxes）
2. 🔲 特征提取和相似度计算
3. 🔲 数据库持久化
4. 🔲 完整的识别逻辑

### **第三阶段：优化和扩展**
1. 🔲 检测结果过滤和优化
2. 🔲 识别准确度提升
3. 🔲 错误处理和异常恢复
4. 🔲 性能优化

---

## 🧪 测试建议

### **分模块测试**
1. 创建 `examples/test_person_detector.py` 测试检测功能
2. 创建 `examples/test_face_recognition.py` 测试识别功能
3. 使用 `standalone_gui.py` 作为功能验证基准

### **集成测试**
1. 在 `main.py` 中逐步集成新模块
2. 对比新模块与 `standalone_gui.py` 的功能一致性
3. 性能基准测试

---

## 💡 实现建议

1. **保持接口一致性**：确保迁移后的接口与当前定义保持一致
2. **分步骤迁移**：先迁移核心功能，再添加高级特性
3. **保留调试功能**：迁移时保留必要的调试输出和错误处理
4. **向后兼容**：确保现有的GUI代码能够无缝切换到新模块

## 🔧 开发工具

- 使用 `git` 跟踪迁移进度
- 运行 `python3 -m py_compile` 检查语法
- 使用 `examples/standalone_gui.py` 作为功能参考
- 在 `main.py` 中测试模块集成

这个指导应该能帮助你有条理地将功能从 `standalone_gui.py` 迁移到独立的模块中。每一步都有明确的源码位置和目标位置，以及具体的实现建议。
