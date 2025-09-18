# MaixPy视觉识别云台系统

## 项目简介

基于MaixPy和M0G3507主控的智能视觉识别云台系统，能够识别和跟踪特定人物目标，并提供安全监控功能。

## 系统功能

### 1. 人物识别功能
- 识别三个不同人物（动漫或真人形象，上半身，不大于5x5cm²）
- 人物贴在白底A4纸上，摄像头距离不少于50厘米
- 使用绿色框标记识别到的人物

### 2. 目标学习与跟踪
- 将目标人物贴纸放置在摄像头前进行学习和记录
- 贴纸移开后，自动识别A4纸上的对应人物
- 使用红色框标记目标人物

### 3. 安全监控系统
- 检测A4纸上是否存在目标人物
- 无目标人物时输出"SAFE"
- 发现目标人物时输出"WARNING"并启动蜂鸣器报警
- 按键解除报警功能

### 4. 云台控制
- 舵机云台控制（C语言实现）
- 自动跟踪目标人物

## 硬件要求

- **主控**: M0G3507
- **摄像头**: MaixPy兼容摄像头
- **云台**: 舵机云台
- **蜂鸣器**: 报警提示
- **按键**: 报警解除

## 软件架构

```
MaixPy_Vision_Tracking/
├── src/                    # 源代码目录
│   ├── vision/            # 视觉处理模块
│   │   ├── detection/     # 人物检测
│   │   ├── tracking/      # 目标跟踪
│   │   └── recognition/   # 人物识别
│   ├── hardware/          # 硬件控制模块
│   │   ├── camera/        # 摄像头控制
│   │   ├── buzzer/        # 蜂鸣器控制
│   │   └── button/        # 按键控制
│   └── utils/             # 工具函数
├── data/                  # 数据目录
│   ├── images/           # 图像数据
│   │   ├── person1/      # 人物1图像
│   │   ├── person2/      # 人物2图像
│   │   ├── person3/      # 人物3图像
│   │   ├── target_learning/ # 目标学习图像
│   │   └── temp/         # 临时图像
│   └── models/           # 模型文件
├── gimbal_c_code/        # 云台C语言代码目录
├── config/               # 配置文件
├── docs/                 # 文档
├── tests/                # 测试文件
└── examples/             # 示例代码
```

## 完成状态

### ✅ 第一阶段：基础视觉功能
- [x] 摄像头初始化和图像采集
- [x] 人物检测算法实现（PersonDetector模块）
- [x] 绿色框标记功能
- [x] 实时FPS监控

### 🚧 第二阶段：目标学习与识别  
- [x] 识别模块框架（FaceRecognition接口）
- [ ] 完整特征提取和匹配算法
- [ ] 红色框标记功能
- [ ] 人物注册和管理系统

### 🔄 第三阶段：安全监控系统
- [ ] 安全状态检测逻辑
- [ ] SAFE/WARNING状态输出
- [ ] 蜂鸣器报警系统

### ✅ 第四阶段：硬件集成
- [x] 虚拟触摸按键系统（VirtualButtonManager）
- [x] 云台控制接口（C语言框架）
- [x] 触摸坐标映射和校准（512x320优化）
- [x] 三种工作模式（RECORD/RECOGNIZE/TRACK）

### ✅ 第五阶段：模块化架构
- [x] 检测模块独立化（person_detector.py）
- [x] 识别模块框架（face_recognition.py）
- [x] 虚拟按钮系统（virtual_button.py）
- [x] 主程序集成（main.py）
- [x] 模块迁移指导文档

## 技术规格

### 核心技术栈
- **编程语言**: Python (MaixPy), C (云台控制)
- **图像处理**: MaixPy内置视觉库, nn.FaceDetector
- **人物识别**: 特征匹配算法, 人脸检测
- **硬件通信**: UART, GPIO, 触摸屏
- **实时性**: 实时图像处理和响应 (25-35 FPS)

### 模块架构
- **PersonDetector**: 人脸检测 → 上半身推算 → 边界框绘制
- **PersonRecognizer**: 特征提取 → 相似度计算 → 人物识别
- **VirtualButtonManager**: 触摸检测 → 坐标映射 → 按钮响应
- **CameraController**: 摄像头初始化 → 图像采集 → 分辨率控制

### 性能指标
- **检测精度**: 人脸检测置信度 > 0.9
- **显示分辨率**: 512x320 (优化) / 640x480 (支持)
- **触摸精度**: 校准后精确度 > 95%
- **内存占用**: 低内存设计，适合嵌入式设备

## 安装与使用

### 环境要求
- MaixPy固件
- M0G3507开发环境
- Python 3.x (开发调试用)

### 快速开始
1. 将项目完整拷贝到设备（确保 `main.py` 与 `src/` 同级）
2. 运行主程序（推荐在设备端运行整个项目）：
```bash
python3 main.py
```
3. 若未部署 `src/` 目录，主程序会自动启用内置摄像头兜底，仍能显示实时画面

## 更新日志

### v1.2.0 (2025-09-19) - 检测模块集成与架构完善
**主要更新:**
- 🔍 **人物检测模块完全集成**：从standalone_gui.py迁移核心检测功能到独立模块
- 🏗️ **模块化架构**：`person_detector.py`提供标准检测接口，支持模块化开发
- 🎯 **main.py功能升级**：集成人物检测，支持RECORD/RECOGNIZE/TRACK三种模式
- 🔧 **虚拟按钮系统**：完整的触摸按钮模块，支持512x320分辨率校准
- 📱 **界面简化**：精简UI显示，专注FPS监控和核心功能

**技术架构改进:**
- 🧩 **PersonDetector类**：标准化检测接口，支持人脸检测和上半身推算
- 🎮 **VirtualButtonManager**：独立的虚拟按钮系统，支持触摸映射和主题
- 📊 **实时FPS显示**：每0.5秒更新，精确监控系统性能
- 🔄 **模式切换**：DEBUG/MODE/EXIT按钮，支持三种工作模式

**检测功能:**
- ✅ **RECOGNIZE模式**：实时人脸检测，绿色框标记，显示置信度
- ✅ **RECORD模式**：录制模式检测，黄色框标记，准备人物注册
- 🔧 **调试支持**：完整的调试信息输出，支持状态诊断

**文件结构:**
- `src/vision/detection/person_detector.py` - 核心检测模块
- `src/vision/recognition/face_recognition.py` - 识别模块框架
- `src/hardware/button/` - 完整的虚拟按钮系统
- `docs/module_migration_guide.md` - 模块迁移指导

### v1.1.0 (2025-09-18) - 结构精简与入口统一
**主要更新:**
- 📦 将示例/调试脚本归档至 `examples/_archive/`，保留核心示例
- 🟢 主入口统一为 `main.py`，自动兼容 MaixPy `/tmp/maixpy_run` 路径
- 🖥️ 默认显示摄像头画面；未找到 `src/` 时启用内置摄像头控制器

**保留的核心示例:**
- `examples/test_camera.py`
- `examples/standalone_gui.py`
- `examples/simple_high_fps_gui.py`

### v1.0.0 (2025-09-14) - 核心功能完成
**主要功能实现:**
- ✅ 完整的人脸检测和识别系统
- ✅ 触摸界面控制系统
- ✅ 高帧率优化版本
- ✅ 触摸坐标精确校准

**新增文件:**
- `examples/simple_high_fps_gui.py` - 高帧率简化界面（推荐使用）
- `examples/standalone_gui.py` - 完整功能独立界面
- `examples/touch_coordinate_debug.py` - 触摸坐标校准工具
- `examples/test_calibrated_mapping.py` - 映射精度验证工具
- `src/vision/recognition/face_recognition.py` - 人脸识别核心模块
- `src/vision/detection/person_detector.py` - 人物检测核心模块

**技术突破:**
- 🎯 精确触摸坐标映射 (Scale: 1.6615x1.7352, Offset: -197.74,-140.00)
- 🚀 高帧率优化 (640x480@25-35FPS)
- 📱 大按键设计 (80x80像素)
- 🧠 简化人脸识别算法
- 🔄 实时FPS显示

**界面功能:**
- **REC按钮**: 2秒记录新人脸 (最多3个)
- **CLR按钮**: 清除所有记录
- **EXIT按钮**: 安全退出
- **实时识别**: 绿色框=已识别，红色框=未知，黄色框=记录中

**开发环境:**
- M0G3507 C语言开发环境 (GCC + VS Code)
- MaixPy触摸屏支持
- 跨平台构建系统

### v0.2.0 (2025-09-13) - 硬件集成
**主要更新:**
- 📱 触摸屏界面开发
- 🎮 虚拟按键系统
- 🔧 M0G3507开发环境配置
- 📡 UART通信协议设计

### v0.1.0 (2025-09-12) - 项目初始化
**项目建立:**
- 📁 完整项目结构
- 📋 开发计划制定
- 🏗️ 代码框架搭建

## 快速开始

### 主程序（推荐）
```bash
# 运行主程序 - 支持三种模式切换
python3 main.py
```

**功能特性：**
- 🎯 **RECOGNIZE模式**：实时人脸检测，绿色框标记
- 📝 **RECORD模式**：人物录制，黄色框标记（待完善）
- 🎮 **TRACK模式**：目标跟踪（待实现）
- 🔧 **DEBUG按钮**：显示系统状态和检测器信息
- 📊 **实时FPS**：性能监控显示

### 独立示例
```bash
# 高帧率人脸识别界面（完整功能）
python3 examples/standalone_gui.py

# 简化高性能版本
python3 examples/simple_high_fps_gui.py
```

### 开发和调试
```bash
# 触摸坐标校准（如需要）
python3 examples/touch_coordinate_debug.py

# 虚拟按钮测试
python3 examples/test_virtual_button.py
```

## 注意事项

### 使用建议
- 🎯 **推荐使用 `main.py`** 获得最新的模块化功能
- 📱 **触摸校准**：512x320分辨率已优化，640x480需要校准
- 🔧 **调试模式**：按DEBUG按钮查看详细系统信息
- 📊 **性能监控**：FPS显示帮助评估系统性能

### 硬件要求
- 确保摄像头与A4纸距离不少于50厘米
- 保持良好的光照条件
- 人物图像应清晰，背景简洁
- 支持触摸屏设备（推荐512x320分辨率）

### 开发提示
- 检测模块支持独立测试和调试
- 识别模块框架已就绪，可继续完善功能
- 虚拟按钮系统支持主题和布局自定义
- 详细的模块迁移指导见 `docs/module_migration_guide.md`

### 故障排除
- 检测器初始化失败：检查nn.FaceDetector模型路径
- 触摸不响应：运行触摸校准工具校准坐标
- FPS过低：降低分辨率或优化检测参数
- 模块导入错误：确保src目录结构完整

