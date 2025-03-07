/***
 * Handler class to update the stores from server database
 * These classes handle, fetching, serializing / deserializing and also fetching related objects
 */

export default class StoreHandler {
    store: any;

    constructor(store: any) {
        this.store = store;
    }

    public fetchFromServer(user: string): Promise<any> {
        return new Promise((resolve, reject) => {})
    }

    public updateInServer(user: string, id: any, data: any): Promise<any> {
        return new Promise((resolve, reject) => {})
    }
}