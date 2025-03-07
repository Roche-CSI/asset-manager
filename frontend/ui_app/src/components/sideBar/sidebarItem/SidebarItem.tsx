
import styles from "./sidebaritem.module.scss";
import { Link } from "react-router-dom";
import React, { useRef } from "react";
import { MenuItem } from "../../common";
import { StoreNames, useStore } from "../../../stores";
import DefaultHandle from "../../dropDown/reactSelectDropDown/DefaultHandle";
import useOpen from '../../dropDown/reactSelectDropDown/useOpen';
import { useOutsideClick } from "../../commonHooks";

import DropDownNew from "../../dropDown/reactSelectDropDown/dropdownNew"

export default function SidebarItem(item: MenuItem, active?: string, onSelect?: Function) {
    const userStore = useStore(StoreNames.userStore, true);
    const classIdStore = useStore(StoreNames.classIdStore);
    const projects = userStore.get('projects')
    const activeProject = userStore.get('active_project')

    const { open, handleOpen, handleOutsideClick } = useOpen()
    const triggerRef = useRef<HTMLInputElement>(null)
    /** Handle outside click */
    useOutsideClick(triggerRef, handleOutsideClick)


    const Icon = item.icon;
    const className = (active === item.name) ? `${styles.sidebarListItem} ${styles.active}` : styles.sidebarListItem;
    const isActive = `${active === item.name && 'font-bold'}`

    const onMenuClicked = (e: any) => {
        onSelect && onSelect(item.name);
    }

    const handleProjectSelection = (id: string) => {
        userStore.set("active_project", id)
        classIdStore.didFullUpdate = false; //force update class list
    }

    const trigger: any =
        <div className={`flex flex-row items-center w-fit cursor-pointer gap-1 text-white 
            ${open && ''}`} ref={triggerRef}
            onClick={handleOpen}
            key={'trigger'}
        >
            {projects?.[activeProject]?.description}
            <div className='pl-1 pt-1'>
                <DefaultHandle open={open} />
            </div>
        </div>

    const items = () => {
        const ls = Object.keys(projects).map((id: string, index: number) => {
            const proj: any = projects[id]
            return (
                <button
                    className='flex p-2 font-medium hover:bg-whiter hover:text-primary 
                            dark:hover:bg-meta-4 bg-white overflow-hidden whitespace-nowrap text-ellipsis'
                    onClick={() => handleProjectSelection(id)}
                    key={id}
                >
                    {proj.description}
                </button>
            )
        })
        ls.push(
            <Link to={'/projects'}
                className='flex py-2 px-2 font-medium hover:bg-whiter hover:text-primary 
                            dark:hover:bg-meta-4 bg-white'
                key='more'>
                {'More...'}
            </Link>)
        // console.log(ls)
        return (
            <div className={'flex flex-col'}>
                {ls}
            </div>
        )
    }

    const projectDropDown = () => {
        if (!activeProject) return null;
        return (
            <div key={'facervew'}>
                <DropDownNew
                    customTrigger={trigger}
                    customMenu={items()}
                    className='!w-full mt-2'
                />
            </div>
        )
    }

    return (
        <div>
            {item.name === 'projects' ?
                projectDropDown()
                :
                <Link key={item.name} to={item.route} onClick={onMenuClicked}>
                    <div className={`cursor-pointer text-white ${isActive}`} key={item.name}>
                        {/* <Icon className={styles.sidebarIcon}/> */}
                        {item.label}
                    </div>
                </Link>
            }
        </div>
    )
}