import assert from "assert";
import {fetchGet, fetchPut, fetchPost, fetchDelete} from "../restUtils";

test("test fetchGet", () => {
    let host = "http://127.0.0.1:5000/";
    let url = `${host}/asset_ref?user=user1`;
    url = 'https://randomuser.me/api/';
    console.log("fetching");
    return fetch(url).then(res => res.json().then(parsed =>
        assert(parsed == 2)
        // console.log(JSON.stringify(parsed))
    ));
})