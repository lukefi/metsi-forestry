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


## Forestry functions
### Cross cutting

The entry point for cross cutting a tree is the `cross_cut` function in `cross_cutting/cross_cutting.py`. It implements the Annika Kangas' cross cutting algorithm originally written in R. The original R scripts are stored in `tests/resources/cross_cutting`, and the test at `tests\cross_cutting_test.py::CrossCuttingTest::test_py_implementation_equals_r_implementation` uses these scripts to ensure that the python implementation follows the original R implementation.

However, the implementation depends on the `breast_height_diameter` argument being a positive real number. Therefore, the `cross_cut` function treats trees whose `breast_height_diameter` is `0` or `None` as energy wood (timber grade = 3), and 
returns a hardcoded volume and value.


