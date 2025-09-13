################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Each subdirectory must supply rules for building sources it contributes
build-367823439: ../empty.syscfg
	@echo 'Building file: "$<"'
	@echo 'Invoking: SysConfig'
	"/home/kyunana/ti/ccs2020/ccs/utils/sysconfig_1.24.0/sysconfig_cli.sh" --script "/home/kyunana/workspace_ccstheia/Template_New_UART/empty.syscfg" -o "." -s "/home/kyunana/ti/mspm0_sdk_2_05_01_00/.metadata/product.json" --compiler ticlang
	@echo 'Finished building: "$<"'
	@echo ' '

device_linker.cmd: build-367823439 ../empty.syscfg
device.opt: build-367823439
device.cmd.genlibs: build-367823439
ti_msp_dl_config.c: build-367823439
ti_msp_dl_config.h: build-367823439
Event.dot: build-367823439

%.o: ./%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: Arm Compiler'
	"/home/kyunana/ti/ccs2020/ccs/tools/compiler/ti-cgt-armllvm_4.0.3.LTS/bin/tiarmclang" -c @"device.opt"  -march=thumbv6m -mcpu=cortex-m0plus -mfloat-abi=soft -mlittle-endian -mthumb -O0 -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/K230_UART" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/SERVO" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Hardware_I2C" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Hardware_SPI" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Software_I2C" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Software_SPI" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/Key" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/Gray_Sensor" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/TB6612" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/MPU6050" -I"/home/kyunana/workspace_ccstheia/Template_New_UART" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Debug" -I"/home/kyunana/ti/mspm0_sdk_2_05_01_00/source/third_party/CMSIS/Core/Include" -I"/home/kyunana/ti/mspm0_sdk_2_05_01_00/source" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/MSPM0" -DMOTION_DRIVER_TARGET_MSPM0 -DMPU6050 -D__MSPM0G3507__ -gdwarf-3 -MMD -MP -MF"$(basename $(<F)).d_raw" -MT"$(@)"  $(GEN_OPTS__FLAG) -o"$@" "$(shell echo $<)"
	@echo 'Finished building: "$<"'
	@echo ' '

startup_mspm0g350x_ticlang.o: /home/kyunana/ti/mspm0_sdk_2_05_01_00/source/ti/devices/msp/m0p/startup_system_files/ticlang/startup_mspm0g350x_ticlang.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: Arm Compiler'
	"/home/kyunana/ti/ccs2020/ccs/tools/compiler/ti-cgt-armllvm_4.0.3.LTS/bin/tiarmclang" -c @"device.opt"  -march=thumbv6m -mcpu=cortex-m0plus -mfloat-abi=soft -mlittle-endian -mthumb -O0 -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/K230_UART" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/SERVO" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Hardware_I2C" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Hardware_SPI" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Software_I2C" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Software_SPI" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/Key" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/Gray_Sensor" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/TB6612" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/MPU6050" -I"/home/kyunana/workspace_ccstheia/Template_New_UART" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Debug" -I"/home/kyunana/ti/mspm0_sdk_2_05_01_00/source/third_party/CMSIS/Core/Include" -I"/home/kyunana/ti/mspm0_sdk_2_05_01_00/source" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/MSPM0" -DMOTION_DRIVER_TARGET_MSPM0 -DMPU6050 -D__MSPM0G3507__ -gdwarf-3 -MMD -MP -MF"$(basename $(<F)).d_raw" -MT"$(@)"  $(GEN_OPTS__FLAG) -o"$@" "$(shell echo $<)"
	@echo 'Finished building: "$<"'
	@echo ' '

%.o: ../%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: Arm Compiler'
	"/home/kyunana/ti/ccs2020/ccs/tools/compiler/ti-cgt-armllvm_4.0.3.LTS/bin/tiarmclang" -c @"device.opt"  -march=thumbv6m -mcpu=cortex-m0plus -mfloat-abi=soft -mlittle-endian -mthumb -O0 -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/K230_UART" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/SERVO" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Hardware_I2C" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Hardware_SPI" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Software_I2C" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Software_SPI" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/Key" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/Gray_Sensor" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/TB6612" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/MPU6050" -I"/home/kyunana/workspace_ccstheia/Template_New_UART" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Debug" -I"/home/kyunana/ti/mspm0_sdk_2_05_01_00/source/third_party/CMSIS/Core/Include" -I"/home/kyunana/ti/mspm0_sdk_2_05_01_00/source" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/MSPM0" -DMOTION_DRIVER_TARGET_MSPM0 -DMPU6050 -D__MSPM0G3507__ -gdwarf-3 -MMD -MP -MF"$(basename $(<F)).d_raw" -MT"$(@)"  $(GEN_OPTS__FLAG) -o"$@" "$(shell echo $<)"
	@echo 'Finished building: "$<"'
	@echo ' '


