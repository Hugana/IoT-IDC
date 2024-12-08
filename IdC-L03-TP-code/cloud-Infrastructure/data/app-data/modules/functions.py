import pandas as pd
import numpy as np
 


def predict(X, model):
    prediction = model.predict(X)[0]
    return prediction


def get_model_response(json_data, model):
    X = pd.DataFrame.from_dict(json_data)
    obj = predict(X, model)
    
    if isinstance(obj, (np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):

            prediction = int(obj)
            
    elif isinstance(obj, (np.float16, np.float32, np.float64)):
            prediction = float(obj)

    elif isinstance(obj, (np.ndarray,)):
            prediction = obj.tolist()

    elif isinstance(obj, (np.bool_)):
            prediction = bool(obj)

    elif isinstance(obj, (np.void)): 
            prediction = None
            
    else:
            prediction = obj
    
    return {
        'status': 200,
        'prediction': prediction
    }
