## SuDoKu Solver

#### Introduction
Tries to solve input SuDoKu puzzle using hidden and naked tuples and backtracking.

#### Algorithm

The program uses two methods in fixing a value to a cell.
1. **Fixed Baseline**: Traverse column wise from top to bottom. If there is any cell that can have only one value then 
set the value.
1. **Most Constrained Variable**: Consider a cell that has least number of allowed values. For each of this value 
recursively try to solve the puzzle. If the number used is unable to solve then reset the board to the state before 
this assumption and check with all other values till you find a solution.

With each cell update the program removes the value from each of the related horizontal and vertical line and that grid.
It then applies inference rules to update the constraints of other cells in the board using naked and hidden tuple.

Also, the program tries to solve each puzzle with minimum first before moving to higher rules.

###### Naked Tuple

A naked N-D cell tuple is observed if total number of different values these cells hold is equal to N. Algorithm for 
this inference rule for each block, i.e., row, column or grid, is as described below.
1. Find all unique N-D tuples of cells.
1. If a tuple is valid, i.e., value of each cell in the tuple is not set, then generate a union of all numbers allowed 
for this tuple of cells.
1. A naked tuple is present if the size of this union is equal to N. Now remove these numbers from all cells except 
those in the tuple in the block.

###### Hidden Tuple

A hidden N-D value tuple is observed if total number of different cells these values can belong to is equal to N. 
Algorithm for this inference rule for each block, i.e., row, column or grid, is as described below.
1. Find all unique N-D tuples of values.
1. If a tuple is valid, i.e., cell in the block is not set by any value in the tuple, then generate a union of all 
cells these values can occupy.
1. A hidden tuple is present if the size of this union is equal to N. Now remove numbers other than these numbers from 
all cells in the union and remove these numbers from cells not belonging to the union.
