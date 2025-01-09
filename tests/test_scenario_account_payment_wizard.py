import datetime
import unittest
from decimal import Decimal

from proteus import Model, Wizard
from trytond.modules.account.tests.tools import (create_chart,
                                                 create_fiscalyear,
                                                 get_accounts)
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        # Install account_payment
        activate_modules('account_payment_wizard')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = create_fiscalyear(company)
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        payable = accounts['payable']
        expense = accounts['expense']

        Journal = Model.get('account.journal')
        journal_expense, = Journal.find([('code', '=', 'EXP')])

        # Create payment journal
        PaymentJournal = Model.get('account.payment.journal')
        payment_journal = PaymentJournal(name='Manual', process_method='manual')
        payment_journal.save()

        # Create parties
        Party = Model.get('party.party')
        customer = Party(name='Customer')
        customer.save()
        supplier = Party(name='Supplier')
        supplier.save()

        # Create payable move
        Move = Model.get('account.move')
        move = Move()
        move.journal = journal_expense
        line = move.lines.new(account=payable,
                              party=supplier,
                              credit=Decimal('50.00'),
                              maturity_date=tomorrow)
        line = move.lines.new(account=expense,
                              debit=Decimal('50.00'),
                              maturity_date=tomorrow)
        move.click('post')

        # Create a payment not approved
        Payment = Model.get('account.payment')
        line, = [l for l in move.lines if l.account == payable]
        pay_line = Wizard('account.move.line.pay', [line])
        pay_line.execute('next_')
        pay_line.execute('next_')
        payment, = Payment.find()
        self.assertEqual(payment.party, supplier)
        self.assertEqual(payment.state, 'draft')
        payment.delete()

        # Create a payment approved
        pay_line = Wizard('account.move.line.pay', [line])
        pay_line.execute('next_')
        pay_line.form.approve = True
        pay_line.execute('next_')
        payment, = Payment.find()
        self.assertEqual(payment.state, 'submitted')
