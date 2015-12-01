# This file is part of the account_payment_wizard module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountPaymentWizardTestCase(ModuleTestCase):
    'Test Account Payment Wizard module'
    module = 'account_payment_wizard'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountPaymentWizardTestCase))
    return suite