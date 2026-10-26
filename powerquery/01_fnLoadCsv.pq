// Query name: fnLoadCsv
// Reads one CSV from DataFolder, promotes headers and turns blank cells into null.
(fileName as text) as table =>
let
    Source = Csv.Document(
        File.Contents(DataFolder & fileName),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    BlankToNull = Table.TransformColumns(
        Promoted,
        List.Transform(Table.ColumnNames(Promoted), (c) => {c, each if _ = "" then null else _})
    )
in
    BlankToNull
