## Quantum Gates Educational Card Game

This is a simple two-player card game that illustrates the functionality of basic single and two-qubit quantum gates. After playing this game, one will have developed a foundation for building quantum circuits and an interest in learning about more complex gates and quantum algorithms.

To play the game, follow the instructions [here](https://docs.microsoft.com/en-us/quantum/quickstarts/install-jupyter) to create and activate a conda environment with the packages required to develop in Q#. 

Then, run all the code cells in `SimpleCardGamePython.ipynb`.

## Rules:

- Both players begin with 50 points

- There are two qubits in the center, which both start off in the state (1 + 0i)|0> + (0 + 0i)|1>

- Players take turns applying 2 operations (each card represents a gate, control, or SWAP operation) to the qubits at a time

    - Gates may be single or two-qubit gates, which allows players to learn about entanglement

- If both qubits are measured to be 1, then the player gets a point, else if both qubits are measured to be 0, the player loses a point, otherwise the player neither gains nor loses any points

    - There is an element of probability because the qubits may be in a superposition of states. In this way, players will gain practice with amplitudes, since they must maximize the coefficient of the state which they want to measure (|1>)

- The next player applies operations to the qubits in the non-collapsed state to which the previous player brought the qubits

- The game ends when a player loses by hitting 0 points or a player wins by hitting 100 points