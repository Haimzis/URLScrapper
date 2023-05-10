# URL Scraping in BFS Manner

The URL Scraping in BFS Manner project is a Python-based web scraping application that extracts information from web pages in a breadth-first search (BFS) manner. It utilizes concurrent execution and database storage to efficiently scrape and classify web pages based on their topics.

## Features

- Scrapes web pages in a BFS manner, exploring links at each level before moving to the next depth level.
- Extracts page features such as links, title, metadata, and text content.
- Cleans and processes the extracted features for further analysis.
- Classifies the topic of each page using a pre-trained transformer model.
- Stores the scraped results in a SQLite database for later analysis.
- Supports checkpoint-based restoration to resume scraping from the last saved state.
- Utilizes concurrent execution for faster scraping using multithreading.
- Provides a Dockerfile for easy containerization and deployment.

## How to Use

1. Clone the repository to your local machine.
2. Install the project dependencies by running the following command:

   ```
   pip install -r requirements.txt
   ```

3. Create a SQLite database and configure its connection details in the `config.py` file.
4. Specify the desired model name, type, candidates labels, and other configuration parameters in the `config.py` file.
5. Run the application using the following command:

   ```
   python main.py --url <initial_url> --max-depth <max_depth>
   ```

   Replace `<initial_url>` with the starting URL for scraping, and `<max_depth>` with the maximum depth (the number of levels to scrape).
   
6. The application will initiate the web scraping process, extracting features, classifying topics, and storing the results in the specified SQLite database.

## Docker

Alternatively, you can use Docker to containerize and run the application. The repository includes a Dockerfile that sets up the necessary environment.

To use Docker:

1. Install Docker on your machine.
2. Build the Docker image using the following command:

   ```
   docker build -t url-scraper .
   ```

3. Run the application inside a Docker container:

   ```
   docker run -it url-scraper --url <initial_url> --max-depth <max_depth>
   ```

   Replace `<initial_url>` with the starting URL for scraping, and `<max_depth>` with the maximum depth (the number of levels to scrape).

Please refer to the code comments and configuration files for more detailed information on the project's functionality and customization options.