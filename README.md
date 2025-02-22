
# Steam Game Review Summarizer

A Flask web application that fetches reviews for a given Steam game (by name), summarizes the reviews using the Facebook BART model, and displays a concise bullet-point summary on a stylish web page.

## Overview

This project does the following:
- Looks up the Steam app ID by game name by scraping the Steam search page.
- Retrieves a specified number of reviews from the Steam Reviews API.
- Cleans and preprocesses the review texts.
- Summarizes the reviews into a short bullet-point summary using a transformer model.
- Displays the summary on a web interface with a clean, responsive design.
- Prints debug information (e.g., token counts and the summary) to the terminal.

## Folder Structure


review_summaries/
├── app/
│   ├── __init__.py         # Initializes the Flask app and imports routes
│   ├── routes.py           # Contains Flask view functions (web routes)
│   ├── summarizer.py       # Functions to fetch reviews and generate summaries
│   └── utils.py            # Utility functions (e.g., text cleaning)
├── static/
│   └── style.css           # CSS file for styling the web page
├── templates/
│   └── index.html          # (Optional) HTML template (if not using inline templates)
├── tests/
│   └── test_app.py         # Test suite for unit and integration tests
├── run.py                  # Entry point to run the Flask application
├── run.sh                  # Shell script to create virtual environment, install dependencies, and run the app
├── requirements.txt        # List of required Python packages
└── README.md               # Project documentation



## Installation and Running the Application

A shell script is provided to simplify the setup and running process.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/redmondoisin/steam_review_summaries
   ```

2. **Make the shell script executable (if not already):**
   ```bash
   chmod +x run.sh
   ```

3. **Run the shell script:**
   ```bash
   ./run.sh
   ```
   This script will:
   - Create a virtual environment (if one doesn't exist)
   - Activate the virtual environment
   - Upgrade pip
   - Install the required packages from `requirements.txt`
   - Start the Flask application (by running `run.py`)

4. **Access the application:**
   Open your web browser and navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/) to use the app.

## Running Tests

The project includes tests that cover:
- Utility functions (e.g., text cleaning)
- Review fetching and summarization logic
- Integration tests for live data (marked with `@pytest.mark.integration`)
- Flask route functionality using the Flask test client

To run the tests, ensure you have pytest installed (it should be in your requirements, or install via `pip install pytest`), then execute:

```bash
pytest --maxfail=1 --disable-warnings -q
```

## Notes

- **API Rate Limiting:**  
  The Steam API is rate-limited, so the code uses a delay between requests to avoid hitting rate limits.

- **Model Loading:**  
  The summarization step uses the Facebook BART model. The first run might be slow as the model downloads and loads into memory.

- **Debugging:**  
  Debug information such as token counts and the final summary are printed to the terminal to help diagnose any issues.

- **Styling:**  
  The application uses CSS (in `static/style.css`) for a clean and responsive design.

## License

This project is licensed under the MIT License.