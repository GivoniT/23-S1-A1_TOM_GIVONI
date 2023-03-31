from __future__ import annotations

from data_structures.stack_adt import ArrayStack


class UndoTracker:
    MAX_OPERATIONS = 10000

    def __init__(self) -> None:
        """
        Initialises instance with two stacks, one for undo and one for redo
        All methods of this class are O(1) best and worst case unless specified otherwise
        """
        self.undo_stack = ArrayStack(UndoTracker.MAX_OPERATIONS)
        self.redo_stack = ArrayStack(UndoTracker.MAX_OPERATIONS)

    def add_action(self, action: PaintAction) -> None:
        """
        Adds an action to the undo tracker.
        Args:
            action: PaintAction
        Returns None

        If collection is already full, exits early and does not add the action.
        """

        if self.undo_stack.is_full():
            return
        else:
            self.undo_stack.push(action)
            self.clear_redo()

    def clear_redo(self) -> None:
        """
        Clears self.redo_stack
        """
        self.redo_stack = ArrayStack(UndoTracker.MAX_OPERATIONS)

    def undo(self, grid: Grid) -> PaintAction | None:
        """
        Undo an operation, and apply the relevant action to the grid.
        If there are no actions to undo, simply do nothing.


        :return: The action that was undone, or None.

        Complexity:
        Best Case O(1): undo stack is empty
        Worst Case O(n) where n is the number of steps in the PaintAction from undo_stack
        """

        if self.undo_stack.is_empty():
            return None
        else:
            action = self.undo_stack.pop()
            self.redo_stack.push(action)
            action.undo_apply(grid)
            return action

    def redo(self, grid: Grid) -> PaintAction | None:
        """
        Redo an operation that was previously undone.
        If there are no actions to redo, simply do nothing.

        :return: The action that was redone, or None.
        Complexity:
        Best Case O(1): redo stack is empty
        Worst Case O(n) where n is the number of steps in the PaintAction from redo_stack
        """

        if self.redo_stack.is_empty():
            return None
        else:
            action = self.redo_stack.pop()
            self.undo_stack.push(action)
            action.redo_apply(grid)
            return action
