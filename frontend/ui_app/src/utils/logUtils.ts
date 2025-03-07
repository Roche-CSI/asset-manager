/***
 * extends console.log for customized logging
 * source: https://javascript.plainenglish.io/lets-extend-console-log-8641bda035c3
 */
export default function loadConsole() {
    const DEBUG = true;
    let LOG_PREFIX = new Date().getDate() + '.' + new Date().getMonth() + '.' + new Date().getFullYear() + ' / ' + new Date().getHours() + ':' + new Date().getMinutes() + ':' + new Date().getSeconds();
    // todo: fix line numbers in logging
    // let log = console.log;
    // console.log = function (){
    //     if (!DEBUG) {
    //         return;
    //     }
    //     // 1. Convert args to a normal array
    //     let args = Array.from(arguments);
    //     // OR you can use: Array.prototype.slice.call( arguments );
    //
    //     // 2. Prepend log prefix log string
    //     args.unshift(LOG_PREFIX + ": ");
    //
    //     // 3. Pass along arguments to console.log
    //     log.apply(console, args);
    // };
}