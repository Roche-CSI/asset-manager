import { DBConfig } from "./db_config2";
/**
 * custom singleton database class to handle indexeddb events
 */

class Database {
    name: string;
    version: number;
    objectStoresMeta: any[];
    db: any;

    public constructor() {
        this.name = DBConfig.name;
        this.version = DBConfig.version;
        this.objectStoresMeta = DBConfig.objectStoresMeta;
    }

    /**
     * Initialization: create all object stores in current database
     */
    createStores(dbReq: any) {
        let stores: any = this.objectStoresMeta.map((x: any) => x.store)
        stores.forEach((storeName: any) => {
            let storeMeta: any = this.objectStoresMeta.find((obj: any) => obj.store === storeName)
            let keyPath: string = storeMeta.storeConfig.keyPath;
            let auto: boolean = storeMeta.storeConfig.autoIncrement;
            if (!dbReq.objectStoreNames.contains(storeName)) {
                dbReq.createObjectStore(storeName, { keyPath: keyPath, autoIncrement: auto });
            }
        })
    }

    /**
    * Delete current database
    */
    delete() {
        let deleteRequest: any = indexedDB.deleteDatabase(this.name)
        deleteRequest.onsuccess = () => {
            console.log("deletetion success")
        }
        deleteRequest.onerror = () => {
            console.log("Deletion error: ", deleteRequest.error)
        }
    }

    /**
     * Delete one store in current database
     * @param {string} storeName store name used to be deleted
     */
    deleteStore(storeName: string, dbReq: any) {
        dbReq.deleteObjectStore(storeName)
    }

    /**
     * Open database and perform initialization
     */
    init() {
        return new Promise((resolve, reject) => {
            if (!('indexedDB' in window)) reject('not supported');
            let openRequest: any = indexedDB.open(this.name, this.version);
            openRequest.onupgradeneeded = (e: any) => {
                let dbReq = openRequest.result; //IDBRequest
                console.log(e.oldVersion)
                switch (e.oldVersion) {
                    case 0: // the client had no database, perform initialization
                        this.createStores(dbReq);
                        break;
                    case 1: // roll out new ver, delete and recreate stores
                        this.delete();
                        this.createStores(dbReq)
                        break;;
                    case 2: // client had version 2 continue
                        break;
                    default:
                        break;
                }
            };
            openRequest.onerror = () => {
                reject(openRequest.error);
            };
            openRequest.onsuccess = (event: any) => {
                // parallel update: if user's db is outdated
                const res: any = event.target.result;
                let dbReq: any = openRequest.result;
                res.onversionchange = () => {
                    dbReq.close();
                    alert('Database upgrade required - Please reload');
                };
                //otherwise, continue working with database using db object
                resolve(dbReq);
            }
        })
    }

    /**
     * Open database and add data to store by storeName
     * @param {string} storeName 
     * @param {any} data an object of key value pairs
     * @param {Function} callback callback function for ease of testing
     */
    public async setBulkItem(storeName: string, data: any, callback?: Function) {
        this.init().then(
            (dbReq: any) => {
                let transaction: any = dbReq.transaction(storeName, "readwrite");
                let store: any = transaction.objectStore(storeName)
                // Set all items in data
                for (let x in data) {
                    store.put(data[x], x)
                }
                transaction.oncomplete = () => {
                    callback && callback()
                }
                transaction.onerror = () => {
                    console.log(transaction.error);
                };
            }
        ).catch((error) => {
            console.log(error)
        })
    }

    public async setItem(storeName: string, key: any, value: any, callback?: Function) {
        this.init().then(
            (dbReq: any) => {
                let transaction: any = dbReq.transaction(storeName, "readwrite");
                let store: any = transaction.objectStore(storeName)
                store.put(value, key)
                transaction.oncomplete = () => {
                    callback && callback()
                }
                transaction.onerror = () => {
                    console.log(transaction.error);
                };
            }
        ).catch((error) => {
            console.log(error)
        })
    }

    /**
     * Open database and get all data from a store
     * @param {string} storeName 
     * @param {Function} callback callback function to update store data after transaction's complete
     * @returns Object contains all the data in store
     */
    public async getBulkItem(storeName: string, callback: Function) {
        return new Promise((resolve, reject) => {
            this.init().then(
                (dbReq: any) => {
                    let data: any = {};
                    let transaction: any = dbReq.transaction(storeName, "readwrite");
                    let store: any = transaction.objectStore(storeName)
                    // called for each key-value pair found by the cursor
                    let request: any = store.openCursor();
                    request.onsuccess = () => {
                        let cursor: any = request.result;
                        if (cursor) {
                            let key: any = cursor.key
                            let value: any = cursor.value
                            try {
                                data[key] = JSON.parse(value)
                            } catch (e: any) {
                                data[key] = value
                            }
                            cursor.continue()
                        }
                    }
                    request.onerror = () => {
                        reject(request.error)
                    }
                    transaction.oncomplete = () => {
                        callback && callback(data)
                        resolve(data);
                    }
                    transaction.onerror = () => {
                        resolve({})
                    };    
                }).catch((error) => {
                    reject(error)
                })
        }
        )
    }

    public async getItem(storeName: string, key: string, callback: Function) {
        return new Promise((resolve, reject) => {
            this.init().then(
                (dbReq: any) => {
                    let transaction: any = dbReq.transaction(storeName, "readwrite");
                    let store: any = transaction.objectStore(storeName)
                    let data: any = store.get(key)
                    transaction.oncomplete = () => {
                        callback && callback(data)
                        resolve(data.result);
                    }
                    transaction.onerror = () => {
                        resolve(null)
                    };    
                }).catch((error) => {
                    reject(error)
                })
        }
        )
    }

    public async deleteItem(storeName: string, key: string, callback: Function) {
        return new Promise((resolve, reject) => {
            this.init().then(
                (dbReq: any) => {
                    let transaction: any = dbReq.transaction(storeName, "readwrite");
                    let store: any = transaction.objectStore(storeName)
                    store.delete(key)
                    transaction.oncomplete = () => {
                        callback && callback()
                        resolve(`deleted ${key}`);
                    }
                }).catch((error) => {
                    reject(error)
                })
        }
        )
    }

}

const database = new Database();
Object.freeze(database)

export default database;