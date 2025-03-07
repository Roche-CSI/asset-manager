import assert from "assert";
import Asset from '../asset';
import AssetClass from "../assetClass";
import data from "./asset_data.json";


test('create AssetPage instance', () => {
    let asset: Asset = new Asset(data);
    // verify asset fields
    assert(asset.id);
    assert(asset.owner);
    assert(asset.top_hash)
    // assert(asset.asset_class instanceof AssetClass);
    assert(asset.url() === "http://127.0.0.1:5000/asset/123e4567-e89b-12d3-a456-426614174000");
})