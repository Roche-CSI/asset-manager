// import {URL, URLSearchParams} from "url";

export enum RestMethods {
    GET = "GET",
    PUT = "PUT",
    POST = "POST",
    DELETE = "DELETE"
}

export interface RestFileData {
    group: string
    name: string,
    file: File
}

export function fetchGet(url: string, params?: {}): Promise<any> {
    /***
     * fetch wrapper for improved error handling, partly based on
     * https://www.bezkoder.com/javascript-fetch/
     */

    let fetchURL = new URL(url);
    if (params) {
        fetchURL.search = new URLSearchParams(params).toString();
    }
    // let fetchURL = url;
    return new Promise((resolve, reject) => {
        fetch(fetchURL.toString(), {credentials: 'include', cache: 'no-store'})
            .then(res => {
                if (!res.ok) {
                    let status = 'Server Error with Status Code: ' + res.status;
                    throw new Error(status)
                } else {
                    res.json().then(data => resolve(data))
                }
            }).catch(err => {
                console.log("fetch error:", err);
                reject(err)
        });
    });

}

export function fetchPost(url: string, data: {}, files: RestFileData[] = []): Promise<any> {
    console.log("fetch post:", data);
    return new Promise((resolve, reject) => {
        fetch(url, {
            method: "post",
            credentials: 'include',
            // headers: {
            //     "Content-Type": "application/json" //"multipart/form-data"
            // },
            body: prepareFormData(data, files)
        }).then(res => {
            if (!res.ok) {
                let status = 'Error with Status Code: ' + res.status;
                return res.json().then(err => { throw new Error(JSON.stringify({status: status, data: err}))})
            } else {
                res.json().then(data => resolve(data))
            }
        }).catch((err) => {
            let error;
            try {
                error = JSON.parse(err.message);
            } catch (e) {
                error = err.message;
            }
            reject(error)
        });
    });
}

/**
 * prepares data for upload, separates out file from json data
 */
function prepareFormData(data: {}, files: RestFileData[] = []) {
    if (!files) return JSON.stringify(data);
    let form = new FormData();
    for (const file of files) {
        form.append(file.group, file.file, file.name)
    }
    form.append("data", JSON.stringify(data))
    console.log("form:", Array.from(form.entries()));
    return form
}



export function fetchPut(url: string, data: {}): Promise<any> {
    return new Promise((resolve, reject) => {
        fetch(url, {
            method: "put",
            credentials: 'include',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        }).then(res => {
            if (!res.ok) {
                res.json().then(data => {
                    let status = 'Error with Status Code: ' + res.status;
                    reject({status: status, data: data});
                })
            } else {
                res.json().then(data => resolve(data))
            }
        }).catch(err => reject(err));
    });
}

export function fetchDelete(url: string, params?: {}): Promise<any> {
    let fetchURL = new URL(url);
    if (params) {
        fetchURL.search = new URLSearchParams(params).toString();
    }
    return new Promise((resolve, reject) => {
        fetch(fetchURL.toString(), {
            method: "delete",
            credentials: 'include',
        }).then(res => {
            if (!res.ok) {
                let status = 'Error with Status Code: ' + res.status
                reject(status);
            } else {
                res.json().then(data => resolve(data))
            }
        }).catch(err => reject(err));
    });
}

export async function fetchWithProgress(url: string, method: RestMethods, progress: Function, params?: any): Promise<any> {
    try {
        let fetchURL = new URL(url);
        if (params) {
            fetchURL.search = new URLSearchParams(params).toString();
        }
        // Step 1: start the fetch and obtain a reader
        let response = await fetch(fetchURL.toString(), {"method": method, credentials: 'include',});
        const reader = (response.body as any).getReader();
        if (response.status >= 200 && response.status < 300) {
            // Step 2: get total length
            const contentLength = +((response.headers as any).get('Content-Length') as number);
            // Step 3: read the data
            let receivedLength = 0; // received that many bytes at the moment
            let chunks = []; // array of received binary chunks (comprises the body)
            while (true) {
                const {done, value} = await reader.read();
                if (done) {
                    break;
                }
                chunks.push(value);
                receivedLength += value.length;
                // console.log(`Received ${receivedLength} of ${contentLength}`)
                progress && progress(receivedLength, contentLength);
            }
            // Step 4: concatenate chunks into single Uint8Array
            let chunksAll = new Uint8Array(receivedLength); // (4.1)
            let position = 0;
            for (let chunk of chunks) {
                chunksAll.set(chunk, position); // (4.2)
                position += chunk.length;
            }
            //https://stackoverflow.com/questions/53714922/type-buffer-is-not-assignable-to-type-blobpart
            return new Blob([chunksAll as BlobPart]);
        } else {
            console.error("error in fetching data:", response);
            return null;
        }
    } catch (error) {
        console.error("error:", error)
        return null;
    }
}
