import re
from joblib import load
model = load("./exported_model.joblib")

def is_correctly_formatted(input_str):
    """
    Checks if the input string is correctly formatted.

    Correct format:
    - Contains a `#`.
    - Characters before `#` must be 3-16 characters (any character).
    - Characters after `#` must be 3-5 characters (any character).

    Args:
        input_str (str): The string to validate.

    Returns:
        bool: True if the input string is correctly formatted, False otherwise.
    """
    # Define the regular expression pattern
    pattern = r'^.{3,16}#.{3,5}$'
    # Use re.fullmatch to check if the string matches the pattern
    return bool(re.fullmatch(pattern, input_str))

def predict_game(features):
    """
    Predict the outcome using the loaded model.
    Args:
        features (list): A list or numpy array of input features.
    Returns:
        bool: The model's prediction.
    """
    
    prediction = model.predict(features)
    return prediction