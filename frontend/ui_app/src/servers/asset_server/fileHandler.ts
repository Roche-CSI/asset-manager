import {FileType} from "./index";

export default class FileHandler {

    public download(url: string, contentType: string): Promise<any> | null {
        return new Promise((resolve, reject) => {
            FileHandler.fileFetch(url)
                .then(blob => FileHandler.parseContentType(blob, contentType))
                .then(data => resolve(data))
                .catch(error => reject(error))
        })
    }

    public downloadWithProgress(url: string, contentType: string, saveAsUrl?: boolean,
        progress?: Function): Promise<any> | null {
       return new Promise((resolve, reject) => {
            FileHandler.fetchWithProgress(url, progress)
                .then(result => {
                    if (result[0]) {
                        FileHandler.parseContentType(result[1], contentType, saveAsUrl).then(data => resolve(data))
                    }else {
                        reject(result[1])
                    }
                }).catch(error => reject(error))
        })
    }

    private static parseContentType(blob: any, fileType: string, saveAsUrl?: boolean): Promise<any> {
        if (saveAsUrl) {
            return new Promise((resolve, reject) => {
                if (blob) {
                    resolve(URL.createObjectURL(blob))
                }else {
                    reject("error blob is null")
                }
            })
        }
        switch (fileType) {
            case FileType.YAML:
            case FileType.JSON: {
                return new Promise((resolve, reject) => {
                    blob.text().then((parsed: string) => resolve(parsed)).catch((err: any) => reject(err))
                }); //jsyaml.load(responseString);
                //JSON.parse(responseString);
            }
            case FileType.IMAGE: {
                //https://stackoverflow.com/questions/50248329/fetch-image-from-api
                return new Promise((resolve, reject) => {
                    if (blob) {
                        resolve(URL.createObjectURL(blob))
                    }else {
                        reject("error blob is null")
                    }
                })
            }

            default: {
                return new Promise((resolve, reject) => {
                    blob.text().then((parsed: string) => resolve(parsed)).catch((err: any) => reject(err))
                });
            }
        }
    }

    /***
     * fetch wrapper for improved error handling, partly based on
     * https://www.bezkoder.com/javascript-fetch/
     */
    private static fileFetch(url: string): Promise<any> {
        let fetchURL = url;
        return new Promise((resolve, reject) => {
            fetch(fetchURL.toString())
                .then(res => {
                    if (!res.ok) {
                        let status = 'Error with Status Code: ' + res.status
                        reject(status);
                    } else {
                        // res.blob().then(blob => blob.text()).then(dataString => resolve(dataString));
                        res.blob().then(blob => resolve(blob));
                    }
                })
                .catch(err => reject(err));
        });
    }

    /** fetch with progress
     * @param url
     * @param progress
     * @private
     */

    private static async fetchWithProgress(url: string, progress?:Function): Promise<any>{
        try {
            // Step 1: start the fetch and obtain a reader
            let response = await fetch(url);
            const reader = (response.body as any).getReader();
            if (response.status >= 200 && response.status < 300) {
                // Step 2: get total length
                const contentLength = +((response.headers as any).get('Content-Length') as number);
                // Step 3: read the data
                let receivedLength = 0; // received that many bytes at the moment
                let chunks = []; // array of received binary chunks (comprises the body)
                while(true) {
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
                for(let chunk of chunks) {
                    chunksAll.set(chunk, position); // (4.2)
                    position += chunk.length;
                }
                //https://stackoverflow.com/questions/53714922/type-buffer-is-not-assignable-to-type-blobpart
                return [true, new Blob([chunksAll as BlobPart])]
            }else {
                return [false, `"error in fetching data:", ${response}`];
            }
        }catch (error) {
            console.error("error:", error)
            return [false, "Permission Denied, You don't have access to this resource"];
        }
    }
}