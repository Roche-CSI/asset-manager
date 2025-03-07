import React, { useEffect } from 'react'
import { DataTable } from 'simple-datatables'
import 'simple-datatables/dist/style.css'

interface TableProps {
  paging: boolean;
  numsPerPage?: number;
  perPageSelect?: any[];
  columns: any[];
  headData: any[];
  renderHead: Function;
  bodyData: object[];
  renderBody: Function;
  styles?: any;
}

const DataTableOne = (props: TableProps) => {
  useEffect(() => {
    const dataTable = new DataTable('#dataTableOne', {
      paging: props.paging,
      perPage: props.numsPerPage || 10,
      perPageSelect: props.perPageSelect || [5, 10, 15, ['All', -1]],
      columns: props.columns,
      tableRender: (_data, table, type) => {
        if (type === 'print') {
          return table
        }
        const tHead = table?.childNodes?.[0]
        const filterHeaders = {
          nodeName: 'TR',
          childNodes: tHead?.childNodes?.[0]?.childNodes?.map((_th, index) => ({
            nodeName: 'TH',
            childNodes: [
              {
                nodeName: 'INPUT',
                attributes: {
                  class: 'datatable-input',
                  type: 'search',
                  'data-columns': `[${index}]`,
                },
              },
            ],
          })),
        }
        tHead?.childNodes?.push(filterHeaders)
        return table
      },
    })
  })


  return (
    <div className='rounded-sm border border-stroke bg-white shadow-default dark:border-strokedark dark:bg-boxdark'>
      <div className='data-table-common data-table-one max-w-full overflow-x-auto leading-4'>
        <table className='table w-full table-auto text-left' id='dataTableOne'>
          {
            props.headData && props.renderHead ? (
              <thead>
                <tr>
                  {props.headData.map((item: any, index: number) => props.renderHead(item, index))}
                </tr>
              </thead>
            ) : null
          }
          {
            props.bodyData && props.renderBody ? (
              <tbody>
                {props.bodyData.map((item: any, index: number) => props.renderBody(item, index))}
              </tbody>
            ) : null
          }
        </table>
      </div>
    </div>
  )
}

export default DataTableOne;
