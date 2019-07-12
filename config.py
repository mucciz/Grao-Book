import os

class Config:
    '''
    General configuration parent class
    '''
    #SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://roy:1234567@localhost/grao'
    SECRET_KEY=('<Flask app2 Secret Key>')
    SQLALCHEMY_TRACK_MODIFICATIONS = False    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    SUBJECT_PREFIX = 'Pitches'
    SENDER_EMAIL = 'roychela@gmail.com'
class ProdConfig(Config):
    '''
    Pruduction configuration child class

    Args:
        Config: The parent configuration class with General configuration settings
    '''
    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://roy:1234567@localhost/grao3'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://deathstar:deathstar@localhost/grao'

class TestConfig(Config):
    '''
    Testing configuration child class

    Args:
        Config: The parent configuration class with General configuration settings 
    '''
    pass

class DevConfig(Config):
    '''
    Development configuration child class
    
    Args:
        Config: The parent configuration class with General configuration settings
    '''

    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://roy:1234567@localhost/grao3'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://deathstar:deathstar@localhost/grao'
    DEBUG = True


config_options = {
    'development': DevConfig,
    'production': ProdConfig,
    'test': TestConfig
}