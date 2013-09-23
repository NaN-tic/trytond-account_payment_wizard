#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.

from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.pyson import Eval, If
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateAction, Button
from trytond.modules.account_payment.payment import KINDS

__all__ = ['CreatePaymentsStart', 'CreatePayments']


class CreatePaymentsStart(ModelView):
    'Create Payments Start'
    __name__ = 'account.payment.create.start'
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', 0)),
            ],)
    journal = fields.Many2One('account.payment.journal', 'Journal',
        required=True, domain=[
            ('company', '=', Eval('company', 0)),
            ],
        depends=['company'])
    kind = fields.Selection(KINDS, 'Kind', required=True)
    approve = fields.Boolean('Approve payments',
        help='Create payments in approved state')

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @staticmethod
    def default_kind():
        return 'payable'


class CreatePayments(Wizard):
    'Create Payments'
    __name__ = 'account.payment.create'
    start = StateView('account.payment.create.start',
        'account_payment_wizard.payment_create_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Process', 'process', 'tryton-ok', default=True),
            ])
    process = StateAction('account_payment.act_payment_form')

    def do_process(self, action):
        pool = Pool()
        Payment = pool.get('account.payment')
        AccountMoveLine = pool.get('account.move.line')
        lines = AccountMoveLine.browse(Transaction().context['active_ids'])

        to_create = []
        for line in lines:
            if not line.party:
                continue
            vals = self.get_payment_values(line)
            to_create.append(vals)
        payments = Payment.create(to_create)
        if self.start.approve:
            Payment.approve(payments)

        return action, {
            'res_id': [p.id for p in payments],
            }

    def get_payment_values(self, line):
        return {
            'company': self.start.company,
            'journal': self.start.journal.id,
            'party': line.party,
            'kind': self.start.kind,
            'line': line.id,
            'date': line.maturity_date,
            'amount': line.payment_amount,
            'description': line.description,
         }
