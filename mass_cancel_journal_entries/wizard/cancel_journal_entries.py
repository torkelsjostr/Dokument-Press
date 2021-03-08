from odoo import api, models, _
from odoo.exceptions import UserError


class CancelJournalEntries(models.TransientModel):
    _name = 'cancel.journal.entries'

    @api.multi
    def cancel_journal_entries(self):
        """ cancel multiple journal entries from the tree view."""
        account_move_recs = self.env['account.move'].browse(
            self._context.get('active_ids'))
        journal_names = account_move_recs.mapped('journal_id').filtered(
            lambda journal: journal.update_posted == False).mapped('name')
        if journal_names:
            error_msg = """You must enable Allow Cancelling Entries\
            from Journals %s""" % ', '.join(journal_names)
            raise UserError(_(error_msg))
        account_move_recs.button_cancel()
        return True
