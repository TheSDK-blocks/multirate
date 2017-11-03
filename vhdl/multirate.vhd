-- This is multirate VHDL model
-- Generated by initentity script
LIBRARY ieee;
USE ieee.std_logic_1164.all;
USE ieee.numeric_std.all;
USE std.textio.all;


ENTITY multirate IS
    PORT( A : IN  STD_LOGIC;
          Z : OUT STD_LOGIC
        );
END multirate;

ARCHITECTURE rtl OF multirate IS
BEGIN
    buf:PROCESS(A)
    BEGIN
        Z<=A;
    END PROCESS;
END ARCHITECTURE;