from kafka import KafkaConsumer
import json
import pickle
import requests
import time

KAFKA_BROKER = 'kafka:9093'  # Internal Kafka address within Docker network
KAFKA_TOPIC = 'logs'
VICTORIAMETRICS_URL = 'http://victoria-metrics:8428/api/v1/import/prometheus'

# Load the trained model and vectorizer
try:
    with open('/app/log_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('/app/vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    print("Model and vectorizer loaded successfully.")
except FileNotFoundError:
    print("Error: model_train.py must be run first to generate log_model.pkl and vectorizer.pkl")
    exit(1)

from kafka.errors import NoBrokersAvailable

consumer = None
MAX_RETRIES = 10
RETRY_DELAY_SEC = 5

for i in range(MAX_RETRIES):
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='log-classifier-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        print(f"Successfully connected to Kafka after {i+1} attempts.")
        break
    except NoBrokersAvailable:
        print(f"Kafka brokers not available. Retrying in {RETRY_DELAY_SEC} seconds... (Attempt {i+1}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY_SEC)
    except Exception as e:
        print(f"An unexpected error occurred during Kafka connection: {e}")
        break

if consumer is None:
    print("Failed to connect to Kafka after multiple retries. Exiting.")
    exit(1)

# Initialize counters
incident_total = 0
warning_total = 0

def push_metrics_to_victoria_metrics():
    global incident_total, warning_total
    metrics = []

    # Prometheus text format
    metrics.append(f'log_incident_total{{source="log_consumer"}} {incident_total}')
    metrics.append(f'log_warning_total{{source="log_consumer"}} {warning_total}')

    payload = "\n".join(metrics)
    headers = {'Content-Type': 'text/plain'}
    
    try:
        response = requests.post(VICTORIAMETRICS_URL, data=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        print(f"Pushed metrics to VictoriaMetrics. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error pushing metrics to VictoriaMetrics: {e}")
        print(f"Payload: {payload}")

if __name__ == "__main__":
    print(f"Starting log consumer for topic: {KAFKA_TOPIC}")
    print(f"Connecting to Kafka broker: {KAFKA_BROKER}")
    print(f"Pushing metrics to VictoriaMetrics at: {VICTORIAMETRICS_URL}")

    last_metric_push_time = time.time()
    metric_push_interval = 10 # seconds

    try:
        for message in consumer:
            log_entry = message.value
            log_message = log_entry.get("message", "")
            log_level = log_entry.get("level", "")

            # Classify log message
            if log_message:
                log_message_vec = vectorizer.transform([log_message])
                prediction = model.predict(log_message_vec)[0]

                print(f"Consumed: {log_entry} -> Classified as: {prediction}")

                if prediction == "incident":
                    incident_total += 1
                elif prediction == "preventive_action":
                    warning_total += 1
            else:
                print(f"Consumed log entry with no message: {log_entry}")

            # Push metrics periodically
            current_time = time.time()
            if current_time - last_metric_push_time >= metric_push_interval:
                push_metrics_to_victoria_metrics()
                last_metric_push_time = current_time

    except KeyboardInterrupt:
        print("\nConsumer stopped by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        consumer.close()
        # Push final metrics before exiting
        push_metrics_to_victoria_metrics()
