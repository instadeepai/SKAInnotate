import os
import logging

LOG_DIR = 'logs/'

class Logger:
  def __init__(self, name='skainnotate', level=logging.DEBUG, log_dir=''):
    self.name = name
    self.logger = logging.getLogger(name)
    self.logger.setLevel(level)
    self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    self.file_handler = None
    self.console_handler = None
    self.log_dir = log_dir
    self.setup_handlers()

  def setup_handlers(self):
    if not os.path.exists(self.log_dir):
      os.makedirs(self.log_dir)
    self.file_handler = logging.FileHandler(os.path.join(self.log_dir, f'{self.name}.log'))
    self.file_handler.setLevel(logging.DEBUG)
    self.file_handler.setFormatter(self.formatter)
    self.logger.addHandler(self.file_handler)

    self.console_handler = logging.StreamHandler()
    self.console_handler.setLevel(logging.DEBUG)
    self.console_handler.setFormatter(self.formatter)
    self.logger.addHandler(self.console_handler)

  def log_debug(self, message):
    self.logger.debug(message)

  def log_info(self, message):
    self.logger.info(message)

  def log_warning(self, message):
    self.logger.warning(message)

  def log_error(self, message):
    self.logger.error(message)

  def log_exception(self, exception, message=None):
    if message:
      self.logger.exception(f"{message}: {str(exception)}")
    else:
      self.logger.exception(str(exception))

  def log_critical(self, message):
    self.logger.critical(message)


logger = Logger(log_dir=LOG_DIR)