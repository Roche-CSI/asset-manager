import {UrlParams} from "../index";

test('urlParams', () => {
    let url = "?version=0.0.0&object=gs:md5_ABC123xyz==::test_data/fake/path1/vmzero_bright.log";
    let parsed = new UrlParams(url);
    console.log("params:", parsed.params);
});