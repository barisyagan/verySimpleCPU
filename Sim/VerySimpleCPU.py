#!/usr/bin/python
"""VerySimpleCpu"""
import sys
import re
import ctypes
#TODO: .v and rs232 output?
#TODO: There may be sign issues...

MEMSIZE = 16384

OPCODELUT = ["ADD", "NAND", "SRL", "MUL", "LT", "CPI", "CP", "BZJ"]
OPDICT = { 
        "ADD"   : (0 << 29),
        "NAND"  : (1 << 29),
        "SRL"   : (2 << 29),
        "LT"    : (3 << 29),
        "CPI"   : (5 << 29),
        "CP"    : (4 << 29),
        "BZJ"   : (6 << 29),
        "MUL"   : (7 << 29),
        "ADDi"  : (0 << 29) | (1 << 28),
        "NANDi" : (1 << 29) | (1 << 28),
        "SRLi"  : (2 << 29) | (1 << 28),
        "LTi"   : (3 << 29) | (1 << 28),
        "CPIi"  : (5 << 29) | (1 << 28),
        "CPi"   : (4 << 29) | (1 << 28),
        "BZJi"  : (6 << 29) | (1 << 28),
        "MULi"  : (7 << 29) | (1 << 28)
        }

VALIDLINES = [
        "^ *[0-9]+: *[A-z]+ +[0-9]+ +[0-9]+ *$",
        "^ *[0-9]+: *[A-z]+ +0x[0-9A-Fa-f]+ +[0-9]+ *$",
        "^ *[0-9]+: *[A-z]+ +0x[0-9A-Fa-f]+ +0x[0-9A-Fa-f]+ *$",
        "^ *[0-9]+: *[A-z]+ +[0-9]+ +0x[0-9A-Fa-f]+ *$",
        "^ *[0-9]+: *[0-9]+ *$",
        "^ *[0-9]+: *0x[0-9A-Fa-f]+ *$",
        "^ *$"
        ]

VALIDARGS = [
            "^ *[0-9]+: *[0-9]+ *$",
            "^ *[0-9]+: *0x[0-9A-Fa-f]+ *$",
        ]


def readnumber(instr):
    """read 0x formatted hex or decimal"""
    val = None
    if instr.count("0x") != 0:
        val = int(instr, 16)
    else: 
        val = int(instr)
    return val

class Opcodes():
    ADD  = 0
    NAND = 1
    SRL  = 2
    LT   = 3
    CP   = 4
    CPI  = 5
    BZ   = 6
    MUL  = 7

class CpuState(object):
    """CPU state object"""
    def __init__(self):
        super(CpuState, self).__init__()
        self.pc_ = 0
        self.pause = False
        self.mem =  [0] * MEMSIZE
        self.modified =  [0] * MEMSIZE

    def dumpmemdecimal(self, filenameout):
        """dump decimal to file"""
        flout = open(filenameout, 'w')
        idx = 0
        for word in self.mem:
            if self.modified[idx]:
                flout.write("{0}: {1}\n".format(idx, int(word)))
            idx += 1
        flout.close()

    def dumpmemhex(self, filenameout):
        """dump hex to file"""
        flout = open(filenameout, 'w')
        idx = 0
        for word in self.mem:
            if self.modified[idx]:
                flout.write("{0}: {1}\n".format(idx, hex(word)))
            idx += 1
        flout.close()

    def readmem(self, filenamein):
        """read memin.txt into memory"""
        flin = open(filenamein, 'r')
        for line in flin:
            line = re.sub(":", "", line)
            words = line.split()
            assert len(words) == 2

            aaa = readnumber(words[0])
            bbb = readnumber(words[1])

            self.mem[aaa] = bbb
            self.modified[aaa] = 1
        flin.close()

    def execute(self):
        """excute one step"""
        modifiedlocal =  [0] * MEMSIZE
        before = list(self.mem)

        op_ = (self.mem[self.pc_] >> 29)
        immediate = (self.mem[self.pc_] >> 28) & 0x00000001
        arg0 = (self.mem[self.pc_] >> 14) & 0x00003FFF
        arg1org = (self.mem[self.pc_]) & 0x00003FFF

        self.pc_ += 1
        self.modified[arg0] = 1
        modifiedlocal[arg0] = 1

        print "------------------"
        print "PC:: " + str(self.pc_ - 1)

        if immediate:
            print "{0}i {1} {2}\n".format(OPCODELUT[op_], arg0, arg1org)
        else:
            print "{0} {1} {2}\n".format(OPCODELUT[op_], arg0, arg1org)

        if not immediate:
            arg1 = self.mem[arg1org]
            self.modified[arg1org] = 1
            modifiedlocal[arg1org] = 1
        else:
            arg1 = arg1org

        if op_ == Opcodes.ADD:
            self.mem[arg0] = self.mem[arg0] + arg1
        elif op_ == Opcodes.NAND:
            self.mem[arg0] = ~(self.mem[arg0] & arg1)
        elif op_ == Opcodes.SRL:
            if arg1 < 32:
                self.mem[arg0] = self.mem[arg0] >> arg1
            else:
                self.mem[arg0] = self.mem[arg0] << (arg1 - 32)
        elif op_ == Opcodes.LT:
            self.mem[arg0] = self.mem[arg0] < arg1
        elif op_ == Opcodes.CP:
            self.mem[arg0] = arg1
        elif op_ == Opcodes.BZ:
            if not immediate:
                if not arg1:
                    if self.pc_ == self.mem[arg0] + 1:
                        self.pause = True
                    self.pc_ = self.mem[arg0]
            else:
                if self.pc_ == self.mem[arg0] + arg1 + 1:
                    self.pause = True
                self.pc_ = self.mem[arg0] + arg1
            print "Jumped to new PC: " + str(self.pc_)
            if self.pc_ > MEMSIZE:
                print "New PC is outside memory bounds. Exiting..."
                quit()
                
        elif op_ == Opcodes.CPI:
            if not immediate:
                self.mem[arg0] = self.mem[self.mem[arg1org]]
                self.modified[arg0] = 1
                self.modified[arg1org] = 1
                self.modified[self.mem[arg1org]] = 1
                modifiedlocal[arg0] = 1
                modifiedlocal[arg1org] = 1
                modifiedlocal[self.mem[arg1org]] = 1
            else:
                self.mem[self.mem[arg0]] = self.mem[arg1org]
                self.modified[self.mem[arg0]] = 1
                self.modified[arg1org] = 1
                self.modified[arg0] = 1
                modifiedlocal[self.mem[arg0]] = 1
                modifiedlocal[arg1org] = 1
                modifiedlocal[arg0] = 1
        elif op_ == Opcodes.MUL:
            self.mem[arg0] = self.mem[arg0] * arg1


        print "\nBefore"
        for i in xrange(MEMSIZE):
            if modifiedlocal[i]:
                print "{0}: {1}".format( i, before[i])

        print "\nAfter"
        for i in xrange(MEMSIZE):
            if modifiedlocal[i]:
                print "{0}: {1}".format( i, self.mem[i])
        print
        

def memgen(filenamein, filenameout):
    """parse code into memin format"""
    flin = open(filenamein, 'r')
    flout = open(filenameout, 'w')
    lineno = 0

    for line in flin:
        lineno += 1
        line = line.strip()
        line = re.sub("//.*", "", line)
        invalid = True
        for lin in VALIDLINES:
            if re.match(lin, line):
                invalid = False
                break

        if invalid:
            print "parse error at line " + (lineno + 1)
            print '"' + line +'"'
            quit()

        #line = re.sub(":", "", line)
        words = line.split()
        if len(words) == 2:
            flout.write("{0} {1}\n".format(words[0], words[1]))
        elif len(words) == 4:
            op_ = None
            if words[1] in OPDICT:
                op_ = OPDICT[words[1]]
            else:
                print "Unkown operation '" + words[1] + "'", 
                print "at line " + str(lineno + 1)
                quit()

            in1 = readnumber(words[2])
            in2 = readnumber(words[3])

            in1 = in1 & 0x3FFF
            in2 = in2 & 0x3FFF
            in1 = in1 << 14
            out = in1 | in2 | op_ 
            flout.write("{0} {1}\n".format(words[0], hex(out)))
        elif len(words) == 0: #empty line
            continue
        else:
            print "Parser messed up somewhere"
            quit()

    flin.close()
    flout.close()


def main():
    """main function"""

    finished = False

    cmd = None

    if len(sys.argv) == 3:
        cmd = sys.argv[2]
    elif len(sys.argv) == 2:
        cmd = "x"
    else:
        print "vscpu.py {input}"
        print "vscpu.py {input} {r|q}"
        quit()


    mycpu = CpuState()
    memgen(sys.argv[1], "memin.txt")
    mycpu.readmem("memin.txt")

    while cmd != 'q' and cmd != 'r':
        print "\nProgram parsed successfully."
        print "Enter 'r' to run 'q' to quit"
        cmd = raw_input()

    while True:
        if finished:
            break
        if mycpu.mem[mycpu.pc_] == 0:
            break

        mycpu.execute()
        while mycpu.pause:
            print ">>>",
            mycpu.pause = False
            intext = raw_input().strip()
            if intext == "exit":
                finished = True
                break

            invalid = True
            for lin in VALIDARGS:
                if re.match(lin, intext):
                    invalid = False
                    break

            if invalid:
                print "Unexpected input"
                mycpu.pause = True
                continue

            intext = re.sub(":", "", intext)
            words = intext.split()
            assert len(words) == 2

            aaa = readnumber(words[0])
            bbb = readnumber(words[1])

            mycpu.mem[aaa] = bbb
            mycpu.modified[aaa] = 1
    mycpu.dumpmemdecimal("memoutd.txt")
    mycpu.dumpmemhex("memouth.txt")

if __name__ == '__main__': 
    main()
