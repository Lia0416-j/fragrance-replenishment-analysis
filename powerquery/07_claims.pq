// Query name: claims
let
    Source = fnLoadCsv("claims.csv"),
    Typed = Table.TransformColumnTypes(
        Source,
        {
            {"claim_id", type text}, {"submit_date", type date}, {"product_id", type text},
            {"quantity", Int64.Type}, {"claim_value", type number}, {"claim_type", type text},
            {"stock_impact", type text}, {"status", type text}, {"resolved_date", type date}
        },
        "en-US"
    ),
    // signed quantity used in the daily stock calculation
    AddSignedQty = Table.AddColumn(
        Typed, "stock_change",
        each if [stock_impact] = "increase" then [quantity] else if [stock_impact] = "decrease" then -[quantity] else 0,
        Int64.Type
    ),
    ReportDate = List.Max(sales[date]),
    AddDaysOpen = Table.AddColumn(
        AddSignedQty, "days_open",
        each Duration.Days((if [resolved_date] = null then ReportDate else [resolved_date]) - [submit_date]),
        Int64.Type
    ),
    AddOverdue = Table.AddColumn(AddDaysOpen, "overdue_30_days", each [status] = "pending" and [days_open] > 30, type logical)
in
    AddOverdue
