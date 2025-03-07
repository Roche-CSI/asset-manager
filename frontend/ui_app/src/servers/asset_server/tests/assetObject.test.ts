import AssetObject from "../assetObject";
import assert from "assert";
import data from "./object_data.json";
import objectList from "./objects_list.json";

test('create object instance', () => {
    let object = new AssetObject(data);
    assert(data.id === object.id)
    assert(object.content.id === data.content.id)
})
