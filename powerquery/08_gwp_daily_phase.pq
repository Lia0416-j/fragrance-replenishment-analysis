// Query name: gwp_daily_phase
// For each GWP promotion and day: gifts given, running total, and whether gifts were still available at the start of the day.
let
    GwpSales = Table.SelectRows(sales, each [promo_type] = "gwp"),
    ByDay = Table.Group(
        GwpSales, {"promo_id", "date"},
        {{"gifts_given", each List.Sum([gift_given]), Int64.Type}, {"units_sold", each List.Sum([quantity]), Int64.Type}}
    ),
    Sorted = Table.Sort(ByDay, {{"promo_id", Order.Ascending}, {"date", Order.Ascending}}),
    WithRunningTotal = Table.Group(
        Sorted, {"promo_id"},
        {{"rows", each
            let
                running = List.Skip(List.Accumulate([gifts_given], {0}, (s, x) => s & {List.Last(s) + x})),
                t = Table.FromColumns(Table.ToColumns(_) & {running}, Table.ColumnNames(_) & {"gifts_cumulative"})
            in
                Table.RemoveColumns(t, {"promo_id"}),
          type table}}
    ),
    Expanded = Table.ExpandTableColumn(WithRunningTotal, "rows", {"date", "gifts_given", "units_sold", "gifts_cumulative"}),
    MergedPromos = Table.NestedJoin(Expanded, {"promo_id"}, promotions, {"promo_id"}, "pr", JoinKind.LeftOuter),
    ExpandedPromos = Table.ExpandTableColumn(MergedPromos, "pr", {"gift_qty", "start_date"}),
    AddDayNumber = Table.AddColumn(ExpandedPromos, "promo_day", each Duration.Days([date] - [start_date]) + 1, Int64.Type),
    AddPhase = Table.AddColumn(
        AddDayNumber, "gift_phase",
        each if [gifts_cumulative] - [gifts_given] < [gift_qty] then "gifts available" else "gifts gone",
        type text
    ),
    Typed = Table.TransformColumnTypes(AddPhase, {{"date", type date}, {"gifts_given", Int64.Type}, {"units_sold", Int64.Type}, {"gifts_cumulative", Int64.Type}}),
    Result = Table.RemoveColumns(Typed, {"start_date"})
in
    Result
