#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于用户示例的触摸按钮测试
直接使用用户提供的触摸检测代码
"""

from maix import touchscreen, app, time, display, image, camera

# 初始化硬件
try:
    ts = touchscreen.TouchScreen()
    has_touchscreen = True
    print("✓ Touchscreen initialized")
except:
    ts = None
    has_touchscreen = False
    print("✗ Touchscreen not available")

disp = display.Display()
cam = camera.Camera(512, 320)

# 触摸状态
pressed_already = False
last_x = 0
last_y = 0
last_pressed = False

# 创建基础图像
img = image.Image(disp.width(), disp.height())

# 按键配置
exit_label = "< Exit"
size = image.string_size(exit_label)
exit_btn_pos = [0, 0, 8*2 + size.width(), 12 * 2 + size.height()]

record_label = "Record"
size = image.string_size(record_label)
record_btn_pos = [0, 0, 8*2 + size[0], 12 * 2 + size[1]]
record_btn_pos[0] = disp.width() - record_btn_pos[2]

clear_label = "Clear"
size = image.string_size(clear_label)
clear_btn_pos = [0, 0, 8*2 + size[0], 12 * 2 + size[1]]
clear_btn_pos[0] = disp.width() - clear_btn_pos[2]
clear_btn_pos[1] = record_btn_pos[1] + record_btn_pos[3] + 10

# 应用状态
recording = False
recorded_count = 0
max_records = 3

def draw_camera_feed(img):
    """绘制摄像头画面"""
    try:
        cam_img = cam.read()
        if cam_img:
            # 缩放摄像头图像到左半部分
            cam_width = disp.width() // 2
            cam_height = disp.height()
            
            # 简单的图像复制（实际应用中可能需要缩放）
            try:
                # 将摄像头图像绘制到左半部分
                img.draw_image(0, 0, cam_img)
            except:
                # 如果绘制失败，用颜色块代替
                img.draw_rect(0, 0, cam_width, cam_height, image.Color.from_rgb(50, 50, 50), -1)
                img.draw_string(cam_width//4, cam_height//2, "Camera", image.Color.from_rgb(255, 255, 255))
    except:
        # 摄像头读取失败，绘制占位符
        cam_width = disp.width() // 2
        cam_height = disp.height()
        img.draw_rect(0, 0, cam_width, cam_height, image.Color.from_rgb(30, 30, 30), -1)
        img.draw_string(cam_width//4, cam_height//2, "No Camera", image.Color.from_rgb(255, 0, 0))

def draw_btns(img):
    """绘制按键"""
    # Exit 按钮
    img.draw_string(8, 12, exit_label, image.Color.from_rgb(255, 255, 255))
    img.draw_rect(exit_btn_pos[0], exit_btn_pos[1], exit_btn_pos[2], exit_btn_pos[3], 
                  image.Color.from_rgb(255, 255, 255), 2)

    # Record 按钮
    record_color = image.Color.from_rgb(255, 255, 0) if recording else image.Color.from_rgb(0, 255, 0)
    record_text = "Stop" if recording else record_label
    
    img.draw_string(record_btn_pos[0] + 8, 12, record_text, record_color)
    img.draw_rect(record_btn_pos[0], record_btn_pos[1], record_btn_pos[2], record_btn_pos[3], 
                  record_color, 2)

    # Clear 按钮
    clear_color = image.Color.from_rgb(255, 0, 0) if recorded_count > 0 else image.Color.from_rgb(100, 100, 100)
    img.draw_string(clear_btn_pos[0] + 8, clear_btn_pos[1] + 12, clear_label, clear_color)
    img.draw_rect(clear_btn_pos[0], clear_btn_pos[1], clear_btn_pos[2], clear_btn_pos[3], 
                  clear_color, 2)

def draw_status(img):
    """绘制状态信息"""
    # 状态文本
    status_y = disp.height() - 80
    
    # 记录状态
    if recording:
        status_text = f"Recording... ({recorded_count}/{max_records})"
        color = image.Color.from_rgb(255, 255, 0)
    else:
        status_text = f"Ready - Records: {recorded_count}/{max_records}"
        color = image.Color.from_rgb(0, 255, 0)
    
    img.draw_string(10, status_y, status_text, color)
    
    # 触摸状态
    touch_status = "Touchscreen OK" if has_touchscreen else "No Touch"
    touch_color = image.Color.from_rgb(0, 255, 255) if has_touchscreen else image.Color.from_rgb(255, 0, 0)
    img.draw_string(10, status_y + 20, touch_status, touch_color)
    
    # 指令
    img.draw_string(10, status_y + 40, "Touch buttons to control", 
                   image.Color.from_rgb(200, 200, 200))

def is_in_button(x, y, btn_pos):
    """检查点是否在按钮内"""
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def on_clicked(x, y):
    """处理点击事件"""
    global img, recording, recorded_count
    
    if is_in_button(x, y, exit_btn_pos):
        print("Exit button clicked")
        app.set_exit_flag(True)
        
    elif is_in_button(x, y, record_btn_pos):
        if not recording:
            if recorded_count < max_records:
                recording = True
                print(f"Started recording {recorded_count + 1}")
            else:
                print("Max records reached!")
        else:
            recording = False
            recorded_count += 1
            print(f"Recording {recorded_count} completed")
            
    elif is_in_button(x, y, clear_btn_pos):
        if recorded_count > 0:
            recorded_count = 0
            recording = False
            print("All records cleared")
        else:
            print("No records to clear")

def main():
    """主函数"""
    global img, pressed_already, last_x, last_y, last_pressed
    
    print("=== Touchscreen Button Test ===")
    print("Based on user provided touch example")
    
    if not has_touchscreen:
        print("⚠️  Warning: Touchscreen not available - display only mode")
    
    # 初始绘制
    img = image.Image(disp.width(), disp.height())
    
    try:
        while not app.need_exit():
            # 清空图像
            img = image.Image(disp.width(), disp.height())
            
            # 绘制摄像头画面
            draw_camera_feed(img)
            
            # 绘制按键和状态
            draw_btns(img)
            draw_status(img)
            
            # 处理触摸事件
            if has_touchscreen:
                try:
                    x, y, pressed = ts.read()
                    
                    # 检查状态变化
                    if x != last_x or y != last_y or pressed != last_pressed:
                        last_x = x
                        last_y = y
                        last_pressed = pressed
                    
                    # 处理触摸
                    if pressed:
                        pressed_already = True
                        # 绘制触摸点
                        img.draw_circle(x, y, 3, image.Color.from_rgb(255, 255, 255), 2)
                    else:
                        # 触摸释放
                        if pressed_already:
                            print(f"Touch released at: ({x}, {y})")
                            pressed_already = False
                            on_clicked(x, y)
                            
                except Exception as e:
                    print(f"Touch error: {e}")
            
            # 显示画面
            disp.show(img)
            
            # 控制帧率
            time.sleep(0.033)  # 约30FPS
            
    except KeyboardInterrupt:
        print("\nProgram interrupted")
    except Exception as e:
        print(f"Program error: {e}")
    finally:
        print("Cleaning up...")
        cam.close()
        print("Program ended")

if __name__ == "__main__":
    main()
