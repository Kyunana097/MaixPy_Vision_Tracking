#ifndef __MSP_H__
#define __MSP_H__

#include <stdint.h>
#include <stdbool.h>

/* MSPM0G3507 基本定义 */
#define __MSPM0G3507__

/* ARM Cortex-M0+ 基本定义 */
#define __CM0PLUS_REV             0x0001U
#define __MPU_PRESENT             0U
#define __VTOR_PRESENT            1U
#define __NVIC_PRIO_BITS          2U
#define __Vendor_SysTickConfig    0U

/* 中断号定义 */
typedef enum {
    NonMaskableInt_IRQn       = -14,
    HardFault_IRQn            = -13,
    SVCall_IRQn               = -5,
    PendSV_IRQn               = -2,
    SysTick_IRQn              = -1,
    UART_0_INST_INT_IRQN      = 8
} IRQn_Type;

/* 基本寄存器类型 */
typedef struct {
    volatile uint32_t DR;       /* Data Register */
    volatile uint32_t RSR_ECR;  /* Status Register */
    volatile uint32_t reserved[4];
    volatile uint32_t FR;       /* Flag Register */
    volatile uint32_t reserved2;
    volatile uint32_t ILPR;     /* IrDA Register */
    volatile uint32_t IBRD;     /* Integer Baud Rate Register */
    volatile uint32_t FBRD;     /* Fractional Baud Rate Register */
    volatile uint32_t LCRH;     /* Line Control Register */
    volatile uint32_t CTL;      /* Control Register */
    volatile uint32_t IFLS;     /* Interrupt FIFO Level Select */
    volatile uint32_t IMSC;     /* Interrupt Mask Set/Clear */
    volatile uint32_t RIS;      /* Raw Interrupt Status */
    volatile uint32_t MIS;      /* Masked Interrupt Status */
    volatile uint32_t ICR;      /* Interrupt Clear Register */
} UART_Regs;

/* UART实例定义 */
extern UART_Regs* UART_0_INST;

#endif /* __MSP_H__ */
