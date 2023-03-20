from __future__ import annotations

from data_structures.referential_array import ArrayR
from layer_store import LayerStore

from data_structures import referential_array
from layer_store import *
class Grid:
    DRAW_STYLE_SET = "SET"
    DRAW_STYLE_ADD = "ADD"
    DRAW_STYLE_SEQUENCE = "SEQUENCE"
    DRAW_STYLE_OPTIONS = (
        DRAW_STYLE_SET,
        DRAW_STYLE_ADD,
        DRAW_STYLE_SEQUENCE
    )

    DEFAULT_BRUSH_SIZE = 2
    MAX_BRUSH = 5
    MIN_BRUSH = 0

    def __init__(self, draw_style, x, y) -> None:
        """
        Initialise the grid object.
        - draw_style:
            The style with which colours will be drawn.
            Should be one of DRAW_STYLE_OPTIONS
            This draw style determines the LayerStore used on each grid square.
        - x, y: The dimensions of the grid.

        Should also intialise the brush size to the DEFAULT provided as a class variable.
        """
        # Initialising self. brush size is set to the default.
        self.brush_size = self.DEFAULT_BRUSH_SIZE
        self.draw_style = draw_style
        # Grid is created as an array of length x with x arrays of length y inside
        self.grid = ArrayR(x)
        for i in range(x):
            temp_array = ArrayR(y)
            for j in range(y): # initialising with the desired layer store class
                if self.draw_style == Grid.DRAW_STYLE_SET:
                    temp_array[j] = SetLayerStore()
                elif self.draw_style == Grid.DRAW_STYLE_ADD:
                    temp_array[j] = AdditiveLayerStore()
                elif self.draw_style == Grid.DRAW_STYLE_SEQUENCE:
                    temp_array[j] = SequenceLayerStore()
                else:
                    temp_array[j] = SetLayerStore()
            self.grid[i] = temp_array

    def increase_brush_size(self):
        """
        Increases the size of the brush by 1,
        if the brush size is already MAX_BRUSH,
        then do nothing.
        """
        if self.brush_size == self.MAX_BRUSH:
            pass
        else:
            self.brush_size += 1

    def decrease_brush_size(self):
        """
        Decreases the size of the brush by 1,
        if the brush size is already MIN_BRUSH,
        then do nothing.
        """
        if self.brush_size == self.MIN_BRUSH:
            pass
        else:
            self.brush_size -= 1

    def special(self):
        """
        Activate the special effect on all grid squares.
        """
        # Switches the SetLayerStore CLASS variable special_flag between True and False
        if SetLayerStore.special_flag:
            SetLayerStore.special_flag = False
        else:
            SetLayerStore.special_flag = True



    def __getitem__(self, index: int) -> T:
        #magic method allowing the array within the grid to be accessed directly. AKA for a grid k, k[x] and even k[x][y]
        """ Returns the object in position index.
        :complexity: O(1)
        :pre: index in between 0 and length - self.array[] checks it
        """
        return self.grid[index]

    def __setitem__(self, index: int, value: T) -> None:
        # magic method allowing the array within the grid to be accessed directly. AKA for a grid k, k[x] and even k[x][y]
        """ Sets the object in position index to value
        :complexity: O(1)
        :pre: index in between 0 and length - self.array[] checks it
        """
        self.grid[index] = value
