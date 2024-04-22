import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { Router } from './Router';
import ReactGA from "react-ga4";

import './app.scss';
import 'animate.css';

import { Header } from './components/Header';
import { Footer } from './components/Footer';

ReactGA.initialize("G-0RVNMKYYDS");

export class App extends React.Component {



    constructor(){
        super();
        this.state = {
            
        }
        
    }

    componentDidMount() {}

    componentDidUpdate() {}

   

    render() {
        return (
            <>
                <Header />

                <BrowserRouter>
                    <div>
                        <Router />
                    </div>
                </BrowserRouter>


                <Footer />

            </>
        )
    }

}


const container = document.getElementsByClassName('app')[0];
const root = createRoot(container);
root.render(<App />);