import sys
import pygame
import random
import glob

Decisions = 24

# The Assets in BG
assetDir = glob.glob('Assets/*.png')
BGIMG = pygame.image.load(assetDir[0])
# Up Next Images
UpnextPic = glob.glob('Assets/UpNext/*.png')

pygame.font.init()
ScoreFont = pygame.font.SysFont('Arial', 20)

# Window settings
pygame.display.set_caption('Tetris 19: ghosts')
logo = pygame.image.load(assetDir[1])
pygame.display.set_icon(logo)


def Quit():
    pygame.quit()
    sys.exit()


# Each coordinate holds a 1 or 0 for on or off
def MakeBoard():
    arr = []
    for x in range(10):
        for y in range(24):
            arr.append((x, y, 0))
    return arr


# Check if something is oob
def SideCollisions(PositionArr):
    for pos in PositionArr:
        if pos[0] < 0 or pos[0] > 9:
            return True
        if pos[1] >= 24:  # Board is sized at 24
            return True
    return False


# Returns T/F based on if 2 arrays contain the same values
def BoardCollisions(PositionArr, board):
    # If the updated position is in the board already, then it is true
    for ArrPos in PositionArr:
        if ArrPos in board:
            return True
    return False


# Creates a random color
# I think eventually, adding color schemes and stuff would be cool e.g. game boy scheme, vaporwave, minecraft etc.
def SetColor():
    Color = (random.randint(100, 255), random.randint(100, 255), random.randint(0, 100))
    print(f'Color value: {Color}')
    return Color


# Creates The Local Coordinates for a Tetris Piece
def MakePiece(typenum):
    # I coords
    if typenum == 1:
        return ((0, 1), (0, 0), (0, -1), (0, -2))

    # T coords
    if typenum == 2:
        return ((-1, 0), (0, 0), (1, 0), (0, -1))

    # O coords
    if typenum == 3:
        return ((0, 0), (0, 1), (1, 0), (1, 1))

    # L piece
    if typenum == 4:
        return ((-1, 1), (-1, 0), (0, 0), (1, 0))

    # J piece
    if typenum == 5:
        return ((1, 1), (-1, 0), (0, 0), (1, 0))

    # s piece
    if typenum == 6:
        return ((-1, 0), (0, 0), (0, 1), (1, 1))

    # z piece
    if typenum == 7:
        return ((1, 0), (0, 0), (0, 1), (-1, 1))

    # 1x1 block for testing
    if typenum == 8:
        return ((0, 0))


# features:
#   Clears the board
#   Handles Movement
#   Checks for collisions?
#   Holds stats like levels and lines cleared
#   Holds a timer, which gets shorter as the level gets higher


#   TODO: main features are added, so now you just need to clean up the source code currently, then move on to:
#        V 1.1 - up next queue
#        V 1.2 - Main Menu, Sounds and perhaps some graphics ;)
#        V 1.3 - Multiple Game Modes - single block mode, maybe a puzzle mode, marathon etc. (will think about this when i get to it)


class GameManager:
    def __init__(self, resolution, screen):
        self.board = MakeBoard()
        self.DecisionCount = 12
        self.boardColor = ((43, 43, 43))
        self.resolution = resolution
        self.screen = screen  # Pygame window
        self.level = 1
        self.line_clears = 0  # Indiviual lines, not 4 stacks. keeps track of lines needed to up the level (10)
        self.total_line_clears = 0  # to keep track of total Lines
        self.timer = 120  # Depletes faster as Level increases
        self.GhostPieces = []  # Each piece object gets added to an array as a Ghost, so it can draw all on screen
        self.PAUSE = False
        self.oldLevel = 0
        self.fastMove = False
        # TODO: Make up next Queue
        # self.upnextArr = self.GETUPNEXT
        self.activePiece = Piece(4)
        self.noOfKeys = 0
        self.score = 0

    # The mainest function, becasue it executes all code
    def Update(self, eventCall):
        self.timer -= self.level
        self.Draw()
        # these are bad for my IDE intellisense but oh well :(
        self.Gravity()
        self.input(eventCall)

    def Draw(self):
        self.DrawAssets()
        self.DrawBoard()
        self.activePiece.UpdatePiece(self.screen, self.resolution, self.board)

    # shows Score, Level and maybe a quit button if i figure that out (not important now)
    def DrawText(self):
        TextColor = (255, 255, 255)
        if self.PAUSE:
            levelText = f'Level: {self.oldLevel}'
        else:
            levelText = f'Level: {self.level}'

        # Score
        level = ScoreFont.render(levelText, False, TextColor)
        levelRect = level.get_rect(y=0)
        levelRect.x = self.screen.get_width() - levelRect.width

        lineClears = ScoreFont.render(f'Lines Cleared: {self.total_line_clears}', False, TextColor)
        LCRect = lineClears.get_rect(y=0)
        LCRect.x = levelRect.x - LCRect.width - 20

        score = ScoreFont.render(f'Score: {self.score}', False, TextColor)
        scoreRect = score.get_rect(y=30)
        scoreRect.x = self.screen.get_width() - 120

        self.screen.blit(level, levelRect)
        self.screen.blit(lineClears, LCRect)
        self.screen.blit(score, scoreRect)

    # Makes the grid in pygame
    def DrawBoard(self):
        for xy in self.board:
            Block = pygame.Rect((xy[0] * self.resolution, xy[1] * self.resolution),
                                (self.resolution, self.resolution))
            pygame.draw.rect(self.screen, self.boardColor, Block, 3)

    def DrawAssets(self):
        # order: 1 - background, 2 - text, 3 - Filled pieces
        self.screen.blit(BGIMG, (0, 0))
        self.DrawText()
        for item in self.GhostPieces:
            item.Draw(self.resolution, self.screen)

    # Executes downward movement every tick
    def Gravity(self):
        if self.timer < 0:
            self.DecisionCount = Decisions
            self.timer = 120
            # Gets all the pieces in actual boardSpace
            self.activePiece.GetBoardState(self.activePiece.LocalCoords, self.activePiece.pos)

            for item in self.activePiece.boardState:
                underPos = (item[0], item[1] + 1, 1)
                # Bottom of screen
                if item[1] >= 23 or underPos in self.board:
                    self.Place()
                    return
            # if no collision, move down 1
            self.activePiece.pos = (self.activePiece.pos[0], self.activePiece.pos[1] + 1)

    def Place(self):
        for index, item in enumerate(self.activePiece.boardState):
            if item[1] < 0:  # Endgame
                Quit()
            # Insert each active piece into the board at the same positions given (active Piece)
            newPosIndex = self.board.index((item[0], item[1], 0))
            self.board[newPosIndex] = item

        # Update board
        self.GhostPieces.append(Ghost(self.activePiece.Color, self.activePiece.boardState))
        self.CheckLines()

        # Creates new piece Randomly
        self.activePiece = Piece(random.randint(1, 7))

    # Every block placement, check for lines
    def CheckLines(self):
        Ypos = []  # the line Y positions to be cleared
        ClearPositions = []  # the positions of all the items in the Line
        for y in range(24):
            # Loops through y, instead of x
            laneTotal = 0
            positions = []
            for x in range(10):
                if (x, y, 1) in self.board:
                    laneTotal += 1
                    positions.append((x, y, 1))
            if laneTotal == 10:  # if lane is full, Give to array of full lines (to test if its a tetris)
                Ypos.append(y)
                ClearPositions.append(positions)
        if len(Ypos) > 0:
            self.RemoveLines(Ypos, ClearPositions)

    # TODO: Old method doesnt take into account if a line sandwiched between 2 line clears is there

    # Actually Removes the lines if there is a match
    def RemoveLines(self, YposArr, LineClearPositions):
        # Pauses Game
        self.PAUSEGAME()
        newBoard = MakeBoard()  # make a new board
        ghostPieces = self.GhostPieces

        # remove all positions that collide with the ghosts
        for line in LineClearPositions:
            EmptyList = False
            while not EmptyList:
                # for some reason it needs to check multiple times. IDK why its checking is so unreliable :/
                if len(line) == 0:
                    EmptyList = True
                for ghost in ghostPieces:
                    posList = ghost.positions
                    for pos in posList:
                        if pos in line:
                            ghost.DelPos(pos)
                            linePosIndex = line.index(pos)
                            line.pop(linePosIndex)

        # for each Y, sub 1 from the y of whatever is above (counters the sandwich possiblitiy)
        for Ypos in YposArr:  # for each Y position
            for ghost in ghostPieces:
                for index, position in enumerate(ghost.positions):  # get each ghost position coordinate
                    # if it y pos is above or (on the clear lines somehow)
                    if position[1] < Ypos:  # todo: think this may have been the bug issue (was <= instead of <)
                        newPos = (position[0], position[1] + 1, 1)
                        ghost.positions[index] = newPos

        # add line clears to linecount
        self.LineCount(len(YposArr))

        for index, boardPos in enumerate(newBoard):
            for ghost in ghostPieces:
                for ghostPos in ghost.positions:
                    if ghostPos[0] == boardPos[0] and ghostPos[1] == boardPos[1]:
                        newBoard[index] = ghostPos

        self.board = newBoard
        self.GhostPieces = ghostPieces
        self.PAUSEGAME()

    def LineCount(self, lines):
        global Decisions
        lineLimit = 5
        self.line_clears += lines  # Add line clears to
        self.total_line_clears += lines
        if self.line_clears >= lineLimit:
            self.oldLevel += 1
            self.line_clears = 0
            if Decisions != 1:
                Decisions -= 1

    # in the words of stamper, PAUSE
    def PAUSEGAME(self):
        self.PAUSE = not self.PAUSE
        if self.PAUSE:
            self.oldLevel = self.level
            self.level = 0
        else:
            self.level = self.oldLevel

    # Get left(a) and right(d) input and Rotation(left/right) Input
    # Gets input from pygame events in main loop
    def input(self, QueEvent):
        if QueEvent is None:
            return
        self.noOfKeys = 0
        if self.DecisionCount > 0:
            # SetDown (insta-drop)
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                # sets it to lowers possible position and then instantly places it
                self.score += self.activePiece.SetDown(self.board, self.level)
                self.activePiece.GetBoardState(self.activePiece.LocalCoords, self.activePiece.pos)
                self.Place()

            # Rotations
            if pygame.key.get_pressed()[pygame.K_LEFT] and self.noOfKeys < 1:
                self.activePiece.Rotate(self.board, Left=True)
                self.noOfKeys += 1
                self.DecisionCount -= 1
                return
            elif pygame.key.get_pressed()[pygame.K_RIGHT] and self.noOfKeys < 1:
                self.activePiece.Rotate(self.board, Left=False)
                self.noOfKeys += 1
                self.DecisionCount -= 1
                return

            # Movement
            if pygame.key.get_pressed()[pygame.K_a] and self.noOfKeys < 2:  # Left
                self.activePiece.Move(self.board, Left=True)
                self.noOfKeys += 1
                self.DecisionCount -= 1
                return
            elif pygame.key.get_pressed()[pygame.K_d] and self.noOfKeys < 2:  # Right
                self.activePiece.Move(self.board, Left=False)
                self.noOfKeys += 1
                self.DecisionCount -= 1
                return
                # FastDrop
            elif pygame.key.get_pressed()[pygame.K_s] and self.noOfKeys < 2:
                self.FastDrop(Fast=True)
                self.score += self.level
                return
            else:
                self.FastDrop(Fast=False)
        else:
            self.timer = 0

    def FastDrop(self, Fast=False):
        if Fast:
            self.timer = 1
        else:
            self.timer = 120


# Makes a piece based on the given type (chosen randomly) 1-7.
# This piece can be moved and rotated
# this will check collision with other pieces in rotation, sides and placement
# Will place on cooridnates with y=0, or on top of another piece

# Rotations For Piece
def RightRotate(coord):
    x = -coord[1]
    y = coord[0]
    return ((x, y))


def LeftRotate(coord):
    x = coord[1]
    y = -coord[0]
    return ((x, y))


class Piece:
    def __init__(self, typeNum, pos=(4, 1)):
        # Color set to 100, so it doesnt go too low and cant be seen by player
        self.Color = SetColor()
        # self.Color = (255,255,255)
        self.LocalCoords = MakePiece(typeNum)  # 1 = i, 2 = o, 3 = T, 4 = S, 5 = Z, 6 = J, 7 = L
        self.pieceType = typeNum  # To be used to self differentiate what kind of piece it is
        self.pos = pos  # Spawns in middle of playfield X
        self.boardState = self.GetBoardState(self.LocalCoords, self.pos)
        self.direction = 1  # 1 = up, 2 = left, 3 = down, 4 = right

    def Move(self, board, Left=False):
        if Left:
            newPos = (self.pos[0] - 1, self.pos[1])
            newBoard = self.GetBoardState(self.LocalCoords, newPos)

            # check its in bounds and if not, return
            if SideCollisions(newBoard):
                return

            if not BoardCollisions(newBoard, board):
                self.pos = newPos
        else:
            newPos = (self.pos[0] + 1, self.pos[1])
            newBoard = self.GetBoardState(self.LocalCoords, newPos)

            # check its in bounds and if not, return
            if SideCollisions(newBoard):
                return

            if not BoardCollisions(newBoard, board):
                self.pos = newPos

    # Gets board positions and turns them on, so that it can be referenced in relation to the board
    def GetBoardState(self, LocalCoords, newPos):
        arr = []
        for item in LocalCoords:
            x = newPos[0] + item[0]
            y = newPos[1] + item[1]
            arr.append((x, y, 1))
        return arr

    # Within the Board, update it so that the new positions are now in place
    def SetBoardPos(self, board):
        for piece in board:
            for pos in self.boardState:
                if piece[0] == pos[0] and piece[1] == pos[1]:
                    piece = pos
                else:  # need to reset the pieces that aren't in use
                    piece = (piece[0], piece[1], 0)

    # Returns true if given position would intersect an x,y value that is already active within the board

    def DrawPiece(self, resolution, screen):
        # Draws to screen
        for item in self.LocalCoords:
            newposx = (self.pos[0] * resolution) + (item[0] * resolution)
            newposy = (self.pos[1] * resolution) + (item[1] * resolution)
            blockRect = pygame.Rect(newposx, newposy, resolution, resolution)
            pygame.draw.rect(screen, self.Color, blockRect, 3)

    # To be used by the GM to check for collisions and drawing
    # Draw the piece based on the coordinates of the LocalCoords and the self.position
    def UpdatePiece(self, screen, resolution, board):
        self.DrawPiece(resolution, screen)
        self.boardState = self.GetBoardState(self.LocalCoords, self.pos)  # Gives block a board Coordinate
        self.SetBoardPos(board)  # Actually updates the board based on info above

    # need to fix I piece
    def Rotate(self, Board, Left=True):
        # Swaps positions to rotate based on direction
        # If a square you cant rotate
        if self.pieceType == 3:
            return
        # if piece is too close to the left or right side, it pushes them out so it can rotate (otherwise coord is oob)
        if Left:
            if self.direction == 4 or self.direction > 4:
                self.direction = 1
            else:
                self.direction += 1
        else:  # for right movement
            if self.direction == 1 or self.direction < 1:
                self.direction = 4
            else:
                self.direction -= 1

        coordArr = []
        # todo: Fix I/1 piece
        # left rotate = (x=y,y=-x)
        # right rotate = (x = -y,y=x)
        if Left:
            for coord in self.LocalCoords:
                coordArr.append(LeftRotate(coord))
        else:
            for coord in self.LocalCoords:
                coordArr.append(RightRotate(coord))

        # gets the board positions of the rotated coordinates
        rotatedArr = self.GetBoardState(coordArr, self.pos)

        xarr = []
        # if coord is outside the board, push it in by the size of the furthest piece that is oob
        for item in rotatedArr:
            xarr.append(item[0])

        diffVal = 0
        # if oob left
        if min(xarr) < 0:
            oldpos = self.pos
            diffVal = abs(min(xarr))
            self.pos = (self.pos[0] + diffVal, self.pos[1])
            rotatedArr = self.GetBoardState(coordArr, self.pos)
            if BoardCollisions(rotatedArr, Board):
                self.pos = oldpos

        # if oob right
        if max(xarr) > 9:
            oldpos = self.pos
            diffVal = max(xarr) - 9
            self.pos = (self.pos[0] - diffVal, self.pos[1])
            rotatedArr = self.GetBoardState(coordArr, self.pos)
            if BoardCollisions(rotatedArr, Board):
                self.pos = oldpos

        # Will return if True
        if SideCollisions(rotatedArr) or BoardCollisions(rotatedArr, Board):
            # Reset Direction due to Collision
            if Left:
                self.direction -= 1
            else:
                self.direction += 1
            return
        self.LocalCoords = coordArr

    # get lowest Y position
    def lowestY(self, ypos):
        lowY = ypos
        for coord in self.boardState:
            if coord[1] < lowY:
                lowY = ypos
        return lowY

    # Just Checks directly underneath each unique X at its lowest Y position. If it finds a collision, it exits
    # but if not, it keeps moving down until it collides or hits the bottom of the well
    # this is very slow method IMO, but seems to work in pretty much every situation without throwing errors
    def SetDown(self, board, levelMulti):
        print('_____________________________SETDOWN START____________________________')
        print(f'Local Coords: {self.LocalCoords}')
        print(f'dir: {self.direction},type: {self.pieceType}')

        distance = 0
        # adjusts positions to move down if there is available space in the Y
        collisions = False
        while not collisions:
            distance += 1
            newPos = []
            for pos in self.boardState:
                new = (pos[0], pos[1] + 1, 1)
                if new[1] > 23:
                    collisions = True  # if oob
                    break
                newPos.append((pos[0], pos[1] + 1, 1))

            # creates only unique Y values
            posList2 = []
            for index, pos in enumerate(newPos):
                if pos not in self.boardState:
                    posList2.append(pos)

            for item in posList2:
                if item in board:
                    collisions = True
                    break

            if not collisions:  # if the unique Y positions arent in the board, then move down but otherwise quit loop
                self.boardState = newPos


        print(f'Final Calculated Position: {self.pos}\nFinal Segments: {self.boardState}')
        return distance * levelMulti


# Gets Places At the Location of a placed tetromino in the board (to be continuously Drawn
class Ghost:
    def __init__(self, Color, Positions):
        self.color = Color
        self.positions = Positions

    def Draw(self, resolution, screen):

        for item in self.positions:
            if type(item) == int:
                pass
            else:
                posRect = pygame.Rect((item[0] * resolution, item[1] * resolution), (resolution, resolution))
                pygame.draw.rect(screen, self.color, posRect)

    # If all positions are Cleared, then Delete. This is only visual and has no source code effect
    def DelPos(self, GivePosition):
        posIndex = self.positions.index(GivePosition)
        del self.positions[posIndex]
        if len(self.positions) == 0:
            del self
