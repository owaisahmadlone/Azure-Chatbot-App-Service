# Azure-Chatbot-App-Service

This repository is dedicated to the development of a cloud-based QnA Chatbot using Milvus as a vector database. The chatbot is deployed as an app service on Microsoft Azure, utilizing FastAPI to create a seamless interface for users to interact with the chatbot.

## Overview

The Azure-Chatbot-App-Service is designed to handle and respond to user queries by leveraging the Retrieval-Augmented Generation (RAG) pipeline. Milvus serves as the vector database, storing embeddings that allow the chatbot to retrieve and process information efficiently. The system is suitable for various applications, including customer support and information retrieval.

## Features

- **QnA Chatbot**: Built for answering questions accurately using a RAG pipeline.
- **Vector Database**: Utilizes Milvus for high-performance similarity searches.
- **FastAPI**: Provides a quick and efficient API for handling user requests and returning responses.
- **Azure App Service**: Easily deployable on Azure, making it accessible as a cloud-based solution.
- **Scalable and Modular Design**: Built to be scalable and easy to modify for specific needs.

## Repository Structure

- **configuration_guide.ipynb**: A Jupyter notebook guide detailing how to configure the project, especially focusing on setting up the connection to Milvus.
- **main.py**: The main entry point for running the FastAPI app, handling user requests and routing them to the appropriate services.
- **models.py**: Contains definitions and setups for the machine learning models used in the chatbot, particularly embedding models for the RAG pipeline.
- **modules.py**: Additional helper functions and modules that support the main application, such as database connectors and utility functions.
- **requirements.txt**: Lists all the dependencies needed to run the project, making it easier to install them with `pip`.
- **startup.sh**: A shell script to start the application and initialize necessary services.

## Getting Started

### Prerequisites

- **Python 3.8 or higher**: Make sure Python is installed on your machine.
- **Azure Account**: To deploy the chatbot as an Azure App Service.
- **Milvus**: A vector database that needs to be set up either locally or in a cloud environment.
- **FastAPI**: This can be installed using the requirements file.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Azure-Chatbot-App-Service.git
   cd Azure-Chatbot-App-Service
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Milvus:
   - Refer to `configuration_guide.ipynb` for detailed instructions on setting up and connecting Milvus with this application.
   
4. Run the application:
   ```bash
   ./startup.sh
   ```

### Deployment on Azure

1. Set up an Azure App Service instance.
2. Configure the app to use Milvus as the backend vector database.
3. Deploy the app using the `startup.sh` script or manually through the Azure portal.

Refer to the [Azure documentation](https://docs.microsoft.com/azure/app-service/) for details on deploying FastAPI applications on Azure App Service.

## Usage

Once the application is running, you can interact with the chatbot through the FastAPI interface. Here’s an example of a typical interaction:

1. Access the chatbot by visiting the deployed service URL.
2. Send a query in the chat interface.
3. The chatbot retrieves relevant information from Milvus and responds with the most accurate answers.

## Configuration

The `configuration_guide.ipynb` notebook provides a step-by-step guide for setting up and configuring Milvus. Key configurations include:

- **Milvus Server URL**: Ensure the connection string matches your Milvus server details.
- **Embedding Model**: Specify the embedding model you are using for generating vector representations.
- **Environment Variables**: Set up necessary API keys and environment variables as required by Azure and Milvus.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! If you’d like to improve this project, please fork the repository and submit a pull request with your proposed changes.

## Contact

For any questions or support, please feel free to open an issue on GitHub.

## Acknowledgments

- [Milvus](https://milvus.io/) - Vector database used for similarity search.
- [FastAPI](https://fastapi.tiangolo.com/) - API framework used for the backend.
- [Azure App Service](https://azure.microsoft.com/services/app-service/) - Platform for deploying cloud-based applications.
