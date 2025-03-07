// import assert from "assert";
import {AssetVersion} from "../assetVersion";

const data = require('./version_data.json');

test("create AssetVersion instance", () => {
    let first_version: any = data[0];
    let version = new AssetVersion(first_version);
    expect(version.id).toEqual(first_version.id);
    expect(version.patch).toEqual(first_version.patch);
})

describe('test AssetVersion applyPatches', () => {

    let assetVersions: AssetVersion[] = [];
  
    const testData: any[] = data;
  
    beforeEach(() => {
      assetVersions = testData.map(testVersion => new AssetVersion(testVersion));
    });
  
    test('resolveVersions should correctly apply patches up to given version', () => {
      const resolved = AssetVersion.resolveVersions(assetVersions, assetVersions[2]);
      const addedItems = testData[0].patch.added.concat(testData[1].patch.added).concat(testData[2].patch.added)
      const deletedItems = testData[0].patch.removed.concat(testData[1].patch.removed).concat(testData[2].patch.removed)
      const expected = new Set(addedItems.filter((item: any) => !deletedItems.includes(item)));
      expect(resolved).toEqual(expected);
    });

    test('resolveVersions should correctly apply patches for altered objects', () => {
      const resolved = AssetVersion.resolveVersions([assetVersions[0], assetVersions[1]], assetVersions[1]);
      const removed: string = "gs:md5_vB8U0==::test_data/occal.log"
      let expected = new Set([...testData[0].patch.added, ...testData[1].patch.added])
      expected.delete(removed);
      expect(resolved).toEqual(expected);
    });

    test('should add items when patch contains added items', () => {
        const base = new Set();
        AssetVersion.applyPatch(base, assetVersions[0].patch);
        expect(base).toEqual(new Set(assetVersions[0].patch.added));
      });
    
      test('should remove an item when patch contains removed items', () => {
        const base = new Set(assetVersions[0].patch.added);
        AssetVersion.applyPatch(base, assetVersions[1].patch);
        expect(base.has(assetVersions[1].patch.removed[0])).toBe(false);
      });
  });


  describe('AssetVersion computeDiff', () => {

    let testData: any[] = data;
    
    let assetVersions: AssetVersion[] = [];
  
    beforeEach(() => {
      assetVersions = testData.map(testVersion => new AssetVersion(testVersion));
    });
  
    test('should compute the difference between two patches', () => {
      const version_one: AssetVersion = assetVersions[0];
      const version_two: AssetVersion = assetVersions[1];
      const {diffObject, diffArray} = AssetVersion.computeDiff(assetVersions[0], assetVersions[2]);
      const expectedAdded = assetVersions[2].patch.added.filter(item => !assetVersions[0].patch.added.includes(item));
      const expectedRemoved = assetVersions[2].patch.removed.filter(item => !assetVersions[0].patch.removed.includes(item));
  
      expect(diffObject.added).toEqual(expectedAdded);
      expect(diffObject.removed).toEqual(expectedRemoved);
    });
  
    test('should compute an empty diff if there is no difference', () => {
      const diff = AssetVersion.computeDiff(assetVersions[0], assetVersions[0]);
  
      expect(diff).toEqual({added: [], removed: []});
    });
  });  