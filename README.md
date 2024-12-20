Introduction to InfraManager

InfraManager is a unified backend solution designed to streamline the management of cloud infrastructure across multiple public cloud providers, such as Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP). Built with FastAPI, this application provides a centralized platform for cloud administrators and developers to manage and automate the deployment, monitoring, and maintenance of their cloud resources in a simple and efficient manner.

With InfraManager, users can interact with various cloud platforms through a single API, eliminating the complexity of managing multiple separate interfaces for each provider. The solution allows for seamless integration and management of critical cloud resources such as virtual machines, compute instances, storage, and more.

Key Features
	•	Multi-cloud management: Supports AWS, Azure, and GCP, enabling you to manage instances and resources across all major cloud platforms from a single interface.
	•	Instance lifecycle management: Start, stop, and manage instances with ease, automating common cloud operations.
	•	Secure API: Implemented with JWT authentication to ensure secure access to cloud resources.
	•	Scalable architecture: Designed to scale with your cloud infrastructure needs, leveraging FastAPI’s high-performance capabilities.
	•	Extensible: Easily add support for more cloud providers and services as your needs grow.

Who is it for?
	•	Cloud Administrators: Automate and centralize cloud resource management across multiple providers.
	•	DevOps Engineers: Simplify cloud management workflows and CI/CD pipelines by interacting with different cloud providers through a single API.
	•	Developers: Integrate cloud resource management into applications without needing to manage multiple cloud SDKs.

InfraManager is designed to reduce the overhead of managing cloud infrastructure, improve productivity, and allow for better resource optimization across diverse cloud platforms. It simplifies cloud operations and provides a powerful API that can be easily extended to suit the needs of your business.


Updated Installation Step
	1.	Clone the Repository



3. Set Up a Virtual Environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

4. Install Dependencies

pip install -r requirements.txt

5. Set Up Environment Variables

Create a .env file in the root directory with the following keys:

# AWS Credentials
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key

# Azure Credentials
AZURE_CLIENT_ID=your-azure-client-id
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_CLIENT_SECRET=your-azure-client-secret

# GCP Credentials
GCP_SERVICE_ACCOUNT_KEY_PATH=/path/to/service-account-key.json

# Application Settings
SECRET_KEY=your-secret-key
DEBUG=True

Usage

Run the Application

uvicorn app.main:app --reload

Access the API Documentation

Once the server is running, you can explore the API at:
	•	Swagger UI: http://127.0.0.1:8000/docs
	•	Redoc: http://127.0.0.1:8000/redoc


Contributing

We welcome contributions! Please follow these steps:
	1.	Fork the repository.
	2.	Create a new branch (git checkout -b feature-name).
	3.	Commit changes (git commit -m "Add feature").
	4.	Push to the branch (git push origin feature-name).
	5.	Create a pull request.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Support

If you encounter any issues or have questions, feel free to open an issue in this repository or contact us at support@inframanager.io.

Let me know if you’d like additional customization!
