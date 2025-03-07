import AssetRef from "../assetRef";
import assert from "assert";
import data from "./asset_ref_data.json";
import {AssetVersion} from "../assetVersion";

test('create asset-ref instance', () => {
    let asset_ref = new AssetRef(data);
    assert(asset_ref.id === data.id);
    assert(asset_ref.src_version.name === "acm_data/1/0.0.0");
    assert(asset_ref.dst_version.name === "genetics/1/0.0.0");
    // assert(asset_ref.url() === "http://127.0.0.1:5000/asset_ref/1");
})

test('fetch asset-ref from asset_server', async () => {
    console.log("fetching data");
    AssetRef.get(AssetRef.URL(), { asset_name: "pipeline/40/0.0.0", project_id: "123e4567-e89b-12d3-a456-426614174000"}).then((data) => {
        console.log("recieved:", data);
    });
})