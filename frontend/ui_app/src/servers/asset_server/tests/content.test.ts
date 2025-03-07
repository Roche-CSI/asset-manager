import Content from "../content";
import assert from "assert";
import data from './content_data.json';

test('create Content instance', () => {
    let content = new Content(data);
    assert(data.id === content.id)
    assert(typeof content.size === 'number')
})

test("fetch content from asset_server", async () => {
    let content_ids: any[] = ["gcr:sha256_ecd64f8b07cb92", "gs:md5_cRLB2q43NQH5ohGjNyaC7g=="];
    let contents: any = await Content.getContents("user1", content_ids);
    console.log(contents)
    assert(typeof contents === "object")
    assert(Object.keys(contents).length === 2)
    assert(contents["gs:md5_cRLB2q43NQH5ohGjNyaC7g=="].hasOwnProperty("size"))
})