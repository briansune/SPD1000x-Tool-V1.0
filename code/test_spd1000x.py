import pyvisa as visa


def list_all_devices(rm):
    print(rm.list_resources())


def connect_dev(rm):
    power_supply = rm.open_resource('USB0::0xF4EC::0xF4EC::SPD13DCQ5R1087::INSTR')
    print(power_supply)
    power_supply.write_termination = '\n'
    power_supply.read_termination = '\n'

    print(rm.list_resources())

    power_supply.write('*IDN?')
    print(power_supply.read())

    power_supply.write('*LOCK?')
    print(power_supply.read())

    power_supply.write('*UNLOCK')

    # power_supply.write('*LOCK')

    # voltage set
    power_supply.write('CH1:VOLT 2.14')
    power_supply.write('CH1:VOLT?')
    print(power_supply.read())

    # current set
    power_supply.write('CH1:CURR 0.02')
    power_supply.write('CH1:CURR?')
    print(power_supply.read())

    # 2-wire mode or 4-wire mode
    power_supply.write('MODE:SET 2W')

    power_supply.write('OUTP CH1,ON')

    power_supply.write('INST?')
    print(power_supply.read())

    power_supply.write('SYST:STAT?')
    print(power_supply.read())

    power_supply.write('MEAS:VOLT?')
    print(power_supply.read())
    power_supply.write('MEAS:CURR?')
    print(power_supply.read())
    power_supply.write('MEAS:POWE?')
    print(power_supply.read())

    power_supply.write('OUTP CH1,OFF')

    power_supply.write('INST?')
    print(power_supply.read())

    power_supply.write('SYST:STAT?')
    print(power_supply.read())

    power_supply.close()


def main():
    rm = visa.ResourceManager()
    list_all_devices(rm)
    connect_dev(rm)


if __name__ == '__main__':
    main()
