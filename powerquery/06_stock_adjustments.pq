// Query name: stock_adjustments
let
    Source = fnLoadCsv("stock_adjustments.csv"),
    Typed = Table.TransformColumnTypes(
        Source,
        {{"adj_id", type text}, {"date", type date}, {"product_id", type text}, {"quantity", Int64.Type}, {"reason", type text}},
        "en-US"
    ),
    MergedProducts = Table.NestedJoin(Typed, {"product_id"}, products, {"product_id"}, "p", JoinKind.LeftOuter),
    ExpandedProducts = Table.ExpandTableColumn(MergedProducts, "p", {"cost"}),
    AddValue = Table.AddColumn(ExpandedProducts, "value_at_cost", each [quantity] * [cost], type number),
    Result = Table.RemoveColumns(AddValue, {"cost"})
in
    Result
