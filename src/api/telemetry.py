# OpenTelemetry Instrumentation for FastAPI
# ==========================================

"""
OpenTelemetry integration for automatic tracing, metrics, and logs.
Integrates with Jaeger, Prometheus, and cloud-native observability platforms.
"""

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.trace import Status, StatusCode
import os


def setup_telemetry(app, service_name: str = "agenticai-api"):
    """
    Configure OpenTelemetry for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service for tracing
    """
    
    # Resource definition
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: os.getenv("APP_VERSION", "1.0.0"),
        "environment": os.getenv("APP_ENV", "production"),
        "deployment.region": os.getenv("DEPLOYMENT_REGION", "us-east-1"),
    })
    
    # Tracing setup
    otlp_trace_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
    
    trace_provider = TracerProvider(resource=resource)
    trace_exporter = OTLPSpanExporter(endpoint=otlp_trace_endpoint, insecure=True)
    trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(trace_provider)
    
    # Metrics setup
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=otlp_trace_endpoint, insecure=True)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    
    # Auto-instrumentation
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()
    RedisInstrumentor().instrument()
    
    # SQLAlchemy instrumentation (will be added when engine is created)
    # SQLAlchemyInstrumentor().instrument(engine=engine)
    
    return trace.get_tracer(__name__), metrics.get_meter(__name__)


def trace_function(name: str = None):
    """
    Decorator to add tracing to any function.
    
    Usage:
        @trace_function("my_custom_function")
        def my_function():
            pass
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = name or func.__name__
            
            with tracer.start_as_current_span(span_name) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = trace.get_tracer(__name__)
            span_name = name or func.__name__
            
            with tracer.start_as_current_span(span_name) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


# Custom metrics
def create_custom_metrics():
    """
    Create custom metrics for business logic monitoring.
    """
    meter = metrics.get_meter(__name__)
    
    # Counter for agent executions
    agent_execution_counter = meter.create_counter(
        name="agent.executions",
        description="Number of agent executions",
        unit="1",
    )
    
    # Histogram for agent execution duration
    agent_execution_duration = meter.create_histogram(
        name="agent.execution.duration",
        description="Duration of agent executions",
        unit="ms",
    )
    
    # Counter for LLM API calls
    llm_api_calls = meter.create_counter(
        name="llm.api.calls",
        description="Number of LLM API calls",
        unit="1",
    )
    
    # Counter for tokens used
    llm_tokens_used = meter.create_counter(
        name="llm.tokens.used",
        description="Total tokens used in LLM calls",
        unit="1",
    )
    
    # Histogram for task processing time
    task_processing_time = meter.create_histogram(
        name="task.processing.time",
        description="Time to process tasks",
        unit="s",
    )
    
    return {
        "agent_execution_counter": agent_execution_counter,
        "agent_execution_duration": agent_execution_duration,
        "llm_api_calls": llm_api_calls,
        "llm_tokens_used": llm_tokens_used,
        "task_processing_time": task_processing_time,
    }


# Example usage in main.py:
"""
from src.api.telemetry import setup_telemetry, create_custom_metrics

app = FastAPI()
tracer, meter = setup_telemetry(app, service_name="agenticai-api")
custom_metrics = create_custom_metrics()

@app.post("/agents/execute")
@trace_function("execute_agent")
async def execute_agent(request: AgentExecuteRequest):
    start_time = time.time()
    
    # Your logic here
    result = await agent.execute(request.task)
    
    # Record metrics
    custom_metrics["agent_execution_counter"].add(1, {"agent_type": agent.type})
    duration_ms = (time.time() - start_time) * 1000
    custom_metrics["agent_execution_duration"].record(duration_ms)
    
    return result
"""
