// Query name: daily_stock
// One row per product per day.
// closing = previous closing + received - sold - shrinkage + claims stock change
let
    FirstDate = List.Min(sales[date]),
    LastDate = List.Max(sales[date]),
    Dates = List.Dates(FirstDate, Duration.Days(LastDate - FirstDate) + 1, #duration(1, 0, 0, 0)),
    Grid = Table.ExpandListColumn(
        Table.AddColumn(Table.SelectColumns(products, {"product_id", "opening_stock"}), "date", each Dates),
        "date"
    ),
    GridTyped = Table.TransformColumnTypes(Grid, {{"date", type date}}),

    Received = Table.Group(
        Table.SelectRows(stock_receipts, each [received_date] <> null),
        {"product_id", "received_date"}, {{"received", each List.Sum([quantity_received]), Int64.Type}}
    ),
    Sold = Table.Group(sales, {"product_id", "date"}, {{"sold", each List.Sum([quantity]), Int64.Type}}),
    Shrink = Table.Group(stock_adjustments, {"product_id", "date"}, {{"shrinkage", each List.Sum([quantity]), Int64.Type}}),
    Claims = Table.Group(claims, {"product_id", "submit_date"}, {{"claims_change", each List.Sum([stock_change]), Int64.Type}}),

    J1 = Table.ExpandTableColumn(Table.NestedJoin(GridTyped, {"product_id", "date"}, Received, {"product_id", "received_date"}, "x", JoinKind.LeftOuter), "x", {"received"}),
    J2 = Table.ExpandTableColumn(Table.NestedJoin(J1, {"product_id", "date"}, Sold, {"product_id", "date"}, "x", JoinKind.LeftOuter), "x", {"sold"}),
    J3 = Table.ExpandTableColumn(Table.NestedJoin(J2, {"product_id", "date"}, Shrink, {"product_id", "date"}, "x", JoinKind.LeftOuter), "x", {"shrinkage"}),
    J4 = Table.ExpandTableColumn(Table.NestedJoin(J3, {"product_id", "date"}, Claims, {"product_id", "submit_date"}, "x", JoinKind.LeftOuter), "x", {"claims_change"}),
    Zeros = Table.ReplaceValue(J4, null, 0, Replacer.ReplaceValue, {"received", "sold", "shrinkage", "claims_change"}),
    AddChange = Table.AddColumn(Zeros, "change", each [received] - [sold] - [shrinkage] + [claims_change], Int64.Type),

    WithClosing = Table.Group(
        AddChange, {"product_id"},
        {{"rows", each
            let
                t = Table.Sort(_, {{"date", Order.Ascending}}),
                closing = List.Skip(List.Accumulate(t[change], {t{0}[opening_stock]}, (s, x) => s & {List.Last(s) + x})),
                withCol = Table.FromColumns(Table.ToColumns(t) & {closing}, Table.ColumnNames(t) & {"closing_stock"})
            in
                Table.RemoveColumns(withCol, {"product_id", "opening_stock"}),
          type table}}
    ),
    Expanded = Table.ExpandTableColumn(WithClosing, "rows", {"date", "received", "sold", "shrinkage", "claims_change", "change", "closing_stock"}),
    Typed = Table.TransformColumnTypes(
        Expanded,
        {{"date", type date}, {"received", Int64.Type}, {"sold", Int64.Type}, {"shrinkage", Int64.Type},
         {"claims_change", Int64.Type}, {"change", Int64.Type}, {"closing_stock", Int64.Type}}
    ),
    AddOpening = Table.AddColumn(Typed, "opening_stock", each [closing_stock] - [change], Int64.Type),
    AddStockout = Table.AddColumn(AddOpening, "stockout_day", each [closing_stock] = 0, type logical),
    AddWeek = Table.AddColumn(AddStockout, "week_start", each Date.StartOfWeek([date], Day.Monday), type date),
    Sorted = Table.Sort(AddWeek, {{"product_id", Order.Ascending}, {"date", Order.Ascending}})
in
    Sorted
