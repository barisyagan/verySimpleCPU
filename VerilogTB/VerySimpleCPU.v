`timescale 1ns / 1ps
module VerySimpleCPU(clk, rst, data_fromRAM, wrEn, addr_toRAM, data_toRAM);

parameter SIZE = 14;

input clk, rst;
input wire [31:0] data_fromRAM;
output reg wrEn;
output reg [SIZE-1:0] addr_toRAM;
output reg [31:0] data_toRAM;

reg[2:0] state, stateNext, cycled, cycledNext;
reg[31:0] opcode,opcodeNext,instruction,instructionNext,immediate = 0,immediateNext,Astar,AstarNext,Bstar,BstarNext,A,Anext,B,Bnext;
reg[SIZE-1:0] programCounter = 0,programCounterNext;


always@(posedge clk) begin
   state <= #1 stateNext;
   programCounter <= #1 programCounterNext;
   immediate <= #1 immediateNext;
	cycled <= #1 cycledNext;
	A <= #1 Anext;
	B <= #1 Bnext;
	opcode <= #1 opcodeNext;
	Astar <= #1 AstarNext;
	Bstar <= #1 BstarNext;
end

always@(*) begin
	Anext = A;
	Bnext = B;
	AstarNext = Astar;
	BstarNext = Bstar;
   stateNext = state;
   programCounterNext = programCounter;
   immediateNext = immediate;
	cycledNext = cycled;
	opcodeNext = opcode; 
	
   if(rst) begin
		stateNext = 0;
		programCounterNext = 0;
		immediateNext = 0;
		cycledNext = 0;
		opcodeNext = 0;
		AstarNext = 0;
		BstarNext = 0;
	end

   else begin
	case(state)
	    0 : begin //Fetch Instruction
			wrEn = 0;
	      addr_toRAM = programCounter; 
	      stateNext = 1;
		 end
	
	    1 : begin //Fetch op1
			immediateNext = data_fromRAM[28];
		   opcodeNext = data_fromRAM[31:29];
			Anext = data_fromRAM[27:14];
			Bnext = data_fromRAM[13:0];
			addr_toRAM = data_fromRAM[27:14];
	      stateNext = 2;
	    end
		
	    2 : begin //Fetch op2
	      AstarNext = data_fromRAM;
			addr_toRAM = Bnext;
	      stateNext = 3;
	    end

	    3 : begin //Execute
			BstarNext = data_fromRAM;
			Bstar = BstarNext;
			case(opcode) 
				0 : begin //ADD and ADDi
					if(immediate) AstarNext = Astar + B;
					else AstarNext = Astar + Bstar;
				end

				1 : begin //NAND and NANDi
					if(immediate) AstarNext = ~(Astar & B);
               else AstarNext = ~(Astar & Bstar);
				end

				2 : begin //SRL and SRLi
					if(immediate) begin
						if(B < 32) AstarNext = Astar >> B;
						else AstarNext = Astar << (B-32);
					end
               else begin
						if(Bstar < 32) AstarNext = Astar >> Bstar;
						else AstarNext = Astar << (Bstar-32);
					end
				end

				3 : begin //LT and LTi
					if(immediate) begin
						if(Astar < B) AstarNext = 1;
						else AstarNext = 0;
					end	
					else begin
					if(Astar < Bstar) AstarNext = 1;
					else AstarNext = 0;
					end
				end

				4 : begin //CP,CPi
					if(immediate) AstarNext = B;
					else AstarNext = Bstar;
				end

				5 : begin //CPI,CPIi
					if(immediate) begin
						Anext = Astar;
						AstarNext = Bstar;
						stateNext = 4;
						programCounterNext = programCounter + 1;
					end
					else begin
						if(!cycled) addr_toRAM = Bstar;
						stateNext = 3;
						cycledNext = 1;
						if(cycled) begin
							AstarNext = Bstar;
							cycledNext = 0;
							stateNext = 4;
							programCounterNext = programCounter + 1;
						end
					end
				end

				6 : begin //BZJ and BZJi
					if(immediate) programCounterNext = Astar + B; 
               else begin
						if(Bstar == 0) programCounterNext = Astar;
						else programCounterNext = programCounter + 1;
					end
				end 
				7 : begin //MUL and MULi
					if(immediate) AstarNext = Astar * B;
					else AstarNext = Astar * Bstar;
				end
			endcase
			if(opcode != 5) stateNext = 4;
		 end

		 4 : begin //Write back
			wrEn = 1;
			addr_toRAM = A;
			data_toRAM = Astar;
			stateNext = 5;
	    end

	    5 : begin //Update Program Counter
			if ((opcode != 6) && (opcode != 5)) programCounterNext = programCounter+1;
			stateNext = 0;
	    end
    endcase
	 end
end
endmodule
