Files in this folder:

VerySimpleCPU.exe: Windows console program (run in a cmd window).
libgnurx-0.dll: Library file required by VerySİmpleCPU.exe.
VerySimpleCPU.py: Python version of VerySimpleCPU.exe (portable but not fully tested).
test.asm: A meaningless program that you should use to test your design. It has every instruction it.
          You should make sure the "after =" values of memory locations are correct after the program
          runs on your VerySimpleCPU design. You should check memory locations in Xilinx ISIM simulator.
          You may want to run also one or more of the programs you wrote in the lab such as recursive
          factorial. See the lab folder one level above this file.

---o---

How to Run VerySimpleCPU.exe:

> VerySimpleCPU.exe {input}
Parses {input} and creates memin.txt, memory.v, mem232.txt
Then asks whether to run the code or quit.

> VerySimpleCPU.exe {input} r
Parses {input} and creates memin.txt, memory.v, mem232.txt.
Runs the code without asking.

> VerySimpleCPU.exe {input} q
Parses {input} and creates memin.txt, memory.v, mem232.txt.
Quits after creating the files without asking.

---o---

Some fancy features VerySimpleCPU.exe:

- During the parsing stage, mid.txt is created. It contains the code with memory address numbers inserted.

- After a clean exit the program generates memoutd.txt and memouth.txt. memoutd.txt contains the memory contents in decimal. memouth.txt contains the memory contents in hex.

- If there is a parse error, the program line causing it gets printed.

- Lines with no address specified have the address of the previous line plus one. Preprocessor figures out addresses and creates a file called mid.txt with all line addresses in place. Then the simulator actually runs this program file.

- Simulator exits if the address PC points to is 0.

- Simulator falls into the prompt mode if PC does not change after an instruction eceutes.

- In prompt mode:
  - "exit" -> exits the simulator and dumps the current memory to memout.txt
  - "A: B" -> where A and B are unsigned numbers, writes B into address A
  - "A: 0xB" -> where A and B are unsigned integers, writes 0xB (hex) into address A
