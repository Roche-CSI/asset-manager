import assert from "assert";
import data from "./asset_class_data.json";
import AssetClass from "../assetClass";

test("create asset-class instance", () => {
    let asset_class = new AssetClass(data);
    assert(asset_class.id === data.id);
    assert(asset_class.name == data.name);
    console.log(asset_class.url())
    assert(asset_class.url() === "http://127.0.0.1:5000/asset_class/123e4567-e89b-12d3-a456-426614174000");
})