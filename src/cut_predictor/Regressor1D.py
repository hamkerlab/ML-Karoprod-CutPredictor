import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .Predictor import Predictor
from .Utils import one_hot

class CutPredictor(Predictor):
    """
    Regression method to predict 1D cuts from process parameters.

    Derives from Predictor, where more useful methods are defined.
    """
        
    def load_data(self, doe, data, process_parameters, position, output, categorical=[], angle=False, index='doe_id'):
        """
        Loads pandas Dataframes containing the data and preprocesses it.

        :param doe: pandas.Dataframe object containing the process parameters (design of experiments table).
        :param data: pandas.Dataframe object containing the experiments.
        :param process_parameters: list of process parameters ti be used. The names must match the columns of the csv file.
        :param categorical: list of process parameters that should be considered as categorical nad one-hot encoded.
        :param position: position variable. The name must match one column of the csv file.
        :param output: output variable(s) to be predicted. The name must match one column of the csv file.
        :param angle: if the position parameter is an angle, its sine and cosine are used as inputs instead.
        :param index: name of the column in doe and data representing the design ID (default: 'doe_id')
        """

        self.has_config = True
        self.data_loaded = True

        # Attributes names
        self.process_parameters = process_parameters
        
        if isinstance(position, list):
            self.position_attributes = position
        else:
            self.position_attributes = [position]
        
        if isinstance(output, list): 
            self.output_attributes = output
        else:
            self.output_attributes = [output]
        
        self.categorical_attributes = categorical
        self.angle_input = angle
        self.doe_id = index

        # Process parameters
        self._preprocess_parameters(doe)

        # Expand the process parameters in the main df
        self._preprocess_variables(data)

        # Get numpy arrays
        self._make_arrays()



    def predict(self, process_parameters, positions):
        """
        Predicts the output variable for a given number of input positions (uniformly distributed between the min/max values used for training).

        :param process_parameters: dictionary containing the value of all process parameters.
        :param positions: number of input positions to be used for the prediction.
        :return: (x, y) where x is an array of 1D positions and y the corresponding value of each output attribute.
        """

        if not self.has_config:
            print("Error: The data has not been loaded yet.")
            return

        if self.model is None:
            print("Error: no model has been trained yet.")
            return

        X = np.empty((positions, 0))

        for idx, attr in enumerate(self.process_parameters):

            if attr in self.categorical_attributes:
                
                code = one_hot([process_parameters[attr]], self.categorical_values[attr])
                code = np.repeat(code, positions, axis=0)
                
                X = np.concatenate((X, code), axis=1)

            else:

                val = ((process_parameters[attr] - self.mean_values[attr] ) / self.std_values[attr]) * np.ones((positions, 1))

                X = np.concatenate((X, val ), axis=1)

        # Position attribute is last
        for attr in self.position_attributes:
            position = np.linspace(self.min_values[attr], self.max_values[attr], positions)

            if not self.angle_input:

                values = (position.reshape((positions, 1)) - self.mean_values[attr] ) / self.std_values[attr]
                X = np.concatenate((X, values), axis=1)

            else:

                X = np.concatenate(
                    (X, np.cos(position).reshape((positions, 1)) ), 
                    axis=1
                )
                X = np.concatenate(
                    (X, np.sin(position).reshape((positions, 1)) ), 
                    axis=1
                )

        y = self.model.predict(X, batch_size=self.batch_size).reshape((positions, len(self.output_attributes)))

        for idx, attr in enumerate(self.output_attributes):
            y[:, idx] = self._rescale_output(attr, y[:, idx])

        return position, y


    def _compare(self, doe_id):

        if self.model is None:
            print("Error: no model has been trained yet.")
            return

        if not doe_id in self.doe_ids:
            print("The experiment", doe_id, 'is not in the dataset.')
            return

        indices = self.df_raw[self.df_raw[self.doe_id]==doe_id].index.to_numpy()
        
        N = len(indices)
        X = self.X[indices]
        t = self.target[indices]
        for idx, attr in enumerate(self.output_attributes):
            t[:, idx] = self._rescale_output(attr, t[:, idx])


        for attr in self.position_attributes:
            position = self.mean_values[attr] +  self.std_values[attr] * X[:, -1] # position is the last index

        y = self.model.predict(X, batch_size=self.batch_size)

        for idx, attr in enumerate(self.output_attributes):
            y[:, idx] = self._rescale_output(attr, y[:, idx])

        for idx, attr in enumerate(self.output_attributes):
            plt.figure()
            plt.plot(position, y[:, idx], label="prediction")
            plt.plot(position, t[:, idx], label="data")
            plt.xlabel(self.position_attributes[0])
            plt.ylabel(attr)
            plt.ylim((self.min_values[attr], self.max_values[attr]))
            plt.legend()
