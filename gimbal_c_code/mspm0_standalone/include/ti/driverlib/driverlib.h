#ifndef __DRIVERLIB_H__
#define __DRIVERLIB_H__

#include <stdint.h>
#include <stdbool.h>

/* UART 函数声明 */
void DL_UART_Main_transmitData(UART_Regs *uart, uint8_t data);
uint8_t DL_UART_Main_receiveDataBlocking(UART_Regs *uart);
uint8_t DL_UART_receiveData(UART_Regs *uart);
bool DL_UART_isBusy(UART_Regs *uart);

/* NVIC 函数声明 */
void NVIC_ClearPendingIRQ(IRQn_Type IRQn);
void NVIC_EnableIRQ(IRQn_Type IRQn);

/* 延时函数声明 */
int mspm0_delay_ms(unsigned long ms);

/* SysTick相关 */
void SysTick_Init(void);

#endif /* __DRIVERLIB_H__ */
