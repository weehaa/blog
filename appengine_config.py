# appengine_config.py
from google.appengine.ext import vendor

# Add any libraries install in the "models" and "models/lib" folder.
vendor.add('models')
vendor.add('models/lib')
