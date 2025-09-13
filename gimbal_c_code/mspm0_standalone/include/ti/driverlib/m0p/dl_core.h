#ifndef __DL_CORE_H__
#define __DL_CORE_H__

#include <stdint.h>

/* ARM CMSIS 核心定义 */
#define __STATIC_INLINE static inline
#define __WEAK          __attribute__((weak))

/* 基本延时函数 */
__STATIC_INLINE void delay_cycles(uint32_t cycles) {
    volatile uint32_t i;
    for (i = 0; i < cycles; i++) {
        __asm__("nop");
    }
}

#endif /* __DL_CORE_H__ */
