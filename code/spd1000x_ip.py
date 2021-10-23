import spd1000_series as _spd


def main():
    spd_hdr = _spd.SPD1000()
    spd_hdr.spd_ip = "192.168.1.214"

    spd_hdr.spdConnect()
    print(spd_hdr.spdQuery(b'*IDN?'))

    spd_hdr.spdSetup(b'*LOCK')

    print(spd_hdr.spdQuery(b'*LOCK?'))

    spd_hdr.spdSetup(b'*UNLOCK')

    spd_hdr.spdSetup(b'CH1:VOLT 2.14')
    print(spd_hdr.spdQuery(b'CH1:VOLT?'))

    spd_hdr.spdSetup(b'CH1:CURR 0.12')
    print(spd_hdr.spdQuery(b'CH1:CURR?'))

    spd_hdr.spdSetup(b'MODE:SET 4W')

    spd_hdr.spdSetup(b'MODE:SET 2W')

    while True:
        spd_hdr.spdSetup(b'OUTP CH1,ON')
        res = spd_hdr.spdQuery(b'SYST:STAT?')
        if int(res, 16) & 0x10 == 0x10:
            break

    print(spd_hdr.spdQuery(b'INST?'))
    print(spd_hdr.spdQuery(b'SYST:STAT?'))

    print('Test Measured var')

    print(spd_hdr.spdQuery(b'MEAS:VOLT?'))
    print(spd_hdr.spdQuery(b'MEAS:CURR?'))
    print(spd_hdr.spdQuery(b'MEAS:POWE?'))

    while True:
        spd_hdr.spdSetup(b'OUTP CH1,OFF')
        res = spd_hdr.spdQuery(b'SYST:STAT?')
        if int(res, 16) & 0x10 == 0x00:
            break

    print(spd_hdr.spdQuery(b'INST?'))
    print(spd_hdr.spdQuery(b'SYST:STAT?'))

    spd_hdr.spdClose()


if __name__ == '__main__':
    main()
