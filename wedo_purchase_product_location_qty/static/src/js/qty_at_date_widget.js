odoo.define('wedo_purchase_product_location_qty.QtyAtDateWidget', function (require) {
"use strict";

var core = require('web.core');
var QWeb = core.qweb;

var Widget = require('web.Widget');
var Context = require('web.Context');
var data_manager = require('web.data_manager');
var widget_registry = require('web.widget_registry');
var config = require('web.config');

var _t = core._t;
var time = require('web.time');

var QtyAtDateWidget = Widget.extend({
    template: 'wedo_purchase_product_location_qty.qtyAtDate',
    events: _.extend({}, Widget.prototype.events, {
        'click .fa-info-circle': '_onClickButton',
    }),

    /**
     * @override
     * @param {Widget|null} parent
     * @param {Object} params
     */
    init: function (parent, params) {
        this.data = params.data;
        this._super(parent);
    },

    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self._setPopOver();
        });
    },

    updateState: function (state) {
        this.$el.popover('dispose');
        var candidate = state.data[this.getParent().currentRow];
        if (candidate) {
            this.data = candidate.data;
            this.renderElement();
            this._setPopOver();
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------
    /**
     * Set a bootstrap popover on the current QtyAtDate widget that display available
     * quantity.
     */
    _setPopOver: function () {
        var self = this;

        if (!self.data.product_id)
        {
            return;
        }
        var $content = $(QWeb.render('wedo_purchase_product_location_qty.QtyDetailPopOver', {
            data: this.data,
        }));
        
        var locations = self._rpc({
            model: 'purchase.order.line',
            method: 'product_info',
            args: [self.data, self.data.product_id.id, self.data.product_stock_quant_ids.res_ids],
            }).then(function(response){
                if (response.length>0)
                    response.map(function(location){
                        console.log(location);
                        $content.find('#quantities_table').append("<tr><td>"+location['name']+"</td><td>"+location['qty']+"</td><td>"+location['last_week_qty']+"</td><td>"+location['last_month_qty']+"</td></tr>");
                    });
                else
                        $content.find('#quantities_table').append("NO Location Found!");
            });

        var options = {
            content: $content,
            html: true,
            placement: 'left',
            title: _t('Consumption Information'),
            trigger: 'focus',
            delay: {'show': 0, 'hide': 100 },
        };
        this.$el.popover(options);

    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    _onClickButton: function () {
        // We add the property special click on the widget link.
        // This hack allows us to trigger the popover (see _setPopOver) without
        // triggering the _onRowClicked that opens the order line form view.
        this.$el.find('.fa-info-circle').prop('special_click', true);
    },

});

widget_registry.add('purchase_product_qty_at_date_widget', QtyAtDateWidget);

return QtyAtDateWidget;
});
