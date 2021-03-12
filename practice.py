from BitVector import *
import copy
import time

Sbox = []

InvSbox = []


AES_modulus = BitVector(bitstring='100011011')

Mixer = [
    [BitVector(hexstring="02"), BitVector(hexstring="03"), BitVector(hexstring="01"), BitVector(hexstring="01")],
    [BitVector(hexstring="01"), BitVector(hexstring="02"), BitVector(hexstring="03"), BitVector(hexstring="01")],
    [BitVector(hexstring="01"), BitVector(hexstring="01"), BitVector(hexstring="02"), BitVector(hexstring="03")],
    [BitVector(hexstring="03"), BitVector(hexstring="01"), BitVector(hexstring="01"), BitVector(hexstring="02")]
]

InvMixer = [
    [BitVector(hexstring="0E"), BitVector(hexstring="0B"), BitVector(hexstring="0D"), BitVector(hexstring="09")],
    [BitVector(hexstring="09"), BitVector(hexstring="0E"), BitVector(hexstring="0B"), BitVector(hexstring="0D")],
    [BitVector(hexstring="0D"), BitVector(hexstring="09"), BitVector(hexstring="0E"), BitVector(hexstring="0B")],
    [BitVector(hexstring="0B"), BitVector(hexstring="0D"), BitVector(hexstring="09"), BitVector(hexstring="0E")]
]

def shiftLeft(arr, n):
    old = arr.copy()    
    for i in range(0, len(arr)):
        arr[i] = old[ (i+n) % len(arr) ]


def subByte(byteVect, sbox):
    byteStr = byteVect.getHexStringFromBitVector()
    vct = BitVector(intVal = sbox[(int(byteStr[0], 16)* 16 +  int(byteStr[1], 16))], size = 8)
    return vct

def subBytes(arr, sbox):
    for i in range(0, len(arr)):
        arr[i] = subByte(arr[i], sbox)

def xorList(a, b):
    c = [x for x in a]
    for i in range(0, len(a)):
        c[i] = a[i] ^ b[i]
    return c

def transposeMat(a):
    b = copy.deepcopy(a)
    for i in range(0, len(b) ):
        for j in range(0, i+1):
            x = b[i][j]
            b[i][j] = b[j][i]
            b[j][i] = x
    return b

def printMat(a):
    for x in a:
        for y in x:
            print(y.getHexStringFromBitVector(), end = " ")
        print()

    
def textToBitMatrix(text):
    mat = []
    while len(text) < 16:
        text = text + '0'
    text = text[0:16]
    mat = [ [ BitVector(intVal=text[j*4 + i], size=8 ) for i in range(0, 4)] for j in range(0, 4) ]
    return mat

def matToText(mat):
    cipher = ""
    for x in mat:
        for y in x:
            cipher += chr(int(y.getHexStringFromBitVector(), 16))
    return cipher

def matToByte(mat):
    byte = []
    for x in mat:
        for y in x:
            byte.append(int(y.getHexStringFromBitVector(), 16)) 
    return byte

def ListToString(bList):
    text = ""
    for i in range(0, len(bList)):
        text += chr(bList[i])
    return text

def bytesToList(byte):
    res = []
    for i in range(0, len(byte)):
        res.append(byte[i])
    return res

def xorMat(a, b):
    c = copy.deepcopy(a)
    for i in range(0, len(a)):
        for j in range(0, len(a[0])):
            c[i][j] = a[i][j] ^ b[i][j]
    return c

def subMat(a, sbox):
    c = copy.deepcopy(a)
    for i in range(0, len(a)):
        subBytes(c[i], sbox)
    return c

def shiftMatLeft(a):
    for i in range(0, len(a)):
        shiftLeft(a[i], i)
    return a

def shiftMatRight(a):
    for i in range(0, len(a)):
        shiftLeft(a[i], len(a[i]) - i)
    return a

def MixColumn(a, b):
    x = [[ BitVector(hexstring="00") for i in range(0, 4) ] for j in range(0, 4) ]
    for i in range(0, 4):
        for j in range(0, 4):
            for k in range(0, 4):
                x[i][j] ^= a[i][k].gf_multiply_modular(b[k][j], AES_modulus, 8)
    return x

class EncryptionKey:
    def __init__(self, key):
        self.keys = []
        self.keys.append(textToBitMatrix(key))

    def getRC(self, i):
        if(i == 1):
            return BitVector(intVal = 1, size = 8)
        rcPrev = self.getRC(i-1)
        val = int(rcPrev.getHexStringFromBitVector(), 16)
        val = val*2    
        if(rcPrev.__lt__( BitVector(hexstring="80"))) :
            return BitVector(intVal=val, size = 8)
        else:
            result = BitVector(intVal = val, size = 12)
            test = BitVector(hexstring="11B")
            result = result ^ test
            strHex = result.getHexStringFromBitVector().upper()[1:3]
            return BitVector(hexstring = strHex )

    def getG(self, arr, i):
        shiftLeft(arr, 1)
        subBytes(arr, Sbox)
        arr[0] = arr[0]^self.getRC(i)

    def nextRoundKey(self, key, round):
        gFunc = key[3].copy() 
        self.getG(gFunc, round)
        newKey = copy.deepcopy(key)
        newKey[0] = xorList(gFunc, key[0])
        for i in range(1, 4):
            newKey[i] = xorList(newKey[i-1], key[i])
        return newKey
    
    def getKey(self, round):
        while(len(self.keys) <= round ):
            self.keys.append( self.nextRoundKey( self.keys[ len(self.keys) -1 ], len(self.keys) ) )
        return self.keys[round]
        
    def print(self, round):
        thisKey = self.getKey(round)
        for x in thisKey:
            for y in x:
                print(y.getHexStringFromBitVector() , end = " ")

def encrypt(text, key):
    enKey = EncryptionKey(key)
    cipherList = []
    while len(text)%16 != 0:
        text.append(32)
    for i in range(0, len(text)//16):
        textMat = transposeMat(textToBitMatrix(text[ i*16 : (i+1)*16 ]) )
        stateMat = xorMat(textMat, transposeMat( enKey.getKey(0) ) )
        for round in range(1, 10):
            stateMat = subMat(stateMat, Sbox)
            stateMat = shiftMatLeft(stateMat)
            stateMat = MixColumn(Mixer, stateMat)
            stateMat = xorMat(stateMat, transposeMat( enKey.getKey(round) ) )
        stateMat = subMat(stateMat, Sbox)
        stateMat = shiftMatLeft(stateMat)
        stateMat = xorMat(stateMat, transposeMat( enKey.getKey(10) ) )
        # cipher += (matToText( transposeMat( stateMat ) ))
        cipherList += ( matToByte( transposeMat( stateMat ) ) )
    return cipherList

def decrypt(text, key):
    plainList = []
    enKey = EncryptionKey(key)
    for i in range(0, len(text)//16):
        textMat = transposeMat(textToBitMatrix(text[i*16 : (i+1)*16 ] ) )        
        stateMat = xorMat(textMat, transposeMat( enKey.getKey(10) ) )
        for round in range(1, 10):
            stateMat = shiftMatRight(stateMat)
            stateMat = subMat(stateMat, InvSbox)
            stateMat = xorMat(stateMat, transposeMat( enKey.getKey(10 - round) ) ) 
            stateMat = MixColumn(InvMixer, stateMat)
        stateMat = shiftMatRight(stateMat)
        stateMat = subMat(stateMat, InvSbox)
        stateMat = xorMat(stateMat, transposeMat( enKey.getKey(0) ) )
        plainList += matToByte( transposeMat( stateMat ) )
    return plainList

def genSBox():
    addTo = BitVector(hexstring = "63")
    for i in range(0, 16):
        for j in range(0, 16):
            val = 16*i + j
            vector = BitVector(intVal = val, size = 8)
            if val != 0:
                vector = vector.gf_MI( AES_modulus , 8)
            s1 = copy.deepcopy(vector)
            s2 = copy.deepcopy(vector)
            s3 = copy.deepcopy(vector)
            s4 = copy.deepcopy(vector)
            s1.__lshift__(1)
            s2.__lshift__(2)
            s3.__lshift__(3)
            s4.__lshift__(4)
            ans = vector ^ s1 ^ s2 ^ s3 ^ s4 ^ addTo
            Sbox.append(ans.int_val())

def genInvSBox():
    addTo = BitVector(hexstring = "05")
    for i in range(0, 16):
        for j in range(0, 16):
            val = 16*i + j
            vector = BitVector(intVal = val, size = 8)
            s1 = copy.deepcopy(vector)
            s2 = copy.deepcopy(vector)
            s3 = copy.deepcopy(vector)
            s1.__lshift__(1)
            s2.__lshift__(3)
            s3.__lshift__(6)
            ans = s1 ^ s2 ^ s3 ^ addTo
            if ans.int_val() != 0:
                ans = ans.gf_MI( AES_modulus , 8)
            InvSbox.append(ans.int_val())

genSBox()
genInvSBox()

key = "Thats my Kung Fu"
text = "Two One Nine Two 5 H"


print("Key : ", end = "")
key = input()

enKey = EncryptionKey( bytesToList( key.encode() ))

for i in range(0, 11):
    print("Round " + str(i) + ":", end = " ")
    enKey.print(i)
    print()
print("Encrypt: (1) Text (2) File")

opt = int(input())
if(opt == 1):
    text = input()
    cipher = encrypt( bytesToList(text.encode() ),  bytesToList(key.encode() ) )
    print("Cipher: " + ListToString(cipher ))
    plain = decrypt( cipher,  bytesToList(key.encode() ) )
    print("Plain: " + ListToString( plain ) )
else:
    print("File name: ")
    fileName = input()
    file = open(fileName, "rb")
    fileEn = open("encrypted", "wb")
    file2 = open("Dec" + fileName, "wb")

    byte = file. read()
    file.close()
    length = bytesToList(str(len(byte)).encode() )
    byte = encrypt( bytesToList( byte ),  bytesToList(key.encode() ) )
    lengthCipher = encrypt( length,  bytesToList(key.encode() ) )

    cipher = bytes(lengthCipher + byte)
    fileEn.write(bytes(cipher))
    fileEn.close()

    fileEnRead = open("encrypted", "rb")    
    plain = decrypt( bytesToList( fileEnRead.read() ),  bytesToList(key.encode() ) )
    fileEnRead.close()

    leng = int( ListToString(plain[0:16]) )
    plain = plain[16: leng + 16]
    file2.write(bytes(plain ))
    file2.close()