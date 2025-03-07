import AssetObject from "../assetObject";
import objectList from "./objects_list.json";
import ObjectTree from "../objectTree";

test('objectTree', () => {
    let objTree = new ObjectTree(objectList.map(o => new AssetObject(o)));
    let tree = objTree.fileTree();
})