import { useState } from 'react'

const useOpen = () => {
    const [open, setOpen] = useState(false)

    const handleOpen = () => {
        setOpen(!open)
    }

    const handleOutsideClick = () => {
        if (open) {
            setOpen(false);
        }
    }

    return { open, handleOpen, handleOutsideClick }

}

export default useOpen;
