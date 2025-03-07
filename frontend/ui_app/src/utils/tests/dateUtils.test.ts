import {stringToDate} from "../dateUtils";
import moment from "moment";
import "moment-timezone";

test('stringToDate', () => {

    let test_data = [
        ["2022-03-24 16:23:42-03:00", "YYYY-MM-DD HH:mm:ssZ"]
        // ["22/03/2016 14:03:01", "dd/mm/yyyy hh:ii:ss"]
    ]
    test_data.forEach((data, index) => {
        // let date = stringToDate(data[0], data[1]);
        // console.assert(date instanceof Date);
        let m = moment(data[0], data[1]);
        let d = m.toDate();
        let s = d.toLocaleDateString();
        let tz = moment().tz("America/Los_Angeles").format();
        console.log("date:", s);
    })

    //
    // let date = stringToDate("22/03/2016 14-03-01", "dd/mm/yyyy hh-ii-ss");
    // console.log(date);
})