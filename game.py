import torch
#pylint: disable=no-member,not-callable

class Cube:
    """ 
    This class represents a rubics cube with a simple representation, resulting
    in 12 possible actions:
    Each of the 6 facets can either be turned clockwise or counterclockwise.
    
    The state of the cube is represented by a 6x3x3 tensor. In our action-representation,
    the color of the middle-cuboid in a facet will never change, thus each facet is
    associated with a specific color. Thus board[f][r][c] represents the color of
    the row r, col c cuboid of facet f. We always have board[f][1][1] == f.
    The game is solved if board[f][i][j] == f for all f,i,j.
    """
    
    def __init__(self):
        self._solved_state = torch.cat(
            [torch.zeros(1,3,3,dtype=torch.int) + i
             for i in range(6)])

        self.board = self._solved_state.clone()
        self.moves = 0
        
        #define both forward and backward map from color/face indices to names.
        self.colors = {0:'blue', 1:'red',
                       2:'yellow', 3:'green',
                       4:'orange', 5:'white'}
        self.ci = {v:k for k,v in self.colors.items()}
        
        self.turns = ['clockwise', 'counterclockwise']
        
        # define colors to print the cube to the terminal
        self._print_color = [
            '\x1b[5;30;44m', #b
            '\x1b[6;30;41m', #r
            '\x1b[6;30;43m', #y
            '\x1b[6;30;42m', #g
            '\x1b[6;30;45m', #o
            '\x1b[6;30;47m' #w
        ]
    
    def is_solved(self):
        return True if torch.all(self.board == self._solved_state) else False

    def reset(self, clean = False):
        self.board = self._solved_state.clone()
        if not clean:
            self.shuffle(100)
        self.moves = 0

    def shuffle(self, n, print=False):
        """Perform n random turns"""
        faces = torch.multinomial(torch.tensor([1/6]*6), n, replacement = True)
        directions = torch.multinomial(torch.tensor([1/2, 1/2]), n, replacement=True)

        for f,d in zip(faces,directions):
            self.turn(f, d, print=False)
        
        if print: self.print_cube()

    def _cuboid_str(self,face,i,o) ->str:
        """Cuboid state with colored terminal printing."""
        col = self.board[face, i, o].item()
        return self._print_color[col] + ' ' + str(col)

    def _row_str(self, face, i):
        """String representation of `i`th row of facet `face`"""
        s = ''
        for j in range(3):
            s += self._cuboid_str(face,i,j) 
        s += '\x1b[0m' # set terminal print color back to normal
        return s 
        
    def print_cube(self):
        """Print the cube in a 3x2 layout."""
        for f in range(3): #right-next-faces
            for r in range(3): # rows
                print(self._row_str(2*f,r) + ' ' + self._row_str(2*f+1,r))
            print('')

    def turn(self, face, direction = 'clockwise', print=False):
        """Turn a facet in the indicated direction."""

        if isinstance(face, str):
            face = self.ci[face]

        if isinstance(direction, str):
            direction = 0 if direction == 'clockwise' else 1

        if direction == 0:
            tmp = self.board[(face+1)%6, 0, :].clone()
            self.board[(face+1)%6, 0, :] = self.board[(face+2)%6,  :, 0]            
            self.board[(face+2)%6, :, 0] = self.board[(face-2)%6, -1, :]
            self.board[(face-2)%6, -1, :] = self.board[(face-1)%6,  :,-1]
            self.board[(face-1)%6,  :, -1] = tmp.clone()
        else: #counterclockwise
            tmp = self.board[(face+1)%6, 0, :].clone()
            self.board[(face+1)%6, 0, :] = self.board[(face-1)%6,  :,-1]
            self.board[(face-1)%6, :,-1] = self.board[(face-2)%6, -1, :]
            self.board[(face-2)%6, -1, :] = self.board[(face+2)%6,  :, 0]
            self.board[(face+2)%6,  :, 0] = tmp.clone()

        self.moves += 1

        if print:
            self.print_cube()



