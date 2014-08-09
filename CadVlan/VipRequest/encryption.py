# -*- coding:utf-8 -*-
'''
Title: CadVlan
Author: masilva / S2it
Copyright: ( c )  2012 globo.com todos os direitos reservados.
'''

from CadVlan.settings import SECRET_KEY
from Crypto.Cipher import AES
from Crypto.Hash import MD5
import logging

BLOCK_SIZE = 32 
INTERRUPT = u'\u0001'
PAD = u'\u0000'   # preenche com chr(0)

def AddPadding(data, interrupt, pad, block_size):
    new_data = ''.join([data, interrupt])
    new_data_len = len(new_data)
    remaining_len = block_size - new_data_len
    to_pad_len = remaining_len % block_size
    pad_string = pad * to_pad_len
    return ''.join([new_data, pad_string])

def StripPadding(data, interrupt, pad):
    return data.rstrip(pad).rstrip(interrupt)

logger = logging.getLogger(__name__)

class Encryption():
    
    def __init__(self):
        
        try:
            #Generates object AES
            #self.cipher = AES.new(MD5.new(SECRET_KEY).hexdigest(), AES.MODE_CBC)
            self.cipher = AES.new(MD5.new(SECRET_KEY).hexdigest(), AES.MODE_ECB)
            
        except Exception, e:
            logger.error(e)
            raise Exception(e)

    def Encrypt(self, plaintext_data):
        encrypted = self.EncryptWithAES(plaintext_data)
        encrypted = self._toHex(encrypted)
        return encrypted
    
    def Decrypt(self, encrypted_data):
        decrypted_data = self._toStr(encrypted_data)
        plaintext_data = self.DecryptWithAES(decrypted_data)
        return plaintext_data 

    def EncryptWithAES(self, plaintext_data):
        plaintext_padded = AddPadding(plaintext_data, INTERRUPT, PAD, BLOCK_SIZE)
        encrypted = self.cipher.encrypt(plaintext_padded)
        return encrypted 

    def DecryptWithAES(self, encrypted_data):
        decoded_encrypted_data = encrypted_data
        decrypted_data = self.cipher.decrypt(decoded_encrypted_data)
        return StripPadding(decrypted_data, INTERRUPT, PAD)
    
    #convert string to hex
    def _toHex(self,s):
        lst = []
        for ch in s:
            hv = hex(ord(ch)).replace('0x', '')
            if len(hv) == 1:
                hv = '0'+hv
            lst.append(hv)
        
        return reduce(lambda x,y:x+y, lst)
    
    #convert hex repr to string
    def _toStr(self,s):
        return s and chr(int(s[:2], base=16)) + self._toStr(s[2:]) or ''

