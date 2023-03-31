from __future__ import annotations
from action import PaintAction
from data_structures.queue_adt import CircularQueue

class ReplayTracker:
    """
    Creating class variable queues for memory and play back

    All methods in this class are O(1) best and worst case complexity unless otherwise stated
    """
    MAX_CAPACITY = 10000
    replay_queue = CircularQueue(MAX_CAPACITY)
    playback_queue = CircularQueue(MAX_CAPACITY)
    def start_replay(self) -> None:
        """
        Called whenever we should stop taking actions, and start playing them back.
        Transfers the replay action to the playback_queue. Resets replay_queue.

        Useful if you have any setup to do before `play_next_action` should be called.
        """
        ReplayTracker.playback_queue = ReplayTracker.replay_queue
        self.reset_replay_queue()

    def reset_replay_queue(self) -> None:
        """
        Resets the class replay_queue
        """
        ReplayTracker.replay_queue = CircularQueue(10000)

    def add_action(self, action: PaintAction, is_undo: bool=False) -> None:
        """
        Adds an action to the replay.

        `is_undo` specifies whether the action was an undo action or not.
        Special, Redo, and Draw all have this is False.
        """
        ReplayTracker.replay_queue.append((action, is_undo))

    def play_next_action(self, grid: Grid) -> bool:
        """
        Plays the next replay action on the grid.
        This function attempts to retrieve an action.
        If found, deciphers if he action is undo, special or draw, then executes.

        Returns a boolean.
            - If there were no more actions to play, and so nothing happened, return True.
            - Otherwise, return False.

        Complexity:
        Best case  O(1): the replay tracker queue was empty
        Worst case O(xyn) when special is called. See Grid.special for details.
        """
        try:
            action = ReplayTracker.playback_queue.serve()
        except: # if the queue is empty
            self.reset_replay_queue()
            return True
        else:
            if action[1]: # checks if is_undo == True
                try: # try except block to prevent issues with undo on empty screen
                    action[0].undo_apply(grid)
                except:
                    pass
                else:
                    return False
            elif action[0].is_special:
                grid.special()
                return False
            else:
                action[0].redo_apply(grid)

        return False

if __name__ == "__main__":
    action1 = PaintAction([], is_special=True)
    action2 = PaintAction([])

    g = Grid(Grid.DRAW_STYLE_SET, 5, 5)

    r = ReplayTracker()
    # add all actions
    r.add_action(action1)
    r.add_action(action2)
    r.add_action(action2, is_undo=True)
    # Start the replay.
    r.start_replay()
    f1 = r.play_next_action(g) # action 1, special
    f2 = r.play_next_action(g) # action 2, draw
    f3 = r.play_next_action(g) # action 2, undo
    t = r.play_next_action(g)  # True, nothing to do.
    assert (f1, f2, f3, t) == (False, False, False, True)

