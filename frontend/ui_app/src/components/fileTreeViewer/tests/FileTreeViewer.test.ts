import { getCurrentIds } from "../FileTreeViewer";

const getCurrentId = (folderTree: any, folderId?: string): any[] => {
    let contentIds: any[] = [];
    let fileMap: any = folderTree.fileMap;
    if (!folderId || (folderId === folderTree.rootFolderId)) { //root folder
        for (let x in fileMap) {
            if (!x.includes("/") && fileMap[x].isFile) {
                contentIds.push(fileMap[x].content_id)
            }
        }
    } else { //nested folder
        let children: any[] = fileMap[folderId].children;
        children.forEach((x: any) => x.isFile && contentIds.push(x.content_id))
    }
    return contentIds
}

const sample_fileTree = {
    "rootFolderId": "xsdsdsdwewe",
    "fileMap": {
        "xsdsdsdwewe": {
            "id": "xsdsdsdwewe",
            "name": "test-asset-class-biswalc/1",
            "isDir": true,
            "childrenIds": [
                "ac_waveforms"
            ],
            "childrenCount": 1,
            "parentId": null
        },
        "ac_waveforms/plot_userwave.py": {
            "id": "ac_waveforms/plot_userwave.py",
            "name": "plot_userwave.py",
            "isFile": true,
            "isDir": false,
            "fileType": "python",
            "content_id": "gs:md5_PfvpftCoeHpjkLuuazPJNg==",
            "object_id": "gs:md5_PfvpftCoeHpjkLuuazPJNg==::ac_waveforms/tools/plot_userwave.py",
            "children": [],
            "childrenCount": 0,
            "childrenIds": [],
            "parentId": "ac_waveforms"
        },
        "verify_userwave_server.py": {
            "id": "verify_userwave_server.py",
            "name": "verify_userwave_server.py",
            "isFile": true,
            "isDir": false,
            "fileType": "python",
            "content_id": "gs:md5_m9X5CG6Z/f41e602dbsW6w==",
            "object_id": "gs:md5_m9X5CG6Z/f41e602dbsW6w==::verify_userwave_server.py",
            "children": [],
            "childrenCount": 0,
            "childrenIds": [],
            "parentId": null
        },
        "ac_waveforms": {
            "id": "ac_waveforms",
            "name": "ac_waveforms",
            "isFile": false,
            "isDir": true,
            "fileType": null,
            "object_id": null,
            "children": [
                {
                    "id": "ac_waveforms/plot_userwave.py",
                    "name": "plot_userwave.py",
                    "isFile": true,
                    "isDir": false,
                    "fileType": "python",
                    "content_id": "gs:md5_PfvpftCoeHpjkLuuazPJNg==",
                    "object_id": "gs:md5_PfvpftCoeHpjkLuuazPJNg==::ac_waveforms/tools/plot_userwave.py",
                    "children": [],
                    "childrenCount": 0
                },
            ],
            "childrenCount": 0,
            "childrenIds": [
                "ac_waveforms/plot_userwave.py"
            ],
            "parentId": "xsdsdsdwewe"
        }
    }
}

test("returns content ids for root folder", () => {
    let contentIds: string[] = getCurrentId(sample_fileTree, undefined)
    expect(contentIds).toEqual(["gs:md5_m9X5CG6Z/f41e602dbsW6w=="])
})

test("returns content ids for root folder with id", () => {
    let contentIds: string[] = getCurrentId(sample_fileTree, "xsdsdsdwewe")
    expect(contentIds).toEqual(["gs:md5_m9X5CG6Z/f41e602dbsW6w=="])
})

test("return content ids for nested folder", () => {
    let contentIds: string[] = getCurrentId(sample_fileTree, "ac_waveforms")
    expect(contentIds).toEqual(["gs:md5_PfvpftCoeHpjkLuuazPJNg=="])
})