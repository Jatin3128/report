# Copyright (c) 2023, jay and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	columns, data = [], []
	columns, data = get_columns(filters), get_data(filters)
	return columns, data


def get_columns(filters):
    columns = [
        {
            'label':'Posting Date',
            'fieldname':"posting_date",
            'fieldtype':"Date",
            'width': 90
        },
        {
            'label':'Invoice No',
            'fieldname':"name",
            'fieldtype':"Link",
            'options':"Sales Invoice",
            'width': 150
        },
        {
            'label':'Customer PO',
            'fieldname':"po_no",
            'fieldtype':"Data",
            'width': 90
        },
        {
            'label':'Due Date',
            'fieldname':"due_date",
            'fieldtype':"Date",
            'width': 90
        },

       {
            'label':'Grand Total',
            'fieldname':"grand_total",
            'fieldtype':"Currency",
            'width': 120
        },
       {
            'label':'Paid Amount',
            'fieldname':"paid_amount",
            'fieldtype':"Currency",
            'width': 120
        },
       {
            'label':'Outstanding Amount',
            'fieldname':"outstanding_amount",
            'fieldtype':"Currency",
            'width': 120
        },
        {
            'label':'Age (Days)',
            'fieldname':"age_days",
            'fieldtype':"Data",
            'width': 120
        },

    ]
    return columns
    
def get_data(filters):
    date_type = ""
    if filters.age_based_on == "Posting Date":
        date_type = 'posting_date'
    elif filters.age_based_on == "Due Date":
        date_type = 'due_date'

    data = frappe.db.sql('''
        SELECT name, po_no, customer, posting_date, due_date, grand_total, paid_amount, outstanding_amount, 
        CAST(DATEDIFF(NOW(), {0}) AS CHAR) AS age_days
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1
        AND outstanding_amount > 0
        AND (customer = IFNULL(%(customer)s, "") OR %(customer)s IS NULL)
        AND {0} <= %(to_date)s
        ORDER BY {0};
        '''.format(date_type),
        {'from_date': filters.from_date, 'to_date': filters.to_date, 'customer': filters.customer}, as_dict=1)

    # Calculate total outstanding amount
    total_outstanding_amount = sum(row['outstanding_amount'] for row in data)

    # Append total to the data
    aging1 = aging(data, 0, 30)
    aging2 = aging(data, 31, 60)
    aging3 = aging(data, 61, 90)
    aging4 = aging(data, 91, 120)
    
    data.append({'total_outstanding_amount': total_outstanding_amount})
    data.append({"first":aging1})
    data.append({"second":aging2})
    data.append({"third":aging3})
    data.append({"fourth":aging4})
    
    return data

def aging(data, start_date, end_date):
    filtered_data = []
    # frappe.throw(f"data")
    for item in data:
        if 'age_days' in item and start_date <= int(item['age_days']) <= end_date:
            filtered_data.append(item)

    # Calculate sum of grand_total and outstanding_amount in filtered data
    sum_outstanding_amount = sum(float(item['outstanding_amount']) for item in filtered_data)

    return sum_outstanding_amount




  