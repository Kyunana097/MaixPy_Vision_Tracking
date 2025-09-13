#ifndef __SERVO_H
#define __SERVO_H
#include "ti_msp_dl_config.h"
#include <math.h>
#include <stdint.h>

// 舵机参数定义
#define SERVO1_MIN_ANGLE     9.0f    // 舵机1最小角度
#define SERVO1_MAX_ANGLE     171.0f  // 舵机1最大角度
#define SERVO2_MIN_ANGLE     13.5f   // 舵机2最小角度
#define SERVO2_MAX_ANGLE     256.5f  // 舵机2最大角度
#define SERVO_PWM_MIN              24      // PWM最小值
#define SERVO_PWM_MAX              96      // PWM最大值
// 更新后的舵机角度限制
#define SERVO_X_MIN_ANGLE -50.4f    // X轴舵机最小角度
#define SERVO_X_MAX_ANGLE 50.4f     // X轴舵机最大角度
#define SERVO_Y_MIN_ANGLE -16.5f    // Y轴舵机最小角度
#define SERVO_Y_MAX_ANGLE 16.5f     // Y轴舵机最大角度

// PID控制器结构体
typedef struct {
    float Kp;           // 比例系数
    float Ki;           // 积分系数
    float Kd;           // 微分系数
    float error;        // 当前误差
    float error_last;   // 上一次误差
    float integral;     // 积分项
    float output;       // 输出值
    float output_max;   // 输出最大值
    float output_min;   // 输出最小值
} PID_Controller;

// 屏幕中心坐标
#define SCREEN_CENTER_X 320
#define SCREEN_CENTER_Y 240

// 全局PID控制器实例
extern PID_Controller pid_x;
extern PID_Controller pid_y;

// 全局变量 - 目标PWM值
extern uint16_t Servo_Target1;
extern uint16_t Servo_Target2;   

void Servo_Init(void);
static float Clamp_Angle(float angle, float min_angle, float max_angle);
static uint16_t Angle_To_PWM(float angle, float min_angle, float max_angle);
void Servo_Limitation(void);
void Set_Servo_Angle(uint8_t servo_num, float angle);
void PID_Init(PID_Controller* pid, float kp, float ki, float kd, float min, float max);
float PID_Calculate(PID_Controller* pid, float target, float current);
float Map_Coordinate_To_Angle(float coordinate, float min_coord, float max_coord, float min_angle, float max_angle);
void Update_Servo_Position(float target_x, float target_y);

#endif