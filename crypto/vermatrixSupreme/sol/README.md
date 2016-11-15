This challenge is just simple matrix operations, where a random IV and seed are generated, and the goal is to recover the IV.

The solution script works by reversing the given algorithm for matrix generation, by:

1. reversing the x and y coordinates of the matrix
2. xoring the resulting matrix and the seed
