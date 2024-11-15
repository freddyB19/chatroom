import secrets

class BaseConfig:
	SECRET_KEY = secrets.token_hex()


class DevConfig(BaseConfig):
	DEBUG = True

class DeploymentConfig(BaseConfig):
	DEBUG = False


configs = {
	'dev': DevConfig,
	'deploy': DeploymentConfig
}