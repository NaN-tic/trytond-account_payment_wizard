#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.pool import Pool
from .payment import *


def register():
    Pool.register(
        PayLineStart,
        module='account_payment_wizard', type_='model')
    Pool.register(
        PayLine,
        module='account_payment_wizard', type_='wizard')
