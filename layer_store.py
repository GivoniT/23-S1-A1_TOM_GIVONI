from __future__ import annotations
from abc import ABC, abstractmethod

from data_structures.stack_adt import ArrayStack
from data_structures.queue_adt import CircularQueue
from layer_util import Layer
from layers import invert


class LayerStore(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    def add(self, layer: Layer) -> bool:
        """
        Add a layer to the store.
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        Returns the colour this square should show, given the current layers.
        """
        pass

    @abstractmethod
    def erase(self, layer: Layer) -> bool:
        """
        Complete the erase action with this layer
        Returns true if the LayerStore was actually changed.
        """
        pass

    @abstractmethod
    def special(self):
        """
        Special mode. Different for each store implementation.
        """
        pass


class SetLayerStore(LayerStore):
    """
    Set layer store. A single layer can be stored at a time (or nothing at all)
    - add: Set the single layer.
    - erase: Remove the single layer. Ignore what is currently selected.
    - special: Invert the colour output.
    """
    # Boolean CLASS variable signalling if 'special' is active or not
    special_flag: bool = False

    def __init__(self):  # Initialising new instances with a current layer as None
        self.current_layer = None

    # sets current_layer as the new one and returns True. If current == new it will return False
    def add(self, layer: Layer) -> bool:
        if self.current_layer == layer:
            return False
        else:
            self.current_layer = layer
            return True

    def erase(self, layer: Layer) -> bool:  # Sets current_layer to None
        if self.current_layer is None:
            return False
        else:
            self.current_layer = None
            return True

    def special(self):  # Switches the CLASS variable flag between True and False
        if SetLayerStore.special_flag:
            SetLayerStore.special_flag = False
        else:
            SetLayerStore.special_flag = True

    # returns the color from a particular layer. Taking special into consideration.
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:

        if self.current_layer is None:  # returning the start input value if current layer is None
            return_value = start
        else:  # returning the valid color otherwise
            return_value = self.current_layer.apply(start, timestamp, x, y)
        if SetLayerStore.special_flag:  # inverts the color if special is on
            return invert.apply(return_value, timestamp, x, y)
        else:
            return return_value


class AdditiveLayerStore(LayerStore):
    """
    Additive layer store. Each added layer applies after all previous ones.
    - add: Add a new layer to be added last.
    - erase: Remove the first layer that was added. Ignore what is currently selected.
    - special: Reverse the order of current layers (first becomes last, etc.)
    """

    # Boolean CLASS variable signalling if 'special' is active or not
    special_flag: bool = False

    def __init__(self):  # Initialising new instances with a current layer as None
        # creating a stack with sufficient capacity ( > 9*100 )
        self.current_layers = ArrayStack(1000)

    def add(self, layer: Layer) -> bool:
        if self.current_layers.is_full():
            return False
        else:
            self.current_layers.push(layer)
            return True

    def erase(self, layer: Layer) -> bool:
        if self.current_layers.is_empty():
            return False
        else:
            # extracting all layers into a temporary stack, emptying self.current_layers
            temp_stack = ArrayStack(1000)
            for i in range(len(self.current_layers)):
                layer = self.current_layers.pop()
                temp_stack.push(layer)
            temp_stack.pop()  # removing last layer (on top of temp stack)
            # return the layers to self.current_layers
            for i in range(len(temp_stack)):
                layer = temp_stack.pop()
                self.current_layers.push(layer)
            return True


class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
    """

    pass
