#-*-coding:utf8;-*-
#eventos

"""
Esta biblioteca obtem dados midi em forma de bytes e codifica para um arquivo de texto.
"""
#Eventos do programa
def start(fname):
  global root
  root = open(fname,"w")

#Tratar Cabecalho
def mthd(fmt,trk,div):
  root.write(f"MThd {fmt} {trk} {div}\n")

#bytes para string
def toStr(vect):
  try:
    st = vect.decode()
  except UnicodeDecodeError:
    st = vect.decode('latin-1')
  except:
    st = "<null>"
  return st

#Tratar Trilha
class mtrk:
  def __init__(self):
    global root
    root.write("MTrk\n")

  #delta times
  def delta(value):
    root.write(f"{value} ")

  #status corrente
  def runStatus(kk,vv):
    root.write(f"run {kk} {vv}\n")

  #Eventos do Canal
  def Event(tpe,ch,attr):
    if tpe == 8:
      root.write(f"noteOff {ch} {attr[0]} {attr[1]}\n")
    elif tpe == 9:
      if attr[1] == 0:
        root.write("noteOff ")
      else:
        root.write("noteOn ")
      root.write(f"{ch} {attr[0]} {attr[1]}\n")
    elif tpe == 10:
      root.write(f"polyKey {ch} {attr[0]} {attr[1]}\n")
    elif tpe == 11:
      root.write(f"control {ch} {attr[0]} {attr[1]}\n")
    elif tpe == 12:
      root.write(f"program {ch} {attr[0]}\n")
    elif tpe == 13:
      root.write(f"pressure {ch} {attr[0]}\n")
    elif tpe == 14:
      pb = attr[1]<<8 | attr[0]
      root.write(f"pitch {ch} {pb}\n")

  def SysEx(evt,leng,props):
    root.write(f"sysEx {evt} {leng} {props}\n")

  #meta-eventos
  def Meta(met,leng,props):
    root.write(f"meta {leng} ")
    if met == 0:
      sn = props[0] << 8 | props[1]
      root.write(f"seqNumber {sn}\n")

    #Eventos de textos e lirismo
    elif met == 1:
      root.write(f"text {toStr(props)}\n")
    elif met == 2:
      root.write(f"copyright {toStr(props)}\n")
    elif met == 3:
      root.write(f"trackName {toStr(props)}\n")
    elif met == 4:
      root.write(f"instName {toStr(props)}\n")
    elif met == 5:
      root.write(f"lyric {toStr(props)}\n")
    elif met == 6:
      root.write(f"marker {toStr(props)}\n")
    elif met == 7:
      root.write(f"cuePoint {toStr(props)}\n")

    #prefixo do canal
    elif met == 0x20:
      root.write(f"chPref {props[0]}\n")
    #tempo em microsegundos
    elif met == 0x51:
      tmp = props[0] <<16 | props[1] << 8 | props[2]
      root.write(f"setTempo {tmp}\n")
    #smpte
    elif met == 0x54:
      root.write(f"smpteOffset {props[0]} {props[1]} {props[2]} {props[3]} {props[4]}\n")
    #divisao de compasso
    elif met == 0x58:
      root.write(f"timeSig {props[0]} {props[1]} {props[2]} {props[3]}\n")
    #acorde principal
    elif met == 0x59:
      if props[0] > 127:
        props[0]= 256 - props[0]
      root.write(f"keySig {props[0]} {props[1]}\n")
    #meta evento especifico
    elif met == 0x7f:
      root.write("spec")
      for bt in props:
        root.write(f" {bt}")
      root.write("\n")

    else:
      root.write("<none>\n")

  def end():
    root.flush()

def end():
  root.close()