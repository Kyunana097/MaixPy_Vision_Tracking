/**
 * @file gimbal_controller.h
 * @brief 舵机云台控制器头文件
 * @author [您的姓名]
 * @date 2025-09-13
 * @description M0G3507主控的舵机云台控制接口定义
 */

#ifndef GIMBAL_CONTROLLER_H
#define GIMBAL_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

// 云台参数定义
#define PAN_MIN_ANGLE   -90     // 水平最小角度
#define PAN_MAX_ANGLE    90     // 水平最大角度
#define TILT_MIN_ANGLE  -30     // 垂直最小角度
#define TILT_MAX_ANGLE   30     // 垂直最大角度

#define PWM_FREQUENCY   50      // PWM频率 (Hz)
#define PWM_PERIOD      20000   // PWM周期 (us)

// 舵机控制结构体
typedef struct {
    float pan_angle;            // 水平角度
    float tilt_angle;           // 垂直角度
    uint16_t pan_pwm;          // 水平舵机PWM值
    uint16_t tilt_pwm;         // 垂直舵机PWM值
    bool initialized;           // 初始化状态
} gimbal_control_t;

// 函数声明
/**
 * @brief 初始化云台控制器
 * @return true 初始化成功, false 初始化失败
 */
bool gimbal_init(void);

/**
 * @brief 设置云台角度
 * @param pan_angle 水平角度 (-90 to 90)
 * @param tilt_angle 垂直角度 (-30 to 30)
 * @return true 设置成功, false 设置失败
 */
bool gimbal_set_angle(float pan_angle, float tilt_angle);

/**
 * @brief 获取当前云台角度
 * @param pan_angle 水平角度指针
 * @param tilt_angle 垂直角度指针
 */
void gimbal_get_angle(float *pan_angle, float *tilt_angle);

/**
 * @brief 云台复位到中心位置
 * @return true 复位成功, false 复位失败
 */
bool gimbal_reset(void);

/**
 * @brief 云台微调
 * @param pan_delta 水平角度增量
 * @param tilt_delta 垂直角度增量
 * @return true 微调成功, false 微调失败
 */
bool gimbal_adjust(float pan_delta, float tilt_delta);

/**
 * @brief 停用云台
 */
void gimbal_deinit(void);

/**
 * @brief 角度到PWM值转换
 * @param angle 角度值
 * @param is_pan true为水平轴, false为垂直轴
 * @return PWM值
 */
uint16_t angle_to_pwm(float angle, bool is_pan);

/**
 * @brief PWM值到角度转换
 * @param pwm PWM值
 * @param is_pan true为水平轴, false为垂直轴
 * @return 角度值
 */
float pwm_to_angle(uint16_t pwm, bool is_pan);

#endif // GIMBAL_CONTROLLER_H
