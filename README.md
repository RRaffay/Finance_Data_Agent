# Finance Agent

This is a Flask application designed to aid knowledge workers in the finance industry. It provides a platform for uploading and analyzing financial documents, as well as asking questions about the data. The application is designed to be extensible and can be customized to suit the needs of different organizations. The application is currently in development and is not yet ready for production use. Current capabilities include:

- Uploading financial documents for analysis.
- Viewing example analysis data.
- Asking questions about the data
- Generating charts and graphs based on the data. (Requires refinement)

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Routes](#routes)
- [Configuration](#configuration)
- [License](#license)

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/RRaffay/Finance_Data_Agent
   cd Finance_Data_Agent
   ```

2. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Set up the environment variables:

   ```sh
   cp flask_app/.env.example flask_app/.env
   ```

2. Run the application:

   ```sh
   cd flask_app
   flask run
   ```

3. Open your browser and navigate to `http://127.0.0.1:5000`.

## Routes

- `/` - Renders the main index page.
- `/upload` - Handles file uploads and processes the uploaded files.
- `/ask` - Endpoint for asking questions (implementation needed).
- `/images` - Serves uploaded images.
- `/images/<filename>` - Serves a specific uploaded image.
- `/example` - Provides example analysis data.

## Configuration

The application configuration is managed in the [`Config`](flask_app/config.py) class. You can modify the configuration settings as needed.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
