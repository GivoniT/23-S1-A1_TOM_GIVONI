from __future__ import annotations

from data_structures.referential_array import ArrayR
from replay import ReplayTracker
from undo import UndoTracker
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
    MAX_OPERATIONS = 10000  # as specified in assignment brief
    REPLAY_STACK = CircularQueue(MAX_OPERATIONS)
    REPLAY_STACK_PLAYBACK = CircularQueue(MAX_OPERATIONS)
    def __init__(self, draw_style, x, y) -> None:
        """
        Initialise the grid object.
        - draw_style:
            The style with which colours will be drawn.
            Should be one of DRAW_STYLE_OPTIONS
            This draw style determines the LayerStore used on each grid square.
        - x, y: The dimensions of the grid.

        Should also intialise the brush size to the DEFAULT provided as a class variable.
        Intialises UndoTracker and ReplayTracker

        All methods written in this class have best and worst case complexity of O(1), unless stated otherwise.

        Complexity:
        Best case: O(1) where x = y = 1
        Worst case: O(xy) as initialising_grid has complexity O(xy)
        """
        # Initialising self. brush size is set to the default.
        self.brush_size = self.DEFAULT_BRUSH_SIZE
        self.draw_style = draw_style
        self.initialising_grid(x, y)
        # Setting up undo tracker
        self.undo_track = UndoTracker()
        # Setting up redo tracker
        self.replay_track = ReplayTracker()
        # These help if opening a new window
        self.x = x
        self.y = y



    def initialising_grid(self, x: int, y: int) -> None:

        """
        Grid is created as an array of length x with x arrays of length y inside
        All grid squares are initialised with a layer store, corresponding with self.draw_style.
        Args:
            x: int
            y: int
        Complexity:
        O(x*y)
        this is because there is a for loop in range y inside a for loop in range x
        """

        self.grid = ArrayR(x)
        for i in range(x):
            temp_array = ArrayR(y)
            for j in range(y):  # initialising with the desired layer store class
                if self.draw_style == Grid.DRAW_STYLE_SEQUENCE:
                    temp_array[j] = SequenceLayerStore()
                elif self.draw_style == Grid.DRAW_STYLE_ADD:
                    temp_array[j] = AdditiveLayerStore()
                else:
                    temp_array[j] = SetLayerStore()
            self.grid[i] = temp_array

    def increase_brush_size(self) -> None:
        """
        Increases the size of the brush by 1,
        if the brush size is already MAX_BRUSH,
        then do nothing.
        """
        if self.brush_size == self.MAX_BRUSH:
            pass
        else:
            self.brush_size += 1

    def decrease_brush_size(self) -> None:
        """
        Decreases the size of the brush by 1,
        if the brush size is already MIN_BRUSH,
        then do nothing.
        """
        if self.brush_size == self.MIN_BRUSH:
            pass
        else:
            self.brush_size -= 1

    def special(self) -> None:
        """
        Activate the special effect on all grid squares.

        Complexity:
        Best case: O(x*y) if all grid squares are SetLayerStore. This is because their special_complexity is O(1)
        Where x,y = grid.x, grid.y

        Worst case: O(x*y*n) if the grid is additive layer store.
        Where x,y,n = grid.x, grid.y, number of layer in layer store instances
        This is because additive special is O(n)
        Note: this is worse than Sequence's special as the number of layers is at most 9
        If the number of layers was unbounded it would also be O(n)
        """
        # triggers the special in method in all grid squares
        for array in self.grid:
            for layer in array:
                layer.special()



    def __getitem__(self, index: int) -> T:
        """ Returns the object in position index.
        :complexity: O(1)
        :pre: index in between 0 and length - self.array[] checks it
        """
        return self.grid[index]

    def __setitem__(self, index: int, value: T) -> None:
        """ Sets the object in position index to value
        :complexity: O(1)
        :pre: index in between 0 and length - self.array[] checks it
        """
        self.grid[index] = value
