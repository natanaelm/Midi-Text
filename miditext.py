from mdata import mtrk
import mdata as Md
import sys
import struct

__author__ = "Natanael Maciel"
"""
Este programa lê e decodifica dados midi e escreve um xml. Cada Evento e Meta-Evento é
precedido de um delta-time.
"""
nTrk=0
index=0
#número de 32 bits
def nbt():
    return struct.unpack(">I",f.read(4))[0]
#tratar delta time
def delta(cnd):
    """
    Esta função lê bytes de uma sequência (Trk)
    e verifica o tamanho dessa variável,
    deslocando 7 bits a esquerda cada vez
    que o 7mo bit é igual a 1.
    Usada para delta-times e
    tamanho de meta-eventos
    """
    global index
    tmp=Trk[index]
    valr=0
    while (tmp>>7)==1:
        valr |= tmp & 0x7f
        valr <<= 7
        index += 1
        tmp = Trk[index]
    valr |= tmp & 0x7f
    index+=1
    if cnd:
        mtrk.delta(valr)
    return valr
#tratar eventos e meta-eventos
def event():
    """
    Função responsável por ler os eventos e
    meta-eventos, e chama as funções para
    escrever os objetos xml de eventos.
    """
    global index
    evt = Trk[index]
    ety = (evt >> 4)
    ch = (evt & 0x0f)
    #running status
    if evt < 128:
        mtrk.runStatus(evt,Trk[index+1])
        index+=2
    #noteOff, noteOn, polyKey, control, pitch
    elif ety in [8,9,10,11,14]:
        mtrk.Event(ety,ch,[Trk[index+1],Trk[index+2]])
        index+=3
    #program, pressure
    elif ety in [12,13]:
        mtrk.Event(ety,ch,[Trk[index+1]])
        index+=2
    #system exclusive
    elif evt in [0xf0,0xf7]:
        index+=1
        leng= delta(False)
        prop=[]
        pr = 0
        while pr < leng:
            prop.append(Trk[index])
            index+=1
            pr+=1
        mtrk.SysEx(evt,leng,bytes(prop))
    #meta
    elif evt == 0xff:
        index+=1
        mty = Trk[index]
        if mty==0x2f:
            mtrk.end()
            index+=2
        else:
            index+=1
            leng= delta(False)
            prop=[]
            for pt in range(leng):
                prop.append(Trk[index])
                index+=1
            mtrk.Meta(mty,leng,bytes(prop))
#colocar cabeçalho MThd
def MThd(length):
    """
    Função que lê o cabeçalho que contém
    informações sobre formato, número de
    trilhas e divisão.
    """
    global nTrk
    arr= struct.unpack(">HHH",f.read(length))
    fmt= arr[0]
    nTrk= arr[1]
    div= arr[2]
    print(f"Formato:{fmt}")
    print(f"Trilhas:{nTrk}")
    print(f"Divisão:{div}")
    #instancia mthd
    Md.mthd(fmt,nTrk,div)
#Analisar cabecalho
def header():
    hdr = f.read(4)
    if hdr == b'MThd':
        MThd(nbt())
    elif hdr == b'MTrk':
        global Trk, index
        length=nbt()
        Trk= f.read(length)
        mtrk()
        while index < length:
            delta(True)
            event()
        index=0
    else:
        print("Erro no Arquivo!")
def main(inFl,ouFl):
    global nTrk
    try:
        global f
        f = open(inFl,"rb")
        Md.start(ouFl)
        header()
        Y = 0
        print("Lendo Arquivo...")
        while Y < nTrk:
            Y+=1
            print(f"Lendo Trilha {Y}")
            header()
        Md.end()
        print("Concluído!")
    except:
        print(f"\033[31mArquivo {inFl} com Erro!\033[0m\nReinicie o programa e tente outra vez.")
        sys.exit(0)
#inicia o programa
if __name__ == "__main__":
    print("Decodificador de MIDI para Texto\n")
    inres = input("Arquivo de Entrada: ")
    outres = input("Arquivo de Saída: ")
    main(inres,outres)