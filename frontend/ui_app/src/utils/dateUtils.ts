import moment from "moment";

const SECOND = 1000; //milliseconds
const MINUTE = 60;
const HOUR = MINUTE * 60;
const DAY = HOUR * 24;

// date format and timezone received from the server
const DEFAULT_DATE_FORMAT = "YYYY/MM/DD HH-mm-ss Z";
const TIMEZONE = "America/Los_Angeles";

export function dateStrToMoment(dateString: string, utc?: boolean): moment.Moment {
    if (utc) {
        return moment.utc(dateString, "YYYY/MM/DD h:mm:ss Z")
    }
    return moment.parseZone(dateString, "YYYY/MM/DD h:mm:ss Z")
}

export function momentDiff(m0: moment.Moment, m1: moment.Moment) {
    return m0.diff(m1)
}

/**
 * Convert datetime to date of client's current time zone
 * @param dateString "YYYY/MM/DD HH-mm-ss Z" dateString received from the server is US/Pacific
 * @param option
 * @returns date string
 */
export function convertToCurrentTimeZone(dateString: string, option?: string) {
    let date = new Date(dateString);
    // console.log(dateString, date.toString(), isValidDate(date));
    if (!isValidDate(date)) {
        date = moment.parseZone(dateString, "YYYY/MM/DD HH-mm-ss Z").toDate();
        // console.log(date);
    }
    if (option === "date") {
        return date.toLocaleDateString("en-US", {timeZone: currentTimeZone()})
    }
    // if is valid date and not date option
    let momentDate = dateStrToMoment(dateString)
    let result = momentDate.clone().local().format("YYYY/MM/DD h:mm:ss A")
    return result
}

export function isValidDate(d: any): boolean {
    return d.toString() !== "Invalid Date";
}

export function currentTimeZone() {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

export function hoursAgo(date: any) {
    return Math.floor(milliSecondsAgo(date) / (1000 * 3600));
}

export function daysAgo(date: any) {
    return Math.floor(hoursAgo(date) / 24);
}

export function milliSecondsAgo(date: any) {
    let d = new Date(date);
    let d1 = new Date();
    return d1.getTime() - d.getTime();
}

export function timeAgoString(date: any) {
    let seconds = milliSecondsAgo(date) / SECOND;
    if (seconds >= DAY) {
        return `${Math.floor(seconds / DAY)} days ago`
    }else if (seconds >= HOUR){
        return `${Math.floor(seconds / HOUR)} hours ago`
    }else {
        return `${Math.floor(seconds / MINUTE)} minutes ago`
    }
}


/**
 * utility to parse datestring into a Date object
 * @param dateString
 * @param format
 */
export function stringToDate(dateString: string, format: any = DEFAULT_DATE_FORMAT): Date {
    format = format || dateString;
    let normalized: string = dateString.replace(/[^a-zA-Z0-9]/g, '-');
    let normalizedFormat: string = format.toLowerCase().replace(/[^a-zA-Z0-9]/g, '-');
    let formatItems: string[] = normalizedFormat.split('-');
    let dateItems: string[] = normalized.split('-');

    let monthIndex = formatItems.indexOf("mm");
    let dayIndex = formatItems.indexOf("dd");
    let yearIndex = formatItems.indexOf("yyyy");
    let hourIndex = formatItems.indexOf("hh");
    let minutesIndex = formatItems.indexOf("ii");
    let secondsIndex = formatItems.indexOf("ss");
    let timeZoneIndex = formatItems.indexOf("z")

    let today = new Date();
    let year: number = yearIndex > -1? parseInt(dateItems[yearIndex]) : today.getFullYear();
    let month: number = monthIndex > -1? parseInt(dateItems[monthIndex]) - 1 : today.getMonth();
    let day: number = dayIndex >- 1? parseInt(dateItems[dayIndex]) : today.getDate();

    let hour: number = hourIndex >-1? parseInt(dateItems[hourIndex]) : today.getHours();
    let minute: number = minutesIndex >-1? parseInt(dateItems[minutesIndex]) : today.getMinutes();
    let second: number = secondsIndex >-1? parseInt(dateItems[secondsIndex]) : today.getSeconds();
    let timeZone = timeZoneIndex >-1? dateItems[timeZoneIndex] : "missing";
    console.log(dateItems);
    console.log("timezone:", timeZone);

    return new Date(year, month, day, hour, minute, second);
}

/**
 * Formats a number of seconds into a string with hours, minutes, and seconds.
 * Example: 10228.486767530441 seconds -> "2h 50m 28s"
 */
export const formatTime = (totalSeconds: number): string => {
    const roundedSeconds = Math.round(Number(totalSeconds));
    const hours = Math.floor(roundedSeconds / 3600);
    const minutes = Math.floor((roundedSeconds % 3600) / 60);
    const seconds = roundedSeconds % 60;
    return `${hours}h ${minutes}m ${seconds}s`;
  };
  