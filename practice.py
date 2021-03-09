from BitVector import *
import copy

Sbox = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

AES_modulus = BitVector(bitstring='100011011')

Mixer = [
    [BitVector(hexstring="02"), BitVector(hexstring="03"), BitVector(hexstring="01"), BitVector(hexstring="01")],
    [BitVector(hexstring="01"), BitVector(hexstring="02"), BitVector(hexstring="03"), BitVector(hexstring="01")],
    [BitVector(hexstring="01"), BitVector(hexstring="01"), BitVector(hexstring="02"), BitVector(hexstring="03")],
    [BitVector(hexstring="03"), BitVector(hexstring="01"), BitVector(hexstring="01"), BitVector(hexstring="02")]
]

def shiftLeft(arr, n):
    old = arr.copy()    
    for i in range(0, len(arr)):
        arr[i] = old[ (i+n) % len(arr) ]


def subByte(byteVect):
    byteStr = byteVect.getHexStringFromBitVector()
    vct = BitVector(intVal = Sbox[(int(byteStr[0], 16)* 16 +  int(byteStr[1], 16))], size = 8)
    return vct

def subBytes(arr):
    for i in range(0, len(arr)):
        arr[i] = subByte(arr[i])

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
    ret = []
    mat = []
    while len(text) < 16:
        text = text + '0'
    text = text[0:16]
    for i in range(0, len(text)):
        ret.append(ord(text[i]))
    mat = [ [ BitVector(intVal=ret[j*4 + i], size=8 ) for i in range(0, 4)] for j in range(0, 4)]
    return mat

def matToText(mat):
    mat = transposeMat(mat)
    cipher = ""
    for x in mat:
        for y in x:
            cipher += y.getHexStringFromBitVector()
    return cipher

def xorMat(a, b):
    c = copy.deepcopy(a)
    for i in range(0, len(a)):
        for j in range(0, len(a[0])):
            c[i][j] = a[i][j] ^ b[i][j]
    return c

def subMat(a):
    c = copy.deepcopy(a)
    for i in range(0, len(a)):
        subBytes(c[i])
    return c

def shiftMat(a):
    for i in range(0, len(a)):
        shiftLeft(a[i], i)
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
        subBytes(arr)
        arr[0] = arr[0]^self.getRC(i)

    def nextRoundKey(self, key, round):
        gFunc = key[3].copy() 
        self.getG(gFunc, round)
        newKey = key
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

# key = "54 68 61 74 73 20 6D 79 20 4B 75 6E 67 20 46 75"
key = "Thats my Kung Fu"
text = "Two One Nine Two"


def encrypt(text, key):
    textMat = transposeMat(textToBitMatrix(text) )
    enKey = EncryptionKey(key)
    stateMat = xorMat(textMat, transposeMat( enKey.getKey(0) ) )
    # printMat(stateMat)
    # print("=================================")
    for round in range(1, 10):
        stateMat = subMat(stateMat)
        stateMat = shiftMat(stateMat)
        stateMat = MixColumn(Mixer, stateMat)
        stateMat = xorMat(stateMat, transposeMat( enKey.getKey(round) ) )
        # printMat(stateMat)
        # print("=================================")
    stateMat = subMat(stateMat)
    stateMat = shiftMat(stateMat)
    stateMat = xorMat(stateMat, transposeMat( enKey.getKey(10) ) )
    printMat(stateMat)
    print(matToText(stateMat))   



encrypt(text, key)



# test = EncryptionKey(key)

# keyVect = test.getKey(0)
# print("====================")
# keyVect = transposeMat(keyVect)
# printMat(keyVect)

# print("====================")

# textMat = textToBitMatrix(text)
# textMat = transposeMat(textMat)
# printMat(textMat)

# print("====================")
# mat = xorMat(keyVect, textMat)
# printMat(mat)

# print("====================")
# mat = subMat(mat)
# printMat(mat)

# print("====================")
# shiftMat(mat)
# printMat(mat)

# print("====================")
# mat = MixColumn(Mixer, mat)
# printMat(mat)

