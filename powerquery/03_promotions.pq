// Query name: promotions
let
    Source = fnLoadCsv("promotions.csv"),
    Typed = Table.TransformColumnTypes(
        Source,
        {
            {"promo_id", type text}, {"name", type text}, {"promo_type", type text},
            {"start_date", type date}, {"end_date", type date}, {"discount_pct", type number},
            {"brand", type text}, {"gift_item", type text}, {"gift_qty", Int64.Type},
            {"qualifying_rule", type text}
        },
        "en-US"
    ),
    AddDays = Table.AddColumn(Typed, "promo_days", each Duration.Days([end_date] - [start_date]) + 1, Int64.Type)
in
    AddDays
