import pytest
from src.target import my_function

@pytest.fixture
def sample_data():
    return {"key": "value"}

@pytest.mark.parametrize("input_val, expected", [
    (1, 2),
    (0, 0),
    (-1, -2),
])
def test_my_function_valid_input_returns_expected(input_val, expected):
    # Arrange
    
    # Act
    result = my_function(input_val)
    
    # Assert
    assert result == expected

def test_my_function_invalid_input_raises_error():
    # Arrange
    invalid_input = None
    
    # Act & Assert
    with pytest.raises(ValueError):
        my_function(invalid_input)
