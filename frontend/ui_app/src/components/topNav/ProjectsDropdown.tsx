import { Link } from "react-router-dom";
import React, {useRef} from "react";
import { StoreNames, useStore } from "../../stores";
import DefaultHandle from "../dropDown/reactSelectDropDown/DefaultHandle";
import useOpen from '../dropDown/reactSelectDropDown/useOpen';
import { useOutsideClick } from "../commonHooks";
import {ChevronDropdown} from "./ChevronDropDown";

const ProjectsDropdown: React.FC = () => {
    const userStore = useStore(StoreNames.userStore, true);
    const classIdStore = useStore(StoreNames.classIdStore);
    const projects = userStore.get('projects')
    const activeProject = userStore.get('active_project')

    const { open, handleOpen, handleOutsideClick } = useOpen()
    const triggerRef = useRef<HTMLInputElement>(null)
    /** Handle outside click */
    useOutsideClick(triggerRef, handleOutsideClick)

    const handleProjectSelection = (id: string) => {
        userStore.set("active_project", id)
        classIdStore.didFullUpdate = false; //force update class list
    }

    const trigger: any =
        <div className={`flex flex-row items-center w-fit cursor-pointer gap-1 text-white font-bold
            ${open && ''}`} ref={triggerRef}
            onClick={handleOpen}
            key={'trigger'}>
            {projects?.[activeProject]?.description}
            <div className='pl-2 pr-24 pt-1'>
                <DefaultHandle open={open} />
            </div>
        </div>

    const items = () => {
        const ls = Object.keys(projects).map((id: string, index: number) => {
            const proj: any = projects[id]
            return (
                <button
                    className='flex px-2 py-1 text-sm hover:bg-whiter hover:text-primary hover:font-semibold transition-colors duration-150 text-neutral-500
                            dark:hover:bg-meta-4 bg-white overflow-hidden whitespace-nowrap text-ellipsis'
                    onClick={() => handleProjectSelection(id)}
                    key={id}
                >
                    {proj.title || proj.name}
                </button>
            )
        })
        ls.push(
            <Link to={'/projects'}
                className='flex py-2 px-2 font-medium hover:bg-whiter hover:text-primary text-sm
                            dark:hover:bg-meta-4 bg-base-100 text-neutral-600'
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
    const options = projects ? Object.values(projects).map((project: any, index: number) => {
        return (
            <div className="block px-4 py-2 text-sm text-gray-700 hover:text-primary hover:underline cursor-pointer"
                 role="menuitem"
                 key={index}
                 onClick={() => handleProjectSelection(project.id)}>
                {project?.title || project?.name}
            </div>
        )
    }) : []
    
    options.push(
        <Link to={'/projects'}
              className='flex py-2 px-4 font-medium hover:bg-whiter hover:text-primary text-sm
                            dark:hover:bg-meta-4 bg-base-100 text-neutral-600'
              key='more'>
            {'More...'}
        </Link>
    )
    if (!activeProject) return null;
    // console.log('activeProject', activeProject)
    const project = projects[activeProject]
    return (
        <ChevronDropdown
            className="border border-base-300 rounded-md"
            label={
                <span className={activeProject ? 'font-semibold': ''}>
                    {project?.title || project.name || project.description || 'Projects'}
                </span>
            }
            buttonClassName="flex flex-col btn btn-sm btn-ghost border border-gray-dark rounded-md text-title-xsm hover:text-primary"
            dropdownClassName="bg-base-100 w-44">
            {options}
        </ChevronDropdown>
    )
}

export default ProjectsDropdown;
