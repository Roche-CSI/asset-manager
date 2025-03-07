import React, { useEffect, useState } from 'react';
import {loadConsole} from "./utils";
import {BrowserRouter, Route } from "react-router-dom";
import DefaultLayout from "./components/layout/DefaultLayout";
import './index.css'
/** import custom preset, restore preset to true in config after bootstrap is removed */
import './reset_preflight.css'

function App(props?: any) {
    const [loading, setLoading] = useState(true)

    const preloader = document.getElementById('preloader')

    if (preloader) {
        setTimeout(() => {
            preloader.style.display = 'none'
            setLoading(false)
        }, 0)
    }

    useEffect(() => {
        setTimeout(() => setLoading(false), 0)
    }, [])

    loadConsole();
    // console.log(props);
    return (
        <div className="App">
            <BrowserRouter>
                <DefaultLayout/>
            </BrowserRouter>
        </div>
    );
}

export default App;
