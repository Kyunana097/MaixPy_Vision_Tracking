# MSPM0G3507 Standalone Makefile
# 独立的ARM-GCC构建系统

# 项目设置
PROJECT_NAME = gimbal_controller
TARGET = $(PROJECT_NAME)

# 工具链设置
TOOLCHAIN_PREFIX = arm-none-eabi-
CC = $(TOOLCHAIN_PREFIX)gcc
AS = $(TOOLCHAIN_PREFIX)as
LD = $(TOOLCHAIN_PREFIX)ld
OBJCOPY = $(TOOLCHAIN_PREFIX)objcopy
OBJDUMP = $(TOOLCHAIN_PREFIX)objdump
SIZE = $(TOOLCHAIN_PREFIX)size
GDB = gdb-multiarch

# MCU设置
MCU = cortex-m0plus
ARCH = -mthumb -mcpu=$(MCU)

# 目录设置
SRC_DIR = src
DRIVERS_DIR = drivers
INCLUDE_DIR = include
BUILD_DIR = build

# 源文件
SOURCES = $(SRC_DIR)/main_simple.c

# 头文件路径
INCLUDES = -I$(INCLUDE_DIR)
INCLUDES += -I$(DRIVERS_DIR)/K230_UART
INCLUDES += -I$(DRIVERS_DIR)/SERVO
INCLUDES += -I$(DRIVERS_DIR)/Key
INCLUDES += -I$(DRIVERS_DIR)/MSPM0
INCLUDES += -Iinclude/ti

# 编译标志
CFLAGS = $(ARCH)
CFLAGS += -Wall -Wextra
CFLAGS += -O2 -g3
CFLAGS += -ffunction-sections -fdata-sections
CFLAGS += -std=c99
CFLAGS += $(INCLUDES)

# 链接标志
LDFLAGS = $(ARCH)
LDFLAGS += -Wl,--gc-sections
LDFLAGS += -specs=nano.specs -specs=nosys.specs
LDFLAGS += --static

# 目标文件
OBJECTS = $(addprefix $(BUILD_DIR)/, $(SOURCES:.c=.o))

# 默认目标
all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).bin $(BUILD_DIR)/$(TARGET).hex

# 创建构建目录
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)
	mkdir -p $(BUILD_DIR)/$(SRC_DIR)
	mkdir -p $(BUILD_DIR)/$(DRIVERS_DIR)/K230_UART
	mkdir -p $(BUILD_DIR)/$(DRIVERS_DIR)/SERVO
	mkdir -p $(BUILD_DIR)/$(DRIVERS_DIR)/Key
	mkdir -p $(BUILD_DIR)/$(DRIVERS_DIR)/MSPM0

# 编译规则
$(BUILD_DIR)/%.o: %.c | $(BUILD_DIR)
	@echo "Compiling $<"
	$(CC) $(CFLAGS) -c $< -o $@

# 链接规则
$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS)
	@echo "Linking $@"
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@
	$(SIZE) $@

# 生成二进制文件
$(BUILD_DIR)/$(TARGET).bin: $(BUILD_DIR)/$(TARGET).elf
	$(OBJCOPY) -O binary $< $@

# 生成十六进制文件
$(BUILD_DIR)/$(TARGET).hex: $(BUILD_DIR)/$(TARGET).elf
	$(OBJCOPY) -O ihex $< $@

# 清理
clean:
	rm -rf $(BUILD_DIR)

# 调试
debug: $(BUILD_DIR)/$(TARGET).elf
	$(GDB) $<

# 显示信息
info:
	@echo "Project: $(PROJECT_NAME)"
	@echo "Target MCU: MSPM0G3507 ($(MCU))"
	@echo "Sources: $(SOURCES)"
	@echo "Objects: $(OBJECTS)"

.PHONY: all clean debug info
