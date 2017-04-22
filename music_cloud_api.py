import os
import base64
import urllib.parse
import json
import random
import binascii
from Crypto.Cipher import AES

modulus = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
nonce = '0CoJUm6Qyw8W8jud'
def createSecretKey(size):
    str='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    r=''
    for i in range(0,size):r+=str[random.randint(0,len(str)-1)]
    return r

def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(secKey, AES.MODE_CBC, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext)
    return str(ciphertext)[2:]
    
def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = int(binascii.hexlify(text.encode()), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)
def generate_seckey():
    return createSecretKey(16)
def generate_encseckey(secKey):
    return rsaEncrypt(secKey, '010001', modulus)
def generate_secpair():
    sec=generate_seckey()
    return (sec,generate_encseckey(sec))
def encrypted_request(text, secKey="", encSecKey=""):
    if secKey=="": secKey,encSecKey = generate_secpair()
    encText = aesEncrypt(aesEncrypt(json.dumps(text), nonce), secKey)
    data = {
        'params': urllib.parse.quote(encText),
        'encSecKey': encSecKey
    }
    return data