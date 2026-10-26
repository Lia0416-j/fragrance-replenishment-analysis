// Query name: weekly_stock
// Weeks run Monday to Sunday. A stockout week has at least one day with closing stock 0.
let
    Weekly = Table.Group(
        daily_stock, {"product_id", "week_start"},
        {
            {"days_in_week", each Table.RowCount(_), Int64.Type},
            {"units_sold", each List.Sum([sold]), Int64.Type},
            {"closing_stock", each Table.Max(_, "date")[closing_stock], Int64.Type},
            {"stockout_days", each List.Count(List.Select([stockout_day], each _ = true)), Int64.Type}
        }
    ),
    AddStockoutWeek = Table.AddColumn(Weekly, "stockout_week", each [stockout_days] > 0, type logical),
    Sorted = Table.Sort(AddStockoutWeek, {{"product_id", Order.Ascending}, {"week_start", Order.Ascending}})
in
    Sorted
