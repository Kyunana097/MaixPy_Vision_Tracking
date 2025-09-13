#ifndef __K230_UART_H
#define __K230_UART_H
#include "ti_msp_dl_config.h"
#include "clock.h"

#define SELF_CHECK_CMD 0x1A
#define STOP_CMD 0x1C
#define TIME_OUT 0xFF
#define END1 0x01
#define END2 0xFE
#define END3 0xFF

// 坐标变量
uint16_t target_x;
uint16_t target_y;

uint8_t K230_Init(void);
void K230_cmd(uint8_t cmd,uint8_t (*func)(uint8_t*));

//可供调用的读取函数
int K230_parse_int(uint8_t* data, uint8_t* index);
float K230_parse_float(uint8_t* data,uint8_t* index);
const char* K230_parse_string(uint8_t* data, uint8_t* index);
uint8_t K230_parse_byte(uint8_t* data, uint8_t* index);
void UART_0_Send_Char(UART_Regs *uart, uint8_t data);
void UART_0_Send_String(UART_Regs *uart, uint8_t *data);

//简明形式
#define KMB(d,i) K230_parse_byte((data),&(i))
#define KMF(d,i) K230_parse_float((data),&(i))
#define KMI(d,i) K230_parse_int((data),&(i))
#define KMS(d,i) K230_parse_string((data),&(i))


//示例函数
// 舵机参数解析函数
uint8_t K230_GetServoParams(uint8_t* data);
uint8_t nod(uint8_t* data);

#endif