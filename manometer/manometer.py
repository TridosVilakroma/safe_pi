from subprocess import run,PIPE
from time import sleep
from os import system

write_reg               = 'i2cset'
read_reg                = 'i2cget'
custom_cmd              = 'i2ctransfer'
read_two_bytes          = 'r2@'    # read commands must be follwed by dev_addr
read_three_bytes        = 'r3@'    # without a space after command
auto_confirm            = '-y'
i2c_bus                 = 1
dev_addr                = 0x76
reset_cmd               = 0x1e
adc_cmd                 = 0x00

pc1                     = 0xa2
pc2                     = 0xa4
pc3                     = 0xa6
pc4                     = 0xa8
pc5                     = 0xaa
pc6                     = 0xac

convert_d1_256          = 0x40
convert_d1_512          = 0x42
convert_d1_1024         = 0x44
convert_d1_2048         = 0x46
convert_d1_4096         = 0x48

convert_d2_256          = 0x50
convert_d2_512          = 0x52
convert_d2_1024         = 0x54
convert_d2_2048         = 0x56
convert_d2_4096         = 0x58

read_loaded_coefficient = f'{custom_cmd} {auto_confirm} {i2c_bus} {read_two_bytes}{dev_addr}'
read_loaded_adc         = f'{custom_cmd} {auto_confirm} {i2c_bus} {read_three_bytes}{dev_addr}'

C1                      = None
C2                      = None
C3                      = None
C4                      = None
C5                      = None
C6                      = None

temperature             = None
pressure                = None

# reset device
def reset():
    reset_device=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {reset_cmd}',shell=True,stdout=PIPE)
    sleep(.1)

# load PROM coefficients
def load_coefficients():
    global C1,C2,C3,C4,C5,C6
    load_c1=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {pc1}',shell=True,stdout=PIPE)
    sleep(.1)
    _c1=run(f'{read_loaded_coefficient}',shell=True,stdout=PIPE)
    sleep(.1)
    r_c1=bytearray(_c1.stdout.decode('utf-8').strip().encode())
    r_c1_0,r_c1_1=r_c1.split()[0],r_c1.split()[1]
    r_c1_0=int(r_c1_0,0)
    r_c1_1=int(r_c1_1,0)
    C1=r_c1_0
    C1<<=8
    C1|=r_c1_1
    C1=int(C1)
    sleep(.1)
    load_c2=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {pc2}',shell=True,stdout=PIPE)
    sleep(.1)
    _c2=run(f'{read_loaded_coefficient}',shell=True,stdout=PIPE)
    sleep(.1)
    r_c2=bytearray(_c2.stdout.decode('utf-8').strip().encode())
    r_c2_0,r_c2_1=r_c2.split()[0],r_c2.split()[1]
    r_c2_0=int(r_c2_0,0)
    r_c2_1=int(r_c2_1,0)
    C2=r_c2_0
    C2<<=8
    C2|=r_c2_1
    C2=int(C2)
    sleep(.1)
    load_c3=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {pc3}',shell=True,stdout=PIPE)
    sleep(.1)
    _c3=run(f'{read_loaded_coefficient}',shell=True,stdout=PIPE)
    sleep(.1)
    r_c3=bytearray(_c3.stdout.decode('utf-8').strip().encode())
    r_c3_0,r_c3_1=r_c3.split()[0],r_c3.split()[1]
    r_c3_0=int(r_c3_0,0)
    r_c3_1=int(r_c3_1,0)
    C3=r_c3_0
    C3<<=8
    C3|=r_c3_1
    C3=int(C3)
    sleep(.1)
    load_c4=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {pc4}',shell=True,stdout=PIPE)
    sleep(.1)
    _c4=run(f'{read_loaded_coefficient}',shell=True,stdout=PIPE)
    sleep(.1)
    r_c4=bytearray(_c4.stdout.decode('utf-8').strip().encode())
    r_c4_0,r_c4_1=r_c4.split()[0],r_c4.split()[1]
    r_c4_0=int(r_c4_0,0)
    r_c4_1=int(r_c4_1,0)
    C4=r_c4_0
    C4<<=8
    C4|=r_c4_1
    C4=int(C4)
    sleep(.1)
    load_c5=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {pc5}',shell=True,stdout=PIPE)
    sleep(.1)
    _c5=run(f'{read_loaded_coefficient}',shell=True,stdout=PIPE)
    sleep(.1)
    r_c5=bytearray(_c5.stdout.decode('utf-8').strip().encode())
    r_c5_0,r_c5_1=r_c5.split()[0],r_c5.split()[1]
    r_c5_0=int(r_c5_0,0)
    r_c5_1=int(r_c5_1,0)
    C5=r_c5_0
    C5<<=8
    C5|=r_c5_1
    C5=int(C5)
    sleep(.1)
    load_c6=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {pc6}',shell=True,stdout=PIPE)
    sleep(.1)
    _c6=run(f'{read_loaded_coefficient}',shell=True,stdout=PIPE)
    sleep(.1)
    r_c6=bytearray(_c6.stdout.decode('utf-8').strip().encode())
    r_c6_0,r_c6_1=r_c6.split()[0],r_c6.split()[1]
    r_c6_0=int(r_c6_0,0)
    r_c6_1=int(r_c6_1,0)
    C6=r_c6_0
    C6<<=8
    C6|=r_c6_1
    sleep(.1)
    C6=int(C6)
    sleep(.1)

lowest_pressure  = +1_000_000*1_000_000 #initiate high and low in extremes
highest_pressure = -1_000_000*1_000_000 #where they will be set in loop for sure

def main():
    global C1,C2,C3,C4,C5,C6
    global lowest_pressure,highest_pressure,temperature,pressure

    #read pressure
    load_d1=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {convert_d1_2048}',shell=True,stdout=PIPE)
    sleep(.1)
    set_adc_d1=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {adc_cmd}',shell=True,stdout=PIPE)
    sleep(.1)
    _d1=run(f'{read_loaded_adc}',shell=True,stdout=PIPE)
    r_d1=bytearray(_d1.stdout.decode('utf-8').strip().encode())
    r_d1_0,r_d1_1,r_d1_2=r_d1.split()[0],r_d1.split()[1],r_d1.split()[2]
    r_d1_0=int(r_d1_0,0)
    r_d1_1=int(r_d1_1,0)
    r_d1_2=int(r_d1_2,0)
    D1=r_d1_0
    D1<<=8
    D1|=r_d1_1
    D1<<=8
    D1|=r_d1_2
    sleep(.1)

    #read temperature
    load_d2=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {convert_d2_2048}',shell=True,stdout=PIPE)
    sleep(.1)
    set_adc_d2=run(f'{write_reg} {auto_confirm} {i2c_bus} {dev_addr} {adc_cmd}',shell=True,stdout=PIPE)
    sleep(.1)
    _d2=run(f'{read_loaded_adc}',shell=True,stdout=PIPE)
    r_d2=bytearray(_d2.stdout.decode('utf-8').strip().encode())
    r_d2_0,r_d2_1,r_d2_2=r_d2.split()[0],r_d2.split()[1],r_d2.split()[2]
    r_d2_0=int(r_d2_0,0)
    r_d2_1=int(r_d2_1,0)
    r_d2_2=int(r_d2_2,0)
    D2=r_d2_0
    D2<<=8
    D2|=r_d2_1
    D2<<=8
    D2|=r_d2_2
    sleep(.1)

    #calculate compensated temperature
    dt          = D2-(C5*pow(2,7))
    temperature =int( 2000+(dt*(C6/pow(2,21))) )
    temperature=round(temperature*.01,2)

    #calculate temperature compensated pressure
    offset      = (C2*pow(2,17))+((C4*dt)//pow(2,5))
    sensitivity = (C1*pow(2,15)+((C3*dt)//pow(2,7)))*2
    pressure    = int((D1*sensitivity/pow(2,21)-offset)/pow(2,15))/10000
    pressure = round(pressure*.001,10)

    #compare and record low and high
    if D1>highest_pressure:
        highest_pressure=D1
    if D1<lowest_pressure:
        lowest_pressure=D1

    system('clear')
    print('\n'*5)
    print('Temperature:          ºc',temperature)
    print('Temperature:          ºf',float((9/5*temperature)+32))
    print('Pressure:            PSI',pressure)
    print('Raw Pressure Reading:   ',D1)
    print('Low:                    ',lowest_pressure)
    print('High:                   ',highest_pressure)

    sleep(.1)

def start():
    reset()
    load_coefficients()
    main()

def update():
    main()