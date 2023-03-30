from __future__ import annotations
from abc import ABC, abstractmethod

from data_structures.stack_adt import ArrayStack
from data_structures.queue_adt import CircularQueue
from data_structures.array_sorted_list import ArraySortedList
from data_structures.sorted_list_adt import ListItem
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

    def __init__(self):  # Initialising new instances with a current layer as None
        self.current_layer = None
        # Boolean INSTANCE variable signalling if 'special' is active or not
        self.special_flag = False

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

    def special(self):  # Switches the INSTANCE variable flag between True and False
        if self.special_flag:
            self.special_flag = False
        else:
            self.special_flag = True

    # returns the color from a particular layer. Taking special into consideration.
    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:

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
    """

    def __init__(self):  # Initialising new instances with a current layer as None
        # creating a stack with sufficient capacity ( > 9*100 )
        self.current_layers = ArrayStack(10)

    def add(self, layer: Layer) -> bool:
        if self.current_layers.is_full():
            return False
        else:
            self.current_layers.push(layer)
            return True

    '''
    erase function empties the stack into a temporary stack, removes the top (oldest) layer
    then returns to the original stack.
    |d|   |a|   | |   | |
    |c|   |b|   |b|   |d|
    |b|-> |c|-> |c|-> |c|
    |a|   |d|   |d|   |b|
    O(n) complexity, where n is the number of layers in self.current_layers
    O(1) best case scenario if self.current_layers is empty
    '''

    def erase(self, layer: Layer) -> bool:
        if self.current_layers.is_empty():
            return False
        else:
            # extracting all layers into a temporary stack, emptying self.current_layers
            temp_stack = ArrayStack(10)
            for i in range(len(self.current_layers)):
                layer = self.current_layers.pop()
                temp_stack.push(layer)
            temp_stack.pop()  # removing last layer (on top of temp stack)
            # return the layers to self.current_layers
            for i in range(len(temp_stack)):
                layer = temp_stack.pop()
                self.current_layers.push(layer)
            return True

    '''
    special empties the self.current_layers stack into a queue. 
    It then serves the queue back into the stack. 
    This results in the order being reversed. 
    Complexity O(n), where n is the number of layers in self.current_layers 
    O(1) best case scenario if self.current_layers is empty
    '''

    def special(self):
        temp_queue = CircularQueue(10)
        # emptying self.current_layers into a temporary queue
        for i in range(len(self.current_layers)):
            layer = self.current_layers.pop()
            temp_queue.append(layer)
        # returning the layers into self.current_layers, reversing the order
        for i in range(len(temp_queue)):
            layer = temp_queue.serve()
            self.current_layers.push(layer)

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        # extracting all layers into a temporary stack, emptying self.current_layers
        temp_stack = ArrayStack(10)
        if self.current_layers.is_empty():
            return start
        for i in range(len(self.current_layers)):
            layer = self.current_layers.pop()
            temp_stack.push(layer)
        # initialising return value
        return_value = start
        # running return value through all layers (from oldest to youngest)
        # then returning the layer to current_layers
        for i in range(len(temp_stack)):
            layer = temp_stack.pop()
            return_value = layer.apply(return_value, timestamp, x, y)
            self.current_layers.push(layer)
        return return_value


class SequenceLayerStore(LayerStore):
    """
    Sequential layer store. Each layer type is either applied / not applied, and is applied in order of index.
    - add: Ensure this layer type is applied.
    - erase: Ensure this layer type is not applied.
    - special:
        Of all currently applied layers, remove the one with median `name`.
        In the event of two layers being the median names, pick the lexicographically smaller one.
    """

    #  Each class instance holds two array sorted lists:
    #  one to hold the layers lexicographically by name and one by index
    def __init__(self):
        self.current_layers_name = ArraySortedList(1000)
        self.current_layers_index = ArraySortedList(1000)
        self.length = 0

    def add(self, layer: Layer) -> bool:
        list_layer_name = ListItem(layer, layer.name)  # List item with name key for layer

        # checking that there is space and the layer does not already exist
        if self.current_layers_name.is_full() or list_layer_name in self.current_layers_name:
            return False
        else:
            # adding the layer to the name array
            self.current_layers_name.add(list_layer_name)
            # adding the layer to the index array
            list_layer_index = ListItem(layer, layer.index)
            self.current_layers_index.add(list_layer_index)
            # incrementing the length
            self.length += 1
            return True

    def erase(self, layer: Layer) -> bool:
        # checking the that there are layers to delete
        if self.current_layers_name.is_empty():
            return False
        else:
            list_layer_name = ListItem(layer, layer.name)  # layer item (name) to be deleted
            self.current_layers_name.remove(list_layer_name)

            list_layer_index = ListItem(layer, layer.index)  # layer item (index) to be deleted
            self.current_layers_index.remove(list_layer_index)
            # decrementing the length
            self.length -= 1
            return True

    def special(self):
        # checking the that there are layers to delete
        if self.current_layers_name.is_empty():
            return
        # working out the smaller median
        lexicographically_smaller_median = (self.length - 1) // 2
        # removing the aforementioned median from the name array, retrieving the layer (name) item
        layer_item_name = self.current_layers_name.delete_at_index(lexicographically_smaller_median)
        # creating the layer (index) item
        layer_item_index = ListItem(layer_item_name.value, layer_item_name.value.index)
        # removing the layer item from the layer (index) array
        self.current_layers_index.remove(layer_item_index)
        # decrementing the length
        self.length -= 1

    def get_color(self, start, timestamp, x, y) -> tuple[int, int, int]:
        # returning starting color if grid is empty
        if self.current_layers_index.is_empty():
            return start
        return_value = start
        # applying all the layers, in order of index
        for i in range(self.length):
            return_value = self.current_layers_index[i].value.apply(return_value, timestamp, x, y)
        return return_value
