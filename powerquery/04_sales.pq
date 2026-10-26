// Query name: sales
// Fixes the three known issues: product_id format, duplicate rows, blank discount.
let
    Source = fnLoadCsv("sales.csv"),
    // 1. product_id: trim spaces and upper case (do this before removing duplicates)
    CleanIds = Table.TransformColumns(Source, {{"product_id", each Text.Upper(Text.Trim(_)), type text}}),
    // 2. remove exact duplicate rows
    RemovedDuplicates = Table.Distinct(CleanIds),
    // 3. blank discount means no discount
    FilledDiscount = Table.ReplaceValue(RemovedDuplicates, null, "0", Replacer.ReplaceValue, {"discount_pct"}),
    Typed = Table.TransformColumnTypes(
        FilledDiscount,
        {
            {"sale_id", type text}, {"date", type date}, {"quantity", Int64.Type},
            {"unit_price", type number}, {"discount_pct", type number}, {"promo_id", type text},
            {"gift_given", Int64.Type}
        },
        "en-US"
    ),
    AddSalesAmount = Table.AddColumn(Typed, "sales_amount", each [quantity] * [unit_price], type number),
    // join product details
    MergedProducts = Table.NestedJoin(AddSalesAmount, {"product_id"}, products, {"product_id"}, "p", JoinKind.LeftOuter),
    ExpandedProducts = Table.ExpandTableColumn(MergedProducts, "p", {"brand", "category", "cost"}),
    AddGrossProfit = Table.AddColumn(ExpandedProducts, "gross_profit", each [sales_amount] - [quantity] * [cost], type number),
    // mark promotion sales and promotion type
    MergedPromos = Table.NestedJoin(AddGrossProfit, {"promo_id"}, promotions, {"promo_id"}, "pr", JoinKind.LeftOuter),
    ExpandedPromos = Table.ExpandTableColumn(MergedPromos, "pr", {"promo_type"}),
    AddInPromotion = Table.AddColumn(ExpandedPromos, "in_promotion", each [promo_id] <> null, type logical),
    Result = Table.RemoveColumns(AddInPromotion, {"cost"})
in
    Result
