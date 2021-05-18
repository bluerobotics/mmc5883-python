import smbus2
import time

REG_PRODUCT_ID = 0x2F
REG_XOUT_L = 0x00
REG_TOUT = 0x06
REG_STATUS = 0x07
REG_CONTROL0 = 0x08
REG_CONTROL1 = 0x09
REG_CONTROL2 = 0x0A

# bits in REG_CONTROL0
REG_CONTROL0_RESET = 0x10
REG_CONTROL0_SET = 0x08
REG_CONTROL0_TMM = 0x01
REG_CONTROL0_TMT = 0x02

# bits in REG_CONTROL1
REG_CONTROL1_SW_RST = 0x80
REG_CONTROL1_BW0 = 0x01
REG_CONTROL1_BW1 = 0x02

MIN_DELAY_SET_SET = 1e-3
MIN_DELAY_MEASURE = 1.6e-3

MMC5883_ID = 0x0C
MMC5883_ADDR = 0x30

class CompassData:
    def __init__(self, rawdata):
        self.x_raw = ((rawdata[1] << 8) | rawdata[0]) - 0x8000
        self.y_raw = ((rawdata[3] << 8) | rawdata[2]) - 0x8000
        self.z_raw = ((rawdata[5] << 8) | rawdata[4]) - 0x8000
        self.t_raw = rawdata[6]

        # field strength in gauss
        self.x = self.x_raw/4096
        self.y = self.y_raw/4096
        self.z = self.z_raw/4096
        self.t = self.t_raw*200.0/256 - 75

class MMC5883:

    def __init__(self, bus=1):
        self._bus = smbus2.SMBus(bus)
        self.reset()
        self._id = self.read_id()
        self.set_BW()

    def reset(self):
        self._bus.write_i2c_block_data(MMC5883_ADDR, REG_CONTROL2, [REG_CONTROL1_SW_RST])
        time.sleep(0.01)

    def set_BW(self, BW=3):
        self._bus.write_i2c_block_data(MMC5883_ADDR, REG_CONTROL1, [BW])

    def read_id(self):
        id = self._bus.read_i2c_block_data(MMC5883_ADDR, REG_PRODUCT_ID, 1)[0]
        return id

    def read_data(self):
        return 

    def measure(self):
        self._bus.write_i2c_block_data(MMC5883_ADDR, REG_CONTROL0, [REG_CONTROL0_TMM | REG_CONTROL0_TMT])
        time.sleep(MIN_DELAY_MEASURE)
        status = self._bus.read_i2c_block_data(MMC5883_ADDR, REG_STATUS, 1)
        while not ((status[0] & 3) == 3):
            status = self._bus.read_i2c_block_data(MMC5883_ADDR, REG_STATUS, 1)
            continue

        rawdata = self._bus.read_i2c_block_data(MMC5883_ADDR, REG_XOUT_L, 7)
        return CompassData(rawdata)
