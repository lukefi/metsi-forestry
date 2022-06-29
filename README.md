# Forestry function library

Forestry function library (ffl) is a container for forestry functions used to manipulate forest stand states of forest data model.

The structure of the library is as follows:
```
forestryfunctions/
    harvest/
        thinning.py
    naturalprocess/
        grow_acta.py
    postprocessing/
        bucking.py
```

### Simulation and model functions

In order to perform a change in state. A state manipulation call is performed. The single call comprises of what is called a simulation and model functions.

From the image under one may understand the main differences in responsibilities, inputs and outputs of these two functions.


![Function division](doc/simulator-and-model-function.drawio.png)


The simulation function manipulates the actual data model holding the state. This is typically a model entity like ForestStand from the forest-data-model library. The model function is a computation function operating on primitive values which the simulation function than uses to define a new state and/or generating the aggregate structure.

Something to keep in mind is that:
1) Simulation function has to always return a state, manipulated or not.
2) Collecting aggregates between changes in old and new state is optional.
