// Query name: stock_receipts
let
    Source = fnLoadCsv("stock_receipts.csv"),
    Typed = Table.TransformColumnTypes(
        Source,
        {
            {"receipt_id", type text}, {"order_date", type date}, {"received_date", type date},
            {"product_id", type text}, {"order_type", type text},
            {"quantity_ordered", Int64.Type}, {"quantity_received", Int64.Type}
        },
        "en-US"
    ),
    AddInTransit = Table.AddColumn(Typed, "in_transit", each [received_date] = null, type logical)
in
    AddInTransit
