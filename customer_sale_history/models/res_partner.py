# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"
    sale_product_count = fields.Integer(compute='_compute_sale_product_count')
    sale_product_ids = fields.One2many('sale.order.line', 'order_partner_id',
                                       string='Shopped Products', copy=False)

    def _compute_sale_product_count(self):
        sale_product_data = self.env['sale.order.line'].read_group(domain=[(
            'order_partner_id', 'child_of', self.ids), (
            'is_downpayment', '=', False)], fields=['order_partner_id'],
            groupby=['order_partner_id'])
        # read to keep the child/parent relation
        # while aggregating the read_group result in the loop
        partner_child_ids = self.read(['child_ids'])
        mapped_data = dict([(sale_data['order_partner_id'][0], sale_data[
            'order_partner_id_count']) for sale_data in sale_product_data])
        for partner in self:
            # let's obtain the partner id and
            # all its child ids from the read up there
            item = next(
                partner_child_id for partner_child_id in partner_child_ids
                if partner_child_id['id'] == partner.id)
            partner_ids = [partner.id] + item.get('child_ids')
            # then we can sum for all the partner's child
            partner.sale_product_count = sum(
                mapped_data.get(child, 0) for child in partner_ids)
