import numpy as np
from flask import Flask, jsonify
import time
import sys

app = Flask(__name__)

class NeuralNetwork():

    def __init__(self,dim):
        self.inputdim = dim
        self.synaptic_weights = 2*np.random.random((dim,1)) - 1
        print("Neuron created.")
        print(f'Assigned random synaptic weights: \n {self.synaptic_weights}')

    def reset(self, newdim):
        self.inputdim = newdim
        self.synaptic_weights = 2 * np.random.random((newdim, 1)) - 1
        print("Neuron reset.")
        print(f'New random synaptic weights: \n {self.synaptic_weights}')

    def sigmoid(self,x):
        return 1/(1+np.exp(-x))

    def sigmoid_derivative(self,x):
        return x*(1-x)

    def train(self, training_inputs, training_outputs, training_iterations):

        for iteration in range(training_iterations):
            output = self.think(training_inputs)
            error = training_outputs - output
            adjustments = np.dot(training_inputs.T, error * self.sigmoid_derivative(output))
            self.synaptic_weights += adjustments
        print(f"Training completed. Current synaptic weights: \n {self.synaptic_weights} ")

    def think(self, inputs):
        inputs = inputs.astype(float)
        output = self.sigmoid(np.dot(inputs,self.synaptic_weights))
        return output

    def quiz(self):
        print("Questioning begins!")
        running = True
        while running:
            inputs = []
            for i in range(self.inputdim):
                data = input(f'Enter input {i+1}: ')
                inputs.append(int(data))
            print(f"Input data => {inputs}")
            print(f"Output data => {self.think(np.array(inputs))}")
            confirm = str(input("Continue? y/n: "))
            running = True if confirm.upper() == "Y" else False
        print("Questioning over.")

@app.route('/')
def train_neuro_network():
    neural_network = NeuralNetwork(4)
    # The ith entry of the training_outputs is the
    # answer of the ith row of the training_inputs
    # Rules: No more than 2 zeros
    training_inputs = np.array([[0,0,1,1],
                                [0,1,0,0],
                                [0,0,0,1],
                                [1,1,1,1],
                                [0,1,1,0],
                                [0,0,1,0],
                                [1,0,0,0]])
    training_outputs = np.array([[1, 0, 0, 1, 1, 0, 0]]).T
    start = time.time()
    neural_network.train(training_inputs, training_outputs,1000000)
    end = time.time()
    if len(sys.argv) < 2:
        return jsonify({"response" : "Something went wrong"})
    return jsonify({"response": "Training time: " + str(end - start) + "seconds"})

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5020)