"""
Test data factories using Factory Boy

Generates realistic test data for Herald exchanges and other entities.
"""

import factory
from faker import Faker
import hashlib
from datetime import datetime, timedelta
import random

fake = Faker()
Faker.seed(12345)  # Deterministic test data


class ExchangeFactory(factory.Factory):
    """Factory for generating exchange test data"""
    
    class Meta:
        model = dict
    
    id = factory.LazyFunction(
        lambda: f"{fake.word()}-{fake.word()}-{fake.word()}-{fake.hex_chars(4)}"
    )
    
    list_a = factory.LazyFunction(
        lambda: f"Test Army List\n{fake.text(max_nb_chars=200)}\n1000 points"
    )
    
    hash_a = factory.LazyAttribute(
        lambda obj: hashlib.sha256(obj.list_a.encode()).hexdigest()
    )
    
    timestamp_a = factory.LazyFunction(datetime.now)
    
    list_b = None
    hash_b = None
    timestamp_b = None
    

class CompletedExchangeFactory(ExchangeFactory):
    """Factory for generating complete exchange test data (both lists submitted)"""
    
    list_b = factory.LazyFunction(
        lambda: f"Test Army List B\n{fake.text(max_nb_chars=200)}\n1000 points"
    )
    
    hash_b = factory.LazyAttribute(
        lambda obj: hashlib.sha256(obj.list_b.encode()).hexdigest()
    )
    
    timestamp_b = factory.LazyFunction(
        lambda: datetime.now() + timedelta(minutes=random.randint(1, 60))
    )


class RequestLogFactory(factory.Factory):
    """Factory for generating request log test data"""
    
    class Meta:
        model = dict
    
    ip = factory.LazyFunction(fake.ipv4)
    
    endpoint = factory.LazyFunction(
        lambda: random.choice([
            "/api/herald/exchange/create",
            "/api/herald/exchange/test-id",
            "/api/herald/stats",
            "/health"
        ])
    )
    
    user_agent = factory.LazyFunction(
        lambda: random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "curl/7.68.0",
            "Python/3.11 httpx/0.26.0"
        ])
    )
    
    timestamp = factory.LazyFunction(datetime.now)


# Convenience functions for test usage

def generate_exchange(**kwargs):
    """Generate exchange test data with optional overrides"""
    return ExchangeFactory(**kwargs)


def generate_complete_exchange(**kwargs):
    """Generate complete exchange test data with optional overrides"""
    return CompletedExchangeFactory(**kwargs)


def generate_request_log(**kwargs):
    """Generate request log test data with optional overrides"""
    return RequestLogFactory(**kwargs)
