import os, secrets

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG")

class BaseConfig:
	SECRET_KEY = os.getenv("SECRET_KEY")

class DevConfig(BaseConfig):
	DEBUG = True
	HOST='0.0.0.0'

class DeploymentConfig(BaseConfig):
	DEBUG = False
	HOST='127.0.0.1'

configs = {
	'dev': DevConfig,
	'deploy': DeploymentConfig
}

__all__ = [
	"DEBUG"
	"configs"
]