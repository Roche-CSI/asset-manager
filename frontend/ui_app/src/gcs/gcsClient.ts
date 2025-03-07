import jsyaml from "js-yaml";
import {FileType} from "../servers/asset_server";

export default class GcsClient {

    constructor() {}

    public getGcsFile(url: string, contentType: string): Promise<any> | null {
        return new Promise((resolve, reject) => {
            GcsClient.gcsFetch(url)
                .then(yamlString => GcsClient.parseContentType(yamlString, contentType))
                .then(data => resolve(data))
                .catch(error => reject(error))
        })
    }

    private static parseContentType(responseString: string, fileType: string) {
        switch (fileType) {
            case FileType.YAML: return jsyaml.load(responseString);
            case FileType.JSON: return JSON.parse(responseString);
            default: return responseString;
        }
    }

    private static gcsFetch(url: string): Promise<any> {
        /***
         * fetch wrapper for improved error handling, partly based on
         * https://www.bezkoder.com/javascript-fetch/
         */
        let fetchURL = url;
        return new Promise((resolve, reject) => {
            fetch(fetchURL.toString())
                .then(res => {
                    if (!res.ok) {
                        let status = 'Error with Status Code: ' + res.status
                        reject(status);
                    } else {
                        res.blob().then(blob => blob.text()).then(dataString => resolve(dataString));
                    }
                })
                .catch(err => reject(err));
        });
    }
}