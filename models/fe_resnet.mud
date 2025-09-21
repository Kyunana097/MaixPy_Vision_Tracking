 
[basic]
type = awnn
param =fe_resnet.param
bin =fe_resnet.bin

[inputs]
inputs_blob = 128,128,3,127.5, 127.5, 127.5,0.0078125, 0.0078125, 0.0078125

[outputs]
FC_blob = 1,1,256

[extra]
outputs_scale =
inputs_scale =
