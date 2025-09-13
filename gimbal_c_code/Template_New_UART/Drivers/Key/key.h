#ifndef KEY_H__
#define KEY_H__

#include "ti_msp_dl_config.h"
#include "clock.h"
#include "interrupt.h"

extern volatile uint8_t key_pressed;  

void Key_Init(void);
uint8_t Key_GetPressed(void);
void Key_ClearPressed(void);

#endif