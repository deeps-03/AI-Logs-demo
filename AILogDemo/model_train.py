import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import numpy as np

# This function generates a synthetic dataset of log messages with predefined labels.
# It creates a balanced set of "incident" (error) and "preventive_action" (warning) logs.
def generate_synthetic_logs(num_samples=1000):
    logs = []
    labels = []
    error_templates = [
        "ERROR: Failed to connect to database: {reason}",
        "ERROR: NullPointerException in {module} at line {line}",
        "ERROR: Disk full on {drive}",
        "ERROR: Authentication failed for user {user}",
        "ERROR: Service {service} is unreachable",
    ]
    warning_templates = [
        "WARNING: Low disk space on {drive}",
        "WARNING: High CPU usage detected on {server}",
        "WARNING: Deprecated function {func} called",
        "WARNING: Cache refresh failed, using old data",
        "WARNING: Too many open files",
    ]

    for _ in range(num_samples // 2):
        # Error logs
        reason = np.random.choice(["timeout", "connection refused", "invalid credentials"])
        module = np.random.choice(["auth_service", "data_processor", "api_gateway"])
        line = np.random.randint(100, 1000)
        drive = np.random.choice(["/dev/sda1", "/mnt/data"])
        user = np.random.choice(["admin", "guest", "dev"])
        service = np.random.choice(["payment_service", "notification_service"])
        
        error_log = np.random.choice(error_templates).format(
            reason=reason, module=module, line=line, drive=drive, user=user, service=service
        )
        logs.append(error_log)
        labels.append("incident")

        # Warning logs
        drive = np.random.choice(["/dev/sda1", "/mnt/data"])
        server = np.random.choice(["web-01", "app-02", "db-01"])
        func = np.random.choice(["old_api", "legacy_method"])

        warning_log = np.random.choice(warning_templates).format(
            drive=drive, server=server, func=func
        )
        logs.append(warning_log)
        labels.append("preventive_action")

    return pd.DataFrame({"log": logs, "label": labels})

if __name__ == "__main__":
    print("Generating synthetic log data...")
    df = generate_synthetic_logs(num_samples=2000)

    # Split the dataset into training and testing sets (80% train, 20% test).
    # `stratify` ensures that the proportion of labels is the same in both sets.
    X_train, X_test, y_train, y_test = train_test_split(
        df["log"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    print("Training TF-IDF Vectorizer...")
    # TF-IDF (Term Frequency-Inverse Document Frequency) converts raw text into a matrix of numerical features.
    # This is a crucial step to prepare the text data for the machine learning model.
    vectorizer = TfidfVectorizer(max_features=1000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Training Logistic Regression model...")
    # Train a Logistic Regression model, a simple and effective algorithm for text classification.
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)

    print("Evaluating model...")
    y_pred = model.predict(X_test_vec)
    print(classification_report(y_test, y_pred))

    print("Saving model and vectorizer...")
    # Save the trained model and the vectorizer to disk using pickle.
    # These files will be loaded by the log consumer service to make predictions on new logs.
    with open("/Users/deepaksuresh/Desktop/AI-Logs-demo/AILogDemo/log_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("/Users/deepaksuresh/Desktop/AI-Logs-demo/AILogDemo/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    print("Model training complete. log_model.pkl and vectorizer.pkl saved.")
