import numpy as np
import pandas as pd


doe = pd.read_csv('../data/doe.csv')

data = pd.read_csv('../data/projection.csv')
data.drop(data[data.doe_id == 1000].index, inplace=True)
data.drop(data[data.doe_id == 247].index, inplace=True)


from mesh_predictor import ProjectionPredictor

reg = ProjectionPredictor()

reg.load_data(
    doe = doe,
    data = data,
    index='doe_id',
    process_parameters = [
        'Blechdicke', 
        'Niederhalterkraft', 
        'Ziehspalt', 
        'Einlegeposition', 
        'Ziehtiefe',
        'Rp0',
    ],
    categorical = [
        'Ziehspalt', 
        'Ziehtiefe',
    ],
    position = ['xp', 'yp'],
    output = ['deviation', 'thickness'],
    validation_split=0.1,
    validation_method='leaveoneout',
    position_scaler='minmax'
)

reg.save_config("../models/projection.pkl")

best_config = reg.autotune(
    save_path='../models/best_projection_model',
    trials=100,
    max_epochs=50, 
    layers=[4, 6],
    neurons=[64, 256, 64],
    dropout=[0.0, 0.5, 0.1],
    learning_rate=[1e-5, 1e-3]
)
print(best_config)


reg.save_h5("../models/projection.h5")
