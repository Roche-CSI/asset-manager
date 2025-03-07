
export class StringExt extends String {
    
    capitalize = () => {
        return this.charAt(0).toUpperCase() + this.slice(1);
    }
    
    toSentenceCase = () => {
        return this.toLowerCase().replace(/(^\s*\w|[.!?]\s*\w)/g, c => c.toUpperCase());
    }
    
    toTitleCase = () => {
        return this.replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase());
    };
    
    normalize = (separator: string="") => {
        // Replace any non-alphanumeric characters (except spaces) with spaces
        let normalized = this.replace(/[^a-zA-Z0-9\s]/g, ' ');
        // Replace multiple spaces with a single space
        normalized = normalized.replace(/\s+/g, ' ');
        // Trim leading and trailing spaces
        normalized = normalized.trim();
        // Replace spaces with the chosen separator
        console.log(this, normalized);
        return new StringExt(normalized.replace(/\s/g, separator));
    };
    
}

/**
 * Checks whether a path starts with or contains a hidden file or a folder.
 * ref: https://stackoverflow.com/questions/8905680/nodejs-check-for-hidden-files/20285137#20285137
 * returns {boolean} - `true` if the source is blacklisted and otherwise `false`.
 */
export const isUnixHiddenPath = function(path: string) {
    return (/(^|\/)\.[^/.]/g).test(path);
};

/**
 * Replace template variables in a string with values from an object
 * @param template string with template variables `Lorem ipsum {var}...`
 * @param obj object with key-value pairs to replace in template {"var": "dolor sit amet", ...}
 */
export const replaceTemplate = (template: string, obj: any) => {
    const pattern = /{\s*(\w+?)\s*}/g; // {property}
    return template.replace(pattern, (_, token) => obj?.[token] || '');
}
