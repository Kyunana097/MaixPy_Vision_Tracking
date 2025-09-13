#ifndef _INTERRUPT_H_
#define _INTERRUPT_H_
#include "ti_msp_dl_config.h"
#include "K230_UART.h"

extern uint8_t enable_group1_irq;
extern uint8_t enable_uart_irq;
extern uint16_t gEchoData;
volatile unsigned char rx_data;
void Interrupt_Init(void);

#endif  /* #ifndef _INTERRUPT_H_ */