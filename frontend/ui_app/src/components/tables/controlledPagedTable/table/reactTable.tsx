import React from "react";
// import defaultStyles from "../table.module.scss";
import {
  flexRender,
  Header,
  HeaderGroup
} from '@tanstack/react-table';

interface Props {
  table: any;
  TheadComponent?: any;
  styles?: any;
}

/**
 * table component with optional header. ref: https://github.com/TanStack/table/issues/508
 */
const ReactTable = (props: Props) => {
  const { table, styles } = props;

  return (
    <div className={styles?.tableWrapper}>
      <table className='table w-full table-auto datatable-table' id='reactTableFilter'>
        {props.TheadComponent ? props.TheadComponent() :
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
                        <div>
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                        </div>
                      )}
                    </th>
                  )
                })}
              </tr>
            ))}
          </thead>
        }
        <tbody>
          {table.getRowModel().rows.map((row: any) => {
            return (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell: any) => {
                  return (
                    <td key={cell.id} className='!text-body'
                      style={{
                        width:
                          cell?.column?.getSize() !== 150 ? cell?.column?.getSize() : undefined,
                      }}>
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