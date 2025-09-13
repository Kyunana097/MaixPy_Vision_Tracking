#include "key.h"

// 消抖时间（ms）
#define DEBOUNCE_TIME_MS    50

void Key_Init(void)
{
    NVIC_EnableIRQ(GPIOA_INT_IRQn);
}

uint8_t Key_GetPressed(void)
{
    return key_pressed;
}

void Key_ClearPressed(void)
{
    key_pressed = 0;
}