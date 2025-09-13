#include "ti_msp_dl_config.h"
#include "interrupt.h"
#include "clock.h"
#include "key.h"


volatile uint8_t key_pressed = 0; 
uint8_t enable_group1_irq = 0;
uint8_t enable_uart_irq = 0;

void Interrupt_Init(void)
{
    if(enable_group1_irq)
    {
        NVIC_EnableIRQ(1);
    }
    if(enable_uart_irq)
    {    
        NVIC_ClearPendingIRQ(UART_0_INST_INT_IRQN);
        NVIC_EnableIRQ(UART_0_INST_INT_IRQN);
    }
}

void SysTick_Handler(void)
{
    tick_ms++;
}

void GROUP1_IRQHandler(void)
{
    switch (DL_Interrupt_getPendingGroup(DL_INTERRUPT_GROUP_1)) 
    {
        #if defined GPIO_MULTIPLE_GPIOA_INT_IIDX
        case GPIO_MULTIPLE_GPIOA_INT_IIDX:
            switch (DL_GPIO_getPendingInterrupt(GPIOA))
            {  
                #if (defined GPIO_KEY_PORT) && (GPIO_KEY_PORT == GPIOA)
                case DL_GPIO_IIDX_DIO28:
                    if (DL_GPIO_readPins(GPIOA, DL_GPIO_PIN_28) == 0) {
                        key_pressed = 1;
                    }
                    break;
                case DL_GPIO_IIDX_DIO29:
                    if (DL_GPIO_readPins(GPIOA, DL_GPIO_PIN_29) == 0) {
                        key_pressed = 2;
                    }
                    break;
                case DL_GPIO_IIDX_DIO30:
                   // if (DL_GPIO_readPins(GPIOA, DL_GPIO_PIN_30) == 0) {
                    if (DL_GPIO_readPins(GPIOA, DL_GPIO_PIN_31) == 0){
                        key_pressed = 3;
                    }
                       else {
                       key_pressed = 4;
                       }
                   // }
                    break;
                case DL_GPIO_IIDX_DIO31:
                    if (DL_GPIO_readPins(GPIOA, DL_GPIO_PIN_31) == 0) {
                        key_pressed = 4;
                    }
                    break;
                #endif

                default:
                    break;
            }
        #endif

        default:
            break;

    }
    
}
 
//串口的中断服务函数
void UART_0_INST_IRQHandler(void)
{
    //如果产生了串口中断
    switch( DL_UART_getPendingInterrupt(UART_0_INST) )
    {
        case DL_UART_IIDX_RX://如果是接收中断
            //接发送过来的数据保存在变量中
            rx_data = DL_UART_Main_receiveData(UART_0_INST);
            //将保存的数据再发送出去
            UART_0_Send_Char(UART_0_INST,rx_data);
            break;
        
        default://其他的串口中断
            break;
    }
}