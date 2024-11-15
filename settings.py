import secrets

class BaseConfig:
	SECRET_KEY = secrets.token_hex()


class DevConfig(BaseConfig):
	DEBUG = True


configs = {
	'dev': DevConfig
}