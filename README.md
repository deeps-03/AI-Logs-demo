# AI Log Demo 🚀

## Project Description 📝
This project provides a complete local end-to-end prototype for **real-time log analysis, streaming, and anomaly detection**. It leverages a robust stack of Dockerized services and Python-based machine learning to demonstrate how to collect, process, classify, and visualize log data efficiently.

## Key Features ✨
*   **Log Generation:** Synthetic log data (INFO, WARNING, ERROR, DEBUG) streamed to Kafka.
*   **Log Classification:** Python ML model (TF-IDF + Logistic Regression) classifies logs into "incident" 🚨 or "preventive_action" 🛠️.
*   **Metrics Collection:** Classified log counts are pushed as metrics to VictoriaMetrics.
*   **Real-time Visualization:** Grafana dashboards provide live insights into log metrics.
*   **Containerized Environment:** All services run seamlessly within Docker Compose for easy setup and portability.
*   **CI/CD Pipeline:** GitHub Actions automate testing, building, and pushing Docker images.
*   **Anomaly Detection:** Automatically detects unusual log patterns and triggers alerts.

## Technologies Used 🛠️
*   **Kafka:** Distributed streaming platform for handling log data.
*   **Zookeeper:** Coordinates Kafka brokers.
*   **VictoriaMetrics:** High-performance, scalable, and cost-effective open-source time series database, compatible with Prometheus.
*   **Grafana:** Open-source platform for monitoring and observability, used for visualizing metrics and triggering alerts.
*   **Python:** Used for log generation, consumption, ML model training, and anomaly detection.
*   **Docker & Docker Compose:** For containerization and orchestration of services.
*   **GitHub Actions:** For Continuous Integration/Continuous Delivery (CI/CD) workflows.

## Architecture Diagram 🗺️
```
+-----------------+      +----------------+      +-------------------+      +-------------------+      +-----------------+
|  Log Producer   |----->|     Kafka      |----->|   Log Consumer    |----->|  VictoriaMetrics  |----->|     Grafana     |
| (Generates Logs)|      | (Log Streaming)|      | (Classifies Logs) |      |  (Stores Metrics) |      | (Visualizes Data)|
+-----------------+      +----------------+      +-------------------+      +---------+---------+      +--------+--------+
                                                                                     |                         ^
                                                                                     | (Reads Metrics)         | (Sends Alerts)
                                                                                     |                         |
                                                                           +---------▼---------+---------------+
                                                                           | Anomaly Detector  |
                                                                           |(Detects Anomalies)|
                                                                           +-------------------+
```

## Pipeline Explanation ⚙️
*   **Kafka Producer:** Generates synthetic log data (INFO, WARNING, ERROR, DEBUG) and streams it to the Kafka "logs" topic.
*   **Kafka Consumer:** Subscribes to the Kafka "logs" topic, consumes log entries, and uses a pre-trained Python ML model (TF-IDF + Logistic Regression) to classify them as "incident" or "preventive_action". It then increments internal counters for these classifications.
*   **VictoriaMetrics:** The Log Consumer pushes the incident and warning counts as metrics to VictoriaMetrics.
*   **Grafana Dashboard:** Grafana connects to VictoriaMetrics as a data source, allowing real-time visualization of the `log_incident_total` and `log_warning_total` metrics.
*   **AI Anomaly Detection:** A separate Python service (`anomaly_detector.py`) reads metrics from VictoriaMetrics, compares current values against historical averages, and detects anomalies, triggering alerts via console log and Grafana API.

## Service Ports 🔌
| Service          | Port   | Description                               |
|------------------|--------|-------------------------------------------|
| Kafka            | 9092   | Message broker (external access)          |
| Zookeeper        | 2181   | Kafka coordination                        |
| VictoriaMetrics  | 8428   | Metrics collection (HTTP API)             |
| Grafana          | 3000   | Dashboard visualization (Web UI)          |
| Log Producer     | N/A    | Runs as Docker service, no external port  |
| Log Consumer     | N/A    | Runs as Docker service, no external port  |
| Anomaly Detector | N/A    | Runs as Docker service, no external port  |

## Getting Started 🚀

Follow these steps to get the AI Log Demo project up and running locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/deeps-03/AI-Logs-demo.git
    ```

2.  **Navigate into the project directory:**
    ```bash
    cd AI-Logs-demo
    ```

3.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # For Windows: .\venv\Scripts\activate
    ```
    *(Ensure your terminal prompt changes to indicate the venv is active, e.g., `(venv) your_user@your_machine`)*

4.  **Install Python dependencies:**
    *(Run this command with the venv active)*
    ```bash
    pip install -r AILogDemo/requirements.txt
    ```

5.  **Train the ML model:**
    This step generates `log_model.pkl` and `vectorizer.pkl` which are used by the `log-consumer`.
    *(Run this command with the venv active from the root `AI-Logs-demo` directory)*
    ```bash
    python3 AILogDemo/model_train.py
    ```

6.  **Navigate into the AILogDemo directory:**
    This is where the `docker-compose.yml` file is located. All `docker-compose` commands must be run from here.
    ```bash
    cd AILogDemo
    ```

7.  **Build Docker images for the services:**
    ```bash
    docker-compose build
    ```

8.  **Start all services using Docker Compose:**
    ```bash
    docker-compose up -d
    ```

9.  **Access Grafana:**
    Open your web browser and go to `http://localhost:3000`.
    *   Default login: `admin` / `admin` (you will be prompted to change the password).
    *   **Add VictoriaMetrics as a Data Source:**
        *   Go to `Connections` -> `Data sources`.
        *   Click `Add data source` and select `Prometheus`.
        *   Set the URL to `http://victoria-metrics:8428`.
        *   Click `Save & Test`.
    *   **Create a Dashboard:**
        *   Go to `Dashboards` -> `New dashboard`.
        *   Click `Add new panel`.
        *   In the "Query" tab, select your VictoriaMetrics data source.
        *   Add queries for `log_incident_total` and `log_warning_total` (for time series graphs) or `sum(log_incident_total)` and `sum(log_warning_total)` (for Stat/Gauge panels).
        *   Click `Apply` and then save your dashboard.

10. **Access VictoriaMetrics UI (Optional):**
    You can access the VictoriaMetrics UI at `http://localhost:8428` to directly query metrics.

11. **Stop all services:**
    Remember to run this from the `AILogDemo` directory.
    ```bash
    docker-compose down
    ```

## Anomaly Detection

The AI Log Demo project includes an anomaly detection feature that continuously monitors log metrics to identify unusual patterns.

### How it Works

The `anomaly_detector.py` script, running as a background service, performs the following:
*   **Metric Collection:** It periodically (every 60 seconds) reads `log_incident_total` and `log_warning_total` metrics from Prometheus (VictoriaMetrics).
*   **Comparison:** It compares the current metrics (last 5 minutes) against their historical average (last 6 hours).
*   **Detection Rules:** An anomaly is detected if:
    *   Current incidents > 2 × historical average
    *   OR current warnings > 2 × historical average
*   **Alerting:** When an anomaly is detected, it triggers alerts:
    *   A message is printed to the console log of the `anomaly-detector` service.
    *   An annotation is sent to Grafana via the Grafana API, which can be displayed on relevant dashboards.

### Setup Instructions

1.  **Script Location:** Ensure the `anomaly_detector.py` script is located in the `AILogDemo` folder.
2.  **Docker Compose Integration:** The script is configured to run as a background service within Docker Compose. Its definition is included in `AILogDemo/docker-compose.yml`.
3.  **Dependencies:** The `anomaly_detector.py` script requires the following Python libraries, which are listed in `AILogDemo/requirements.txt`:
    *   `requests` (for API calls to Prometheus and Grafana)
    *   `python-dotenv` (for loading environment variables)

## Grafana Persistence

To ensure that your Grafana dashboard configurations, users, and settings persist across Docker Compose restarts, a Docker volume has been added for Grafana.

This means you won't have to re-configure your dashboards or log in again after restarting the Docker services.

### Volume Configuration Example (from `AILogDemo/docker-compose.yml`)

```yaml
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - victoria-metrics
    networks:
      - log-streaming

# ... (other services)

volumes:
  victoria-metrics-data:
  grafana-data:
```

## Grafana API Setup

The anomaly detection service uses a Grafana API key to send annotations (alerts) to your Grafana instance. This key is securely stored as an environment variable.

### Steps to Generate and Store the API Key

1.  **Generate a Grafana API Key:**
    *   Log in to your Grafana instance (`http://localhost:3000`).
    *   Navigate to **Administration** -> **Users and access** -> **API Keys**.
    *   Click **Add new API key**.
    *   Provide a **Key name** (e.g., `anomaly-detector-key`).
    *   Set the **Role** to `Editor` or `Admin` (Editor is usually sufficient for creating annotations).
    *   Click **Add**.
    *   **Copy the generated key immediately.** It will only be shown once.

2.  **Store the Key in `.env`:**
    *   In the `AILogDemo` directory (the same directory as `docker-compose.yml`), create or open a file named `.env`.
    *   Add or update the `GRAFANA_API_KEY` variable with your copied key:

    ```
    GRAFANA_API_KEY=your_generated_grafana_api_key_here
    ```
    *   **Important:** Replace `your_generated_grafana_api_key_here` with the actual key you copied from Grafana.

3.  **How the Anomaly Detector Uses the Key:**
    The `anomaly_detector.py` script reads this `GRAFANA_API_KEY` from the `.env` file and uses it in the `Authorization` header when making API calls to Grafana's annotation endpoint (`/api/annotations`). This allows the anomaly detector to programmatically create alerts that appear on your Grafana dashboards.

## Notes and Troubleshooting 💡

*   Ensure Docker Desktop (or your Docker environment) is running before starting services.
*   To check the status of all running Docker services, use: `docker-compose ps`
*   To view logs for any specific service (e.g., `kafka`, `log-producer`, `log-consumer`, `anomaly-detector`), use: `docker-compose logs -f <service_name>`
*   If `docker-compose up -d` fails, it will usually indicate which service failed to start.
    *   **Identify the failing service:** Look for messages like `Error starting userland proxy: ...` or `Container <service_name> Exited`. You can also run `docker-compose ps` to see the status of all services (look for `Exit <code_number>` in the STATUS column).
    *   **Check the logs:** Once you identify the problematic service, use `docker-compose logs -f <service_name>` to view its logs. Look for `ERROR`, `FATAL`, `Exception`, or `Failed` keywords.
    *   **Common issues:**
        *   **Port conflicts:** Another application might be using a port required by a Docker service.
        *   **Dependency issues:** A service might fail if a service it depends on (e.g., Kafka depends on Zookeeper) is not yet ready or failed to start.
        *   **Configuration errors:** Typos or incorrect values in `docker-compose.yml` or service-specific configuration files.
        *   **Image issues:** Problems pulling or building a Docker image.
*   If Python scripts fail with `ModuleNotFoundError`, ensure your virtual environment is activated and dependencies are installed (`pip install -r AILogDemo/requirements.txt`).
*   **Deactivating the Virtual Environment:**
    *   To deactivate your virtual environment, simply type `deactivate` in your terminal.
    *   You should deactivate it when you are done working on this project or when you want to switch to another project that uses different Python dependencies. Deactivating returns your terminal to the system's default Python environment.
*   If Grafana shows "No data", double-check your data source URL (`http://victoria-metrics:8428`) and the time range selected on your dashboard.
