import pygame
import random

# features:
#   Clears the board
#   Handles Movement
#   Checks for collisions?
#   Holds stats like levels and lines cleared
#   Holds a timer, which gets shorter as the level gets higher


#   TODO: main features are added, so now you just need to clean up the source code currently, then move on to:
#        V 1.1 - up next queue, score and level increase
#        V 1.2 - Main Menu, Sounds and perhaps some graphics ;)
#        V 1.3 - Multiple Game Modes - single block mode, maybe a puzzle mode, marathon etc. (will think about this when i get to it)

class GameManager:
    def __init__(self, resolution, screen):
        self.board = self.MakeBoard()
        self.boardColor = ((43, 43, 43))
        self.resolution = resolution
        self.screen = screen  # Pygame window
        self.level = 12
        self.line_clears = 0    # Indiviual lines, not 4 stacks
        self.timer = 120        # Depletes faster as Level increases
        self.pieceArray = []    # Each piece object gets added to an array as a Ghost, so it can draw all on screen
        self.PAUSE = False
        self.oldLevel = 0
        # TODO: Make up next Queue
        #self.upnextArr = self.GETUPNEXT
        self.activePiece = Piece(1)

    # Each coordinate holds a 1 or 0
    # If the line == 10, then it is a full line (see checklines method)
    def MakeBoard(self,testing=False):
        arr = []
        for x in range(10):
            for y in range(24):
                arr.append((x, y, 0))

        if testing:
            testArr = []
            for y in range(20,24):
                for x in range(10):
                    if x == 4:
                        continue
                    else:
                        arr[arr.index((x,y,0))] = (x,y,1)
                        testArr.append(Piece(8,((x,y))),(255,255,255))

            return arr,testArr
        return arr

    # Makes the grid in pygame
    def DrawBoard(self):
        for item in self.board:
            Block = pygame.Rect((item[0] * self.resolution, item[1] * self.resolution),
                                (self.resolution, self.resolution))
            pygame.draw.rect(self.screen, self.boardColor, Block, 3)

    # Draws the board, and pieces
    def Update(self):
        # these are bad for my IDE intellisense but oh well :(
        self.screen.fill((0, 0, 0))
        for item in self.pieceArray:
            item.Draw(self.resolution,self.screen)
        self.DrawBoard()
        self.activePiece.UpdatePiece(self.screen,self.resolution,self.board)
        self.Gravity()

    # Executes downward movement every tick
    def Gravity(self):
        self.timer -= self.level
        if self.timer <0:
            self.CheckLines()
            self.timer = 120
            # Gets all the pieces in actual boardSpace
            ActivePos = self.activePiece.GetBoardState(self.activePiece.type,self.activePiece.pos)
            CanMove = True
            for item in ActivePos:
                # Bottom of screen
                if item[1] >= 23:
                    CanMove = False
                    break
                # If coordinate Under Tetris Piece is in Board, then place it (so it places ontop)
                underPos = (item[0],item[1]+1,1)
                #print(f'underPos = {underPos}\n pos = {item}')
                if underPos in self.board:
                    print('Collision?')
                    CanMove = False


            if CanMove:
                # adds 1 because world origin in top left
                self.activePiece.pos = (self.activePiece.pos[0],self.activePiece.pos[1]+1)
            else:
                self.Place(ActivePos)


        # The piece gets added to the piece Array (to keep drawing it)
        # The piece then sets the board spots to 1 (which it should be doing anyway)
        # Then a new piece needs to be generated, and added to the top of the screen
    def Place(self,positions):
        BoardPositions = positions
        for item in BoardPositions:
            #Gets locations and turns them on
            newPosIndex = self.board.index((item[0],item[1],0))
            self.board[newPosIndex] = item
        self.pieceArray.append(Ghost(self.activePiece.Color,positions))

        #Creates new piece Randomly
        self.activePiece = Piece(random.randint(1,7))
        #self.activePiece = Piece(1)


    # Every block placement, check for lines
    def CheckLines(self):
        lineNums = []
        # To be changed and then sent back as the final board
        for y in range(24):
            # Loops through y, instead of x
            laneTotal = 0
            for x in range(10):
                if (x,y,1) in self.board:
                    laneTotal +=1
            if laneTotal == 10: #if lane is full, Give to array of full lines (to test if its a tetris)
                lineNums.append(y)

        if len(lineNums) > 0:
            self.RemoveLines(lineNums)

    # in the words of stamper, PAUSE
    def PAUSEGAME(self):
        self.PAUSE = not self.PAUSE
        if self.PAUSE:
            self.oldLevel = self.level
            self.level = 0
        else:
            self.level = self.oldLevel


    #TODO: FINISHE LINE REMOVAL

    # so far i have this: all positions above the lowest y (0,0 starts from top left)
    # to be pulled down by the size of the array (max 4)
    # Once you do that, you need to give each ghost piece all positions that were wiped.
    # Using that info they will remove segments, or delete them
    # Then they will move thier positions down by lenght of array

    def getActivePieces(self,laneNum):
        arr = []
        for y in laneNum:
            for x in range(10):
                # just move the coords above Down one
                arr.append((x,y,1))
        return arr

    def RemoveGhosts(self,ghostList,activePieceList,NewBoardList,laneSize):
        # Ghost Piece positions
        newGhosts = ghostList       #The updated ghosts
        activePieces = activePieceList  # The list of active positions to be cleared
        newBoard = NewBoardList         # The new board, to replace the old one after updating
        TetrisSize = laneSize
        laneY = activePieces[0][1]
        print(f'yPos = {laneY}')

        for ghost in newGhosts:  # for every ghost in list
            posArr = []  # array to store all positions that are in line clear
            for ghostPos in ghost.positions:  # get each of the 4 positions
                # This should always be able to happen
                if ghostPos in activePieces:  # If its already in the active position list (to be deleted basically)
                    posArr.append(tuple(ghostPos))


            # once it has the correct positions, remove all the pieces at once, so it doesnt give wierd results
            for position in posArr:
                ghost.DelPos(position)  # delete the block at the position

        newGhosts = self.GhostDown(ghostList,TetrisSize)    # These ghosts have the final Actual positions
        newBoard = self.MoveDown(newBoard,ghostList)

        #Return with results
        return newGhosts,activePieces,newBoard

    def GhostDown(self,GhostPieces,TetrisSize):
        ghosts = GhostPieces
        MoveSize = TetrisSize

        for ghost in ghosts:
            for position in ghost.positions:
                if position[1] == 23:   #if at range Limit, dont calculate whats below because it will crash
                    continue
                posIndex = ghost.positions.index(position)
                ghost.positions[posIndex] = (position[0],position[1] + MoveSize,1)
        return ghosts


    def MoveDown(self,board,ghosts):
        finalBoard = board
        positions = []  # List of ghost Positions
        # Get the positions each ghost POST UPDATE  (i know this is heavily segmented, but once i get something working
        # Then you can refactor and make it gucci ;)
        for ghost in ghosts:
            for position in ghost.positions:
                positions.append(position)

        #getY = lambda y: y[1]
        # sory by Y value
        #positions.sort(key=getY)
#        print(positions)

        # make a new board lol
#        newBoard = self.MakeBoard()
#        print(newBoard)
        for position in positions:# turn all ghost positions into taken board spaces
            if (position[0],position[1],0) in finalBoard:
                posindex = finalBoard.index((position[0],position[1],0))  # get the index of the position thats going to be deleted
                finalBoard[posindex] = position   # activate the position that was previously inactive

        return finalBoard


    # Actually Removes the lines if there is a match
    def RemoveLines(self,laneNumArr):
        # Pauses Game
        self.PAUSEGAME()
        newGhosts = self.pieceArray
        newBoard = self.MakeBoard() #make a new board lol cuz we straight up resetting this biznatch
        # active Pieces are the positions of the lines being removed
        activePieces = self.getActivePieces(laneNumArr)

        # get the higest Y (lowest because 0,0 is top left)
        lowestY = activePieces[0][1]
        for item in activePieces:
            if item[1] < lowestY:
                lowestY = item[1]

        # Apply changes to the Ghost Pieces
        self.RemoveGhosts(newGhosts,activePieces,newBoard,len(laneNumArr))
        print(f'No of ghosts: {len(newGhosts)}\n'
              f'deleted Line Coords: {activePieces}\n'
              f'Old BoardState: {self.board}\n'
              f'New BoardState: {newBoard}')

        self.board = newBoard
        self.pieceArray = newGhosts
        self.PAUSEGAME()

    # Get left(a) and right(d) input and Rotation(left/right) Input
    # Gets input from pygame events in main loop
    def input(self,QueEvent):
        if QueEvent.type == pygame.KEYDOWN:
            # Rotations
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                self.activePiece.Rotate(self.board,Left=True)
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.activePiece.Rotate(self.board,Left=False)
            # Movement
            if pygame.key.get_pressed()[pygame.K_a]:#Left
                self.activePiece.Move(self.board,Left=True)
            if pygame.key.get_pressed()[pygame.K_d]:#Right
                self.activePiece.Move(self.board,Left=False)



# Makes a piece based on the given type (chosen randomly) 1-7.
# This piece can be moved and rotated
# this will check collision with other pieces in rotation, sides and placement
# Will place on cooridnates with y=0, or on top of another piece

class Piece:
    def __init__(self, typeNum, pos=(4,-3)):
        #Color set to 100, so it doesnt go too low and cant be seen by player

        self.Color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.type = self.MakePiece(typeNum)  # 1 = i, 2 = o, 3 = T, 4 = S, 5 = Z, 6 = J, 7 = L
        self.pieceType = typeNum    # To be used to self differentiate what kind of piece it is
        self.pos = pos  # Spawns in middle of playfield X
        self.boardState = self.GetBoardState(self.type,self.pos)
        self.direction = 1  # 1 = up, 2 = left, 3 = down, 4 = right


    def SetColor(self):
        rgb = random.randint(1,3)
        if rgb == 1: # Red
            Color = (random.randint(100, 255), random.randint(0, 255), random.randint(0, 255))
        if rgb == 2:
            Color = (random.randint(0, 255), random.randint(100, 255), random.randint(0, 255))
        if rgb == 3:
            Color = (random.randint(0, 255), random.randint(0, 255), random.randint(100, 255))
        return Color



    def MakePiece(self, typenum):
        # Each tuple represents a shape
        if typenum == 1:
            # I coords
            return ((0, 1), (0, 0), (0, -1), (0, -2))
        if typenum == 2:
            # T coords
            return ((-1, 0), (0, 0), (1, 0), (0, -1))
        if typenum == 3:    # Square
            return ((0,0),(0,1),(1,0),(1,1))
        if typenum == 4:    #L piece
            return ((0,-1),(0,0),(0,1),(1,1))
        if typenum == 5:    #J piece
            return ((0,-1),(0,0),(0,1),(-1,1))
        if typenum == 6:    #s piece
            return ((-1,0),(0,0),(0,1),(1,1))
        if typenum == 7:    #J piece
            return ((1,0),(0,0),(0,1),(-1,1))
        if typenum == 8:
            return ((0,0))

    def SideCollisions(self,newType):
        for item in newType:
            if item[0] < 0 or item[0] > 9:
                return True
            if item[1] >= 24:    # Board is sized at 24 but i forgot lol
                return True
        return False

    def Move(self,board,Left=False):
        if Left:
            newPos = (self.pos[0] - 1,self.pos[1])
            newBoard = self.GetBoardState(self.type,newPos)

            #check its in bounds and if not, return
            if self.SideCollisions(newBoard):
                return

            if self.BoardCollisions(newBoard,board):
                print('collides')
            else:
                print('doesnt Collide')
                self.pos = newPos
        else:
            newPos = (self.pos[0] + 1,self.pos[1])
            newBoard = self.GetBoardState(self.type,newPos)

            #check its in bounds and if not, return
            if self.SideCollisions(newBoard):
                return

            if self.BoardCollisions(newBoard,board):
                print('collides')
            else:
                print('doesnt Collide')
                self.pos = newPos

    # Takes a position array (x,y) and a turns it into positions on the board (x,y,1)
    # Gets board positions and turns them on, so that it can be refrenced in relation to the board
    def GetBoardState(self,typeArr,pos):
        arr = []
        for item in typeArr:
            x = pos[0] + item[0]
            y = pos[1] + item[1]
            arr.append((x,y,1))
        return arr

    # Within the Board, update it so that the new positions are now in place
    def SetBoardPos(self,board):
        for piece in board:
            for pos in self.boardState:
                if piece[0] == pos[0] and piece[1] == pos[1]:
                    piece = pos
                else:# need to reset the pieces that arent in use
                    piece = (piece[0],piece[1],0)

    # Returns true if given position would intersect an x,y value that is already active within the board
    def BoardCollisions(self,upPos,board):
        # If the updated position is in the board already, then it is true
        for i in upPos:
            print(i)
            if i in board:
                print(f'{i} is active on board')
                return True
        return False

    def DrawPiece(self,resolution,screen):
        # Draws to screen
        for item in self.type:
            newposx = (self.pos[0] * resolution) + (item[0] * resolution)
            newposy = (self.pos[1] * resolution) + (item[1] * resolution)
            blockRect = pygame.Rect(newposx, newposy, resolution, resolution)
            pygame.draw.rect(screen, self.Color, blockRect, 3)

    # To be used by the GM to check for collisions and drawing
    # Draw the piece based on the coordinates of the type and the self.position
    def UpdatePiece(self,screen,resolution,board):
        self.DrawPiece(resolution, screen)
        self.boardState = self.GetBoardState(self.type,self.pos)  # Gives block a board Coordinate
        self.SetBoardPos(board) # Actually updates the board based on info above

    def Rotate(self,Board,Left=True):
        # Swaps positions to rotate based on direction
        # If a square you cant rotate
        if self.pieceType == 3:
            return

        if Left:
            if self.direction == 4 or self.direction > 4:
                self.direction = 1
            else:
                self.direction += 1
        else:                           # for right movement
            if self.direction == 1 or self.direction < 1:
                self.direction = 4
            else:
                self.direction -= 1

        coordArr = []
        # Matrix = up to left = swap x/y and negate x,
        # left to down = swap x/y,
        # down to right = swap to x and negate,
        # right to up = swap x/y
        if Left:
            for coord in self.type:
                coordArr.append(self.LeftRotate(coord))
        else:
            for coord in self.type:
                coordArr.append((self.RightRotate(coord)))
        print(coordArr)
        # gets the board positions of the rotated coordinates
        rotatedArr = self.GetBoardState(coordArr,self.pos)
        print(rotatedArr)
        # Will return if True
        if self.SideCollisions(rotatedArr) or self.BoardCollisions(rotatedArr,Board):
            # Reset Direction due to Collision
            if Left:
                self.direction -= 1
            else:
                self.direction += 1
            return
        self.type = coordArr
        print(self.type)
        print(self.direction)

    def LeftRotate(self,coord):
        # 1 to 2
        if self.direction == 1:
            x = -coord[1]
            y = coord[0]
            return ((x, y))
            # 2 to 3
        if self.direction == 2:
            x = -coord[1]
            y = coord[0]
            return ((x, y))
            # 3 to 4
        if self.direction == 3:
            x = -coord[1]
            y = coord[0]
            return ((x, y))
            # 4 to 1
        if self.direction == 4:
            x = -coord[1]
            y = coord[0]
            return ((x, y))
        return coord

    def RightRotate(self, coord):
        print(coord)
        # 1 to 4
        if self.direction == 1:
            x = coord[1]
            y = -coord[0]
            return ((x, y))
            # 4 to 3
        if self.direction == 2:
            x = coord[1]
            y = -coord[0]
            return ((x, y))
            # 3 to 2
        if self.direction == 3:
            x = coord[1]
            y = -coord[0]
            return ((x, y))
            # 2 to 1
        if self.direction == 4:
            x = coord[1]
            y = -coord[0]
            return ((x, y))
        return coord


# Gets Places At the Location of a placed tetromino in the board (to be continuously Drawn
class Ghost:
    def __init__(self,Color,Positions):
        self.color = Color
        self.positions = Positions

    def Draw(self,resolution,screen):
        # Draw items at world Coordinate
        for item in self.positions:
            posRect = pygame.Rect((item[0]*resolution,item[1]*resolution),(resolution,resolution))
            pygame.draw.rect(screen,self.color,posRect)

    # If all positions are Cleared, then Delete. This is only visual and has no source code effect
    def DelPos(self,GivePosition):
        posIndex = self.positions.index(GivePosition)
        del self.positions[posIndex]
        if len(self.positions) == 0:
            print('deletin')
            del self

    # Needs finishing
    # Clear positions in self array, from the given positions from actual board.
    def ClearLines(self,positions):
        for item in positions:
            if item in self.positions:
                pass



