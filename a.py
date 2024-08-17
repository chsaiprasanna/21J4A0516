from flask import Flask, request, jsonify
import requests
from collections import deque

app = Flask(__name__)

# Settings
WINDOW_SIZE = 10
THIRD_PARTY_API_URL = 'http://localhost:9876/numbers/e'  # Replace with the actual API endpoint
REQUEST_TIMEOUT = 0.5  # 500 milliseconds

# In-memory number storage
number_storage = deque(maxlen=WINDOW_SIZE)

def retrieve_number(identifier):
    """Fetch a number from the third-party API using the provided identifier."""
    api_endpoint = f"{THIRD_PARTY_API_URL}/numbers/{identifier}"
    try:
        response = requests.get(api_endpoint, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json().get('number')
    except (requests.RequestException, ValueError):
        return None

def compute_average(numbers_list):
    """Compute the average value of the given list of numbers."""
    if not numbers_list:
        return 0
    return sum(numbers_list) / len(numbers_list)

@app.route('/numbers/<identifier>', methods=['GET'])
def handle_request(identifier):
    """Process GET request to fetch and handle a number based on identifier."""
    number = retrieve_number(identifier)
    
    if number is not None:
        if number not in number_storage:
            if len(number_storage) == WINDOW_SIZE:
                number_storage.popleft()  # Remove the oldest number if the window is full
            number_storage.append(number)
    
    # Prepare and send the response
    current_numbers = list(number_storage)
    avg = compute_average(current_numbers)
    
    response = {
        'numbers_before': current_numbers[:-1] if number is not None else current_numbers,
        'numbers_after': current_numbers,
        'average': avg
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
