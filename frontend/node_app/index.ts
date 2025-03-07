import * as http from "http";
import * as https from "https";
import * as fs from "fs";
import App from "./app";
import { Logger } from "./logger/logger";

const port = 3000;

App.set("port", port);
// const server = http.createServer(App);
// server.listen(port);
const MOUNT_DIR = "/cert";
const KEY = "yours.key";
const CERT = "yours.crt";
const options = {
    key: fs.readFileSync(`${MOUNT_DIR}/${process.env.KEY_FILE_NAME || KEY}`),
    cert: fs.readFileSync(`${MOUNT_DIR}/${process.env.CERT_FILE_NAME || CERT}`),
};

const logger = new Logger();
const server = https.createServer(options, App);
server.listen(port);
// server.on("listening", function(): void {
//     const addr = server.address();
//     const bind = (typeof addr === "string") ? `pipe ${addr}` : `port ${addr.port}`;
//     logger.info(`Listening on ${bind}`);
//  });

module.exports = App;