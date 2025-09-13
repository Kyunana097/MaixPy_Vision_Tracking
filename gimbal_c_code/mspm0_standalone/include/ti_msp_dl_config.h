/*
 * Copyright (c) 2023, Texas Instruments Incorporated - http://www.ti.com
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

/*
 *  ============ ti_msp_dl_config.h =============
 *  Configured MSPM0 DriverLib module declarations
 *
 *  DO NOT EDIT - This file is generated for the MSPM0G350X
 *  by the SysConfig tool.
 */
#ifndef ti_msp_dl_config_h
#define ti_msp_dl_config_h

#define CONFIG_MSPM0G350X
#define CONFIG_MSPM0G3507

#if defined(__ti_version__) || defined(__TI_COMPILER_VERSION__)
#define SYSCONFIG_WEAK __attribute__((weak))
#elif defined(__IAR_SYSTEMS_ICC__)
#define SYSCONFIG_WEAK __weak
#elif defined(__GNUC__)
#define SYSCONFIG_WEAK __attribute__((weak))
#endif

#include <ti/devices/msp/msp.h>
#include <ti/driverlib/driverlib.h>
#include <ti/driverlib/m0p/dl_core.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 *  ======== SYSCFG_DL_init ========
 *  Perform all required MSP DL initialization
 *
 *  This function should be called once at a point before any use of
 *  MSP DL.
 */


/* clang-format off */

#define POWER_STARTUP_DELAY                                                (16)


#define CPUCLK_FREQ                                                     32000000



/* Defines for PWM_SERVO */
#define PWM_SERVO_INST                                                     TIMA1
#define PWM_SERVO_INST_IRQHandler                               TIMA1_IRQHandler
#define PWM_SERVO_INST_INT_IRQN                                 (TIMA1_INT_IRQn)
#define PWM_SERVO_INST_CLK_FREQ                                            40000
/* GPIO defines for channel 0 */
#define GPIO_PWM_SERVO_C0_PORT                                             GPIOB
#define GPIO_PWM_SERVO_C0_PIN                                      DL_GPIO_PIN_0
#define GPIO_PWM_SERVO_C0_IOMUX                                  (IOMUX_PINCM12)
#define GPIO_PWM_SERVO_C0_IOMUX_FUNC                 IOMUX_PINCM12_PF_TIMA1_CCP0
#define GPIO_PWM_SERVO_C0_IDX                                DL_TIMER_CC_0_INDEX
/* GPIO defines for channel 1 */
#define GPIO_PWM_SERVO_C1_PORT                                             GPIOB
#define GPIO_PWM_SERVO_C1_PIN                                      DL_GPIO_PIN_1
#define GPIO_PWM_SERVO_C1_IOMUX                                  (IOMUX_PINCM13)
#define GPIO_PWM_SERVO_C1_IOMUX_FUNC                 IOMUX_PINCM13_PF_TIMA1_CCP1
#define GPIO_PWM_SERVO_C1_IDX                                DL_TIMER_CC_1_INDEX



/* Defines for CLOCK */
#define CLOCK_INST                                                       (TIMA0)
#define CLOCK_INST_IRQHandler                                   TIMA0_IRQHandler
#define CLOCK_INST_INT_IRQN                                     (TIMA0_INT_IRQn)
#define CLOCK_INST_LOAD_VALUE                                            (4999U)



/* Defines for UART_0 */
#define UART_0_INST                                                        UART0
#define UART_0_INST_FREQUENCY                                           32000000
#define UART_0_INST_IRQHandler                                  UART0_IRQHandler
#define UART_0_INST_INT_IRQN                                      UART0_INT_IRQn
#define GPIO_UART_0_RX_PORT                                                GPIOA
#define GPIO_UART_0_TX_PORT                                                GPIOA
#define GPIO_UART_0_RX_PIN                                        DL_GPIO_PIN_11
#define GPIO_UART_0_TX_PIN                                        DL_GPIO_PIN_10
#define GPIO_UART_0_IOMUX_RX                                     (IOMUX_PINCM22)
#define GPIO_UART_0_IOMUX_TX                                     (IOMUX_PINCM21)
#define GPIO_UART_0_IOMUX_RX_FUNC                      IOMUX_PINCM22_PF_UART0_RX
#define GPIO_UART_0_IOMUX_TX_FUNC                      IOMUX_PINCM21_PF_UART0_TX
#define UART_0_BAUD_RATE                                                (115200)
#define UART_0_IBRD_32_MHZ_115200_BAUD                                      (17)
#define UART_0_FBRD_32_MHZ_115200_BAUD                                      (23)
/* Defines for UART_1 */
#define UART_1_INST                                                        UART2
#define UART_1_INST_FREQUENCY                                           32000000
#define UART_1_INST_IRQHandler                                  UART2_IRQHandler
#define UART_1_INST_INT_IRQN                                      UART2_INT_IRQn
#define GPIO_UART_1_RX_PORT                                                GPIOA
#define GPIO_UART_1_TX_PORT                                                GPIOA
#define GPIO_UART_1_RX_PIN                                        DL_GPIO_PIN_22
#define GPIO_UART_1_TX_PIN                                        DL_GPIO_PIN_21
#define GPIO_UART_1_IOMUX_RX                                     (IOMUX_PINCM47)
#define GPIO_UART_1_IOMUX_TX                                     (IOMUX_PINCM46)
#define GPIO_UART_1_IOMUX_RX_FUNC                      IOMUX_PINCM47_PF_UART2_RX
#define GPIO_UART_1_IOMUX_TX_FUNC                      IOMUX_PINCM46_PF_UART2_TX
#define UART_1_BAUD_RATE                                                (115200)
#define UART_1_IBRD_32_MHZ_115200_BAUD                                      (17)
#define UART_1_FBRD_32_MHZ_115200_BAUD                                      (23)
/* Defines for UART_2 */
#define UART_2_INST                                                        UART1
#define UART_2_INST_FREQUENCY                                           32000000
#define UART_2_INST_IRQHandler                                  UART1_IRQHandler
#define UART_2_INST_INT_IRQN                                      UART1_INT_IRQn
#define GPIO_UART_2_RX_PORT                                                GPIOA
#define GPIO_UART_2_TX_PORT                                                GPIOA
#define GPIO_UART_2_RX_PIN                                        DL_GPIO_PIN_18
#define GPIO_UART_2_TX_PIN                                        DL_GPIO_PIN_17
#define GPIO_UART_2_IOMUX_RX                                     (IOMUX_PINCM40)
#define GPIO_UART_2_IOMUX_TX                                     (IOMUX_PINCM39)
#define GPIO_UART_2_IOMUX_RX_FUNC                      IOMUX_PINCM40_PF_UART1_RX
#define GPIO_UART_2_IOMUX_TX_FUNC                      IOMUX_PINCM39_PF_UART1_TX
#define UART_2_BAUD_RATE                                                (115200)
#define UART_2_IBRD_32_MHZ_115200_BAUD                                      (17)
#define UART_2_FBRD_32_MHZ_115200_BAUD                                      (23)





/* Defines for PIN_LED_R: GPIOB.7 with pinCMx 24 on package pin 59 */
#define GPIO_LED_PIN_LED_R_PORT                                          (GPIOB)
#define GPIO_LED_PIN_LED_R_PIN                                   (DL_GPIO_PIN_7)
#define GPIO_LED_PIN_LED_R_IOMUX                                 (IOMUX_PINCM24)
/* Defines for PIN_LED_W: GPIOB.9 with pinCMx 26 on package pin 61 */
#define GPIO_LED_PIN_LED_W_PORT                                          (GPIOB)
#define GPIO_LED_PIN_LED_W_PIN                                   (DL_GPIO_PIN_9)
#define GPIO_LED_PIN_LED_W_IOMUX                                 (IOMUX_PINCM26)
/* Defines for PIN_LED_B: GPIOA.13 with pinCMx 35 on package pin 6 */
#define GPIO_LED_PIN_LED_B_PORT                                          (GPIOA)
#define GPIO_LED_PIN_LED_B_PIN                                  (DL_GPIO_PIN_13)
#define GPIO_LED_PIN_LED_B_IOMUX                                 (IOMUX_PINCM35)
/* Defines for PIN_LED_G: GPIOB.26 with pinCMx 57 on package pin 28 */
#define GPIO_LED_PIN_LED_G_PORT                                          (GPIOB)
#define GPIO_LED_PIN_LED_G_PIN                                  (DL_GPIO_PIN_26)
#define GPIO_LED_PIN_LED_G_IOMUX                                 (IOMUX_PINCM57)
/* Port definition for Pin Group GPIO_KEY */
#define GPIO_KEY_PORT                                                    (GPIOA)

/* Defines for PIN_KEY1: GPIOA.28 with pinCMx 3 on package pin 35 */
// pins affected by this interrupt request:["PIN_KEY1","PIN_KEY2","PIN_KEY3"]
#define GPIO_KEY_INT_IRQN                                       (GPIOA_INT_IRQn)
#define GPIO_KEY_INT_IIDX                       (DL_INTERRUPT_GROUP1_IIDX_GPIOA)
#define GPIO_KEY_PIN_KEY1_IIDX                              (DL_GPIO_IIDX_DIO28)
#define GPIO_KEY_PIN_KEY1_PIN                                   (DL_GPIO_PIN_28)
#define GPIO_KEY_PIN_KEY1_IOMUX                                   (IOMUX_PINCM3)
/* Defines for PIN_KEY2: GPIOA.29 with pinCMx 4 on package pin 36 */
#define GPIO_KEY_PIN_KEY2_IIDX                              (DL_GPIO_IIDX_DIO29)
#define GPIO_KEY_PIN_KEY2_PIN                                   (DL_GPIO_PIN_29)
#define GPIO_KEY_PIN_KEY2_IOMUX                                   (IOMUX_PINCM4)
/* Defines for PIN_KEY3: GPIOA.30 with pinCMx 5 on package pin 37 */
#define GPIO_KEY_PIN_KEY3_IIDX                              (DL_GPIO_IIDX_DIO30)
#define GPIO_KEY_PIN_KEY3_PIN                                   (DL_GPIO_PIN_30)
#define GPIO_KEY_PIN_KEY3_IOMUX                                   (IOMUX_PINCM5)
/* Defines for PIN_KEY4: GPIOA.31 with pinCMx 6 on package pin 39 */
#define GPIO_KEY_PIN_KEY4_PIN                                   (DL_GPIO_PIN_31)
#define GPIO_KEY_PIN_KEY4_IOMUX                                   (IOMUX_PINCM6)

/* clang-format on */

void SYSCFG_DL_init(void);
void SYSCFG_DL_initPower(void);
void SYSCFG_DL_GPIO_init(void);
void SYSCFG_DL_SYSCTL_init(void);
void SYSCFG_DL_PWM_SERVO_init(void);
void SYSCFG_DL_CLOCK_init(void);
void SYSCFG_DL_UART_0_init(void);
void SYSCFG_DL_UART_1_init(void);
void SYSCFG_DL_UART_2_init(void);


bool SYSCFG_DL_saveConfiguration(void);
bool SYSCFG_DL_restoreConfiguration(void);

#ifdef __cplusplus
}
#endif

#endif /* ti_msp_dl_config_h */
