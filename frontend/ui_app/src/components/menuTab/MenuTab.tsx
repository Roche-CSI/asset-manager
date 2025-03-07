import React, { FunctionComponent } from 'react';
import "./breadcrumb.css";
import { Link } from 'react-router-dom'

interface Props {
  paths: object[];
  children?: any;
}

const MenuTab: FunctionComponent<Props> = (props: Props) => {
  // const [openTab, setOpenTab] = useState(1);

  const activeClasses = '!font-bold !border-slate-600'
  const inactiveClasses = 'border-transparent hover:text-primary'

  return (
    <div className='p-7 dark:border-strokedark dark:bg-boxdark'>
      <div className='mb-7.5 flex flex-wrap gap-5 border-b border-stroke dark:border-strokedark sm:gap-10'>
        {props.paths.map((path: any, index: number) => {
          return (
            <Link key={index}
              className={`border-b-2 !text-lg font-medium p-2 md:text-base cursor-pointer hover:text-primary 
                        flex items-center justify-center dark:hover:bg-primary 
                        ${path.active ? activeClasses : inactiveClasses}`}
              to={path.route}
              onClick={() => { }}
            >
              <span className='capitalize'>{path.label}</span>
            </Link>
          )
        })}
      </div>
      <div className=''>
        {props.children}
      </div>
    </div>
  )
}

export default MenuTab;