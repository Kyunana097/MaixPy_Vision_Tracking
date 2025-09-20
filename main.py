#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MaixPy 视觉识别云台系统 - 主程序
作者: Kyunana
描述: 主程序入口，负责系统初始化和主循环控制
"""

import sys
import os
import time

# 可选的MaixPy模块（显示与退出标志）
try:
    from maix import display as _maix_display
except Exception:
    _maix_display = None
try:
    from maix import app as _maix_app
except Exception:
    _maix_app = None


# 路径设置：确保能导入 src 包（兼容 /tmp/maixpy_run 等环境）
project_root = os.path.dirname(os.path.abspath(__file__))
candidate_roots = [
    project_root,
    os.path.abspath(os.path.join(project_root, "..")),
    "/home/kyunana/MaixPy_Vision_Tracking",
    "/flash",
    "/sdcard",
]
for base in candidate_roots:
    try:
        if os.path.isdir(os.path.join(base, "src")) and base not in sys.path:
            sys.path.insert(0, base)
            break
    except Exception:
        pass


USING_EMBEDDED_CAMERA = False
try:
    from src.hardware.camera.camera_controller import CameraController
except Exception:
    print("[Warn] 'src' package not found. Using embedded CameraController fallback.")
    try:
        from maix import camera as _maix_camera
    except Exception as _e:
        print("[Error] Maix camera module not available:", _e)
        raise

class MaixVisionSystem:
    def __init__(self):
        print("=== MaixPy Vision Tracking System ===")
        print("Initializing system...")

        self.camera = CameraController(width=512, height=320)
        self.detector = None  # 待集成：检测模块
        self.recognizer = None  # 待集成：识别模块
        self.gimbal = None  # 待集成：云台模块
        self.running = False
        self.disp = None
        self.mode = os.getenv("MODE", "recognize")  # record | recognize | track
        if self.mode not in ("record", "recognize", "track"):
            self.mode = "recognize"
        print(f"Mode: {self.mode}")
        self.max_persons = 3
        
        # 虚拟按钮管理器
        self.button_manager = None
        self.button_click_count = 0
        
        # 缩略图显示相关
        self.current_thumbnail_person = None  # 当前显示缩略图的人物ID
        
        # FPS计算相关
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0.0
        self.last_fps_update = time.time()

    def initialize_modules(self):
        try:
            print("📷 Initializing camera...")
            ok = self.camera.initialize_camera()
            if not ok:
                print("❌ Camera init failed")
                return False
            print("✅ Camera ok")

            # 初始化人物检测器
            print("🔍 Initializing person detector...")
            try:
                from src.vision.detection.person_detector import PersonDetector
                camera_width, camera_height = self.camera.get_resolution()
                self.detector = PersonDetector(camera_width, camera_height)
                print("✅ Person detector initialized")
            except Exception as e:
                print(f"✗ Person detector initialization failed: {e}")
                self.detector = None

            # 初始化人物识别器
            print("🧠 Initializing person recognizer...")
            try:
                from src.vision.recognition.face_recognition import PersonRecognizer
                # 传入检测器实例，用于真实的图像相似度计算
                self.recognizer = PersonRecognizer(
                    max_persons=self.max_persons,
                    detector=self.detector  # 关键：传入检测器用于图像比较
                )
                print("✅ Person recognizer initialized with real image comparison")
            except Exception as e:
                print(f"✗ Person recognizer initialization failed: {e}")
                self.recognizer = None

            print("🎮 Initializing gimbal... (skipped - to be integrated)")

            # 初始化显示（如果可用）
            if _maix_display is not None:
                try:
                    self.disp = _maix_display.Display()
                except Exception:
                    self.disp = None
            
            # 初始化虚拟按钮
            print("🔘 Initializing virtual buttons...")
            try:
                from src.hardware.button import VirtualButtonManager, ButtonPresets
                camera_width, camera_height = self.camera.get_resolution()
                self.button_manager = VirtualButtonManager(camera_width, camera_height)
                self._setup_buttons()
                print("✅ Virtual buttons initialized")
            except Exception as e:
                print(f"✗ Virtual buttons initialization failed: {e}")
                self.button_manager = None

            print("✅ All modules initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize modules: {e}")
            return False

    def start_system(self):
        if not self.initialize_modules():
            print("Failed to start system")
            return

        print("🚀 Starting main loop...")
        self.running = True
        try:
            self.main_loop()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"❌ System error: {e}")
        finally:
            self.cleanup()

    def main_loop(self):
        while self.running and (_maix_app is None or not _maix_app.need_exit()):
            img = self.camera.capture_image()
            if img is None:
                continue

            # 显示画面
            if self.disp is not None:
                try:
                    # 处理虚拟按钮输入
                    if self.button_manager:
                        clicked_button = self.button_manager.check_touch_input()
                        self.button_manager.update()
                    
                    # 运行当前模式（占位，待模块接入）
                    if self.mode == "record":
                        self._mode_record(img)
                    elif self.mode == "recognize":
                        self._mode_recognize(img)
                    elif self.mode == "track":
                        self._mode_track(img)
                    
                    # 绘制界面信息
                    self._draw_ui_info(img)
                    
                    # 绘制虚拟按钮
                    if self.button_manager:
                        self.button_manager.draw_all(img)
                        self.button_manager.draw_touch_indicator(img)
                    
                    # 显示
                    self.disp.show(img)
                except Exception:
                    pass

            # TODO: 检测/识别/云台/触摸UI等

            # 初始化帧计数器（如果还没有）
            if not hasattr(self, 'frame_count'):
                self.frame_count = 0
            self.frame_count += 1
            
            # 更新FPS计算
            self._update_fps()
            
            time.sleep(0.01)

    def cleanup(self):
        print("🧹 Cleaning up...")
        try:
            if self.camera:
                self.camera.release_camera()
            # 云台模块尚未集成
        finally:
            print("✅ Cleanup completed")

    # =============== 虚拟按钮相关 ===============
    def _update_fps(self):
        """更新FPS计算（每半秒更新一次）"""
        self.fps_counter += 1
        current_time = time.time()
        
        # 每半秒更新一次FPS显示
        if current_time - self.last_fps_update >= 0.5:
            time_diff = current_time - self.fps_start_time
            if time_diff > 0:
                self.current_fps = self.fps_counter / time_diff
                
            # 重置计数器
            self.fps_counter = 0
            self.fps_start_time = current_time
            self.last_fps_update = current_time
    
    def _get_mode_button_texts(self):
        """根据当前模式返回功能按钮的文本"""
        if self.mode == "recognize":
            return "START", "STOP"
        elif self.mode == "record":
            return "ADD", "CLEAR"
        elif self.mode == "track":
            return "PREV", "NEXT"
        else:
            return "FUNC1", "FUNC2"
    
    def _setup_buttons(self):
        """设置虚拟按钮"""
        if not self.button_manager:
            return
        
        try:
            from src.hardware.button import ButtonPresets
            
            # 创建简化的控制按钮（适合调试）
            width, height = self.camera.get_resolution()
            
            # 调试按钮
            debug_btn = self.button_manager.create_button(
                button_id='debug',
                x=width - 100,
                y=20,
                width=80,
                height=40,
                text='DEBUG'
            )
            debug_btn.set_colors(
                normal=(100, 100, 200),  # 蓝色
                active=(150, 150, 255),  # 亮蓝色
                disabled=(60, 60, 60)
            )
            debug_btn.set_click_callback(self._on_button_click)
            
            # 模式切换按钮
            mode_btn = self.button_manager.create_button(
                button_id='mode',
                x=width - 100,
                y=70,
                width=80,
                height=40,
                text=self.mode.upper()
            )
            mode_btn.set_colors(
                normal=(200, 100, 0),    # 橙色
                active=(255, 150, 0),    # 亮橙色
                disabled=(60, 60, 60)
            )
            mode_btn.set_click_callback(self._on_button_click)
            
            # 功能按钮1 (左侧)
            func1_text, func2_text = self._get_mode_button_texts()
            func1_btn = self.button_manager.create_button(
                button_id='func1',
                x=width - 100,
                y=120,
                width=70,
                height=35,
                text=func1_text
            )
            func1_btn.set_colors(
                normal=(0, 150, 100),    # 绿色
                active=(0, 200, 150),    # 亮绿色
                disabled=(60, 60, 60)
            )
            func1_btn.set_click_callback(self._on_button_click)
            
            # 功能按钮2 (右侧)
            func2_btn = self.button_manager.create_button(
                button_id='func2',
                x=width - 100,
                y=160,
                width=70,
                height=35,
                text=func2_text
            )
            func2_btn.set_colors(
                normal=(150, 0, 150),    # 紫色
                active=(200, 0, 200),    # 亮紫色
                disabled=(60, 60, 60)
            )
            func2_btn.set_click_callback(self._on_button_click)
            
            # 退出按钮
            exit_btn = self.button_manager.create_button(
                button_id='exit',
                x=20,
                y=20,
                width=60,
                height=30,
                text='EXIT'
            )
            exit_btn.set_colors(
                normal=(150, 0, 0),      # 红色
                active=(200, 0, 0),      # 亮红色
                disabled=(60, 60, 60)
            )
            exit_btn.set_click_callback(self._on_button_click)
            
            print(f"Created {len(self.button_manager.buttons)} virtual buttons")
            
        except Exception as e:
            print(f"Button setup error: {e}")
    
    def _on_button_click(self, button_id: str):
        """
        按钮点击回调函数
        
        Args:
            button_id: 被点击的按钮ID
        """
        self.button_click_count += 1
        print(f"🔘 Button clicked: {button_id} (total clicks: {self.button_click_count})")
        
        if button_id == 'debug':
            self._handle_debug_button()
        elif button_id == 'mode':
            self._handle_mode_button()
        elif button_id == 'exit':
            self._handle_exit_button()
        elif button_id == 'func1':
            self._handle_func1_button()
        elif button_id == 'func2':
            self._handle_func2_button()
    
    def _handle_debug_button(self):
        """处理调试按钮点击"""
        print("=" * 50)
        print("🐛 === SYSTEM DEBUG INFO ===")
        print(f"  Current mode: {self.mode}")
        print(f"  Frame count: {getattr(self, 'frame_count', 0)}")
        print(f"  FPS: {self.current_fps:.2f}")
        print(f"  Camera resolution: {self.camera.get_resolution()}")
        
        if self.button_manager:
            print(f"  Touch available: {self.button_manager.has_touchscreen}")
            print(f"  Button count: {len(self.button_manager.buttons)}")
        
        if self.detector:
            debug_info = self.detector.get_debug_info()
            print(f"  Detector status: {debug_info}")
        else:
            print("  Detector: Not initialized")
        
        if self.recognizer:
            status = self.recognizer.get_status_info()
            print(f"  Recognizer status:")
            print(f"    Registered persons: {status['registered_count']}/{status['max_persons']}")
            print(f"    Total samples: {status['total_samples']}")
            print(f"    Face detector: {status['has_face_detector']}")
            target_person = status.get('target_person', {})
            target_name = target_person.get('name', 'None') if target_person else 'None'
            print(f"    Target person: {target_name}")
            print(f"    Thumbnail person: {self.current_thumbnail_person}")
            
            # 列出所有已注册人物
            persons = self.recognizer.get_registered_persons()
            if persons:
                print("  Registered persons:")
                for person_id, info in persons.items():
                    print(f"    {person_id}: {info['name']} ({info['sample_count']} samples)")
            else:
                print("  No registered persons")
        else:
            print("  Recognizer: Not initialized")
        
        print("=" * 50)
    
    def _handle_mode_button(self):
        """处理模式切换按钮"""
        modes = ["record", "recognize", "track"]
        current_idx = modes.index(self.mode)
        next_idx = (current_idx + 1) % len(modes)
        self.mode = modes[next_idx]
        
        print(f"🔄 Mode switched to: {self.mode}")
        
        # 更新按钮文字
        if self.button_manager:
            mode_btn = self.button_manager.get_button('mode')
            if mode_btn:
                mode_btn.set_text(self.mode.upper())
            
            # 更新功能按钮文字
            func1_text, func2_text = self._get_mode_button_texts()
            func1_btn = self.button_manager.get_button('func1')
            func2_btn = self.button_manager.get_button('func2')
            if func1_btn:
                func1_btn.set_text(func1_text)
            if func2_btn:
                func2_btn.set_text(func2_text)
    
    def _handle_exit_button(self):
        """处理退出按钮"""
        print("🚪 Exit button pressed - stopping system")
        self.running = False
    
    def _handle_func1_button(self):
        """处理功能按钮1点击"""
        if self.mode == "recognize":
            self._handle_recognize_start()
        elif self.mode == "record":
            self._handle_record_add()
        elif self.mode == "track":
            self._handle_track_prev()
    
    def _handle_func2_button(self):
        """处理功能按钮2点击"""
        if self.mode == "recognize":
            self._handle_recognize_stop()
        elif self.mode == "record":
            self._handle_record_clear()
        elif self.mode == "track":
            self._handle_track_next()
    
    # =============== 各模式功能按钮处理方法（预留接口） ===============
    def _handle_recognize_start(self):
        """处理识别模式的开始按钮"""
        print("🚀 Recognize mode: START button pressed")
        # TODO: 启动识别功能
        pass
    
    def _handle_recognize_stop(self):
        """处理识别模式的停止按钮"""
        print("⏹️ Recognize mode: STOP button pressed")
        # TODO: 停止识别功能
        pass
    
    def _handle_record_add(self):
        """处理录制模式的添加按钮"""
        print("➕ Record mode: ADD button pressed")
        
        if not self.recognizer:
            print("✗ 识别器未初始化")
            return
        
        # 获取当前画面
        img = self.camera.capture_image()
        if img is None:
            print("✗ 无法获取摄像头图像")
            return
        
        # 检查是否已达到最大人数
        status = self.recognizer.get_status_info()
        if status['available_slots'] <= 0:
            print(f"✗ 已达到最大人数限制 ({status['max_persons']})")
            return
        
        # 生成人物名称
        person_name = f"Person{status['registered_count'] + 1}"
        
        # 注册新人物
        print(f"🔄 开始注册人物: {person_name}")
        success, person_id, message = self.recognizer.register_person(img, person_name)
        if success:
            print(f"✅ {message}")
            print(f"   人物ID: {person_id}")
            # 更新缩略图显示
            self.current_thumbnail_person = person_id
        else:
            print(f"✗ 注册失败: {message}")
    
    def _handle_record_clear(self):
        """处理录制模式的清空按钮"""
        print("🗑️ Record mode: CLEAR button pressed")
        
        if not self.recognizer:
            print("✗ 识别器未初始化")
            return
        
        # 清空所有人物数据
        success, message = self.recognizer.clear_all_persons()
        if success:
            print(f"✅ {message}")
        else:
            print(f"✗ 清空失败: {message}")
    
    def _handle_track_prev(self):
        """处理跟踪模式的上一个按钮"""
        print("⬅️ Track mode: PREV button pressed")
        
        if not self.recognizer:
            print("✗ 识别器未初始化")
            return
        
        # 获取已注册人物列表
        persons = self.recognizer.get_registered_persons()
        if not persons:
            print("✗ 暂无已注册人物")
            return
        
        person_ids = list(persons.keys())
        current_target = self.recognizer.get_target_person()
        
        if current_target is None:
            # 如果没有目标，选择最后一个
            new_target_id = person_ids[-1]
        else:
            # 切换到上一个
            current_idx = person_ids.index(current_target['id'])
            new_target_id = person_ids[(current_idx - 1) % len(person_ids)]
        
        # 设置新目标
        success, message = self.recognizer.set_target_person(new_target_id)
        if success:
            print(f"✅ {message}")
            # 更新缩略图显示
            self.current_thumbnail_person = new_target_id
        else:
            print(f"✗ 切换失败: {message}")
    
    def _handle_track_next(self):
        """处理跟踪模式的下一个按钮"""
        print("➡️ Track mode: NEXT button pressed")
        
        if not self.recognizer:
            print("✗ 识别器未初始化")
            return
        
        # 获取已注册人物列表
        persons = self.recognizer.get_registered_persons()
        if not persons:
            print("✗ 暂无已注册人物")
            return
        
        person_ids = list(persons.keys())
        current_target = self.recognizer.get_target_person()
        
        if current_target is None:
            # 如果没有目标，选择第一个
            new_target_id = person_ids[0]
        else:
            # 切换到下一个
            current_idx = person_ids.index(current_target['id'])
            new_target_id = person_ids[(current_idx + 1) % len(person_ids)]
        
        # 设置新目标
        success, message = self.recognizer.set_target_person(new_target_id)
        if success:
            print(f"✅ {message}")
            # 更新缩略图显示
            self.current_thumbnail_person = new_target_id
        else:
            print(f"✗ 切换失败: {message}")
    
    def _draw_ui_info(self, img):
        """
        绘制界面信息
        
        Args:
            img: 图像对象
        """
        try:
            # 检查是否有MaixPy的image模块
            try:
                from maix import image as _image
            except:
                return
            
            # 系统标题
            title = f"{self.mode.upper()} Mode"
            white_color = _image.Color.from_rgb(255, 255, 255)  # 白色
            img.draw_string(200, 10, title, color=white_color, scale=1.0)
            
            # 在EXIT按钮下方显示FPS
            fps_text = f"FPS: {self.current_fps:.1f}"
            yellow_color = _image.Color.from_rgb(255, 255, 0)  # 黄色
            img.draw_string(20, 105, fps_text, color=yellow_color, scale=1.2)
            
            # 显示识别器状态信息
            if self.recognizer:
                status = self.recognizer.get_status_info()
                status_text = f"Persons: {status['registered_count']}/{status['max_persons']}"
                # 使用RGB颜色值替代不存在的颜色常量
                cyan_color = _image.Color.from_rgb(0, 255, 255)  # 青色
                img.draw_string(20, 130, status_text, color=cyan_color, scale=1.0)
                
                # 显示当前目标（track模式）
                if self.mode == "track":
                    target = self.recognizer.get_target_person()
                    if target:
                        target_text = f"Target: {target['name']}"
                        green_color = _image.Color.from_rgb(0, 255, 0)  # 绿色
                        img.draw_string(20, 150, target_text, color=green_color, scale=1.0)
                        # 设置当前缩略图
                        if not self.current_thumbnail_person:
                            self.current_thumbnail_person = target['id']
                    else:
                        gray_color = _image.Color.from_rgb(128, 128, 128)  # 灰色
                        img.draw_string(20, 150, "Target: None", color=gray_color, scale=1.0)
                
                # 显示人物缩略图（屏幕下方）
                self._draw_person_thumbnail(img)
            
        except Exception as e:
            # 绘制错误时输出调试信息
            print(f"UI draw error: {e}")
            import traceback
            traceback.print_exc()
    
    def _draw_person_thumbnail(self, img):
        """
        在屏幕下方绘制人物缩略图
        
        Args:
            img: 图像对象
        """
        if not self.recognizer:
            return
        
        try:
            from maix import image as _image
            
            # 获取屏幕尺寸
            img_width = img.width() if callable(img.width) else img.width
            img_height = img.height() if callable(img.height) else img.height
            
            # 缩略图显示位置（屏幕下方中央）
            thumbnail_size = 64
            thumbnail_x = (img_width - thumbnail_size) // 2
            thumbnail_y = img_height - thumbnail_size - 10
            
            # 绘制缩略图背景框
            bg_color = _image.Color.from_rgb(50, 50, 50)  # 深灰色背景
            img.draw_rect(thumbnail_x - 2, thumbnail_y - 2, 
                         thumbnail_size + 4, thumbnail_size + 4, 
                         color=bg_color, thickness=-1)  # 填充
            
            # 获取要显示的人物
            display_person = None
            
            if self.mode == "track" and self.current_thumbnail_person:
                # Track模式显示选中的人物
                display_person = self.current_thumbnail_person
            else:
                # 其他模式显示第一个已注册人物
                persons = self.recognizer.get_registered_persons()
                if persons:
                    display_person = list(persons.keys())[0]
                    if self.mode == "track":
                        self.current_thumbnail_person = display_person
            
            # 显示缩略图信息
            if display_person:
                # 获取人物信息
                person_info = self.recognizer.get_registered_persons().get(display_person, {})
                person_name = person_info.get('name', display_person)
                sample_count = person_info.get('sample_count', 0)
                
                # 绘制人物信息框
                white_color = _image.Color.from_rgb(255, 255, 255)
                info_color = _image.Color.from_rgb(0, 200, 0)  # 绿色
                
                # 绘制边框
                img.draw_rect(thumbnail_x, thumbnail_y, thumbnail_size, thumbnail_size,
                            color=white_color, thickness=2)
                
                # 显示人物名称
                name_x = thumbnail_x + (thumbnail_size - len(person_name) * 8) // 2
                img.draw_string(name_x, thumbnail_y + 20, person_name, 
                              color=white_color, scale=1.0)
                
                # 显示样本数量
                sample_text = f"Samples: {sample_count}"
                sample_x = thumbnail_x + (thumbnail_size - len(sample_text) * 6) // 2
                img.draw_string(sample_x, thumbnail_y + 40, sample_text, 
                              color=info_color, scale=0.8)
                
                # 获取并显示实际缩略图
                thumbnail = self.recognizer.get_person_thumbnail(display_person)
                if thumbnail:
                    try:
                        # 确保缩略图大小合适
                        thumb_w = thumbnail.width() if callable(thumbnail.width) else thumbnail.width
                        thumb_h = thumbnail.height() if callable(thumbnail.height) else thumbnail.height
                        
                        # 如果尺寸不匹配，调整缩略图大小
                        if thumb_w != thumbnail_size or thumb_h != thumbnail_size:
                            thumbnail = thumbnail.resize(thumbnail_size, thumbnail_size)
                        
                        # 使用MaixPy最常见的图像合成方法
                        success = False
                        
                        # 方法1：尝试 draw_image (最常见)
                        try:
                            img.draw_image(thumbnail, thumbnail_x, thumbnail_y)
                            success = True
                        except:
                            pass
                        
                        # 方法2：尝试 copy_to (备选)
                        if not success:
                            try:
                                thumbnail.copy_to(img, thumbnail_x, thumbnail_y)
                                success = True
                            except:
                                pass
                        
                        # 方法3：尝试 blit (备选)
                        if not success:
                            try:
                                img.blit(thumbnail, thumbnail_x, thumbnail_y)
                                success = True
                            except:
                                pass
                        
                        # 如果都失败，显示加载成功提示
                        if not success:
                            img.draw_string(thumbnail_x + 5, thumbnail_y + 5, "LOADED", 
                                          color=info_color, scale=0.6)
                        
                    except Exception:
                        # 显示加载失败提示
                        img.draw_string(thumbnail_x + 10, thumbnail_y + 5, "FAILED", 
                                      color=_image.Color.from_rgb(255, 100, 100), scale=0.6)
                else:
                    # 显示"NO IMG"标识
                    img.draw_string(thumbnail_x + 15, thumbnail_y + 5, "NO IMG", 
                                  color=_image.Color.from_rgb(255, 100, 100), scale=0.6)
            else:
                # 显示无人物提示
                white_color = _image.Color.from_rgb(255, 255, 255)
                img.draw_rect(thumbnail_x, thumbnail_y, thumbnail_size, thumbnail_size,
                            color=white_color, thickness=1)
                img.draw_string(thumbnail_x + 15, thumbnail_y + 25, "No Person", 
                              color=white_color, scale=0.7)
            
        except Exception as e:
            print(f"✗ 缩略图绘制失败: {e}")

    # =============== 模式实现（占位，用于分模块调试） ===============
    def _mode_record(self, img):
        # 检测+注册流程模式
        if self.detector:
            # 检测人物
            detections = self.detector.detect_persons(img)
            
            if detections:
                # 绘制检测框（录制模式用黄色）
                try:
                    from maix import image as _image
                    for detection in detections:
                        bbox = detection['bbox']
                        x, y, w, h = bbox
                        yellow_color = _image.Color.from_rgb(255, 255, 0)
                        img.draw_rect(x, y, w, h, color=yellow_color, thickness=2)
                        
                        # 绘制提示
                        img.draw_string(x, max(y-20, 0), "Recording...", color=yellow_color)
                except:
                    pass
                
                # TODO: 添加注册逻辑
                # if self.recognizer:
                #     for detection in detections:
                #         face_bbox = detection.get('face_bbox')
                #         if face_bbox:
                #             success, person_id, message = self.recognizer.register_person(img, "NewPerson", face_bbox)
        else:
            # 检测器未初始化时显示提示
            try:
                from maix import image as _image
                white_color = _image.Color.from_rgb(255, 255, 255)  # 白色
                img.draw_string(10, 200, "Person detector not available", color=white_color)
            except:
                pass

    def _mode_recognize(self, img):
        # 检测+识别+目标标记模式
        if self.detector:
            # 检测人物
            detections = self.detector.detect_persons(img)
            
            if detections:
                # 绘制检测框
                img = self.detector.draw_detection_boxes(img, detections)
                
                # 进行人物识别
                if self.recognizer:
                    for detection in detections:
                        face_bbox = detection.get('face_bbox')
                        if face_bbox:
                            person_id, confidence, person_name = self.recognizer.recognize_person(img, face_bbox)
                            
                            # 绘制识别结果（改进显示效果）
                            try:
                                from maix import image as _image
                                face_x, face_y, face_w, face_h = face_bbox
                                
                                # 选择文字颜色和内容
                                if person_id is not None:
                                    # 识别到已保存人物 - 显示人物名称
                                    color = _image.Color.from_rgb(0, 255, 0)  # 绿色
                                    text = f"{person_name}"  # 只显示名称，不显示"recognizing"
                                    confidence_text = f"({confidence:.2f})"
                                    
                                    # 绘制人物名称（更大字体）
                                    img.draw_string(face_x, max(face_y - 45, 0), text, 
                                                  color=color, scale=1.2)
                                    # 绘制置信度（较小字体）
                                    img.draw_string(face_x, max(face_y - 25, 0), confidence_text, 
                                                  color=color, scale=0.8)
                                else:
                                    # 未识别人物 - 显示"Recognizing..."
                                    color = _image.Color.from_rgb(255, 255, 0)  # 黄色
                                    text = "Recognizing..."
                                    confidence_text = f"({confidence:.2f})"
                                    
                                    # 绘制识别提示
                                    img.draw_string(face_x, max(face_y - 45, 0), text, 
                                                  color=color, scale=0.9)
                                    img.draw_string(face_x, max(face_y - 25, 0), confidence_text, 
                                                  color=color, scale=0.7)
                                
                            except Exception as e:
                                print(f"绘制识别结果失败: {e}")
        else:
            # 检测器未初始化时显示提示
            try:
                from maix import image as _image
                white_color = _image.Color.from_rgb(255, 255, 255)  # 白色
                img.draw_string(10, 200, "Person detector not available", color=white_color)
            except:
                pass

    def _mode_track(self, img):
        # 待接入：检测+识别+云台追踪。当前仅显示原图。
        pass


def main():
    system = MaixVisionSystem()
    system.start_system()


if __name__ == "__main__":
    main()
