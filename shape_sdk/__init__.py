__title__ = 'Shape-SDK'
__author__ = 'AndcoolSystems'
__version__ = '0.0.1'

from dotenv import load_dotenv
load_dotenv()
from . import api_manager, products, user, orders
from .types.user_type import UserType
from .types.product_type import ProductType
from .types.corrections_type import CorrectionType
from .types.order_type import OrderResultType, OrderType

