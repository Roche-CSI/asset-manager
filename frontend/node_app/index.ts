import * as http from "http";
import * as fs from "fs";
import App from "./app";
import { Logger } from "./logger/logger";

const port = 3000;

App.set("port", port);

// const MOUNT_DIR = "/cert";
// const KEY = "yours.key";
// const CERT = "yours.crt";
// const options = {
//     key: fs.readFileSync(`${MOUNT_DIR}/${process.env.KEY_FILE_NAME || KEY}`),
//     cert: fs.readFileSync(`${MOUNT_DIR}/${process.env.CERT_FILE_NAME || CERT}`),
// };

const logger = new Logger();
const server = http.createServer(App);
server.listen(port);

module.exports = App;
