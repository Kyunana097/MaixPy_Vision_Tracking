################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Each subdirectory must supply rules for building sources it contributes
Drivers/Key/%.o: ../Drivers/Key/%.c $(GEN_OPTS) | $(GEN_FILES) $(GEN_MISC_FILES)
	@echo 'Building file: "$<"'
	@echo 'Invoking: Arm Compiler'
	"/home/kyunana/ti/ccs2020/ccs/tools/compiler/ti-cgt-armllvm_4.0.3.LTS/bin/tiarmclang" -c @"device.opt"  -march=thumbv6m -mcpu=cortex-m0plus -mfloat-abi=soft -mlittle-endian -mthumb -O0 -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/K230_UART" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/SERVO" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Hardware_I2C" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Hardware_SPI" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Software_I2C" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/OLED_Software_SPI" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/Key" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/Gray_Sensor" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/TB6612" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/MPU6050" -I"/home/kyunana/workspace_ccstheia/Template_New_UART" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Debug" -I"/home/kyunana/ti/mspm0_sdk_2_05_01_00/source/third_party/CMSIS/Core/Include" -I"/home/kyunana/ti/mspm0_sdk_2_05_01_00/source" -I"/home/kyunana/workspace_ccstheia/Template_New_UART/Drivers/MSPM0" -DMOTION_DRIVER_TARGET_MSPM0 -DMPU6050 -D__MSPM0G3507__ -gdwarf-3 -MMD -MP -MF"Drivers/Key/$(basename $(<F)).d_raw" -MT"$(@)"  $(GEN_OPTS__FLAG) -o"$@" "$(shell echo $<)"
	@echo 'Finished building: "$<"'
	@echo ' '


