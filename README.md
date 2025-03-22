
# RVC Inference GUI

RVC Inference GUI is a user-friendly graphical interface designed to facilitate inference using Retrieval based Voice  Conversion (RVC) models. This tool simplifies the process of voice conversion by providing an intuitive platform for users to interact with RVC models without delving into complex command-line operations.

## Features

- **User-Friendly Interface:** Easily navigate and operate RVC models through a graphical interface.
- **Model Management:** Seamlessly add, remove, and switch between different RVC models.
- **Easy Conversion:** Perform voice conversion tasks efficiently with easy Settings.
- **Output Management:** Access and manage converted audio files directly within the application.

## Prerequisites

Before setting up the RVC Inference GUI, ensure you have the following installed:

- **Python 3.8 or higher:** [Download Python](https://www.python.org/downloads/)
- **Pip:** Python package installer, typically included with Python installations.
- **Git:** Version control system to clone the repository. [Download Git](https://git-scm.com/downloads)

## Installation

Follow these steps to set up the RVC Inference GUI:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/onxlmao/rvc_inference.git
   ```

2. **Navigate to the Project Directory:**

   ```bash
   cd rvc_inference
   ```

3. **Install Dependencies:**

   It's recommended to use a virtual environment to manage dependencies:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use 'env\Scripts\activate'
   ```

   Then, install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Download RVC Models:**

   Place your RVC models in the `rvc_models` directory. Ensure they are in the correct format as specified by the RVC framework.

5. **Run the Application:**

   ```bash
   python webui.py
   ```

   The application should open in your default web browser. If it doesn't, navigate to `http://localhost:5000` manually.

## Usage

1. **Load a Model:**  
   In the GUI, navigate to the "Models" section and select the desired RVC model from the list. If your model isn't listed, ensure it's placed in the `rvc_models` directory and refresh the list.

2. **Input Audio:**  
   Upload the audio file you wish to convert using the "Upload" button. Supported formats include WAV and MP3.

3. **Configure Settings:**  
   Adjust any conversion parameters as needed. Refer to the RVC documentation for detailed explanations of each parameter.

4. **Perform Conversion:**  
   Click the "Convert" button to initiate the voice conversion process. The converted audio will be available in the "Output" section upon completion.

5. **Manage Outputs:**  
   Access and download your converted files from the "Outputs" section. Files are stored in the `song_output` directory by default.


## Contributing

Contributions are welcome! 
Please fork the repository and submit a pull request with your enhancements or bug fixes.
Ensure your code adheres to the project's coding standards and includes appropriate documentation.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

Special thanks to the developers and contributors of the RVC framework for their foundational work in voice conversion technologies.
