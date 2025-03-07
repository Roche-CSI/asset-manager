import React from "react";
import { csvParse, csvUnparse } from "./csvUtils";
import { HotTable } from '@handsontable/react';
import { registerAllModules } from 'handsontable/registry';

import 'handsontable/dist/handsontable.full.css'; //Import the Handsontable styles

interface Props {
    value: any; // comma separated string
    onChange?: Function;
    className?: string;
    readonly?: boolean;
    minCols? : number;
    minRows?: number;
    minSpareRows?: string;
    stretch? : boolean;
    colHeaders?: boolean;
    rowHeaders?: boolean;
    filters?: boolean;
    dropdownMenu?: boolean;
    sort?: boolean;
}

export default function CsvEditor(props: Props) {
    let minCols: number = props.minCols ?? 10;
    let minRows: number = props.minRows ?? 6;
    let defaultGrid = [...Array(minRows)].map(e => Array(minCols));
    let grid = props.value ? csvParse(props.value) : defaultGrid; // converts to array of arrays

    const onChange = (value: string | undefined) => {
        props.onChange && props.onChange(value);
    }

    registerAllModules(); // register Handsontable's modules

    /**
     * Callback to handle changes of the table
     * @param changes 2D array about info of edited cells [[row, prop, oldVal, newVal], ...]
     */
    const changeGrid: (changes: Array<any>) => void = (changes) => {
        if (changes) {
            changes.forEach(c => {
                grid[c[0]][c[1]] = c[3]
            })
            let stringAfterChanges = csvUnparse(grid)
            onChange(stringAfterChanges);
        }
    }

    return (
        <div className={props.className || ""}>
            <HotTable
                data={grid}
                colHeaders={props.colHeaders ?? false}
                rowHeaders={props.rowHeaders ?? false}
                height='auto'
                width='auto'
                stretchH={props.stretch? "all" :"none"}
                licenseKey="non-commercial-and-evaluation"
                minCols={minCols}
                minRows={minRows}
                minSpareRows={props.minSpareRows ? Number(props.minSpareRows): 1}
                readOnly={props.readonly}
                filters={props.filters ?? false}
                dropdownMenu={props.dropdownMenu ?? false}
                multiColumnSorting={props.sort ?? false}
                afterChange={(changes: any) => changeGrid(changes)}
            />
        </div>
    );
}