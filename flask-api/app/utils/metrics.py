from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import request, Response
from functools import wraps
import time


# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

articles_total = Gauge(
    'articles_total',
    'Total number of articles',
    ['status']
)

db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation']
)

kafka_messages_sent_total = Counter(
    'kafka_messages_sent_total',
    'Total Kafka messages sent',
    ['event_type', 'success']
)

kafka_message_send_errors_total = Counter(
    'kafka_message_send_errors_total',
    'Total Kafka message send errors'
)


def init_metrics(app):
    """
    Initialize Prometheus metrics endpoint

    Args:
        app: Flask application
    """
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def track_request(f):
    """
    Decorator to track HTTP requests with Prometheus metrics

    Args:
        f: Function to wrap

    Returns:
        Wrapped function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        # Get endpoint name
        endpoint = request.endpoint or 'unknown'
        method = request.method

        try:
            # Execute the actual function
            response = f(*args, **kwargs)

            # Get status code
            if isinstance(response, tuple):
                status = response[1] if len(response) > 1 else 200
            else:
                status = getattr(response, 'status_code', 200)

            # Record metrics
            http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()

            return response

        except Exception as e:
            # Record error metrics
            http_requests_total.labels(method=method, endpoint=endpoint, status=500).inc()
            raise

        finally:
            # Record request duration
            duration = time.time() - start_time
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)

    return decorated_function


def record_db_query(operation):
    """
    Record a database query

    Args:
        operation (str): Type of operation (select, insert, update, delete)
    """
    db_queries_total.labels(operation=operation).inc()


def record_kafka_message(event_type, success=True):
    """
    Record a Kafka message sent

    Args:
        event_type (str): Type of event
        success (bool): Whether the message was sent successfully
    """
    kafka_messages_sent_total.labels(
        event_type=event_type,
        success='true' if success else 'false'
    ).inc()

    if not success:
        kafka_message_send_errors_total.inc()


def update_article_count(status, count):
    """
    Update article count gauge

    Args:
        status (str): Article status
        count (int): Number of articles
    """
    articles_total.labels(status=status).set(count)
