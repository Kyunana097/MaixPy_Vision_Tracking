#include "servo.h"

uint16_t Servo_Target1 = 0;
uint16_t Servo_Target2 = 0;

//舵机归位
void Servo_Init(void)
{
        DL_Timer_setCaptureCompareValue(TIMA1, 60, DL_TIMER_CC_0_INDEX);//上位归中
        DL_Timer_setCaptureCompareValue(TIMA1, 60, DL_TIMER_CC_1_INDEX);//下位归中
}

// 角度限制函数
static float Clamp_Angle(float angle, float min_angle, float max_angle)
{
    if (angle < min_angle) return min_angle;
    if (angle > max_angle) return max_angle;
    return angle;
}

// 角度转PWM函数
static uint16_t Angle_To_PWM(float angle, float min_angle, float max_angle)
{
    // 限制角度在有效范围内
    angle = Clamp_Angle(angle, min_angle, max_angle);
    
    // 线性映射角度到PWM值
    float pwm = SERVO_PWM_MIN + (angle - min_angle) * (SERVO_PWM_MAX - SERVO_PWM_MIN) / (max_angle - min_angle);
    
    // 四舍五入并返回整数PWM值
    return (uint16_t)(pwm + 0.5f);
}

void Servo_Limitation(void)
{
    //上位舵机1的极限值为9°-171°，下位舵机2的极限值为13.5°-256.5°
    //对应PWM为24-96
    uint16_t Amplitude_H = 96, Amplitude_L = 24;
    if (Servo_Target1 < Amplitude_L)  Servo_Target1 = Amplitude_L;
    if (Servo_Target1 > Amplitude_H)  Servo_Target1 = Amplitude_H;
    if (Servo_Target2 < Amplitude_L)  Servo_Target2 = Amplitude_L;
    if (Servo_Target2 > Amplitude_H)  Servo_Target2 = Amplitude_H;
}


// 设置舵机角度函数
void Set_Servo_Angle(uint8_t servo_num, float angle)
{
    uint16_t PWM_value;
    
    if (servo_num == 1)
     {
        // 舵机1角度转PWM
        PWM_value = Angle_To_PWM(angle, SERVO1_MIN_ANGLE, SERVO1_MAX_ANGLE);
        Servo_Target1 = PWM_value;
        DL_Timer_setCaptureCompareValue(TIMA1, PWM_value, DL_TIMER_CC_0_INDEX);
    } 
    else if (servo_num == 2) 
    {
        // 舵机2角度转PWM
        PWM_value = Angle_To_PWM(angle, SERVO2_MIN_ANGLE, SERVO2_MAX_ANGLE);
        Servo_Target2 = PWM_value;
        DL_Timer_setCaptureCompareValue(TIMA1, PWM_value, DL_TIMER_CC_1_INDEX);
    }
    
    // 确保PWM值在限制范围内
    Servo_Limitation();
}

// 初始化PID控制器
void PID_Init(PID_Controller* pid, float kp, float ki, float kd, float min, float max) 
{
    pid->Kp = kp;
    pid->Ki = ki;
    pid->Kd = kd;
    pid->error = 0.0f;
    pid->error_last = 0.0f;
    pid->integral = 0.0f;
    pid->output = 0.0f;
    pid->output_max = max;
    pid->output_min = min;
}

// PID计算函数
float PID_Calculate(PID_Controller* pid, float target, float current) 
{
    // 计算误差
    pid->error = target - current;
    
    // 积分项(抗积分饱和)
    pid->integral += pid->error;
    if (pid->integral > pid->output_max) pid->integral = pid->output_max;
    if (pid->integral < pid->output_min) pid->integral = pid->output_min;
    
    // 微分项
    float derivative = pid->error - pid->error_last;
    
    // 计算输出
    pid->output = pid->Kp * pid->error + pid->Ki * pid->integral + pid->Kd * derivative;
    
    // 限制输出范围
    if (pid->output > pid->output_max) pid->output = pid->output_max;
    if (pid->output < pid->output_min) pid->output = pid->output_min;
    
    // 保存当前误差
    pid->error_last = pid->error;
    
    return pid->output;
}

// 坐标到舵机角度的映射函数
float Map_Coordinate_To_Angle(float coordinate, float min_coord, float max_coord, float min_angle, float max_angle)
{
    // 线性映射坐标到角度
    float angle = min_angle + (coordinate - min_coord) * (max_angle - min_angle) / (max_coord - min_coord);
    
    // 限制角度范围
    if (angle < min_angle) angle = min_angle;
    if (angle > max_angle) angle = max_angle;
    
    return angle;
}

// 更新舵机位置(根据目标点坐标)
void Update_Servo_Position(float target_x, float target_y) 
{
    // 计算X轴PID控制
    float current_angle_x = Map_Coordinate_To_Angle(target_x, 0, 640, SERVO_X_MIN_ANGLE, SERVO_X_MAX_ANGLE);
    float pid_output_x = PID_Calculate(&pid_x, SCREEN_CENTER_X, target_x);
    float new_angle_x = current_angle_x + pid_output_x;
    
    // 计算Y轴PID控制
    float current_angle_y = Map_Coordinate_To_Angle(target_y, 0, 480, SERVO_Y_MIN_ANGLE, SERVO_Y_MAX_ANGLE);
    float pid_output_y = PID_Calculate(&pid_y, SCREEN_CENTER_Y, target_y);
    float new_angle_y = current_angle_y + pid_output_y;
    
    // 设置舵机角度
    Set_Servo_Angle(1, new_angle_x);  // 控制X轴舵机
    Set_Servo_Angle(2, new_angle_y);  // 控制Y轴舵机
}