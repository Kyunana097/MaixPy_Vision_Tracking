#include "K230_UART.h"

volatile uint8_t rx_data;
volatile uint8_t rx_order[] =
{
    //帧头
    [0] = 0x00,
    [1] = 0x00,
    //x坐标
    [2] = 0x00,
    [3] = 0x00,
    //y坐标
    [4] = 0x00,
    [5] = 0x00,
    //校验位
    [6] = 0x00,
    //帧位
    [7] = 0x00,
    [8] = 0x00,
};
volatile uint8_t last_data = 0x00;
volatile uint8_t pt = 0x00;

uint8_t K230_Init(void)
{ 
    //清除串口中断标志
    NVIC_ClearPendingIRQ(UART_0_INST_INT_IRQN);
    //使能串口中断
    NVIC_EnableIRQ(UART_0_INST_INT_IRQN);

    DL_UART_Main_transmitData(UART_0_INST,SELF_CHECK_CMD);
    while(DL_UART_isBusy(UART_0_INST));
    mspm0_delay_ms(100);
    uint8_t data = 0;
    uint8_t time = 0;
    while (data != 0x1B)
     {
        if(time++ >= TIME_OUT)
            return 0;
        data = DL_UART_Main_receiveDataBlocking(UART_0_INST);
    } 
    return 1; 
}

void UART_0_rx_DataFrame(void)
{
    rx_data = DL_UART_receiveData(UART_0_INST);
    if(last_data == rx_data && rx_data == 0xAA)
    {
        pt = 2;
        rx_order[0] = 0xAA;
        rx_order[1] = 0xAA;
    }
    else if (last_data == rx_data && rx_data == 0xFF) 
    {
        if(rx_order[2] + rx_order [3] + rx_order[4] + rx_order[5] == rx_order[6])
        {
            //接收坐标
            // 组合x坐标 (高字节 << 8 | 低字节)
            target_x = ((uint16_t)rx_order[2] << 8) | rx_order[3];
            // 组合y坐标
            target_y = ((uint16_t)rx_order[4] << 8) | rx_order[5];
        }
    }
    else 
    {
        rx_order[pt] = rx_data;
        pt++;
        pt %= 9;//防溢出
    }
    last_data = rx_data;
}

//写命令 func为要调用的原型函数
void K230_cmd(uint8_t cmd,uint8_t (*func)(uint8_t*))
{
    DL_UART_Main_transmitData(UART_0_INST,cmd);
    while(DL_UART_isBusy(UART_0_INST));
    mspm0_delay_ms(100);
    uint8_t loop_flag = 1;
    uint8_t data[128];
    while(loop_flag)
    {
        DL_UART_Main_receiveDataBlocking(UART_0_INST);
        uint8_t temp = DL_UART_Main_receiveDataBlocking(UART_0_INST);
        uint8_t last_temp = 0;
        uint8_t last_last_temp = 0;
        uint8_t i = 0;
        while(!(temp == END3 && last_temp == END2 && last_last_temp == END1))
        {
            data[i++] = temp;
            last_last_temp = last_temp;
            last_temp = temp;
            temp = DL_UART_Main_receiveDataBlocking(UART_0_INST);
        }
        loop_flag = func(data);
        mspm0_delay_ms(50);
    }
    DL_UART_Main_transmitData(UART_0_INST,STOP_CMD);
    while(DL_UART_isBusy(UART_0_INST));
    mspm0_delay_ms(50);
}

int K230_parse_int(uint8_t* data, uint8_t* index) 
{
    int i = (int)(
        ((int32_t)data[*index]) |
        ((int32_t)data[*index + 1] << 8) |
        ((int32_t)data[*index + 2] << 16) |
        ((int32_t)data[*index + 3] << 24)
    );
    *index +=4;
    return i;
}

float K230_parse_float(uint8_t* data,uint8_t* index)
{
    union {
        uint32_t i;
        float f;
    } u;

    u.i = ((uint32_t)data[*index]) |
          ((uint32_t)data[*index + 1] << 8) |
          ((uint32_t)data[*index + 2] << 16) |
          ((uint32_t)data[*index + 3] << 24);
    *index +=4;
    return u.f;
}

const char* K230_parse_string(uint8_t* data, uint8_t* index) 
{
    const char* str = (const char*)(data + *index);
    uint8_t length = 0;
    while (data[*index + length] != '\0') {
        length++;
    }
    *index += length + 1;
    return str;
}

uint8_t K230_parse_byte(uint8_t* data, uint8_t* index)
{
    uint8_t val = data[*index];
    *index += 1;
    return val;
}

void UART_0_Send_Char(UART_Regs *uart, uint8_t data)
{
    DL_UART_Main_transmitDataBlocking(uart, data);
}

void UART_0_Send_String(UART_Regs *uart, uint8_t *data)
{
    while(*data != 0 && data != 0)
    {
        UART_0_Send_Char(uart, *data);
        data++;
    }
}

//示例函数
//接受测试代码
uint8_t nod(uint8_t* data)
{
    if(DL_UART_Main_receiveDataBlocking(UART_0_INST) == 'E')
    {
        while(DL_UART_isBusy(UART_0_INST));
        DL_UART_Main_transmitData(UART_0_INST,'A');
    }
    return 0;
}

// 舵机参数解析函数
uint8_t K230_GetServoParams(uint8_t* data)
{
    uint8_t ptr = 0;
    uint8_t received_data[10];
    uint8_t checksum = 0;
    
    // 1. 接收完整数据帧（10字节）
    for(int i = 0; i < 10; i++) {
        received_data[i] = KMB(data, ptr);
    }
    DL_UART_Main_transmitData(UART_0_INST,'A');
    // 2. 检查帧头 (0xFF 0xFE)
    if(received_data[0] != 0xFF || received_data[1] != 0xFE) {
        // 帧头错误，发送错误信息
        DL_UART_Main_transmitData(UART_0_INST, 'E');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, 'o');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, ':');
        DL_UART_Main_transmitData(UART_0_INST, ' ');
        DL_UART_Main_transmitData(UART_0_INST, 'I');
        DL_UART_Main_transmitData(UART_0_INST, 'n');
        DL_UART_Main_transmitData(UART_0_INST, 'v');
        DL_UART_Main_transmitData(UART_0_INST, 'a');
        DL_UART_Main_transmitData(UART_0_INST, 'l');
        DL_UART_Main_transmitData(UART_0_INST, 'i');
        DL_UART_Main_transmitData(UART_0_INST, 'd');
        DL_UART_Main_transmitData(UART_0_INST, ' ');
        DL_UART_Main_transmitData(UART_0_INST, 'H');
        DL_UART_Main_transmitData(UART_0_INST, 'e');
        DL_UART_Main_transmitData(UART_0_INST, 'a');
        DL_UART_Main_transmitData(UART_0_INST, 'd');
        DL_UART_Main_transmitData(UART_0_INST, 'e');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, '\n');
        while(DL_UART_isBusy(UART_0_INST));
        return 0;
    }
    DL_UART_Main_transmitData(UART_0_INST,'B');
    
    // 3. BBC校验计算 (对数据位前7位进行异或校验)
    checksum = received_data[2]; // 第一个数据字节
    for(int i = 3; i < 9; i++) {
        checksum ^= received_data[i];
    }
    DL_UART_Main_transmitData(UART_0_INST,'C');
    
    // 4. 校验检查
    if(checksum != received_data[9]) {
        // 校验错误，发送错误信息
        DL_UART_Main_transmitData(UART_0_INST, 'E');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, 'o');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, ':');
        DL_UART_Main_transmitData(UART_0_INST, ' ');
        DL_UART_Main_transmitData(UART_0_INST, 'C');
        DL_UART_Main_transmitData(UART_0_INST, 'h');
        DL_UART_Main_transmitData(UART_0_INST, 'e');
        DL_UART_Main_transmitData(UART_0_INST, 'c');
        DL_UART_Main_transmitData(UART_0_INST, 'k');
        DL_UART_Main_transmitData(UART_0_INST, 's');
        DL_UART_Main_transmitData(UART_0_INST, 'u');
        DL_UART_Main_transmitData(UART_0_INST, 'm');
        DL_UART_Main_transmitData(UART_0_INST, ' ');
        DL_UART_Main_transmitData(UART_0_INST, 'E');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, 'o');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, '\n');
        while(DL_UART_isBusy(UART_0_INST));
        return 0;
    }
    DL_UART_Main_transmitData(UART_0_INST,'D');
    
    // 5. 提取舵机角度 (数据位第1位和第2位)
    uint8_t base_servo_angle = received_data[2]; // 底部舵机角度
    uint8_t arm_servo_angle = received_data[3];  // 摇臂舵机角度
    
    // 6. 检查角度范围 (0~171)
    if(base_servo_angle > 171 || arm_servo_angle > 171) {
        // 角度超出范围，发送错误信息
        DL_UART_Main_transmitData(UART_0_INST, 'E');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, 'o');
        DL_UART_Main_transmitData(UART_0_INST, 'r');
        DL_UART_Main_transmitData(UART_0_INST, ':');
        DL_UART_Main_transmitData(UART_0_INST, ' ');
        DL_UART_Main_transmitData(UART_0_INST, 'A');
        DL_UART_Main_transmitData(UART_0_INST, 'n');
        DL_UART_Main_transmitData(UART_0_INST, 'g');
        DL_UART_Main_transmitData(UART_0_INST, 'l');
        DL_UART_Main_transmitData(UART_0_INST, 'e');
        DL_UART_Main_transmitData(UART_0_INST, ' ');
        DL_UART_Main_transmitData(UART_0_INST, 'O');
        DL_UART_Main_transmitData(UART_0_INST, 'u');
        DL_UART_Main_transmitData(UART_0_INST, 't');
        DL_UART_Main_transmitData(UART_0_INST, ' ');
        DL_UART_Main_transmitData(UART_0_INST, 'o');
        DL_UART_Main_transmitData(UART_0_INST, 'f');
        DL_UART_Main_transmitData(UART_0_INST, ' ');
        DL_UART_Main_transmitData(UART_0_INST, 'R');
        DL_UART_Main_transmitData(UART_0_INST, 'a');
        DL_UART_Main_transmitData(UART_0_INST, 'n');
        DL_UART_Main_transmitData(UART_0_INST, 'g');
        DL_UART_Main_transmitData(UART_0_INST, 'e');
        DL_UART_Main_transmitData(UART_0_INST, '\n');
        while(DL_UART_isBusy(UART_0_INST));
        return 0;
    }
    DL_UART_Main_transmitData(UART_0_INST,'E');
    
    // 7. 发送解析结果
    // 发送底部舵机角度
    DL_UART_Main_transmitData(UART_0_INST, 'B');
    DL_UART_Main_transmitData(UART_0_INST, 'a');
    DL_UART_Main_transmitData(UART_0_INST, 's');
    DL_UART_Main_transmitData(UART_0_INST, 'e');
    DL_UART_Main_transmitData(UART_0_INST, ':');
    DL_UART_Main_transmitData(UART_0_INST, ' ');
    
    DL_UART_Main_transmitData(UART_0_INST,'F');
    // 将角度值转换为ASCII字符串发送
    if(base_servo_angle >= 100) {
        DL_UART_Main_transmitData(UART_0_INST, '0' + base_servo_angle/100);
        DL_UART_Main_transmitData(UART_0_INST, '0' + (base_servo_angle%100)/10);
        DL_UART_Main_transmitData(UART_0_INST, '0' + base_servo_angle%10);
    } else if(base_servo_angle >= 10) {
        DL_UART_Main_transmitData(UART_0_INST, '0' + base_servo_angle/10);
        DL_UART_Main_transmitData(UART_0_INST, '0' + base_servo_angle%10);
    } else {
        DL_UART_Main_transmitData(UART_0_INST, '0' + base_servo_angle);
    }
    
    DL_UART_Main_transmitData(UART_0_INST, ' ');
    DL_UART_Main_transmitData(UART_0_INST, 'd');
    DL_UART_Main_transmitData(UART_0_INST, 'e');
    DL_UART_Main_transmitData(UART_0_INST, 'g');
    DL_UART_Main_transmitData(UART_0_INST, '\n');
    
    // 发送摇臂舵机角度
    DL_UART_Main_transmitData(UART_0_INST, 'A');
    DL_UART_Main_transmitData(UART_0_INST, 'r');
    DL_UART_Main_transmitData(UART_0_INST, 'm');
    DL_UART_Main_transmitData(UART_0_INST, ':');
    DL_UART_Main_transmitData(UART_0_INST, ' ');
    
    if(arm_servo_angle >= 100) {
        DL_UART_Main_transmitData(UART_0_INST, '0' + arm_servo_angle/100);
        DL_UART_Main_transmitData(UART_0_INST, '0' + (arm_servo_angle%100)/10);
        DL_UART_Main_transmitData(UART_0_INST, '0' + arm_servo_angle%10);
    } else if(arm_servo_angle >= 10) {
        DL_UART_Main_transmitData(UART_0_INST, '0' + arm_servo_angle/10);
        DL_UART_Main_transmitData(UART_0_INST, '0' + arm_servo_angle%10);
    } else {
        DL_UART_Main_transmitData(UART_0_INST, '0' + arm_servo_angle);
    }
    
    DL_UART_Main_transmitData(UART_0_INST, ' ');
    DL_UART_Main_transmitData(UART_0_INST, 'd');
    DL_UART_Main_transmitData(UART_0_INST, 'e');
    DL_UART_Main_transmitData(UART_0_INST, 'g');
    DL_UART_Main_transmitData(UART_0_INST, '\n');
    
    while(DL_UART_isBusy(UART_0_INST));
    
    return 0; // 处理完成
}
