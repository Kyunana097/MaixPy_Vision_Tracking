# API参考文档

## 概述

本文档描述了MaixPy视觉识别云台系统的API接口。

## 核心模块

### 1. 视觉处理模块 (src.vision)

#### PersonDetector类
- `detect_persons(image)` - 检测图像中的人物
- `draw_green_boxes(image, detections)` - 绘制绿色标记框

#### FaceRecognition类  
- `learn_target(target_image)` - 学习目标人物特征
- `extract_features(image)` - 提取图像特征
- `match_target(person_image)` - 匹配目标人物

#### TargetTracker类
- `track_target(image, target_detections)` - 跟踪目标人物
- `draw_red_box(image, position)` - 绘制红色标记框
- `get_gimbal_control_signal()` - 获取云台控制信号

### 2. 硬件控制模块 (src.hardware)

#### CameraController类
- `initialize_camera()` - 初始化摄像头
- `capture_image()` - 采集图像
- `set_resolution(width, height)` - 设置分辨率

#### BuzzerController类
- `start_alarm(frequency, duration)` - 开始报警
- `stop_alarm()` - 停止报警
- `beep(times, interval)` - 蜂鸣指定次数

#### ButtonController类
- `is_pressed()` - 检查按键状态
- `wait_for_press(timeout)` - 等待按键按下
- `register_callback(callback_function)` - 注册回调函数

#### GimbalInterface类
- `set_angle(pan_angle, tilt_angle)` - 设置云台角度
- `get_angle()` - 获取当前角度
- `track_target(target_x, target_y, image_width, image_height)` - 自动跟踪

### 3. 工具模块 (src.utils)

#### ConfigManager类
- `load_config()` - 加载配置文件
- `save_config()` - 保存配置
- `get_camera_config()` - 获取摄像头配置

#### ImageProcessor类
- `resize_image(image, width, height)` - 调整图像大小
- `crop_image(image, x, y, w, h)` - 裁剪图像
- `draw_rectangle(image, x, y, w, h, color, thickness)` - 绘制矩形
- `draw_text(image, text, x, y, color, size)` - 绘制文本

#### SystemState类
- `set_mode(mode)` - 设置系统模式
- `get_mode()` - 获取当前模式
- `set_safety_state(state)` - 设置安全状态

## 使用示例

```python
# 初始化系统
camera = CameraController()
detector = PersonDetector()
recognizer = FaceRecognition()
tracker = TargetTracker()
gimbal = GimbalInterface()

# 主循环
while True:
    # 采集图像
    image = camera.capture_image()
    
    # 检测人物
    detections = detector.detect_persons(image)
    
    # 跟踪目标
    if target_learned:
        position, found = tracker.track_target(image, detections)
        if found:
            gimbal.track_target(position[0], position[1], image.width, image.height)
```

## 配置参数

详见 `config/system_config.json` 文件。

## 错误处理

所有API函数都包含适当的错误处理和返回状态码。
