import pygame
import os
import random
from time import sleep
from colors import *
from tetrominos import *

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 600
TILE_SIZE = 30
colors = [0, red, orange, yellow, green, cyan, blue, purple]

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris By: Lu")

class Grid:
	def __init__(self):
		self.rows = 20
		self.columns = 10
		self.counter = 0
		
		# creating a 2D matrix full of zeros
		self.matrix = []
		for i in range(self.rows):
		    row = []
		    for j in range(self.columns):
		        row.append(0) 
		    self.matrix.append(row)

		# creates a rect shape trim it 2 px, so we can move it 1 pxX pxY and center the tile
		self.surface = pygame.Surface((TILE_SIZE - 2, TILE_SIZE - 2))

	# draws the grid and locked pieces
	def draw(self):
		for i in range(self.rows):
			for j in range(self.columns):

				#assign a color value according to what is display on the grid
				current_color = self.matrix[i][j]
				self.surface.fill(colors[current_color])

				#draw the grid in the window
				window.blit(self.surface, (j * TILE_SIZE + 1, i * TILE_SIZE + 1))

	# this method will let us know if the current row is full
	def rowFull(self, current_row):
		column_counter = 0
		for i in range(self.columns):
			if self.matrix[current_row][i] != 0:
				column_counter += 1
		if column_counter > 9:
			return True

		return False

	# this method will be called when the current row is full, therefore proceed to clear the current row
	def clearCurrentRow(self, current_row):
		for i in range(self.columns):
			self.matrix[current_row][i] = 0

	# after the row gets cleaerd we need to bring down the rows on top
	def moveRowDown(self, current_row):
		for i in range(self.columns):
			if current_row == 0:
				break
			self.matrix[current_row][i] = self.matrix[current_row - 1][i]

	# this method will check for full rows iterating throw the 2D array, 
	def checkFullRows(self):
		full_rows = 0

		for i in range(self.rows):
			# this will keep the last index of the row, we need to check the rows backuards in order to bring down the rows
			# after the rows get cleared
			last_row = (self.rows - 1) - i

			# if the rows are full count how many full rows we'll have
			if self.rowFull(last_row):
				self.clearCurrentRow(last_row)
				full_rows += 1

			# acording to how many full rows we cleared, this is how many rows we'll move the rows on top
			if full_rows > 0:
				self.moveRowDown(last_row)

		# after clearing and moving the rows, we reset the counter to 0
		full_rows = 0

	# displays the matrix in the console
	def printData(self):
		self.counter += 1
		self.counter %= 12
		clear = 'cls'
		if os.name == "posix":
			clear = "clear"
		if self.counter == 0:
			os.system(clear)
			for i in range(self.filas):
				for j in range(self.columnas):
					print(self.matrix[i][j], " ", end = "")
				print()
			print("\n")
	

class Block:
	def __init__(self):
		self.tetrominos = [L,J,T,I,O,Z,S]
		self.currentPiece = self.getRandomBlock()
		self.colorId = self.checkTetrominoShape()
		

		# these offset values takes care of the coordinates on the window
		self.offset_row = 0
		self.offset_column = TILE_SIZE * 3

		# these values takes care of the coordinates on the 2D array, 
		# we need to keep track of both since locked pieces in play are  writen values on the 2D array
		self.current_grid_row = 0
		self.current_grid_column = 3

		# this array will be used to give us the current location of each block
		# that makes the tetromino shape, in order to have collision detection
		self.current_position = []

		# this will change the index on the 2D array of the current piece
		self.rotation = 0

		self.surface = pygame.Surface((TILE_SIZE - 2, TILE_SIZE - 2))
		#self.surface.fill(colors[self.colorId])

		# these values will be for movement and speed
		self.counter = 0

		self.counter_reset = 15



	# assign a random tetromino shape to the current piece in play
	def getRandomBlock(self):
		if len(self.tetrominos) == 0:
			self.tetrominos = [L,J,T,I,O,Z,S]
		block = random.choice(self.tetrominos)
		self.tetrominos.remove(block)
		return block

	# moving the piece to the right with after the keypress
	def moveRight(self, grid):
		self.current_grid_column += 1
		self.offset_column += 1 * TILE_SIZE

		self.current_position = self.getCoordinates()
		if self.isInside() == False:
			for i in range(4):
				# bring it back if out of bounds
				if self.current_position[i][0] > 9:
					self.current_grid_column -= 1
					self.offset_column -= TILE_SIZE
					break
		# if there is a block taken, do not occupy space and bring it back
		elif self.isTaken(grid, self.current_position):
			self.current_grid_column -= 1
			self.offset_column -= TILE_SIZE


	def moveLeft(self, grid):
		self.current_grid_column -= 1
		self.offset_column -= 1 * TILE_SIZE

		self.current_position = self.getCoordinates()
		if self.isInside() == False:
			for i in range(4):
				# bring it back if out of bounds
				if self.current_position[i][0] < 0:
					self.current_grid_column += 1
					self.offset_column += TILE_SIZE
					break
		# if there is a block taken, do not occupy space and bring it back
		elif self.isTaken(grid, self.current_position):
			self.current_grid_column += 1
			self.offset_column += TILE_SIZE

	# rotates the current piece in play
	def rotate(self):
		self.rotation += 4
		if self.rotation > 12:
			self.rotation = 0
		# if we want to prevent rotation, we need to get the cordinates after rotating, do not rely on getting coordinates on the update function
		# because rotation happens 1 per event, 
		self.current_position = self.getCoordinates()
		if self.isInside() == False:
			self.rotation -= 4
		
	# draws the current piece in play in the window
	def draw(self):
		for i in range(4): # 16
			for j in range(4): # 4
				if self.currentPiece[i + self.rotation][j] == 'x':
					self.surface.fill(colors[self.colorId])
					window.blit(self.surface, (self.offset_column + TILE_SIZE * j , self.offset_row + TILE_SIZE * i))

	# this method will take care of the movement of the current piece, and it will check the collision between the pieces
	def update(self, grid):		
		# increment the counter so the pice can move down
		self.counter += 1

		# delay the movement down
		self.counter %= self.counter_reset
		if self.counter == 0:
			self.offset_row += TILE_SIZE
			self.current_grid_row += 1

		# by getting the current position of the blocks, we can cehck if the block falls on top of a pice, or if the block reaches the bottom
		self.current_position = self.getCoordinates()
		
		# if the piece reaches the bottom
		if self.isBelow():
			# get the coordinates again
			self.current_position = self.getCoordinates()
			# bring the piece up. since after getting the coordinates, the piece will be bellow the grid
			for i in range(4):
				self.current_position[i][1] -= 1

			# once the pice has been brought back up, assign the coordinates of each tile of the piec into the grid
			for i in range(4):
				grid[self.current_position[i][1]][self.current_position[i][0]] = self.colorId

			# reset the position, and assign a new tetromino block to the piece
			self.offset_row = 0
			self.offset_column = TILE_SIZE * 3
			self.current_grid_row = 0
			self.current_grid_column = 3
			
			self.rotation = 0
			self.currentPiece = self.getRandomBlock()
			self.colorId = self.checkTetrominoShape()

		# same as the previous if, but only this time we check if there is a space taken bellow the current piece
		elif self.isTaken(grid, self.current_position):
			self.current_position = self.getCoordinates()
			for i in range(4):
				self.current_position[i][1] -= 1

			for i in range(4):
				grid[self.current_position[i][1]][self.current_position[i][0]] = self.colorId

			self.offset_row = 0
			self.offset_column = TILE_SIZE * 3
			self.current_grid_row = 0
			self.current_grid_column = 3

			self.rotation = 0
			self.currentPiece = self.getRandomBlock()
			self.colorId = self.checkTetrominoShape()		

	# this methot will give us the coordinates of each block that makes the tetromino shape, so we can confirm if the block goes out of bounds,
	# or if the block tries to go where there is already a block in place
	def getCoordinates(self):
		grid_index = []
		for i in range(4):
			for j in range(4):
				if self.currentPiece[i + self.rotation][j] == 'x':
					grid_index.append([self.current_grid_column + j, self.current_grid_row + i])
		return grid_index

	# this method will check if the current piece in play is not outside of the playing area left and right 
	def isInside(self):
		for i in range(4):
			if self.current_position[i][0] < 0 or self.current_position[i][0] > 9:
				return False
		return True

	# this method will let us know if the piece is bellow the playing area
	def isBelow(self):
		for i in range(4):
			if self.current_position[i][1] > 19:
				return True
		return False

	# this methos will let us know if the piece is going on a taken coordinate on the 2D array
	def isTaken(self, grid, position):
		for i in range(4):
			if grid[self.current_position[i][1]][self.current_position[i][0]] > 0:
				return True
		return False

	# this method returns a color ID according to the shape of the tetromino
	def checkTetrominoShape(self):
		if self.currentPiece == L:
			return 1
		elif self.currentPiece == J:
			return 2
		elif self.currentPiece == T:
			return 3
		elif self.currentPiece == I:
			return 4
		elif self.currentPiece == O:
			return 5
		elif self.currentPiece == Z:
			return 6
		elif self.currentPiece == S:
			return 7

grid = Grid()
block = Block()

running = True
while running:
	for event in pygame.event.get():
		
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False
			elif event.key == pygame.K_SPACE:
				block.rotate()
			elif event.key == pygame.K_LEFT:
				block.moveLeft(grid.matrix)
			elif event.key == pygame.K_RIGHT:
				block.moveRight(grid.matrix)
			elif event.key == pygame.K_DOWN:
				block.counter_reset = 1
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_DOWN:
				block.counter_reset = 15

	grid.printData()

	# if the tetrominos stack at the top of the playing area
	# game over
	for i in range(grid.columns):
		if grid.matrix[0][i] > 0:
			window.fill(0)
			running = False

	# keep checking if 1 or more rows become full
	grid.checkFullRows()
	
	# update the current block in place, we pass the matrix 2D array, in order to check collision
	block.update(grid.matrix)

	window.fill(0)
	#window.fill(dark_blue)
	grid.draw()
	block.draw()

	pygame.display.update()
	sleep(10/1000)
