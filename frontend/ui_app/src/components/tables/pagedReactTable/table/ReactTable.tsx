import React from "react";
import {
  flexRender,
  Header,
  HeaderGroup,
} from '@tanstack/react-table';

import Filter from "../filter/Filter";
// import defaultStyles from "../table.module.scss";

interface Props {
  table: any;
  styles?: any;
}


const ReactTable = (props: Props) => {
  const { table, styles } = props;

  return (
    <div className={styles?.tableWrapper}>
      <table className='table w-full table-auto datatable-table' id='reactTableFilter'>
        <thead>
          {table.getHeaderGroups().map((headerGroup: HeaderGroup<any>) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header: Header<any, any>) => {
                return (
                  <th key={header.id} colSpan={header.colSpan} className='!text-body'
                    style={{
                      width:
                        header.getSize() !== 150 ? header.getSize() : undefined,
                    }}>
                    {header.isPlaceholder ? null : (
                      <>
                        <div
                          {...{
                            className: header.column.getCanSort()
                              ? 'cursor-pointer select-none'
                              : '',
                            onClick: header.column.getToggleSortingHandler(),
                          }}
                        >
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                          {{
                            asc: ' ▲',
                            desc: ' ▼',
                          }[header.column.getIsSorted() as string] ?? null}
                        </div>
                        {header.column.getCanFilter() ? (
                          <div>
                            <Filter column={header.column} table={table} />
                          </div>
                        ) : null}
                      </>
                    )}
                  </th>
                )
              })}
            </tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row: any) => {
            return (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell: any) => {
                  return (
                    <td key={cell.id} className='!text-body'>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </td>
                  )
                })}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  );
};

export default ReactTable;