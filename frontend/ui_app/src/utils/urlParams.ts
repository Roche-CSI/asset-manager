/**
 * Custom URLParams class instead of the standard URLSearchParams class
 * The URLSearchParams class doesn't handle + signs and md5 paddings (i.e. ==) in the object ids.
 */

export default class UrlParams {

    private qs: string;
    params: any;

    constructor(search: string) {
        this.qs = (search).substring(1);
        this.params = {};
        this.parseQueryString();
    }

    parseQueryString() {
        this.qs.split('&').reduce((a: any, b: string) => {
            // let [key, val] = b.split('=');
            let [key, val] = UrlParams.splitParam(b);
            a[key] = val;
            return a;
        }, this.params);
    }

    get(key: any) {
        return this.params[key];
    }

    /**
     * ignores == instances and splits with only =
     * this is because: '==' are used for md5 padding
     * @param s
     * @private
     */
    private static splitParam(s: string) {
        let comps: string[] = [];
        let start = 0;
        let i = 0;
        while (i < s.length) {
            if (s[i] === "=") {
                // check for double == which are md5 paddings
                if (s[i + 1] === "=") {
                    i += 2;
                }else {
                    // split and add to comps
                    comps.push(s.substring(start, i));
                    i += 1
                    start = i;
                }
                continue;
            }
            i += 1;
        }
        comps.push(s.substring(start, s.length)); // add the remaining
        return comps
    }
}