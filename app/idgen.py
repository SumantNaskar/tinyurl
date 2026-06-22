import time
import threading

class SnowflakeIDGenerator:

    def __init__(self, machine_id:int):
        if machine_id < 0 or machine_id > 1023:
            raise ValueError(
                "Machine ID must be b/w 0 & 1023"
            )

        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1
        self.epoch = 1700000000000
        self.lock = threading.Lock()

    def generate_id(self):
        with self.lock:

            timestamp = int(time.time()*1000)

            if timestamp < self.last_timestamp:
                raise Exception("Clock moved backwards")

            if timestamp == self.last_timestamp:

                self.sequence = (self.sequence + 1) & 0xFFF

                if self.sequence == 0:
                    while timestamp <= self.last_timestamp:
                        time.sleep(0.001)
                        timestamp = int(time.time()*1000)
            
            else:
                self.sequence = 0
            
            self.last_timestamp = timestamp

            id_value = (((timestamp - self.epoch) << 22) | (self.machine_id << 12) | self.sequence)

            return id_value
    
BASE62_Alphabets = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(num:int):
    if num == 0:
        return BASE62_Alphabets[0]

    base = len(BASE62_Alphabets)
    output = []

    while num > 0:
        remainder = num % base
        output.append(BASE62_Alphabets[remainder])
        num //= base
    
    return "".join(reversed(output))

def decode(short_code:str):

    num = 0
    base = len(BASE62_Alphabets)
    char_map = {c: i for i, c in enumerate(BASE62_Alphabets)}

    for char in short_code:
        num = num * base + char_map[char]

    return num               


snowflake = SnowflakeIDGenerator(machine_id=1)

def generate_short_code():
    return encode(snowflake.generate_id())

