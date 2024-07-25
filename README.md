# Inquisitive Streamlit App
*Inquisitive Input Screen*
![Inquisitive Input Screen](https://github.com/NaveenDeveloperR/inquisitive-streamlit-app/blob/main/images/user_input.png)

*Inquisitive Response Screen*
![Inquisitive Response Screen](https://github.com/NaveenDeveloperR/inquisitive-streamlit-app/blob/main/images/output.png)


## Overview

**Inquisitive** is a Streamlit application designed to facilitate question generation using Google Generative AI and language detection. It serves as a valuable tool for educators, content creators, and anyone seeking to enrich text content with relevant questions.

## Features

- **Language Detection**: Automatically identifies the language of input text.
- **Text Translation**: Translates non-English text into English for processing.
- **Question Generation**: Utilizes Google Generative AI to create questions based on the input text.
- **Multi-Language Support**: Ensures generated questions can be translated back to the original language.

## Installation

To run this project locally, follow these steps:

### Prerequisites

Make sure you have the following installed:

- Python 3.8 or higher
- Git

### Clone the Repository

```sh
git clone https://github.com/NaveenDeveloperR/inquisitive-streamlit-app.git
cd inquisitive-streamlit-app
```

### Set Up the Virtual Environment

It's recommended to use a virtual environment to manage dependencies. Run the following commands:

```sh
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### Install Dependencies

Install the required Python packages using pip:

```sh
pip install -r requirements.txt
```

## Usage

To launch the Inquisitive Streamlit app, execute the following command:

```sh
streamlit run app.py
```

## Configuration

Before running the app, ensure you have your Google Generative AI API key ready. Configure the API key in your `app.py` file:

```python
palm.configure(api_key="YOUR_API_KEY_HERE")
```

## File Structure

Here's the basic structure of the project directory:

```
inquisitive-streamlit-app/
├── app.py
├── requirements.txt
├── README.md
└── images/
    ├── user_input.png
    └── output.png
```

## Contributing

We welcome contributions to enhance the Inquisitive app. To contribute, follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request on GitHub.

## License

This project is licensed under the MIT License. 


