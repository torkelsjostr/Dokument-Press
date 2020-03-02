# -*- coding: utf-8 -*-
def migrate(cr, version):
    cr.execute("""
        UPDATE stock_pack_operation AS spo
        SET date = sp.manual_transfer_date
        FROM stock_picking AS sp
        WHERE sp.id = spo.picking_id
            AND sp.state = 'done'
            AND manual_transfer_date IS NOT NULL
            AND date_done != manual_transfer_date;  
    """)
    cr.execute("""
        UPDATE stock_quant AS sq
        SET in_date = (
            SELECT sm.manual_transfer_date
            FROM stock_move AS sm
            JOIN stock_quant_move_rel AS rel ON rel.move_id = sm.id AND rel.quant_id = sq.id
            WHERE sm.manual_transfer_date IS NOT NULL
                AND sq.in_date != sm.manual_transfer_date
            ORDER BY sm.sequence, id
            LIMIT 1
            )
    """)
    cr.execute("""
        UPDATE stock_move
        SET date = manual_transfer_date
        WHERE state='done'
            AND manual_transfer_date IS NOT NULL
            AND date != manual_transfer_date;
    """)
    cr.execute("""
    UPDATE stock_picking
    SET date_done = manual_transfer_date
    WHERE state='done'
        AND manual_transfer_date IS NOT NULL
        AND date_done != manual_transfer_date;    
    """)
