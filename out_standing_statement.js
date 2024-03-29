// Copyright (c) 2023, jay and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.datetime.get_start_of_week = function(date) {
    var curr = new Date(date);
    var first = curr.getDate() - curr.getDay() + 1;
    var firstDay = new Date(curr.setDate(first));
    return firstDay.toISOString().slice(0, 10);
};

frappe.datetime.get_end_of_week = function(date) {
    var curr = new Date(date);
    var last = curr.getDate() - curr.getDay() + 7;
    var lastDay = new Date(curr.setDate(last));
    return lastDay.toISOString().slice(0, 10);
};

frappe.datetime.get_last_day_of_last_month = function() {
    var today = new Date();
    var lastDayOfLastMonth = new Date(today.getFullYear(), today.getMonth(), 0);
    return lastDayOfLastMonth.toISOString().slice(0, 10);
};

// Now you can use the get_start_of_week, get_end_of_week, and get_last_day_of_last_month functions in your report configuration
var defaultFromDate = frappe.datetime.get_start_of_week(frappe.datetime.nowdate());
var defaultToDate = frappe.datetime.get_last_day_of_last_month();

frappe.query_reports['Out standing statement'] = {
    "filters": [
        {
            'label':"Ageing Based On",
            'fieldname':"age_based_on",
            'fieldtype':"Select",
            'options': ["Posting Date","Due Date"],
            "default": "Posting Date",
            'width': 80,
        },
        {
            'label':"As ON",
            'fieldname':"to_date",
            'fieldtype':"Date",
            'width': 80,
            "default": defaultToDate,
        },
        {
            'label': "Customer Name",
            'fieldname': "customer",
            'fieldtype': "Link",
            'options': "Customer",
            'width': 80,
            'on_change': function () {
                var customer_name = frappe.query_report.get_filter_value('customer');
                if (customer_name) {
                    // Fetch and set customer_tax directly when the customer is selected
                    fetchAndSetCustomerTax(customer_name);
                }
                else {
                    // Clear the "Customer TRN number" filter if tax_id is not available
                    console.log('Customer TRN number');
                    frappe.query_report.set_filter_value('customer_tax', '');
                }
            }
        },
		{
            'label': "Customer Address",
            'fieldname': "primary_address",
            'fieldtype': "Data",
            'width': 80,
        },
    ],
    "get_query": function (filters) {
        // Customize the query based on the filters
        var query = {
            // Your query configuration here
        };

        // Exclude "To Date" filter from the query when printing
        if (frappe.query_report.is_print) {
            query.filters = query.filters.filter(filter => filter.fieldname !== 'to_date');
        }

        return query;
    },
};

function fetchAndSetCustomerTax(customer_name) {
    // Make an asynchronous request to fetch the customer_tax based on the selected customer
    frappe.db.get_value('Customer', customer_name, 'primary_address')
        .then(r => {
            console.log(r.message.primary_address); // Output the fetched tax_id to the console

            if (r.message.primary_address) {
                // Set the fetched customer_tax directly into the "Customer TRN number" filter
                frappe.query_report.set_filter_value('primary_address', r.message.primary_address);
            } 
        });
}