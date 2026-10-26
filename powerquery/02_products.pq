// Query name: products
let
    Source = fnLoadCsv("products.csv"),
    Typed = Table.TransformColumnTypes(
        Source,
        {
            {"product_id", type text}, {"brand", type text}, {"product_name", type text},
            {"category", type text}, {"size_ml", Int64.Type}, {"price", type number},
            {"cost", type number}, {"safety_stock", Int64.Type}, {"opening_stock", Int64.Type},
            {"case_size", Int64.Type}
        },
        "en-US"
    )
in
    Typed
