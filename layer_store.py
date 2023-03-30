from __future__ import annotations
from abc import ABC, abstractmethod

from data_structures.stack_adt import ArrayStack
from data_structures.queue_adt import CircularQueue
from data_structures.array_sorted_list import ArraySortedList
from data_structures.bset import BSet
from data_structures.sorted_list_adt import ListItem
from layer_util import Layer
from layer_util import get_layers
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

    All methods written in this class have best and worst case complexity of O(1), unless stated otherwise.
    """


    def __init__(self):
        """
        Initialising new instances with a current layer as None
        """
        self.current_layer = None
        # Boolean INSTANCE variable signalling if 'special' is active or not
        self.special_flag = False

    def add(self, layer: Layer) -> bool:
        """
            Sets current_layer as the new one and returns True. If current == new it will return False

            Args:
            - layer: object of type Layer

            Returns:
            True if successful
            False if unsuccessful
            """
        if self.current_layer == layer:
            return False
        else:
            self.current_layer = layer
            return True

    def erase(self, layer: Layer) -> bool:
        """
            Sets current_layer to None

            Args:
            - layer: object of type Layer (is ignored)

            Returns:
            True if successful
            False if unsuccessful
            """
        if self.current_layer is None:
            return False
        else:
            self.current_layer = None
            return True

    def special(self):
        """
        Switches the INSTANCE variable flag between True and False
        No return value
        """

        if self.special_flag:
            self.special_flag = False
        else:
            self.special_flag = True

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        returns the color from a particular layer. Taking special into consideration.

        Args:
            - start: tuple of three integers
            - timestamp
            - x: integer
            - y: integer

        Returns:
            tuple of three integers, representing the resulting colour
        """

        if self.current_layer is None:  # returning the start input value if current layer is None
            return_value = start
        else:  # returning the valid color otherwise
            return_value = self.current_layer.apply(start, timestamp, x, y)
        if self.special_flag:  # inverts the color if special is on
            return invert.apply(return_value, timestamp, x, y)
        else:
            return return_value


class AdditiveLayerStore(LayerStore):
    """
    Additive layer store. Each added layer applies after all previous ones.
    - add: Add a new layer to be added last.
    - erase: Remove the first layer that was added. Ignore what is currently selected.
    - special: Reverse the order of current layers (first becomes last, etc.)

    All methods written in this class have best and worst case complexity of O(1), unless stated otherwise
    """
    MAX_CAPACITY = 100*9  # as per requirement, 'capacity of the store at least 100 times the number of layers [9].'

    def __init__(self):  # Initialising new instances with a current layer as None
        """
        Creates class instance, with self.current_layers as a Queue of length MAX_CAPACITY
        """
        self.current_layers = CircularQueue(self.MAX_CAPACITY)

    def add(self, layer: Layer) -> bool:
        """
            Appends layer to current layers and returns True. If self.current_layers is full it will return False

            Args:
            - layer: object of type Layer

            Returns:
            True if successful
            False if unsuccessful
        """

        if self.current_layers.is_full():
            return False
        else:
            self.current_layers.append(layer)
            return True

    def erase(self, layer: Layer) -> bool:
        """
            Erases the oldest layer by serving it.

            Args:
            - layer: object of type Layer (is ignored)

            Returns:
            False if empty,
            True otherwise
        """
        if self.current_layers.is_empty():
            return False
        else:
            self.current_layers.serve()
            return True

    def special(self):
        """
            Reverses the order of the layers

            Complexity:
            Best case O(1): self.current_layers is empty
            Worst case O(n) where n is the length of self.current_layers
        """
        if self.current_layers.is_empty():
            return
        # Creating temporary stack
        temp_stack = ArrayStack(self.MAX_CAPACITY)
        # emptying self.current_layers into a temporary stack
        for i in range(len(self.current_layers)):
            layer = self.current_layers.serve()
            temp_stack.push(layer)
        # returning the layers into self.current_layers, reversing the order
        for i in range(len(temp_stack)):
            layer = temp_stack.pop()
            self.current_layers.append(layer)

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        """
        returns the color from a particular layer store instance.

        Args:
            - start: tuple of three integers
            - timestamp
            - x: integer
            - y: integer

        Returns:
            tuple of three integers, representing the resulting colour

        Complexity:
            Best case O(1): self.current_layers is empty
            Worst case O(n) where n is the length of self.current_layers
        """
        # initialising return value
        return_value = start
        if self.current_layers.is_empty():
            return return_value
        # running the return value through all the layers
        for i in range(len(self.current_layers)):
            layer = self.current_layers.serve()
            return_value = layer.apply(return_value, timestamp, x, y)
            self.current_layers.append(layer)

        return return_value


class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.

    All methods written in this class have best and worst case complexity of O(1), unless stated otherwise
    """

    MAX_CAPACITY = 1000  # as required in assignment instructions
    NUMBER_OF_LAYERS = len(get_layers())-1

    def __init__(self):
        """
        Each class instance holds an array sorted list to sort layers lexicographically by name and
        a bitvector set to hold the layers by index
        """
        self.current_layers_name = ArraySortedList(self.MAX_CAPACITY)
        self.current_layers_index = BSet(self.NUMBER_OF_LAYERS)

    def add(self, layer: Layer) -> bool:
        """
            Turns on layer in layer store instance

            Args:
            - layer: object of type Layer

            Returns:
            True if successful
            False if unsuccessful
        """
        list_layer_name = ListItem(layer, layer.name)  # List item with name key for layer

        # checking that there is space and the layer does not already exist
        if self.current_layers_name.is_full() or list_layer_name in self.current_layers_name:
            return False
        else:
            # adding the layer to the name array
            self.current_layers_name.add(list_layer_name)
            # adding the layer to the index array
            list_layer_index = layer.index
            self.current_layers_index.add(list_layer_index+1)
            return True

    def erase(self, layer: Layer) -> bool:
        # checking the that there are layers to delete
        if self.current_layers_name.is_empty() or layer.index not in self.current_layers_index:
            return False
        else:
            list_layer_name = ListItem(layer, layer.name)  # layer item (name) to be deleted
            self.current_layers_name.remove(list_layer_name)

            list_layer_index = layer.index # layer index to delete
            self.current_layers_index.remove(list_layer_index+1)
            return True

    def special(self):
        # checking the that there are layers to delete
        if self.current_layers_name.is_empty():
            return
        # working out the smaller median
        lexicographically_smaller_median = (len(self.current_layers_index) - 1) // 2
        # removing the aforementioned median from the name array, retrieving the layer (name) item
        layer_item_name = self.current_layers_name.delete_at_index(lexicographically_smaller_median)
        # creating the layer (index) item
        layer_item_index = layer_item_name.value.index
        # removing the layer item from the layer (index) Bset
        self.current_layers_index.remove(layer_item_index+1)

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        # returning starting color if grid is empty
        if self.current_layers_index.is_empty():
            return start
        return_value = start
        # applying all the layers, in order of index
        for i in range(self.NUMBER_OF_LAYERS):
            if i+1 in self.current_layers_index:
                layer = get_layers()[i]
                return_value = layer.apply(return_value, timestamp, x, y)
        return return_value