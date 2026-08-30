import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "RecoverIQ")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Razorpay API credentials
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

    # Razorpay webhook secret
    RAZORPAY_WEBHOOK_SECRET = os.getenv(
        "RAZORPAY_WEBHOOK_SECRET",
        "dev_webhook_secret",
    )


settings = Settings()