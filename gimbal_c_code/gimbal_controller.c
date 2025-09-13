/**
 * @file gimbal_controller.c
 * @brief 舵机云台控制器实现文件
 * @author [您的姓名]
 * @date 2025-09-13
 * @description M0G3507主控的舵机云台控制实现
 */

#include "gimbal_controller.h"
// TODO: 添加M0G3507相关头文件
// #include "m0g3507_pwm.h"
// #include "m0g3507_gpio.h"

// 全局变量
static gimbal_control_t gimbal_ctrl = {0};

/**
 * @brief 初始化云台控制器
 */
bool gimbal_init(void)
{
    // TODO: 实现云台初始化
    // 1. 初始化PWM输出引脚
    // 2. 配置PWM频率和周期
    // 3. 设置云台到中心位置
    // 4. 标记初始化完成
    
    gimbal_ctrl.pan_angle = 0.0f;
    gimbal_ctrl.tilt_angle = 0.0f;
    gimbal_ctrl.initialized = true;
    
    return true;
}

/**
 * @brief 设置云台角度
 */
bool gimbal_set_angle(float pan_angle, float tilt_angle)
{
    // TODO: 实现角度设置
    // 1. 检查角度范围
    // 2. 转换为PWM值
    // 3. 输出PWM信号
    // 4. 更新当前角度
    
    if (!gimbal_ctrl.initialized) {
        return false;
    }
    
    // 角度范围检查
    if (pan_angle < PAN_MIN_ANGLE || pan_angle > PAN_MAX_ANGLE) {
        return false;
    }
    
    if (tilt_angle < TILT_MIN_ANGLE || tilt_angle > TILT_MAX_ANGLE) {
        return false;
    }
    
    // 更新角度
    gimbal_ctrl.pan_angle = pan_angle;
    gimbal_ctrl.tilt_angle = tilt_angle;
    
    return true;
}

/**
 * @brief 获取当前云台角度
 */
void gimbal_get_angle(float *pan_angle, float *tilt_angle)
{
    // TODO: 实现角度获取
    if (pan_angle != NULL) {
        *pan_angle = gimbal_ctrl.pan_angle;
    }
    
    if (tilt_angle != NULL) {
        *tilt_angle = gimbal_ctrl.tilt_angle;
    }
}

/**
 * @brief 云台复位到中心位置
 */
bool gimbal_reset(void)
{
    // TODO: 实现云台复位
    return gimbal_set_angle(0.0f, 0.0f);
}

/**
 * @brief 云台微调
 */
bool gimbal_adjust(float pan_delta, float tilt_delta)
{
    // TODO: 实现云台微调
    float new_pan = gimbal_ctrl.pan_angle + pan_delta;
    float new_tilt = gimbal_ctrl.tilt_angle + tilt_delta;
    
    return gimbal_set_angle(new_pan, new_tilt);
}

/**
 * @brief 停用云台
 */
void gimbal_deinit(void)
{
    // TODO: 实现云台停用
    // 1. 停止PWM输出
    // 2. 释放资源
    // 3. 标记未初始化
    
    gimbal_ctrl.initialized = false;
}

/**
 * @brief 角度到PWM值转换
 */
uint16_t angle_to_pwm(float angle, bool is_pan)
{
    // TODO: 实现角度到PWM转换
    // 一般舵机: 0.5ms-2.5ms对应-90°到+90°
    // PWM值 = (角度 + 90) / 180 * (2500 - 500) + 500
    
    float min_angle = is_pan ? PAN_MIN_ANGLE : TILT_MIN_ANGLE;
    float max_angle = is_pan ? PAN_MAX_ANGLE : TILT_MAX_ANGLE;
    
    // 限制角度范围
    if (angle < min_angle) angle = min_angle;
    if (angle > max_angle) angle = max_angle;
    
    // 转换为PWM值 (500us - 2500us)
    uint16_t pwm = (uint16_t)((angle - min_angle) / (max_angle - min_angle) * 2000 + 500);
    
    return pwm;
}

/**
 * @brief PWM值到角度转换
 */
float pwm_to_angle(uint16_t pwm, bool is_pan)
{
    // TODO: 实现PWM到角度转换
    float min_angle = is_pan ? PAN_MIN_ANGLE : TILT_MIN_ANGLE;
    float max_angle = is_pan ? PAN_MAX_ANGLE : TILT_MAX_ANGLE;
    
    // 限制PWM范围
    if (pwm < 500) pwm = 500;
    if (pwm > 2500) pwm = 2500;
    
    // 转换为角度
    float angle = (float)(pwm - 500) / 2000 * (max_angle - min_angle) + min_angle;
    
    return angle;
}
