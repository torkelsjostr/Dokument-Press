/*
# -*- coding: utf-8 -*-
##############################################################################
#
#       Copyright © SUREKHA TECHNOLOGIES PRIVATE LIMITED, 2019.
#
#       You can not extend,republish,modify our code,app,theme without our
#       permission.
#
#       You may not and you may not attempt to and you may not assist others
#       to remove, obscure or alter any intellectual property notices on the
#       Software
#
##############################################################################
*/
odoo.define('st_dynamic_list.shcolumns', function(require) {
    "use strict";

var core = require('web.core');
var ListController = require('web.ListController');
var QWeb = core.qweb;

ListController.include({
    renderButtons: function($node) {
        var self = this;
        this._super.apply(this, arguments);
        this.$buttons.on('click', '.oe_select_columns', this.my_setup_columns.bind(this));
        this.$buttons.on('click', '.oe_dropdown_btn', this.hide_show_columns.bind(this));
        this.$buttons.on('click', '.oe_dropdown_menu', this.stop_event.bind(this));

        if (this.$buttons) {
            this.contents = this.$buttons.find('ul#show-menu');
            var columns = []
            _.each(this.renderer.arch.children, function(node) {
                var name = node.attrs.name
                var description = node.attrs.string || self.renderer.state.fields[name].string;
                columns.push({
                    'field_name': node.attrs.name,
                    'label': description,
                    'invisible': node.attrs.modifiers.column_invisible || false
                })
            })
            this.contents.append($(QWeb.render('ColumnSelectionDropDown', {
                widget: this,
                columns: columns
            })));
        }
    },

    my_setup_columns: function() {
        $("#show-menu").show();
    },

    stop_event: function(e) {
        e.stopPropagation();
    },

    hide_show_columns: function() {
        $("#show-menu").hide();
        this.setup_columns()
        var state = this.model.get(this.handle);
        this.renderer.updateState(state, {
            reload: true
        })
    },

    setup_columns: function() {
        var self = this;
        _.each(this.contents.find('li.item_column'), function(item) {
            var checkbox_item = $(item).find('input');
            var field = _.find(self.renderer.arch.children, function(field) {
                return field.attrs.name === checkbox_item.data('name')
            });
            if (checkbox_item.prop('checked')) {
                field.attrs.modifiers.column_invisible = false;
            } else {
                field.attrs.modifiers.column_invisible = true;
            }
        })
    },
});

$(document).click(function() {
    $('.oe_select_columns').click(function() {
        $("#show-menu").show();
    });
    $("#show-menu").hide();
});

});