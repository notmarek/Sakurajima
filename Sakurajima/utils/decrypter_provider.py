from Crypto.Cipher import AES

class DecrypterProvider(object):

    def __init__(self, network, m3u8):
        self.__network = network
        self.m3u8 = m3u8
        self.key = None
        self.uri = self.m3u8.data["keys"][1]["uri"]

    def get_key_by_comparison(self) -> bytearray:
        if self.key == None:
            key1 = bytearray(self.__network.get(self.uri).content)
            key2 = key1
            tries = 1
            while key1 == key2 and tries <=25:
                key2 = bytearray(self.__network.get(self.uri).content)
                tries += 1
            final_key = []
            for index in range(len(key1)):
                smaller = min(key1[index], key2[index])
                final_key.append(smaller)
            self.key = bytearray(final_key)
        return self.key
    
    def get_key(self) -> bytearray:
        if self.key == None:
            self.key = bytearray(self.__network.get(self.uri).content)
        return self.key

    @staticmethod
    def create_initialization_vector(chunk_number) -> bytearray:
        iv = [0 for _ in range(0, 16)]
        for i in range(12, 16):
            iv[i] = chunk >> 8 * (15 - i) & 255
        return bytearray(iv)
    
    def get_decryptor(self, chunk_number) -> AES:
        iv = self.create_initialization_vector(chunk_number)
        return AES.new(self.get_key(), AES.MODE_CBC, iv = iv)